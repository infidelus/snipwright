"""Estimating how much longer a job has to run.

Both the export dialog and the Batch Manager show a time remaining, worked out
the same way: measure how long the visible progress has taken so far and
project it forward.  The maths lives here so the two can't drift apart and
quote different figures for the same piece of work.

Two details matter more than the arithmetic:

* **The clock starts at the first real percentage, not when the job starts.**
  Indexing a recording happens before anything can be counted, and on a large
  file that's a good few seconds of silence.  Timing from the job's start would
  fold that dead time into the rate and badly over-estimate everything after.

* **A re-encode gets its own clock.**  When a job moves from stream-copying to
  re-encoding, the bar starts climbing again from zero and the work is orders
  of magnitude slower per percent.  Carrying the earlier rate over would
  promise a finish time it has no hope of meeting, so the estimate is measured
  from the moment the re-encode itself began.
"""

import time


# Phases that re-encode video or audio.  These run at a completely different
# rate from a stream copy and restart the progress bar, so they're timed
# separately.
RECODE_PHASES = ("recode_audio", "recode_full", "rebuild_audio", "crop")


def format_seconds(secs):
    """A short, human-readable duration: '9s', '4m 12s', '1h 02m 30s'."""
    secs = int(round(secs))
    if secs < 60:
        return f"{secs}s"
    m, s = divmod(secs, 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m {s:02d}s"


class EtaTracker:
    """Turns a stream of progress updates into a time remaining.

    Feed it the same ``info`` dicts the exporter emits.  ``remaining`` is then
    the estimate in seconds, or None when there isn't a meaningful one - before
    the first measurable progress, during an indeterminate phase, and once the
    job is finished.  Callers should show nothing (or an ellipsis) rather than
    inventing a figure when it's None.
    """

    def __init__(self):
        self._start = None
        self._recode_start = None
        self._remaining = None

    def reset(self):
        """Forget everything - call between jobs."""
        self._start = None
        self._recode_start = None
        self._remaining = None

    @property
    def remaining(self):
        """Seconds left, or None if there's no meaningful estimate."""
        return self._remaining

    def update(self, info):
        """Take one progress update and return the new estimate (or None)."""
        percent = info.get("percent", 0)
        phase = info.get("phase", "")

        if not isinstance(percent, (int, float)):
            return self._remaining

        # A negative percent means "busy, but with nothing to count" - the
        # mkvmerge mux, the audio graft and the verify pass all report this.
        # There's no rate to measure, so say nothing rather than freeze the
        # last estimate and let it tick down to a lie.
        if percent < 0:
            self._remaining = None
            return None

        now = time.perf_counter()

        if self._start is None and percent > 0:
            self._start = now

        recoding = phase in RECODE_PHASES
        if recoding:
            if self._recode_start is None and percent > 0:
                self._recode_start = now
            base = self._recode_start
        else:
            # Back to copying (or never left): the re-encode clock is stale.
            self._recode_start = None
            base = self._start

        if base is None or not 0 < percent < 100:
            self._remaining = None
            return None

        elapsed = now - base
        if elapsed <= 0:
            self._remaining = None
            return None

        estimated_total = elapsed / (percent / 100.0)
        self._remaining = max(0.0, estimated_total - elapsed)
        return self._remaining
