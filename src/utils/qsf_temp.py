"""Finding and clearing up Quick Stream Fix working copies.

When a recording needs repairing before it can be cut, Snipwright remuxes it
into the system temporary folder and edits that copy instead.  Those working
copies are whole video files - frequently several gigabytes - and until now
nothing ever removed them.

On Linux that went unnoticed because `/tmp` is cleared at reboot.  On Windows
`%TEMP%` is never cleared automatically, so a few sessions of repairing
broadcast recordings can quietly consume tens of gigabytes.  Disk Cleanup and
Storage Sense can remove them, but neither is on by default and neither is
something a user should have to know about to use a video editor.

The rule here is that a working copy is dead as soon as nothing is reading it:
it exists only so the editor has something valid to cut, and once the session
that made it has finished there is no reason to keep it.  A copy left behind by
a crash is caught later by age.
"""

import logging
import os
import tempfile

log = logging.getLogger("snipwright")

# What the editor names its working copies: "<recording> - QSF.ts", and
# "<recording> - QSF (2).ts" when the first name is already in use.
MARKER = " - QSF"

# Only ever consider files that look like video, so a stray match on the marker
# can't delete something unrelated.
VIDEO_EXTS = {".ts", ".m2ts", ".mkv", ".mp4", ".mov", ".avi",
              ".mpg", ".mpeg", ".vob", ".m2v"}


# Working copies live in a folder of their own inside the chosen one.  They
# used to sit loose in it, named "<recording> - QSF.ts" - which is also what
# Quick Stream Fix's Save a Copy suggests for a repaired copy kept beside the
# recording on purpose.  Pointed at a recordings folder, the age sweep below
# would have deleted those kept copies (code scan, 2026-11-13).
WORKING_SUBFOLDER = "snipwright-working"


def temp_dir():
    """Where working copies are written: a folder of our own inside
    base_dir(), so the sweep can never reach anything else."""
    base = base_dir()
    sub = os.path.join(base, WORKING_SUBFOLDER)
    try:
        os.makedirs(sub, exist_ok=True)
        if os.access(sub, os.W_OK):
            return sub
    except OSError:
        pass
    log.warning("Could not use %s for working copies; using %s itself.",
                sub, base)
    return base


def _sweep_folders(folder=None):
    """The folders the listing and the sweeps look in.

    Our own subfolder - plus, while copies made by older versions may still
    be lying loose in it, the system temporary folder itself, but only when
    that IS the chosen folder: nothing a person keeps on purpose lives there.
    A folder the user chose is never swept outside our subfolder.
    """
    if folder:
        return [folder]
    folders = [temp_dir()]
    base = base_dir()
    if os.path.normcase(os.path.abspath(base)) == \
            os.path.normcase(os.path.abspath(tempfile.gettempdir())):
        folders.append(base)
    return folders


def base_dir():
    """The folder chosen for working copies (the setting), or the system
    temporary folder.

    The system temporary folder unless `settings.qsf_temp_dir` names
    somewhere else.  Configurable because retention does not solve the
    problem it looks like it solves: cleaning up afterwards is no help when a
    single working copy needs more room than the drive has in the first
    place, and a working copy is a full remux of the source - roughly the
    size of the original recording.  On Windows the system temporary folder
    is on the system drive, which is the smallest one on most machines and
    the worst place to put several gigabytes of video.

    Falls back silently to the system folder when the configured path is
    missing, is not a folder, or cannot be written to.  A repair that refuses
    to run because a setting has gone stale - a disconnected share, a renamed
    drive - would be a worse failure than the one this exists to prevent.
    """
    configured = ""
    try:
        from config.loader import ensure_config
        configured = str(
            ensure_config().get("settings", {}).get("qsf_temp_dir", "") or ""
        ).strip()
    except Exception:
        configured = ""

    if configured:
        expanded = os.path.expanduser(configured)
        if os.path.isdir(expanded) and os.access(expanded, os.W_OK):
            return expanded
        log.warning(
            "The configured Quick Stream Fix folder is not usable, falling "
            "back to the system temporary folder: %s", expanded,
        )
    return tempfile.gettempdir()


def looks_like_working_copy(path):
    """Whether `path` is one of ours.

    Deliberately strict: the marker must be in the file name *and* the
    extension must be a video one.  This function decides what gets deleted, so
    a false positive is somebody's data.
    """
    stem, ext = os.path.splitext(os.path.basename(path))
    return MARKER in stem and ext.lower() in VIDEO_EXTS


def list_working_copies(folder=None):
    """Every working copy in the temp folder, newest first.

    Returns a list of (path, size_bytes, mtime).  Unreadable entries are
    skipped rather than raising - this feeds a settings page, not a backup.
    """
    out = []
    paths = []
    for each in _sweep_folders(folder):
        try:
            paths += [os.path.join(each, n) for n in os.listdir(each)]
        except OSError:
            continue
    for path in paths:
        if not looks_like_working_copy(path):
            continue
        try:
            if not os.path.isfile(path):
                continue
            st = os.stat(path)
        except OSError:
            continue
        out.append((path, st.st_size, st.st_mtime))
    out.sort(key=lambda row: row[2], reverse=True)
    return out


def human_size(num):
    """A size a person can read: '2.4 GB'."""
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if num < 1024 or unit == "TB":
            return "%.0f %s" % (num, unit) if unit == "bytes" \
                else "%.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f TB" % num


def _norm(path):
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def delete(paths, keep=()):
    """Delete the given working copies, skipping anything in `keep`.

    `keep` is the set of files something is still reading - the recording open
    in the editor, and the source of any export running in the background.
    Returns (files_deleted, bytes_reclaimed).
    """
    protected = {_norm(p) for p in keep if p}
    freed = 0
    count = 0
    for path in paths:
        if _norm(path) in protected:
            continue
        if not looks_like_working_copy(path):
            continue          # never delete something we didn't create
        try:
            size = os.path.getsize(path)
            os.remove(path)
        except OSError:
            continue
        freed += size
        count += 1
    return count, freed


def prune_orphans(max_age_days, keep=(), folder=None):
    """Remove working copies left behind by an earlier session.

    Age is the safeguard: a second copy of Snipwright may be running with a
    working copy of its own, and deleting that would break somebody's edit
    mid-session.  A file older than the threshold cannot belong to a session
    that started today.  0 or less disables the sweep entirely.

    Returns (files_deleted, bytes_reclaimed).
    """
    try:
        days = float(max_age_days)
    except (TypeError, ValueError):
        return 0, 0
    if days <= 0:
        return 0, 0

    import time
    cutoff = time.time() - days * 86400
    stale = [p for p, _s, m in list_working_copies(folder) if m < cutoff]
    return delete(stale, keep=keep)
