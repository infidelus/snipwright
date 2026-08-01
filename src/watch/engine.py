"""The watcher engine: find new recordings, run Comskip, write a .vprj.

Deliberately free of any Qt or UI code so it can be unit-tested headlessly and
reused.  A standalone tray app drives it on a timer; it could equally be driven
from a cron-style one-shot.

For each recording it finds that it hasn't already handled and that has
finished recording, it runs Comskip to detect the commercials and writes a
.vprj of those cuts into the output folder.  It never edits or exports the
recording - the produced project is a starting point the user reviews and
confirms in the editor (via the Batch Manager) before anything is cut.
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
from project.vprj import save_vprj_from_cuts
from repair.comskip import run_comskip, ComskipError, pick_comskip_ini

log = logging.getLogger("snipwright.watch")


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

class ProcessedLog:
    """Remembers which recordings have already been scanned (one path/line)."""

    def __init__(self, path):
        self.path = str(path)
        self._set = set()
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

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                for p in sorted(self._set):
                    f.write(p + "\n")
        except OSError:
            pass

    def contains(self, path):
        return path in self._set

    def add(self, path):
        self._set.add(path)

    def prune_missing(self):
        """Drop entries whose recording no longer exists, so re-recording the
        same path later gets picked up again."""
        before = len(self._set)
        self._set = {p for p in self._set if os.path.exists(p)}
        return before - len(self._set)

    def __len__(self):
        return len(self._set)


# --------------------------------------------------------------------------- #
# Processing
# --------------------------------------------------------------------------- #

def process_recording(source, comskip_binary, comskip_ini, output_dir,
                      progress_cb=None, cancel_cb=None,
                      save_when_empty=True,
                      _run_comskip=run_comskip):
    """Run Comskip on one recording and write a .vprj of the commercials.

    Returns a ProcessResult.  When commercials are found, the project lists
    those cuts.  When none are found and ``save_when_empty`` is true (the
    default), a full-length project with an empty cut list is written anyway, so
    the recording still reaches the Batch Manager ready to review or copy; with
    it false, nothing is written (the old behaviour).  Never raises for a
    Comskip "no commercials" result; genuine failures are returned as
    result.error.
    """
    tmp_dir = tempfile.mkdtemp(prefix="snipwright-watch-")
    try:
        try:
            edl_path = _run_comskip(
                comskip_binary, comskip_ini, source, tmp_dir,
                progress_cb=progress_cb, cancel_cb=cancel_cb,
            )
        except ComskipError as exc:
            return ProcessResult(source, error=str(exc))

        cuts = parse_edl_cuts(edl_path) if edl_path else []
        if not cuts and not save_when_empty:
            return ProcessResult(source, vprj_path=None, cut_count=0)

        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(source))[0]
        vprj_path = os.path.join(output_dir, base + ".vprj")

        # An empty cut list is valid: save_vprj_from_cuts writes a project that
        # keeps the whole recording (no cuts), which is exactly what we want
        # when Comskip found no commercials.
        save_vprj_from_cuts(
            vprj_path, source, cuts,
            duration_seconds=probe_duration(source),
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
              _process=process_recording):
    """Scan all configured roots once.

    on_event(kind, result) is called as work proceeds, with kind one of:
        "processing" (result.source set, about to run Comskip)
        "done"       (a recording was scanned; result has vprj_path/cut_count)
        "skip"       (skipped; result.skipped_reason explains why)
        "error"      (result.error set)

    cancel_cb is a hard stop: it's also passed to Comskip, so the current file
    is abandoned immediately (used on Quit).  pause_cb is a graceful stop: it's
    checked only between files, so the file being processed runs to completion
    and the scan then stops before starting the next one (used on Pause).

    Returns a summary dict with counts.
    """
    cancel_cb = cancel_cb or (lambda: False)
    pause_cb = pause_cb or (lambda: False)
    ignore_patterns = ignore_patterns or []
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
               "skipped": 0, "errors": 0, "ignored": 0, "paused": False}

    # Give any newly-added ignore entries a starting date, and forget the ones
    # that have since been deleted by hand.
    seen_dirty = False
    if ignore_seen is not None:
        seen_dirty = ignore_seen.sync(ignore_patterns)

    log.info(
        "Scan starting: roots=%s, pattern=%s, settle=%ds, %d already on the "
        "processed list.",
        cfg.input_roots, cfg.pattern, cfg.settle_seconds, len(processed),
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
            log.info(
                "Skipped (still recording - not untouched for %ds yet): %s",
                cfg.settle_seconds, name,
            )
            emit("skip", ProcessResult(source, skipped_reason="still recording"))
            continue

        log.info("Processing: %s", name)
        emit("processing", ProcessResult(source))
        source_ini = comskip_ini
        if cfg.ini_by_channel:
            source_ini = pick_comskip_ini(source, comskip_ini)
        log.info(
            "  Comskip .ini: %s",
            os.path.basename(source_ini) if source_ini
            else "(none - Comskip defaults)",
        )
        result = _process(
            source, comskip_binary, source_ini, cfg.output_dir,
            cancel_cb=cancel_cb,
            save_when_empty=cfg.save_when_no_adverts,
        )

        if cancel_cb() and result.error:
            # Cancelled mid-Comskip - don't mark processed, try again next time.
            log.info("Processing cancelled mid-Comskip: %s", name)
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

    # Forget recordings that have since been deleted.
    processed.prune_missing()
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
