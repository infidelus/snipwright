"""The watcher engine: find new recordings, detect the adverts, write a project.

Deliberately free of any Qt or UI code so it can be unit-tested headlessly and
reused.  A standalone tray app drives it on a timer; it could equally be driven
from a cron-style one-shot.  This is why the Chalkline entry point it calls
lives in chalkline.py rather than in chalkline_worker.py, which imports Qt.

For each recording it finds that it hasn't already handled and that has
finished recording, it runs the chosen detector - Chalkline or Comskip - to
find the commercials and writes a project of those cuts into the output folder
- a .swproj or a .vprj, whichever Settings > Files & folders chooses.
Which one runs is the editor's setting, not a separate one here: a recording
should not be detected one way unattended and another way by hand.  It never
edits or exports the recording - the produced project is a starting point the
user reviews and confirms in the editor (via the Batch Manager) before
anything is cut.
"""

import calendar
import datetime
import fnmatch
import json
import logging
import os
import shutil
import tempfile
import time

from project.edl import parse_edl_cuts
from project.formats import save_project_from_cuts
from repair.chalkline import run_chalkline, ChalklineError
from repair.comskip import run_comskip, ComskipError, pick_comskip_ini

log = logging.getLogger("snipwright.watch")


# --------------------------------------------------------------------------- #
# Detectors
# --------------------------------------------------------------------------- #

# The two detectors, as stored in the editor's config.  Chalkline is the
# default everywhere, including when the setting is missing or unreadable.
DETECTOR_CHALKLINE = "chalkline"
DETECTOR_COMSKIP = "comskip"
DEFAULT_DETECTOR = DETECTOR_CHALKLINE

# What to call each one in a log line.  The logs are read when something has
# gone wrong, and "Comskip failed" is a great deal more use than "detection
# failed" when only one of the two is even installed.
DETECTOR_NAMES = {
    DETECTOR_CHALKLINE: "Chalkline",
    DETECTOR_COMSKIP: "Comskip",
}


def detector_name(detector):
    """The display name for a detector key, for logs and status messages."""
    return DETECTOR_NAMES.get(detector, str(detector))


class ProcessResult:
    """Outcome of handling one recording."""

    def __init__(self, source, vprj_path=None, cut_count=0, skipped_reason=None,
                 error=None):
        self.source = source
        self.vprj_path = vprj_path
        self.cut_count = cut_count
        self.skipped_reason = skipped_reason
        self.error = error

    @property
    def ok(self):
        return self.error is None and self.skipped_reason is None


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #

def iter_recordings(roots, pattern="*.ts"):
    """Yield recording paths under each root (recursively) matching pattern."""
    seen = set()
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if fnmatch.fnmatch(name.lower(), pattern.lower()):
                    full = os.path.join(dirpath, name)
                    if full not in seen:
                        seen.add(full)
                        yield full


def file_settled(path, settle_seconds, now=None):
    """True if the file hasn't been modified for at least settle_seconds, i.e.
    the recording has almost certainly finished.  Guards against scanning a
    recording that's still being written."""
    if settle_seconds <= 0:
        return True
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return False
    now = now if now is not None else time.time()
    return (now - mtime) >= settle_seconds


def probe_duration(path):
    """Best-effort container duration in seconds (header read, no decode).
    Returns 0.0 if it can't be determined."""
    try:
        import av
        with av.open(path) as container:
            if container.duration:
                return float(container.duration) / 1_000_000.0
    except Exception:
        pass
    return 0.0


# --------------------------------------------------------------------------- #
# Ignore list
# --------------------------------------------------------------------------- #

def load_ignore_patterns(path):
    """Read the ignore list (one programme-title pattern per line).  Blank
    lines and lines starting with '#' are skipped."""
    patterns = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except OSError:
        pass
    return patterns


# How an ignore entry is compared against a recording's file name.
#
#   "start"    - the file name must BEGIN with the entry.  Recording file names
#                start with the programme title, so this is what people mean
#                when they type one, and it will not fire on a word that merely
#                appears later in an episode title.  ("Gone" ignoring "Star Trek
#                S01E03 Where No Man Has Gone Before" is the failure this
#                exists to prevent.)
#   "anywhere" - the entry may appear anywhere in the name.  More catching, and
#                correspondingly easier to catch the wrong thing.
#
# Either way, an entry written with a leading * is always matched anywhere, so
# a keyword can be used without changing the setting for the whole list.
MATCH_START = "start"
MATCH_ANYWHERE = "anywhere"
DEFAULT_MATCH_MODE = MATCH_START


