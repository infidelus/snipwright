"""Single-instance coordination for the Snipwright Watcher.

The Watcher itself uses this to refuse starting a second copy (two tray icons
and two background scanners would be a mess), and the editor's "Launch Snipwright
Watcher" menu item uses it to tell the user it's already running instead of
spawning a duplicate.  Both agree on one lock-file path defined here so they
can never disagree.
"""

import os
import tempfile


def watcher_lock_path():
    """Return the per-user lock-file path in the system temp directory.

    The owning user's id is folded into the name so two people sharing a
    machine don't block one another.
    """
    if hasattr(os, "getuid"):
        name = "snipwright-watcher-%d.lock" % os.getuid()
    else:
        name = "snipwright-watcher.lock"

    return os.path.join(tempfile.gettempdir(), name)


def watcher_is_running():
    """Best-effort check: True if a live Watcher currently holds the lock.

    Uses QLockFile, which treats a lock left behind by a dead process as stale,
    so a Watcher that crashed won't be mistaken for a running one.  Never
    raises - any problem is reported as "not running" so the caller can simply
    try to start it.
    """
    try:
        from PySide6.QtCore import QLockFile

        probe = QLockFile(watcher_lock_path())
        probe.setStaleLockTime(0)

        if probe.tryLock(50):
            # Nothing was holding it - release immediately so the real Watcher
            # can take it when it starts.
            probe.unlock()
            return False

        return True
    except Exception:
        return False
