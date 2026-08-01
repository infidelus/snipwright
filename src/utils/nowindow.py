"""Stop Windows flashing a console window for every helper process.

Snipwright shells out to ffmpeg, ffprobe, mkvmerge and Comskip constantly - well
over forty call sites, several of them inside a loop over scenes.  On Windows
each one pops a console window, and worse, that window takes focus: a user
trying to work in another application while an export runs has the focus yanked
away every few seconds.

Patching forty call sites individually would be tedious and, more to the point,
would keep being wrong - the next call added elsewhere would flash again.  So
this wraps subprocess.Popen once, at startup, and supplies the flags every child
needs unless the caller has said otherwise.

Does nothing at all on Linux and macOS, where the problem doesn't exist.
"""

import subprocess
import sys

# Windows-only; CREATE_NO_WINDOW exists on Python 3.7+ but only on Windows.
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

_installed = False


def install():
    """Make every subprocess in this process start without a console window.

    Safe to call more than once.  Returns True if the patch was applied - i.e.
    on Windows and not already installed.
    """
    global _installed
    if _installed or sys.platform != "win32":
        return False

    original_init = subprocess.Popen.__init__

    def patched_init(self, *args, **kwargs):
        # Respect an explicit choice: a caller that has set creationflags or
        # startupinfo deliberately knows what it wants.
        if not kwargs.get("creationflags") and not kwargs.get("startupinfo"):
            kwargs["creationflags"] = (
                kwargs.get("creationflags", 0) | CREATE_NO_WINDOW
            )
            # CREATE_NO_WINDOW alone is enough for a console application, but
            # SW_HIDE covers the case of a helper that creates its own window.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = si
        return original_init(self, *args, **kwargs)

    subprocess.Popen.__init__ = patched_init
    _installed = True
    return True


def no_window_kwargs():
    """Flags for a single call, for anywhere the global patch isn't in force.

    Returns an empty dict off Windows, so it can be splatted into any
    subprocess call unconditionally:  subprocess.run(cmd, **no_window_kwargs())
    """
    if sys.platform != "win32":
        return {}
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    return {"creationflags": CREATE_NO_WINDOW, "startupinfo": si}