def matching_ignore_patterns(filename, patterns, mode=DEFAULT_MATCH_MODE):
    """The ignore entries that match this recording's file name.

    Returns the entries as written, so the caller can name them in a log line
    or hand them to the pruner - which matches on the text of the line.
    """
    name = os.path.basename(filename).lower()
    hits = []
    for raw in patterns:
        entry = (raw or "").strip()
        if not entry:
            continue
        if entry.startswith("*"):
            needle = entry[1:].strip().lower()
            if needle and needle in name:
                hits.append(raw)
        elif mode == MATCH_ANYWHERE:
            if entry.lower() in name:
                hits.append(raw)
        elif name.startswith(entry.lower()):
            hits.append(raw)
    return hits


def matches_ignore(filename, patterns, mode=DEFAULT_MATCH_MODE):
    """True if any ignore entry matches this recording's file name."""
    return bool(matching_ignore_patterns(filename, patterns, mode))


def rewrite_ignore_file(path, drop):
    """Remove the given entries from the ignore file, leaving everything else -
    comments, blank lines, ordering - exactly as it was.

    Matching is case-insensitive and ignores surrounding whitespace, so an
    entry removed here is the same entry the matcher would have used.  Returns
    the number of lines dropped.
    """
    wanted = {p.strip().lower() for p in drop if p and p.strip()}
    if not wanted:
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return 0

    kept = []
    removed = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") \
                and stripped.lower() in wanted:
            removed += 1
            continue
        kept.append(line)

    if not removed:
        return 0
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(kept)
    except OSError:
        return 0
    return removed


# --------------------------------------------------------------------------- #
# Ignore-list ageing
# --------------------------------------------------------------------------- #

def recording_date(path, today=None):
    """The date a recording was made, taken from its modification time.

    Clamped so a file with a clock-skewed future timestamp can't push an ignore
    entry's last-seen date beyond today.  Returns None if unreadable.
    """
    try:
        stamp = datetime.date.fromtimestamp(os.path.getmtime(path))
    except (OSError, OverflowError, ValueError):
        return None
    today = today or datetime.date.today()
    return min(stamp, today)


