"""Owns the batch queue, its settings and the running worker.

The controller lives on the main window, not on the Batch Manager dialog, so a
batch keeps running in the background when the dialog is closed - and so the
queue (and each job's outcome) survives both closing the dialog and restarting
the app.  The dialog is just a view: it reads the controller's jobs and reacts
to its signals.
"""

import os

from PySide6.QtCore import QObject, Signal

from batch.job import (
    BatchJob, QUEUED, RUNNING, DONE, FAILED, CANCELLED, NEEDS_REVIEW,
)
from batch.runner import BatchRunner
from addons.output_profiles import default_profile_name
from utils.eta import EtaTracker


def norm_path(path):
    """A path in the one form every comparison here uses.

    Absolute, normalised and case-folded where the platform is case-insensitive.
    Kept as one shared function precisely because duplicate checks that each
    rolled their own normalisation were how the same recording managed to get
    queued twice.
    """
    if not path:
        return ""
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


class BatchController(QObject):

    # The job list changed (added / removed / reordered / cleared).
    jobs_changed = Signal()
    # Per-job updates, by row index.
    job_started = Signal(int)
    job_progress = Signal(int, dict)
    job_done = Signal(int, dict)
    job_failed = Signal(int, str)
    job_held = Signal(int, str)
    # batch_finished(completed, failed, held, cancelled)
    batch_finished = Signal(int, int, int, bool)
    # Whether a batch is currently running.
    running_changed = Signal(bool)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.jobs = []
        self.runner = None
        # The estimate lives here rather than on the dialog because a batch
        # keeps running with the Batch Manager closed - if the tracker were
        # rebuilt when the window reopened, it would time the remaining work
        # from the moment you looked at it and promise something absurd.
        self._eta = EtaTracker()
        # Exports adopted from the editor: id(job) -> {"worker", "eta"}.  Keyed
        # by identity because rows move as the queue is edited.
        self._external = {}
        # Adopted exports whose row should disappear once the worker confirms
        # it has stopped, rather than the instant we ask it to.
        self._remove_when_cancelled = set()
        self._load_queue()

    # ------------------------------------------------------------------ #
    # Settings (persisted in config["batch"])
    # ------------------------------------------------------------------ #

    def _cfg(self):
        return self.config.setdefault("batch", {})

    @property
    def out_folder(self):
        return self._cfg().get("output_folder") or os.path.join(
            os.path.expanduser("~"), "Videos"
        )

    @out_folder.setter
    def out_folder(self, value):
        self._cfg()["output_folder"] = value
        self._persist()

    @property
    def default_profile(self):
        """Name of the profile a freshly-queued job starts on.  Defaults to a
        favourite (or the first profile) until the user picks one here."""
        return self._cfg().get("default_profile") or default_profile_name(
            self.config
        )

    @default_profile.setter
    def default_profile(self, value):
        self._cfg()["default_profile"] = value
        self._persist()

    @property
    def modifier(self):
        return self._cfg().get("modifier", "")

    @modifier.setter
    def modifier(self, value):
        self._cfg()["modifier"] = value
        self._persist()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #

    def _persist(self):
        try:
            from config.loader import save_config
            save_config(self.config)
        except Exception:
            pass

    def _load_queue(self):
        # The queue lives in its own file (queue.json) rather than in
        # settings.json - it's transient state, and keeping it separate means a
        # problem with one file can't take the other down.  Migrate any queue
        # an older version stored inline under config["batch"]["queue"].
        from config.loader import load_sidecar, save_sidecar
        entries = load_sidecar("queue.json", default=None)
        if entries is None:
            legacy = self.config.get("batch", {}).get("queue")
            if legacy:
                entries = legacy
                save_sidecar("queue.json", entries)
                self.config.get("batch", {}).pop("queue", None)
                self._persist()          # drop the old key from settings.json
            else:
                entries = []
        for data in entries:
            self.jobs.append(BatchJob.from_dict(data))
        # Drop entries whose files are gone - but only finished ones.  A DONE
        # job is just a record; if its source or output has since been deleted
        # there's nothing to keep.  A QUEUED job is left alone even if its file
        # isn't reachable right now, because that's often a temporarily
        # unmounted drive (an NFS/SMB share), not a real deletion - purging it
        # would silently lose pending work the moment a network share was down
        # at startup.
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if self._job_worth_keeping(j)]
        if len(self.jobs) != before:
            self.save_queue()            # persist the pruned list immediately

    @staticmethod
    def _job_worth_keeping(job):
        """Whether a loaded job should stay in the queue.  Finished jobs are
        dropped once their referenced files no longer exist; unfinished jobs
        are always kept (a missing file may just be an unmounted drive)."""
        if job.status != DONE:
            return True
        # A finished job: keep it only while something it refers to still
        # exists - the output if we recorded one, otherwise the source project.
        ref = job.dest_path or job.vprj_path
        return bool(ref and os.path.exists(ref))

    def save_queue(self):
        from config.loader import save_sidecar
        save_sidecar("queue.json", [j.to_dict() for j in self.jobs])

    def persist_now(self):
        """Write the queue to disk immediately, callable from the runner
        thread the instant a job reaches a terminal status.

        The dialog's normal save happens via the job_done/job_failed signals,
        which are delivered on the main thread by the event loop - but if the
        app or Batch Manager is torn down before that delivery drains (for
        example the user stops "after current job" and closes straight away),
        the finished status would never reach disk and the job would come back
        as queued on next launch.  Writing here, synchronously, closes that
        window.  save_config already serialises to a temp file and renames, so
        a concurrent main-thread save can't corrupt it - last write wins, and
        both write the same DONE state.
        """
        self.save_queue()

    # ------------------------------------------------------------------ #
    # Queue editing
    # ------------------------------------------------------------------ #

    def queued_sources(self):
        """The recordings every queued job refers to, normalised.

        Read from the project files rather than taken from the jobs, because a
        job only resolves its source when it runs.  Built once so a caller
        checking a folderful of projects doesn't re-read the whole queue for
        each one.
        """
        from project.vprj import read_source_filename

        sources = set()
        for job in self.jobs:
            if not job.vprj_path:
                continue
            try:
                embedded = read_source_filename(job.vprj_path)
            except Exception:
                continue
            if embedded:
                sources.add(norm_path(embedded))
        return sources

    def jobs_for_source(self, source_path):
        """How many queued jobs already cut this recording.

        Queue-to-Batch writes each project into a staging file stamped with the
        time, so two entries for the same recording never share a .vprj path -
        comparing those would never spot a duplicate.  What matters is the
        recording each project refers to, so that's what's compared, read from
        the project files themselves.
        """
        if not source_path:
            return 0

        from project.vprj import read_source_filename

        target = norm_path(source_path)
        count = 0

        for job in self.jobs:
            if not job.vprj_path:
                continue
            try:
                embedded = read_source_filename(job.vprj_path)
            except Exception:
                continue
            if embedded and norm_path(embedded) == target:
                count += 1

        return count

    def jobs_for_path(self, vprj_path):
        """How many queued jobs already point at this project file.

        Lets the UI ask before adding the same project twice - which is
        usually an accidental double-click, but is a legitimate thing to want
        when comparing output settings, so it's a question rather than a
        refusal.
        """
        if not vprj_path:
            return 0

        target = norm_path(vprj_path)

        return sum(
            1 for j in self.jobs
            if j.vprj_path and norm_path(j.vprj_path) == target
        )

    def add_job(self, vprj_path, profile_name=None):
        self.jobs.append(BatchJob(vprj_path, profile_name or self.default_profile))
        self.save_queue()
        self.jobs_changed.emit()

    def add_jobs(self, paths):
        for p in paths:
            self.jobs.append(BatchJob(p, self.default_profile))
        if paths:
            self.save_queue()
            self.jobs_changed.emit()

    def eta_seconds(self, row=None):
        """Seconds remaining on a job, or None when there's no meaningful
        estimate.  With no row, the job the batch runner is processing."""
        if row is None:
            return self._eta.remaining if self.runner is not None else None
        if 0 <= row < len(self.jobs):
            job = self.jobs[row]
            tracker = self._external.get(id(job))
            if tracker is not None:
                return tracker["eta"].remaining
            if self.runner is not None and row == self.running_row():
                return self._eta.remaining
        return None

    # ------------------------------------------------------------------ #
    # Adopting an export the editor already has in flight
    # ------------------------------------------------------------------ #

    def adopt_export(self, worker, vprj_path, profile_name, dest_path,
                     percent=0, phase="", eta=None):
        """Take over an export that is already running in the editor.

        The worker keeps going untouched - nothing is cancelled and nothing
        restarts - so no encoding time is lost and the file still lands where
        the Save Video dialog said it would.  All this does is give the work a
        row in the queue and re-point the worker's signals here, so the Batch
        Manager can report it and the editor can let go.

        `percent`, `phase` and `eta` carry across where the export had already
        reached, so the row doesn't appear to restart from zero and the time
        remaining stays continuous.

        Returns the BatchJob standing in for the export.
        """
        job = BatchJob(vprj_path, profile_name or self.default_profile)
        job.status = RUNNING
        job.external = True
        job.dest_path = dest_path
        job.fixed_dest = dest_path
        job.percent = int(percent) if isinstance(percent, (int, float)) \
            and percent > 0 else 0
        job.phase = phase or ""

        self.jobs.append(job)
        self._external[id(job)] = {
            "worker": worker,
            "eta": eta if eta is not None else EtaTracker(),
        }
        self.save_queue()
        self.jobs_changed.emit()

        # Bound to the job object rather than a row number: rows shift as other
        # jobs are added or removed, and an index captured now would end up
        # reporting against the wrong one.
        worker.progress.connect(
            lambda info, j=job: self._on_external_progress(j, info)
        )
        worker.finished_ok.connect(
            lambda stats, j=job: self._on_external_done(j, stats)
        )
        worker.failed.connect(
            lambda message, j=job: self._on_external_failed(j, message)
        )
        worker.cancelled.connect(
            lambda j=job: self._on_external_cancelled(j)
        )
        return job

    def has_external_running(self):
        """True while an adopted export is still being written."""
        return any(j.externally_running for j in self.jobs)

    def external_sources(self):
        """The files adopted exports are currently reading, so nothing else
        overwrites one mid-export."""
        out = set()
        for job in self.jobs:
            if not job.externally_running:
                continue
            entry = self._external.get(id(job))
            worker = entry.get("worker") if entry else None
            path = getattr(worker, "source_path", "")
            if path:
                out.add(norm_path(path))
        return out

    def cancel_export(self, row, remove_after=True):
        """Stop one adopted export.

        Encoders don't stop the moment they're asked, so this can't be
        synchronous: the worker is told to cancel and the row is marked as
        stopping.  When the worker confirms, the part-finished file is discarded
        (the export's own cancel path does that) and the row is removed if that
        was the point of asking.

        Returns True if there was an export here to stop.
        """
        if not (0 <= row < len(self.jobs)):
            return False
        job = self.jobs[row]
        if not job.externally_running or job.cancelling:
            return False
        entry = self._external.get(id(job))
        worker = entry.get("worker") if entry else None
        if worker is None:
            return False

        job.cancelling = True
        if remove_after:
            self._remove_when_cancelled.add(id(job))
        try:
            worker.cancel()
        except Exception:
            log.exception("Couldn't cancel adopted export %s", job.name)
            job.cancelling = False
            self._remove_when_cancelled.discard(id(job))
            return False
        self.jobs_changed.emit()
        return True

    def cancel_external(self, ms=10000):
        """Stop every adopted export and wait for the workers to unwind.
        Used when the application is closing, since the threads can't outlive
        it and a half-written file is no use to anyone."""
        self._remove_when_cancelled.clear()
        workers = [entry.get("worker") for entry in self._external.values()]
        for worker in workers:
            if worker is None:
                continue
            try:
                worker.cancel()
            except Exception:
                pass
        for worker in workers:
            if worker is None:
                continue
            try:
                worker.wait(ms)
            except Exception:
                pass

    def _row_of(self, job):
        try:
            return self.jobs.index(job)
        except ValueError:
            return -1

    def _finish_external(self, job, status, message=""):
        self._external.pop(id(job), None)
        job.external = False
        job.cancelling = False
        job.status = status
        job.message = message
        if status == DONE:
            job.percent = 100
        self.save_queue()

    def _on_external_progress(self, job, info):
        entry = self._external.get(id(job))
        if entry is not None:
            entry["eta"].update(info)
        percent = info.get("percent")
        if isinstance(percent, (int, float)) and percent >= 0:
            job.percent = int(percent)
        job.phase = info.get("phase", job.phase)
        row = self._row_of(job)
        if row >= 0:
            self.job_progress.emit(row, info)

    def _on_external_done(self, job, stats):
        self._finish_external(job, DONE)
        row = self._row_of(job)
        if row >= 0:
            self.job_done.emit(row, stats if isinstance(stats, dict) else {})
        self.jobs_changed.emit()

    def _on_external_failed(self, job, message):
        self._finish_external(job, FAILED, message)
        row = self._row_of(job)
        if row >= 0:
            self.job_failed.emit(row, message)
        self.jobs_changed.emit()

    def _on_external_cancelled(self, job):
        # Cancelled on the user's behalf via Remove: now the encoder has
        # actually stopped and its part-finished file is gone, the row can go
        # too.  Doing it here rather than when Remove was pressed means the row
        # never vanishes while its encoder is still shutting down.
        drop = id(job) in self._remove_when_cancelled
        self._remove_when_cancelled.discard(id(job))

        self._finish_external(job, CANCELLED)
        row = self._row_of(job)

        if drop and row >= 0:
            del self.jobs[row]
            self.save_queue()
            self.jobs_changed.emit()
            return

        if row >= 0:
            self.job_failed.emit(row, "")
        self.jobs_changed.emit()

    def running_row(self):
        """The row currently being processed, or -1 if none.  Used to protect
        the active job from being removed while the queue runs."""
        if self.runner is None:
            return -1
        return getattr(self.runner, "current_index", -1)

    def protected_rows(self):
        """Rows that must not be removed: the job the runner is processing, and
        any export running under the editor's own worker.  Without the second,
        an actively-encoding row could be deleted out from under its worker."""
        rows = set()
        active = self.running_row()
        if active >= 0:
            rows.add(active)
        for i, job in enumerate(self.jobs):
            if job.externally_running:
                rows.add(i)
        return rows

    def remove(self, rows):
        """Remove the given rows.  The job that's currently being processed is
        never removed - stop the batch first - but anything waiting can go, even
        while the queue is running."""
        protected = self.protected_rows()
        rows = [r for r in rows if r not in protected]
        if not rows:
            return
        for r in sorted(rows, reverse=True):
            if 0 <= r < len(self.jobs):
                del self.jobs[r]
        # The runner walks this same list by index, so keep its cursor honest.
        if self.runner is not None:
            self.runner.note_removed(rows)
        self.save_queue()
        self.jobs_changed.emit()

    def move(self, row, delta):
        nr = row + delta
        if 0 <= row < len(self.jobs) and 0 <= nr < len(self.jobs):
            # Never move the running job, and never swap another job past it -
            # the UI gates this too, but guard here as the source of truth.
            if self.jobs[row].status == RUNNING or \
                    self.jobs[nr].status == RUNNING:
                return row
            self.jobs[row], self.jobs[nr] = self.jobs[nr], self.jobs[row]
            self.save_queue()
            self.jobs_changed.emit()
            return nr
        return row

    def clear_finished(self):
        """Remove the jobs that actually finished.

        Only DONE jobs go.  A cancelled job never finished - it was interrupted
        and produced no usable output, and pressing Start again picks it up
        where it left off - so it stays, as do failed jobs and ones held for
        review.  Anything unwanted can still be removed by hand.

        Safe to call while the batch is running: DONE jobs are inert, and this
        goes through the same cursor-aware removal as remove(), so the runner's
        position stays correct and the job being processed is untouched.
        """
        done_rows = [i for i, j in enumerate(self.jobs) if j.status == DONE]
        if not done_rows:
            return
        for r in sorted(done_rows, reverse=True):
            del self.jobs[r]
        if self.runner is not None:
            self.runner.note_removed(done_rows)
        self.save_queue()
        self.jobs_changed.emit()

    def set_job_profile(self, row, name):
        if 0 <= row < len(self.jobs):
            self.jobs[row].profile_name = name
            self.save_queue()

    # ------------------------------------------------------------------ #
    # Running
    # ------------------------------------------------------------------ #

    def is_running(self):
        return self.runner is not None

    def is_finishing(self):
        """True when a stop-after-current-job is pending: the batch is still
        running but will halt once the job in progress completes.  Lets the
        dialog restore the "stopping after the current file" message when it's
        reopened, instead of reverting to plain "batch running"."""
        return (self.runner is not None
                and getattr(self.runner, "_finish_current", False))

    def pending_count(self):
        # Jobs that Start would actually process: not already done, and not
        # held for review (those wait for the user to release them via Edit).
        return sum(
            1 for j in self.jobs
            if j.status not in (DONE, NEEDS_REVIEW) and not j.externally_running
        )

    def held_count(self):
        return sum(1 for j in self.jobs if j.status == NEEDS_REVIEW)

    def requeue(self, row):
        """Release a held (needs-review) job back to the queue so the next run
        will retry it - used when the user opens it via Edit to confirm."""
        if 0 <= row < len(self.jobs) and self.jobs[row].status == NEEDS_REVIEW:
            self.jobs[row].status = QUEUED
            self.jobs[row].message = ""
            self.save_queue()
            self.jobs_changed.emit()

    def start(self):
        if self.runner is not None:
            return
        self._eta.reset()
        self.runner = BatchRunner(
            self.jobs, self.out_folder, self.modifier, self.config, self
        )
        self.runner.job_started.connect(self._on_job_started)
        self.runner.job_progress.connect(self._on_job_progress)
        self.runner.job_done.connect(self._on_job_done)
        self.runner.job_failed.connect(self._on_job_failed)
        self.runner.job_held.connect(self._on_job_held)
        self.runner.batch_finished.connect(self._on_batch_finished)
        self.running_changed.emit(True)
        self.runner.start()

    def stop(self, after_current=False):
        if self.runner is not None:
            self.runner.stop(after_current=after_current)

    def wait(self, ms=5000):
        if self.runner is not None:
            self.runner.wait(ms)

    # Runner signal handlers - persist as we go, then re-emit for the dialog.
    def _on_job_started(self, index):
        # Each job is timed on its own: the one before it may have been a
        # stream copy finishing in seconds while this one is a full re-encode.
        self._eta.reset()
        self.job_started.emit(index)

    def _on_job_progress(self, index, info):
        self._eta.update(info)
        self.job_progress.emit(index, info)

    def _on_job_done(self, index, stats):
        self._eta.reset()
        self.save_queue()
        self.job_done.emit(index, stats)

    def _on_job_failed(self, index, message):
        self._eta.reset()
        self.save_queue()
        self.job_failed.emit(index, message)

    def _on_job_held(self, index, reason):
        self._eta.reset()
        self.save_queue()
        self.job_held.emit(index, reason)

    def _on_batch_finished(self, completed, failed, held, cancelled):
        self.runner = None
        self._eta.reset()
        self.save_queue()
        self.running_changed.emit(False)
        self.batch_finished.emit(completed, failed, held, cancelled)
