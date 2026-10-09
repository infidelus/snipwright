"""What Snipwright is running on: the versions of everything it depends on.

Shown in the About box, and copied from there into bug reports.  It exists
because the Python libraries are pinned (see requirements.txt) but nothing can
stop other software changing them afterwards - a user's auto-updater, say, or
a manual pip install into Snipwright's environment.  Rather than check at
every start and nag, the versions are simply visible: anyone who wants to know
what is installed can look, and a library that differs from the version
Snipwright was tested with is marked.

The FFmpeg inside PyAV is listed separately from the FFmpeg program.  They are
two different copies - PyAV brings its own, which does the decoding and the
re-encoding at cut points, while the program is what Snipwright runs for
probing and some export steps - and confusing the two is easy.

Everything here is best effort: a component that cannot be found or asked its
version is reported as missing rather than raising, because the About box
must always open.
"""

import importlib.metadata
import os
import platform
import re
import shutil
import subprocess

# src/utils/components.py -> the project root, where requirements.txt lives.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIREMENTS = os.path.join(_ROOT, "requirements.txt")

_PIN = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([0-9][^\s#]*)")
# A range ("av>=18.1.0,!=19.0.0,<20") names its tested versions in its
# comment, "tested: 18.1.0, 19.0.1".  A range lets pip install a release
# nobody has tried, so it is the tested list that is compared, not the range.
_RANGE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*>=")
_TESTED = re.compile(r"tested:\s*([0-9][0-9.]*(?:\s*,\s*[0-9][0-9.]*)*)")

# The Python libraries worth listing, as (id, distribution name).  bitstring's
# own helpers (bitarray, tibs) are left out: they are bitstring's business,
# and listing them adds lines without helping anyone diagnose anything.
_LIBRARIES = (
    ("pyside6", "PySide6"),
    ("pyav", "av"),
    ("numpy", "numpy"),
    ("bitstring", "bitstring"),
    ("tqdm", "tqdm"),
)


def tested_versions(path=REQUIREMENTS):
    """The versions requirements.txt was tested with, by lower-case name.

    An exact (==) pin gives its version.  A range gives the versions its
    comment lists as tested, joined with " / " - a range with no such list
    is not compared at all, which is why each range line must carry one.
    """
    pins = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                match = _PIN.match(line)
                if match:
                    pins[match.group(1).lower()] = match.group(2)
                    continue
                match = _RANGE.match(line)
                listed = _TESTED.search(line)
                if match and listed:
                    pins[match.group(1).lower()] = " / ".join(
                        v.strip() for v in listed.group(1).split(","))
    except OSError:
        pass
    return pins


def _library_version(dist):
    try:
        return importlib.metadata.version(dist)
    except Exception:
        return None


def _tool_version(path, args, pattern):
    """Ask an external program its version; None if it can't be asked."""
    if not path:
        return None
    try:
        out = subprocess.run(
            [path] + list(args), capture_output=True, text=True,
            errors="replace", timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(pattern, (out.stdout or "") + (out.stderr or ""))
    return match.group(1) if match else None


def _system():
    """The operating system, as a user would name it."""
    try:
        release = platform.freedesktop_os_release()
        name = release.get("PRETTY_NAME") or release.get("NAME")
        if name:
            return name
    except (OSError, AttributeError):
        pass
    if platform.system() == "Windows":
        return f"Windows {platform.release()} ({platform.version()})"
    return f"{platform.system()} {platform.release()}".strip()


def components(config=None):
    """Everything Snipwright depends on, as (id, version, tested) tuples.

    `version` is None for something that could not be found.  `tested` is the
    version requirements.txt pins, for the Python libraries only, or None.
    """
    tested = tested_versions()
    rows = [("system", _system(), None),
            ("python", platform.python_version(), None)]
    for ident, dist in _LIBRARIES:
        rows.append((ident, _library_version(dist), tested.get(dist.lower())))
        if ident == "pyside6":
            try:
                from PySide6.QtCore import qVersion
                rows.append(("qt", qVersion(), None))
            except Exception:
                rows.append(("qt", None, None))
        elif ident == "pyav":
            try:
                import av
                rows.append(("pyav_ffmpeg",
                             getattr(av, "ffmpeg_version_info", None), None))
            except Exception:
                rows.append(("pyav_ffmpeg", None, None))

    # The external programs, found the way the rest of Snipwright finds them:
    # ffmpeg on PATH (with any build chosen in Settings already put first),
    # mkvmerge from Settings or PATH.
    rows.append(("ffmpeg", _tool_version(
        shutil.which("ffmpeg"), ["-version"], r"ffmpeg version (\S+)"), None))
    configured = ((config or {}).get("paths", {}).get("mkvmerge_binary")
                  or "").strip()
    mkvmerge = (configured if configured and os.path.isfile(configured)
                else shutil.which("mkvmerge"))
    rows.append(("mkvmerge", _tool_version(
        mkvmerge, ["--version"], r"mkvmerge v(\S+)"), None))
    return rows


def differs(version, tested):
    """True when a library is not a version Snipwright was tested with."""
    return bool(version and tested and version not in tested.split(" / "))
