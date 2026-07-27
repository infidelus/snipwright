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

import subprocess
import tempfile


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