def months_before(when, months):
    """The date `months` calendar months before `when`.

    Calendar arithmetic rather than an approximate number of days, so "12
    months" means the same date last year regardless of month lengths.
    """
    months = max(0, int(months))
    year = when.year
    month = when.month - months
    while month <= 0:
        month += 12
        year -= 1
    day = min(when.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def months_between(earlier, later):
    """Whole calendar months from `earlier` to `later` (never negative)."""
    months = (later.year - earlier.year) * 12 + (later.month - earlier.month)
    if later.day < earlier.day:
        months -= 1
    return max(0, months)


class IgnoreSeenLog:
    """Remembers when each ignore entry last matched a *new* recording.

    The date stored is the recording's own timestamp, not the date of the scan
    that noticed it.  That distinction is the whole trick: recordings a
    housemate leaves sitting in the folder are re-matched on every scan, so
    stamping "now" would keep every entry looking permanently fresh and nothing
    would ever age out.  A recording's own date only moves forward when a
    genuinely new episode appears, which is exactly what "still being watched"
    means.

    An entry seen for the first time is stamped with today, so a title added
    this morning doesn't look a decade stale because the only matching
    recordings are old ones.
    """

    def __init__(self, path):
        self.path = str(path)
        self._seen = {}
        self.load()

    # --- persistence ------------------------------------------------------ #

    def load(self):
        self._seen = {}
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        for pattern, text in data.items():
            parsed = self._parse(text)
            if parsed is not None:
                self._seen[pattern] = parsed

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            payload = {p: d.isoformat() for p, d in sorted(self._seen.items())}
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError:
            pass

    @staticmethod
    def _parse(text):
        try:
            return datetime.date.fromisoformat(str(text))
        except (TypeError, ValueError):
            return None

    # --- queries ---------------------------------------------------------- #

    def last_seen(self, pattern):
        return self._seen.get(pattern)

    def __len__(self):
        return len(self._seen)

    # --- updates ---------------------------------------------------------- #

    def sync(self, patterns, today=None):
        """Stamp entries we haven't met before with today, and forget entries
        for titles that are no longer on the list.  Returns True if anything
        changed, so the caller can skip a pointless write."""
        today = today or datetime.date.today()
        current = {p for p in patterns if p and p.strip()}
        changed = False
        for pattern in current:
            if pattern not in self._seen:
                self._seen[pattern] = today
                changed = True
        for gone in [p for p in self._seen if p not in current]:
            del self._seen[gone]
            changed = True
        return changed

    def note(self, pattern, when):
        """Record that `pattern` matched a recording dated `when`, keeping the
        most recent date seen.  Older recordings never drag the date back."""
        if when is None or not pattern:
            return False
        existing = self._seen.get(pattern)
        if existing is None or when > existing:
            self._seen[pattern] = when
            return True
        return False

    def forget(self, patterns):
        for pattern in patterns:
            self._seen.pop(pattern, None)

    # --- staleness -------------------------------------------------------- #

    def aged(self, patterns, today=None):
        """[(pattern, last_seen_date, age_in_days), …] for every entry, oldest
        first.  Entries with no record yet are reported as last seen today."""
        today = today or datetime.date.today()
        rows = []
        for pattern in patterns:
            if not pattern or not pattern.strip():
                continue
            seen = self._seen.get(pattern, today)
            rows.append((pattern, seen, (today - seen).days))
        rows.sort(key=lambda row: (row[1], row[0].lower()))
        return rows

    def stale(self, patterns, months, today=None):
        """The entries not seen for at least `months` calendar months."""
        today = today or datetime.date.today()
        cutoff = months_before(today, months)
        return [row for row in self.aged(patterns, today) if row[1] < cutoff]


def prune_ignore_list(ignore_path, seen, patterns, processed=None,
                      cfg=None):
    """Remove `patterns` from the ignore file and forget their seen-dates.

    When a `processed` log and `cfg` are supplied, any recording still sitting
    in the watched folders that matched one of the removed titles is marked as
    already processed first.  Without that, dropping a title would hand the
    watcher a back-catalogue of old episodes it had been deliberately skipping
    and it would dutifully Comskip the lot - which is not what anyone means by
    tidying up a list.  Genuinely new episodes are unaffected: they aren't on
    the processed log, so they're picked up as normal.

    Returns (lines_removed, recordings_marked).
    """
    patterns = [p for p in patterns if p and p.strip()]
    if not patterns:
        return 0, 0

    marked = 0
    if processed is not None and cfg is not None:
        for source in iter_recordings(cfg.input_roots, cfg.pattern):
            if processed.contains(source):
                continue
            if matching_ignore_patterns(
                    source, patterns,
                    getattr(cfg, "ignore_match_mode", DEFAULT_MATCH_MODE)):
                processed.add(source)
                marked += 1
        if marked:
            processed.save()

    removed = rewrite_ignore_file(ignore_path, patterns)
    seen.forget(patterns)
    seen.save()
    if removed:
        log.info(
            "Pruned %d ignore entry/entries (%s); %d existing recording(s) "
            "marked as already processed so they aren't picked up now.",
            removed, ", ".join(sorted(patterns)), marked,
        )
    return removed, marked


# --------------------------------------------------------------------------- #
# Processed log
# --------------------------------------------------------------------------- #

def root_available(root):
    """Whether a scan root can actually be read right now.

    os.path.isdir() alone is not enough.  A stale NFS file handle leaves the
    mount point looking like a directory while every read of it fails, and an
    empty result from that is indistinguishable from "the share is up and
    holds nothing" - which is how a whole processed list came to be discarded
    twice in one day.  Listing it is the cheap way to tell the difference.
    """
    if not root:
        return False
    try:
        if not os.path.isdir(root):
            return False
        os.listdir(root)
    except OSError:
        return False
    return True


class ProcessedLog:
    """Remembers which recordings have already been scanned (one path/line).

    Entries are only forgotten when the recording has genuinely gone.  That
    sounds obvious and is the whole difficulty: a recording on a network share
    that is rebooting is missing in exactly the way a deleted one is.  Two
    guards, because neither covers the other's case:

    - An entry under a root that cannot be read is never even considered.  The
      root being down is evidence about the root, not about the file.
    - Anything else that goes missing is held for a grace period first, and
      only dropped once it has stayed missing that long.  This is what covers
      a share that is mounted but broken, where the root looks readable and
      the files under it do not.
    """

    def __init__(self, path, missing_path=None, grace_seconds=0):
        self.path = str(path)
        self.missing_path = str(missing_path) if missing_path else ""
        self.grace_seconds = max(0, int(grace_seconds or 0))
        self._set = set()
        # path -> unix time it was first noticed missing.
        self._missing_since = {}
        self.load()

    def load(self):
        self._set = set()
        try:
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._set.add(line)
        except OSError:
            pass
        self._load_missing()

    def _load_missing(self):
        self._missing_since = {}
        if not self.missing_path:
            return
        try:
            with open(self.missing_path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        for key, when in data.items():
            try:
                self._missing_since[key] = float(when)
            except (TypeError, ValueError):
                continue

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                for p in sorted(self._set):
                    f.write(p + "\n")
        except OSError:
            pass
        self._save_missing()

    def _save_missing(self):
        if not self.missing_path:
            return
        try:
            os.makedirs(os.path.dirname(self.missing_path), exist_ok=True)
            if not self._missing_since:
                # Nothing is missing: remove the sidecar rather than leave an
                # empty file, so its presence means something.
                if os.path.exists(self.missing_path):
                    os.remove(self.missing_path)
                return
            with open(self.missing_path, "w", encoding="utf-8") as f:
                json.dump(self._missing_since, f, indent=2, sort_keys=True)
        except OSError:
            pass

    def contains(self, path):
        return path in self._set

    def add(self, path):
        self._set.add(path)
        # Back from wherever it went: forget it was ever missing, so a file
        # that flickers does not accumulate its way to the grace period.
        self._missing_since.pop(path, None)

    def missing_count(self):
        """How many entries are currently being held over a missing file."""
        return len(self._missing_since)

    def prune_missing(self, roots=None, now=None):
        """Drop entries whose recording has genuinely gone.

        Returns (dropped, held): how many entries were forgotten, and how many
        are missing but being kept for now.  `roots` is the configured scan
        roots; passing them is what allows an unreachable share to be told
        from a deleted file, so a caller that has them should always pass them.
        """
        now = now if now is not None else time.time()

        # Resolved once: on a down share each check can block, and there is no
        # sense paying that per entry.
        unreachable = [
            r for r in (roots or []) if r and not root_available(r)
        ]
        if unreachable:
            log.warning(
                "Not reading %d scan root(s) - %s. Nothing under them will be "
                "removed from the processed list.",
                len(unreachable), ", ".join(unreachable),
            )

        def under_unreachable_root(entry):
            for root in unreachable:
                # A path comparison rather than os.path.commonpath, which
                # raises on paths that share no root at all.
                prefix = os.path.join(os.path.abspath(root), "")
                if os.path.abspath(entry).startswith(prefix):
                    return True
            return False

        keep = set()
        dropped = 0

        for entry in self._set:
            try:
                present = os.path.exists(entry)
            except OSError:
                # A stale handle raises rather than answering.  Not evidence
                # of deletion.
                present = True

            if present:
                keep.add(entry)
                self._missing_since.pop(entry, None)
                continue

            if under_unreachable_root(entry):
                # Say nothing about it, not even that it is missing: when the
                # share returns it must look exactly as it did before.
                keep.add(entry)
                continue

            first = self._missing_since.get(entry)
            if first is None:
                first = now
                self._missing_since[entry] = first

            if self.grace_seconds and (now - first) < self.grace_seconds:
                keep.add(entry)
                continue

            dropped += 1
            self._missing_since.pop(entry, None)

        self._set = keep
        # Anything that is no longer on the list has nothing to be missing
        # from, so its held entry would otherwise linger for ever.
        self._missing_since = {
            k: v for k, v in self._missing_since.items() if k in self._set
        }
        held = len(self._missing_since)

        if dropped or held:
            log.info(
                "Processed list: %d entry(s) forgotten, %d missing but held.",
                dropped, held,
            )
        return dropped, held

    def __len__(self):
        return len(self._set)


# --------------------------------------------------------------------------- #
# Processing
# --------------------------------------------------------------------------- #

def process_recording(source, comskip_binary, comskip_ini, output_dir,
                      progress_cb=None, cancel_cb=None,
                      save_when_empty=True,
                      detector=DEFAULT_DETECTOR,
                      project_format="vprj",
                      _run_comskip=run_comskip,
                      _run_chalkline=run_chalkline):
    """Detect the adverts in one recording and write a project of them -
    a .swproj or a .vprj, as `project_format` says.

    ``detector`` chooses between Chalkline and Comskip.  The Comskip
    arguments are kept whichever is chosen - they are simply unused on the
    Chalkline path, which needs no binary and no .ini - so the injection
    seams and every existing caller keep working unchanged.

    Returns a ProcessResult.  When commercials are found, the project lists
    those cuts.  When none are found and ``save_when_empty`` is true (the
    default), a full-length project with an empty cut list is written anyway, so
    the recording still reaches the Batch Manager ready to review or copy; with
    it false, nothing is written (the old behaviour).  Never raises for a
    "no commercials" result from either detector - for Chalkline that is a
    deliberate answer rather than a failure, and it is the right one on a BBC
    recording; genuine failures are returned as result.error.

    Chalkline never learns from what happens here.  Learning needs ground
    truth, and an unattended detection is a guess: teaching Chalkline from
    its own output would compound whatever it got wrong.  It learns only
    from a project the user has corrected and saved in the editor.
    """
    tmp_dir = tempfile.mkdtemp(prefix="snipwright-watch-")
    try:
        try:
            if detector == DETECTOR_CHALKLINE:
                # run_chalkline hands back (path, info).  The EDL is the
                # result - the same as Comskip's, which is what keeps one
                # parsing path below rather than two - but the info says
                # which technique fired and whether a remembered logo was
                # used, and an unattended run is exactly where nobody is
                # watching, so it goes in the log.
                edl_path, info = _run_chalkline(
                    source, tmp_dir,
                    progress_cb=progress_cb, cancel_cb=cancel_cb,
                )
                log.info(
                    "  Chalkline: logo %s brackets, shape %s, sar %s, "
                    "anchors %s, coincidence %s",
                    info.get("logo_brackets", 0),
                    info.get("shape_brackets", 0),
                    info.get("sar_brackets", 0),
                    info.get("anchor_brackets", 0),
                    info.get("coincidence_brackets", 0),
                )
                if info.get("mask_unfit") is not None:
                    log.info(
                        "  Chalkline: remembered %spx %s logo for %s not "
                        "used - it matches only %.1f%% of this recording",
                        info.get("mask_pixels"), info.get("mask_kind"),
                        info.get("channel"), 100 * info["mask_unfit"],
                    )
                if info.get("mask_brackets"):
                    log.info(
                        "  Chalkline: remembered %spx %s logo for %s "
                        "supplied %s bracket(s)",
                        info.get("mask_pixels"), info.get("mask_kind"),
                        info.get("channel"), info["mask_brackets"],
                    )
                if info.get("reason"):
                    log.info("  Chalkline: no breaks reported - %s",
                             info["reason"])
            else:
                edl_path = _run_comskip(
                    comskip_binary, comskip_ini, source, tmp_dir,
                    progress_cb=progress_cb, cancel_cb=cancel_cb,
                )
        except (ComskipError, ChalklineError) as exc:
            return ProcessResult(source, error=str(exc))

        cuts = parse_edl_cuts(edl_path) if edl_path else []
        if not cuts and not save_when_empty:
            return ProcessResult(source, vprj_path=None, cut_count=0)

        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(source))[0]
        ext = ".swproj" if project_format == "swproj" else ".vprj"
        vprj_path = os.path.join(output_dir, base + ext)

        # An empty cut list is valid: this writes a project that keeps the
        # whole recording (no cuts), which is exactly what we want when the
        # detector found no commercials.  A .swproj also records that the
        # detector found these cuts and nobody has reviewed them yet.
        try:
            from version import VERSION_STRING as made_with
        except Exception:
            made_with = ""
        save_project_from_cuts(
            vprj_path, source, cuts,
            duration_seconds=probe_duration(source),
            made_by=detector if detector in ("chalkline", "comskip")
            else "unknown",
            made_with=made_with,
        )
        return ProcessResult(source, vprj_path=vprj_path, cut_count=len(cuts))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Scan orchestration
# --------------------------------------------------------------------------- #

def scan_once(cfg, processed, comskip_binary=None, comskip_ini=None,
              on_event=None, cancel_cb=None, pause_cb=None,
              ignore_patterns=None, ignore_seen=None,
              detector=None,
              _process=process_recording):
    """Scan all configured roots once.

    on_event(kind, result) is called as work proceeds, with kind one of:
        "processing" (result.source set, about to run the detector)
        "done"       (a recording was scanned; result has vprj_path/cut_count)
        "skip"       (skipped; result.skipped_reason explains why)
        "error"      (result.error set)

    ``detector`` overrides the editor's setting, for a caller that wants to
    force one; left None it is read from the shared config, so the Watcher
    and the editor's Detect Commercials always agree.

    cancel_cb is a hard stop: it's also passed to the detector, so the current
    file is abandoned immediately (used on Quit).  pause_cb is a graceful stop:
    it's checked only between files, so the file being processed runs to
    completion and the scan then stops before starting the next one (used on
    Pause).

    Returns a summary dict with counts.
    """
    cancel_cb = cancel_cb or (lambda: False)
    pause_cb = pause_cb or (lambda: False)
    ignore_patterns = ignore_patterns or []
    if detector is None:
        detector = getattr(cfg, "ad_detector", DEFAULT_DETECTOR)
    name_of_detector = detector_name(detector)
    # Comskip's paths are read whichever detector is in use.  They cost a
    # config read and nothing else, and reading them unconditionally keeps
    # the branch below to one place rather than two.
    if comskip_binary is None or comskip_ini is None:
        comskip_binary, comskip_ini = cfg.comskip_paths()

    def emit(kind, result):
        if on_event:
            try:
                on_event(kind, result)
            except Exception:
                log.exception("watch on_event listener failed")

    seen_paths = []
    summary = {"scanned": 0, "projects": 0, "no_ads": 0,
               "skipped": 0, "errors": 0, "ignored": 0, "paused": False,
               "forgotten": 0, "held": 0, "unreachable": [],
               # When the first still-recording file will have been quiet for
               # the settle time (epoch seconds), so the tray can come back
               # for it then rather than at the next regular scan.
               "settles_at": None}

    # Checked before any work, so the log says plainly that a share was down
    # rather than leaving a scan that found nothing to be read as a scan that
    # found nothing new.
    summary["unreachable"] = [
        r for r in cfg.input_roots if r and not root_available(r)
    ]
    if summary["unreachable"]:
        log.warning(
            "%d of %d scan root(s) could not be read: %s. Recordings under "
            "them are left on the processed list.",
            len(summary["unreachable"]), len(cfg.input_roots),
            ", ".join(summary["unreachable"]),
        )

    # Give any newly-added ignore entries a starting date, and forget the ones
    # that have since been deleted by hand.
    seen_dirty = False
    if ignore_seen is not None:
        seen_dirty = ignore_seen.sync(ignore_patterns)

    log.info(
        "Scan starting: detector=%s, roots=%s, pattern=%s, settle=%ds, %d "
        "already on the processed list.",
        name_of_detector, cfg.input_roots, cfg.pattern, cfg.settle_seconds,
        len(processed),
    )

    for source in iter_recordings(cfg.input_roots, cfg.pattern):
        if cancel_cb():
            log.info("Scan cancelled.")
            break
        # Graceful pause: the previous file (if any) has finished; stop before
        # starting the next one.
        if pause_cb():
            summary["paused"] = True
            log.info("Scan paused before the next file.")
            break
        seen_paths.append(source)
        name = os.path.basename(source)

        # Skip recordings on the ignore list (housemates' programmes, etc.).
        # Deliberately NOT marked processed, so removing a title from the list
        # later lets it be picked up.
        matched = matching_ignore_patterns(
            source, ignore_patterns, getattr(cfg, "ignore_match_mode",
                                             DEFAULT_MATCH_MODE)
        )
        if matched:
            summary["ignored"] += 1
            # Note the recording's own date against each entry it matched, so
            # entries for programmes still being recorded stay fresh and ones
            # for programmes that stopped can age out.
            if ignore_seen is not None:
                when = recording_date(source)
                for pattern in matched:
                    if ignore_seen.note(pattern, when):
                        seen_dirty = True
            # Name the entry that matched.  With a long ignore list, "it was
            # on the list" is not enough to work out why something was skipped.
            log.info("Ignored (ignore list entry %s): %s",
                     ", ".join('"%s"' % m for m in matched), name)
            continue
        if processed.contains(source):
            # Already done in an earlier scan.  This is the decision that used
            # to be silent - logging it explains why a recording the user can
            # see in the folder is being left alone (remove it from
            # watch_processed.txt to have it picked up again).
            log.info("Skipped (already on the processed list): %s", name)
            continue
        if not file_settled(source, cfg.settle_seconds):
            summary["skipped"] += 1
            try:
                ready = os.path.getmtime(source) + cfg.settle_seconds
                if summary["settles_at"] is None or ready < summary["settles_at"]:
                    summary["settles_at"] = ready
            except OSError:
                pass
            log.info(
                "Skipped (still recording - not untouched for %ds yet): %s",
                cfg.settle_seconds, name,
            )
            emit("skip", ProcessResult(source, skipped_reason="still recording"))
            continue

        log.info("Processing: %s", name)
        emit("processing", ProcessResult(source))
        source_ini = comskip_ini
        if detector == DETECTOR_COMSKIP:
            if cfg.ini_by_channel:
                source_ini = pick_comskip_ini(source, comskip_ini)
            log.info(
                "  Comskip .ini: %s",
                os.path.basename(source_ini) if source_ini
                else "(none - Comskip defaults)",
            )
        else:
            # Chalkline has no configuration at all, so there is nothing to
            # report here beyond which detector is running - and that is
            # worth saying, because otherwise the log gives no clue why the
            # Comskip .ini line has vanished.
            log.info("  Detector: Chalkline (no configuration needed)")
        result = _process(
            source, comskip_binary, source_ini, cfg.output_dir,
            cancel_cb=cancel_cb,
            save_when_empty=cfg.save_when_no_adverts,
            detector=detector,
            project_format=cfg.project_format,
        )

        if cancel_cb() and result.error:
            # Cancelled mid-detection - don't mark processed, try again next
            # time.
            log.info("Processing cancelled mid-%s: %s",
                     name_of_detector, name)
            break

        if result.error:
            summary["errors"] += 1
            log.warning("Error processing %s: %s", name, result.error)
            emit("error", result)
            # Mark processed so a persistently-bad file doesn't jam every scan.
            processed.add(source)
            processed.save()
            continue

        processed.add(source)
        processed.save()
        summary["scanned"] += 1
        # "projects" tracks recordings that actually had commercials; a
        # full-length project saved for an advert-free recording still counts
        # as "no ads" so the stat stays meaningful.
        if result.cut_count > 0:
            summary["projects"] += 1
            log.info(
                "Done: %s - %d commercial break(s), project written to %s",
                name, result.cut_count, result.vprj_path or cfg.output_dir,
            )
        else:
            summary["no_ads"] += 1
            log.info("Done: %s - no commercials found.", name)
        emit("done", result)

    # Forget recordings that have since been deleted - but only ones we can
    # actually tell are deleted.  The roots go in so an unreachable share is
    # not mistaken for a folderful of vanished recordings.
    dropped, held = processed.prune_missing(roots=cfg.input_roots)
    summary["forgotten"] = dropped
    summary["held"] = held
    processed.save()
    if ignore_seen is not None and seen_dirty:
        ignore_seen.save()
    log.info(
        "Scan finished: %d new, %d with commercials, %d advert-free, "
        "%d still recording, %d ignored, %d error(s).",
        summary["scanned"], summary["projects"], summary["no_ads"],
        summary["skipped"], summary["ignored"], summary["errors"],
    )
    return summary
