"""Running ffmpeg without deadlocking on its own chatter.

Every long-running ffmpeg call here follows the same shape: stdout carries
machine-readable `-progress` output that we read line by line, and stderr
carries warnings we only want if something goes wrong.  The obvious way to
write that - both streams as pipes, read stdout in a loop, read stderr
afterwards - deadlocks.

A pipe holds about 64 KiB.  Once stderr fills, ffmpeg blocks trying to write
the next warning; because it is blocked it writes no more progress to stdout;
because there is no more stdout we sit forever waiting for a line that will
never arrive.  Neither side can move, and the wait is genuinely indefinite -
not slow, stuck.

It takes a surprisingly ordinary file to hit: remuxing an MPEG program stream
produced 3.7 MB of "buffer underflow" warnings, roughly sixty times the buffer,
on a thirty-second clip.  Damaged broadcast recordings - exactly what Quick
Stream Fix exists for - are just as capable of it.

The fix is to give stderr somewhere unbounded to go.  A temporary file costs
nothing, never blocks the writer, and can be read back in full afterwards for
the error message.
"""

import logging
import os
import subprocess
import tempfile

log = logging.getLogger(__name__)

# Longest a quick check - an ffprobe of a file's headers, an mkvmerge -J, one
# frame grabbed with ffmpeg - may take before it is stopped.  Each normally
# answers in well under a second, and a deep probe of a recording on a slow
# network share in a few; two minutes is far beyond any of that, and only
# there so a hang ends.
QUICK_TIMEOUT = 120


def run_quick(cmd, timeout=QUICK_TIMEOUT, **kwargs):
    """subprocess.run() for a short check, with a time limit.

    These checks had none, so a network share that stalled, or a damaged file
    that sent ffprobe round in circles, left the export, the window or the
    batch waiting for ever, and Cancel could not reach it (code scan,
    2026-11-13).  A check that runs out of time is stopped, logged, and
    returned as a FAILED run - returncode -1, nothing on stdout - which every
    caller already handles, because it is exactly what a check that cannot
    read its file returns.

    Only for checks that read headers or a little of a file.  Anything that
    reads a whole recording (a decode, a copy, -count_packets) must not use
    this: a long recording on a busy machine would trip it.
    """
    try:
        return subprocess.run(cmd, timeout=timeout, **kwargs)
    except subprocess.TimeoutExpired:
        target = next((a for a in reversed(cmd)
                       if isinstance(a, str) and os.sep in a), "")
        log.warning("%s gave no answer in %d s and was stopped%s",
                    os.path.basename(str(cmd[0])), timeout,
                    " (reading %s)" % target if target else "")
        text = (kwargs.get("text") or kwargs.get("universal_newlines")
                or kwargs.get("encoding") or kwargs.get("errors"))
        empty = "" if text else b""
        piped = kwargs.get("capture_output")
        out = empty if piped or kwargs.get("stdout") == subprocess.PIPE else None
        err = empty if piped or kwargs.get("stderr") == subprocess.PIPE else None
        return subprocess.CompletedProcess(cmd, -1, stdout=out, stderr=err)


def popen_progress(cmd, **kwargs):
    """Start `cmd` with stdout piped for streaming and stderr to a temp file.

    Returns (proc, err_file).  Read proc.stdout as normal; once the process has
    finished, pass `err_file` to `read_stderr()` for its output.
    """
    err_file = tempfile.TemporaryFile(mode="w+", errors="replace")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=err_file,
        text=True,
        **kwargs,
    )
    return proc, err_file


def read_stderr(err_file, limit=64000):
    """Read back what a process wrote to stderr, and close the file.

    Trimmed to the last `limit` characters: ffmpeg can produce megabytes of
    repetitive warnings, and the tail is the part worth showing - the fatal
    error, when there is one, comes last.
    """
    if err_file is None:
        return ""
    try:
        err_file.seek(0)
        text = err_file.read()
    except Exception:
        return ""
    finally:
        try:
            err_file.close()
        except Exception:
            pass
    if limit and len(text) > limit:
        return "…\n" + text[-limit:]
    return text


def run_cancellable(cmd, cancel_cb=None):
    """Run `cmd` to completion, polling so a cancel request is acted on.

    Equivalent to subprocess.run(capture_output=True) but interruptible.  Both
    streams go to temporary files rather than pipes, so a chatty process can't
    block while we're polling rather than reading.
    """
    if cancel_cb is None:
        return subprocess.run(cmd, capture_output=True, text=True)

    out_file = tempfile.TemporaryFile(mode="w+", errors="replace")
    err_file = tempfile.TemporaryFile(mode="w+", errors="replace")
    proc = subprocess.Popen(cmd, stdout=out_file, stderr=err_file, text=True)
    while proc.poll() is None:
        try:
            if cancel_cb():
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                break
        except Exception:
            pass
        try:
            proc.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            continue

    def _read(f):
        try:
            f.seek(0)
            return f.read()
        except Exception:
            return ""
        finally:
            try:
                f.close()
            except Exception:
                pass

    return subprocess.CompletedProcess(
        cmd, proc.returncode, _read(out_file), _read(err_file)
    )
