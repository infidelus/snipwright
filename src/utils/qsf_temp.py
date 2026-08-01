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

import os
import tempfile

# What the editor names its working copies: "<recording> - QSF.ts", and
# "<recording> - QSF (2).ts" when the first name is already in use.
MARKER = " - QSF"

# Only ever consider files that look like video, so a stray match on the marker
# can't delete something unrelated.
VIDEO_EXTS = {".ts", ".m2ts", ".mkv", ".mp4", ".mov", ".avi",
              ".mpg", ".mpeg", ".vob", ".m2v"}


def temp_dir():
    """Where working copies are written."""
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
    folder = folder or temp_dir()
    out = []
    try:
        names = os.listdir(folder)
    except OSError:
        return out
    for name in names:
        path = os.path.join(folder, name)
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


def total_size(folder=None):
    """Bytes currently taken up by working copies."""
    return sum(size for _p, size, _m in list_working_copies(folder))


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
