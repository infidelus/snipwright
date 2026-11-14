"""Move renamed files to their targets with byte-level progress.

Shared by the TV and Film renamers.  A plain ``shutil.move`` is one opaque
blocking call, so moving a multi-gigabyte recording to a NAS leaves the progress
bar stuck at 0% until the whole transfer finishes.  Here we move file by file
but, when the destination is on a different filesystem (the NAS case), copy in
chunks and report progress as the data actually lands.  Plain writes only reach
the OS write cache - which fills in a second and then drains to the NAS in the
background - so the copy is flushed to the destination periodically and only the
flushed bytes are counted, keeping the bar in step with the real transfer rather
than racing ahead and stalling.  A same-filesystem move stays an instant
``os.rename``.

Progress is reported as permille (0-1000) of the total bytes to move, not the
raw byte count: Qt progress values are 32-bit and a multi-gigabyte byte count
would overflow.
"""

import errno
import os
import shutil
import logging

log = logging.getLogger("snipwright")

_CHUNK = 4 * 1024 * 1024            # 4 MiB per read/write
_SYNC_EVERY = 16 * 1024 * 1024      # force data out to the NAS ~every 16 MiB


def _safe_remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _permille(done, total):
    return int(max(0, min(done, total)) * 1000 / total)


def _flush_to_disk(fout):
    """Block until everything written so far is actually on the destination.

    Plain writes only reach the OS cache, which fills in a flash and then drains
    to the NAS in the background - so without this the progress bar races ahead
    to wherever the cache fills and then stalls while the real transfer happens.
    fdatasync makes the copy keep pace with the actual transfer; fsync is the
    fallback where fdatasync isn't available.
    """
    fout.flush()
    try:
        os.fdatasync(fout.fileno())
    except (AttributeError, OSError):
        try:
            os.fsync(fout.fileno())
        except OSError:
            pass


def _move_one(src, dst, base_copied, total_bytes, label, progress_cb,
              final=None):
    """Move one file from ``src`` to ``dst``.

    Same filesystem -> an instant ``os.rename``.  Different filesystem (e.g. a
    NAS) -> copy in chunks, flushing to the destination roughly every 16 MiB and
    reporting only the bytes that have actually landed (so the bar tracks the
    real transfer, not the OS write cache), then delete the source.  Returns True
    if the move was cancelled part-way, in which case the partial destination is
    removed and the source left untouched.

    ``final``, when given, is where the file really belongs and something is
    already there: the file goes to ``dst`` (a working name beside it) and is
    swapped into ``final`` only once it has fully arrived.  Whatever was at
    ``final`` survives any failure on the way, and the source is removed only
    after the swap.  The old order - delete what was there, then move - lost
    that file whenever the move failed (code scan, 2026-11-13).
    """
    try:
        os.rename(src, dst)
    except OSError as exc:
        if exc.errno != errno.EXDEV:
            raise                                      # a real error, not cross-device
    else:
        if final is not None:
            try:
                os.replace(dst, final)
            except OSError:
                os.rename(dst, src)                    # put it back as it was
                raise
        return False                                   # instant, same filesystem

    committed = 0                                      # bytes confirmed on the destination
    pending = 0                                        # written since the last flush

    def report():
        return progress_cb(
            _permille(base_copied + committed, total_bytes), 1000, label
        )

    try:
        with open(src, "rb") as fin, open(dst, "wb") as fout:
            while True:
                chunk = fin.read(_CHUNK)
                if not chunk:
                    break
                fout.write(chunk)
                pending += len(chunk)
                if pending >= _SYNC_EVERY:
                    _flush_to_disk(fout)               # block until it's really there
                    committed += pending
                    pending = 0
                    if not report():
                        _safe_remove(dst)              # cancelled: drop the partial copy
                        return True
            _flush_to_disk(fout)                       # the final remainder
            committed += pending
            if not report():
                _safe_remove(dst)
                return True
    except Exception:
        _safe_remove(dst)                              # don't leave a half-written file
        raise
    try:
        shutil.copystat(src, dst)                      # best effort; SMB may refuse
    except OSError:
        pass
    if final is not None:
        try:
            os.replace(dst, final)
        except OSError:
            _safe_remove(dst)                          # source and old file both kept
            raise
    os.remove(src)
    return False


def _same_file(a, b):
    """True if `a` and `b` are the same file on disk.

    On a filesystem that ignores case - Windows, and a Samba share mounted
    on Linux - "show s01e01.ts" and "Show S01E01.ts" are one file, so the
    target "exists" when it is the source itself.  Treated as an ordinary
    existing file, overwrite deleted it: the recording.
    """
    from utils.same_file import is_same_file
    return is_same_file(a, b)


