"""
Run Comskip on a video to detect commercial breaks, on a worker thread.

Comskip decodes the whole file looking for commercials, which can take a few
minutes on an HD recording, so it runs in the background with progress.  We
ask it to write an EDL (the simplest output) into a temporary directory and
hand that path back; the caller parses it and populates the timeline.

Comskip prints progress to stdout in the form of a percentage; we parse that
for a progress bar.
"""

import os
import re
import shutil
import subprocess
import tempfile

from PySide6.QtCore import (
    QCoreApplication,
    QThread,
    Signal,
)


class ComskipError(Exception):
    pass


# Comskip rewrites a single status line in place as it scans, e.g.
#
#   " 0:41:35 - 62378 frames in 116.82 sec(533.97 fps), 1.00 sec(488.00 fps), 56%"
#
# The fields are: position in the recording, frames processed so far, elapsed
# time, and percentage complete.  Updates are separated by carriage returns
# rather than newlines - `text=True` on the Popen turns those into newlines,
# which is the only reason iterating the pipe yields one update at a time.
#
# The percentage is taken from anywhere on the line.  An earlier attempt
# anchored it to the start on the assumption that the figure came first; it
# does not, and the bar sat at 0% for the whole scan.  Do not tighten this
# without output from the real binary in front of you - Comskip's console
# output all goes through one Debug() function and the format is undocumented.
_PERCENT_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")

# The position within the recording, used to tell a new pass from progress.
# Comskip scans a file more than once when it cannot settle on a logo, and on
# each new pass this timestamp returns to the beginning while the frame counter
# keeps climbing.  Measured on a Sky Mix recording: three passes, 234,316
# frames processed for a 109,470-frame programme.
_POSITION_RE = re.compile(r"(\d+):([0-5]\d):([0-5]\d)\s*-\s*\d+\s+frames")


def pick_comskip_ini(filename, default_ini, prefix="comskip_"):
    """Choose the Comskip .ini for one recording.

    When per-channel selection is on, look next to ``default_ini`` for files
    named ``Comskip_<name>.ini``; if ``<name>`` appears in the recording's
    filename, that file is used - the longest, most specific match winning, so
    ``Comskip_BBC One.ini`` beats ``Comskip_BBC.ini``.  With no match, no
    folder, or no default set, the caller's ``default_ini`` is kept.  Matching
    is case-insensitive.  This only helps when the recorder writes the channel
    into the filename (e.g. Tvheadend's ``$c``).
    """
    if not default_ini:
        return default_ini
    folder = os.path.dirname(default_ini)
    if not folder or not os.path.isdir(folder):
        return default_ini
    name = os.path.basename(filename).lower()
    best = None                       # (match_length, path)
    try:
        entries = os.listdir(folder)
    except OSError:
        return default_ini
    for entry in entries:
        low = entry.lower()
        if not (low.startswith(prefix) and low.endswith(".ini")):
            continue
        key = entry[len(prefix):-4]   # the <name> between "Comskip_" and ".ini"
        if key and key.lower() in name:
            if best is None or len(key) > best[0]:
                best = (len(key), os.path.join(folder, entry))
    return best[1] if best else default_ini


def run_comskip(binary, ini, source_path, out_dir,
                progress_cb=None, cancel_cb=None):
    """Run Comskip on source_path, writing output into out_dir.

    Returns the path to the produced .edl file.  Raises ComskipError on
    failure.

    progress_cb(percent, pass_number) is called as scanning proceeds.  Comskip
    scans a file more than once when it cannot settle on a logo, so the
    percentage returns to 0 at the start of each pass; the pass number is
    supplied so the caller can say so rather than appearing to reset itself.
    """
    if not binary or not os.path.isfile(binary):
        raise ComskipError(
            "The Comskip program hasn't been set. Add it in "
            "Settings > Folders."
        )

    cmd = [binary]
    if ini and os.path.isfile(ini):
        cmd.append(f"--ini={ini}")

    # Write all output into our temp dir so we never litter the user's folders.
    cmd.append(f"--output={out_dir}")
    cmd.append(source_path)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        raise ComskipError(f"Could not start Comskip:\n{exc}")

    last_pct = -1
    last_position = None
    pass_no = 1
    if proc.stdout is not None:
        for line in proc.stdout:
            if cancel_cb is not None and cancel_cb():
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                raise ComskipError(QCoreApplication.translate(
                    "Comskip", "Commercial detection cancelled."))

            if progress_cb:
                # A new pass shows up as the position in the recording jumping
                # back towards the start.  Detect it from the position rather
                # than from the percentage falling: the percentage is rounded
                # to whole numbers, so it repeats constantly during a pass and
                # would be far too noisy to use.
                pos = _POSITION_RE.search(line)
                position = None
                if pos:
                    h, m, s = (int(g) for g in pos.groups())
                    position = h * 3600 + m * 60 + s
                    if last_position is not None and position + 60 < last_position:
                        pass_no += 1
                    last_position = position

                m = _PERCENT_RE.search(line)
                if m:
                    try:
                        pct = int(float(m.group(1)))
                    except ValueError:
                        pct = last_pct
                    pct = max(0, min(99, pct))
                    # Report what Comskip reports, including a drop back to 0
                    # at the start of a new pass.  An earlier build clamped
                    # this so it could only rise, which looked tidier but
                    # froze the bar for the whole of every pass after the
                    # first - real work, shown as no progress at all.  The
                    # pass number is what makes a reset make sense.
                    if pct != last_pct:
                        last_pct = pct
                        progress_cb(pct, pass_no)

    proc.wait()

    if proc.returncode not in (0, 1):
        # Comskip returns 0 when commercials were found and 1 when none were
        # found; both are success for our purposes.  Anything else is an error.
        raise ComskipError(
            f"Comskip exited with code {proc.returncode}."
        )

    # Find the EDL it wrote (named after the source file).
    base = os.path.splitext(os.path.basename(source_path))[0]
    edl_path = os.path.join(out_dir, base + ".edl")

    if not os.path.isfile(edl_path):
        # Some builds/configs may not emit an EDL if no commercials were found.
        # Fall back to any .edl in the output dir.
        candidates = [
            os.path.join(out_dir, f)
            for f in os.listdir(out_dir)
            if f.lower().endswith(".edl")
        ]
        if candidates:
            edl_path = candidates[0]
        else:
            raise ComskipError(
                "Comskip produced no EDL output (it may have found no "
                "commercials, or the .ini disables EDL output)."
            )

    if progress_cb:
        progress_cb(100, pass_no)

    return edl_path


class ComskipWorker(QThread):

    finished_ok = Signal(str)     # emits the EDL path
    failed = Signal(str)
    progress = Signal(int, int)

    def __init__(self, binary, ini, source_path, parent=None):
        super().__init__(parent)
        self.binary = binary
        self.ini = ini
        self.source_path = source_path
        self._cancel = False
        self._out_dir = tempfile.mkdtemp(prefix="snipwright-comskip-")

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            edl = run_comskip(
                self.binary,
                self.ini,
                self.source_path,
                self._out_dir,
                progress_cb=self.progress.emit,
                cancel_cb=lambda: self._cancel,
            )
            if not self._cancel:
                self.finished_ok.emit(edl)
        except Exception as exc:
            self.failed.emit(str(exc))

    def cleanup(self):
        """Remove the temporary output directory."""
        try:
            shutil.rmtree(self._out_dir, ignore_errors=True)
        except Exception:
            pass