def _key(path):
    return os.path.normcase(os.path.abspath(path))


def move_jobs(jobs, overwrite, progress_cb, label_for):
    """Move each ``(row, target)`` in ``jobs`` to its target.

    ``label_for(row)`` gives the file's *original* name.  ``progress_cb(done,
    total, label)`` is called as bytes are copied - ``done``/``total`` in
    permille - and returns False once the user cancels.  On a successful move a
    row's ``path`` is updated to its target and ``status`` set to ``"done"``.

    The label reports what is actually happening to each file: it shows the
    rename (old name -> new name) and then, when the file also changes folder,
    the move - always naming the *new* file, not the original.  The caller's
    progress dialog supplies no verb of its own, so the wording here is the
    whole message.

    Returns ``(done, skipped, failed)``.  No Qt access here, so it's safe to run
    on a background thread.
    """
    sizes = []
    for row, _target in jobs:
        try:
            sizes.append(os.path.getsize(row.path))
        except OSError:
            sizes.append(0)
    total_bytes = max(sum(sizes), 1)                   # avoid divide-by-zero

    done = skipped = failed = 0
    copied = 0
    n = len(jobs)
    # Targets this run has already filled.  Two recordings given one name - an
    # episode recorded twice, in HD and SD - must not have the second delete
    # the first, whatever the overwrite setting.
    placed = set()

    for idx, (row, target) in enumerate(jobs):
        count = " (%d of %d)" % (idx + 1, n)
        old_name = label_for(row)
        new_name = os.path.basename(target)
        src = row.path                      # original path, before reassignment
        renamed = old_name != new_name
        moved = (os.path.abspath(os.path.dirname(row.path))
                 != os.path.abspath(os.path.dirname(target)))

        # Phase labels describing what happens to THIS file.  A renamed-and-
        # moved file shows the rename first and then the move; a file that is
        # only renamed (or only moved) shows just the one that applies.  Either
        # way the new name is what's shown, never the original.
        rename_label = ("Renaming: %s → %s%s" % (old_name, new_name, count)
                        if renamed else None)
        move_label = ("Moving: %s%s" % (new_name, count)) if moved else None
        work_label = move_label or rename_label or (new_name + count)

        # Announce the rename first (the first of the two messages for a file
        # that's both renamed and moved).
        if not progress_cb(_permille(copied, total_bytes), 1000,
                           rename_label or work_label):
            break                                      # cancelled

        if os.path.abspath(target) == os.path.abspath(row.path):
            row.status = "done"                        # already correctly placed
            log.debug("renamer: already in place: %s", src)
            copied += sizes[idx]
            continue

        if _key(target) in placed:
            skipped += 1
            log.warning(
                "renamer: skipped - another file in this run was already "
                "given the name %s; nothing was overwritten: %s", target, src)
            copied += sizes[idx]
            continue

        # The target is this very file under another spelling - a change of
        # case on a filesystem that ignores case.  A plain rename does it;
        # treating it as an existing file to overwrite deleted the recording.
        same = _same_file(src, target)
        exists = os.path.exists(target) and not same
        if exists and not overwrite:
            skipped += 1                               # don't clobber
            log.info(
                "renamer: skipped (target exists, not overwriting): %s", target
            )
            copied += sizes[idx]
            continue

        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            # Now show the move (the second message) before the transfer starts,
            # for a file that was both renamed and is changing folder.
            if move_label and rename_label:
                if not progress_cb(_permille(copied, total_bytes), 1000,
                                   move_label):
                    break
            if exists:
                # Overwrite: land beside the old file, then swap - the old one
                # goes only once the new one has fully arrived.
                cancelled = _move_one(
                    row.path, target + ".part", copied, total_bytes,
                    work_label, progress_cb, final=target,
                )
            else:
                cancelled = _move_one(
                    row.path, target, copied, total_bytes, work_label,
                    progress_cb,
                )
            if cancelled:
                log.info("renamer: cancelled part-way through: %s", src)
                break
            if exists:
                log.info("renamer: overwrote existing target: %s", target)
            placed.add(_key(target))
            row.path = target
            row.status = "done"
            done += 1
            if renamed and moved:
                log.info("renamer: renamed & moved: %s → %s", src, target)
            elif moved:
                log.info("renamer: moved: %s → %s", src, target)
            else:
                log.info("renamer: renamed: %s → %s", src, target)
        except (OSError, shutil.Error) as exc:
            failed += 1
            log.warning("renamer: FAILED: %s → %s (%s)", src, target, exc)
        copied += sizes[idx]

    progress_cb(1000, 1000, "")
    log.info(
        "renamer: finished - %d renamed/moved, %d skipped, %d failed",
        done, skipped, failed,
    )
    return done, skipped, failed
