"""Owns the batch queue, its settings and the running worker.

The controller lives on the main window, not on the Batch Manager dialog, so a
batch keeps running in the background when the dialog is closed - and so the
queue (and each job's outcome) survives both closing the dialog and restarting
the app.  The dialog is just a view: it reads the controller's jobs and reacts
to its signals.
"""

import logging
import os

from PySide6.QtCore import QObject, Signal

from batch.job import (
    BatchJob, QUEUED, RUNNING, DONE, FAILED, CANCELLED, NEEDS_REVIEW,
)
from batch.runner import BatchRunner
from addons.output_profiles import default_profile_name
from utils.eta import EtaTracker

log = logging.getLogger("snipwright.batch")


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


def staging_dir():
    """The folder Queue to Batch writes its staging projects into.

    Must stay in step with the path main.py's _write_queue_project builds, or
    a staged file would be created in one folder and looked for in another -
    which is the shape of the fault this cleanup exists to fix, only inverted.
    """
    from config.loader import CONFIG_DIR
    return os.path.join(str(CONFIG_DIR), "queue")


def is_staged(path):
    """Whether a project file is one the application staged for the queue.

    Only these may be deleted.  A user who adds their own .vprj through the
    Batch Manager keeps it wherever they saved it, and removing that job must
    leave their file alone - it is their project, not our scratch copy.
    """
    if not path:
        return False
    return norm_path(os.path.dirname(path)) == norm_path(staging_dir())


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
    # all_finished(completed, failed, held, cancelled): every piece of batch
    # work has ended - the runner's queue AND any export handed over from
    # the editor (Send to Batch), which runs outside the runner and never
    # reaches batch_finished.  Counts cover both.  This is what the desktop
    # notification listens to: an adopted export finishing on its own sent
    # nothing (found on Windows in testing), and a queue that ended while an
    # adopted export was still encoding announced itself too early.
    all_finished = Signal(int, int, int, bool)
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
        # Every job id this instance has ever held - loaded at startup or added
        # since.  save_queue() uses it to tell a job another copy of Snipwright
        # added (leave it alone) from one this copy removed (keep it removed).
        self._known_ids = set()
        # How many foreign jobs the last save kept, so the message is logged
        # when that number changes rather than on every single save.
        self._last_foreign_count = 0
        # Tallies for all_finished, since the last time everything was idle.
        self._tally = [0, 0, 0, False]
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
        # Everything we have just loaded counts as known, so a job that is
        # later removed here is not treated as another instance's and put back.
        self._known_ids = {j.id for j in self.jobs}
        # Drop entries whose files are gone - but only finished ones.  A DONE
        # job is just a record; if its source or output has since been deleted
        # there's nothing to keep.  A QUEUED job is left alone even if its file
        # isn't reachable right now, because that's often a temporarily
        # unmounted drive (an NFS/SMB share), not a real deletion - purging it
        # would silently lose pending work the moment a network share was down
        # at startup.
        before = len(self.jobs)
        dropped = [j for j in self.jobs if not self._job_worth_keeping(j)]
        self.jobs = [j for j in self.jobs if self._job_worth_keeping(j)]
        if len(self.jobs) != before:
            self.save_queue()            # persist the pruned list immediately
            self._discard_staged([j.vprj_path for j in dropped])
        # Anything left in the staging folder that no job claims is an orphan
        # from a crash or a kill between writing the project and recording the
        # job.  Swept here, after the queue is loaded, so a file a job still
        # needs is never among them.
        self.sweep_staging()

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
        """Write the queue, keeping jobs another instance may have added.

        The queue used to be written as a straight dump of `self.jobs`, which
        is loaded once at startup.  Two copies of Snipwright therefore each
        held their own snapshot and whichever saved last erased the other's
        additions - silently, with no error and nothing in the log.  The writes
        themselves are atomic, so nothing was ever corrupted; the loss happened
        in the gap between reading at startup and writing minutes later.

        So re-read immediately before writing and merge, which is the pattern
        the logo store already uses (`load_store` -> `store_set` -> `save_store`
        back to back in chalkline.py).

        The distinction that makes this work is between a job we have never
        seen - another instance added it, so leave it alone - and one we HAD
        and no longer have, which this instance deliberately removed and must
        not resurrect.  `_known_ids` is what separates them, and it is why a
        job needs a stable id at all: every other field changes while a job
        sits in the queue.

        Single-instance operation is unaffected: nothing else is writing, so
        the merge finds only our own jobs and the result is what a plain dump
        would have produced.
        """
        from config.loader import load_sidecar, save_sidecar

        mine = [j.to_dict() for j in self.jobs]
        mine_ids = {d["id"] for d in mine}

        try:
            on_disk = load_sidecar("queue.json", default=None)
        except Exception:
            on_disk = None
        if not isinstance(on_disk, list):
            # Nothing readable to merge with - our list is the whole truth.
            save_sidecar("queue.json", mine)
            self._known_ids |= mine_ids
            return

        foreign = []
        for data in on_disk:
            if not isinstance(data, dict):
                continue
            jid = data.get("id")
            if jid and jid in mine_ids:
                continue          # ours, and ours is the newer copy
            if jid and jid in self._known_ids:
                continue          # we had it and removed it - stay removed
            if not jid:
                # Written by a version before ids existed.  Our own jobs came
                # from this same file at startup and were given ids on load,
                # so an id-less entry here is one of ours seen in its old
                # form - keeping it would duplicate the job.  Dropped, and the
                # copy in `mine` carries it forward with its new id.
                continue
            foreign.append(data)

        if foreign and len(foreign) != self._last_foreign_count:
            # Only when the number changes. Every queue edit saves, so logging
            # unconditionally produced three identical lines inside one second
            # during testing, which buries anything worth reading.
            log.info("Batch queue: kept %d job(s) added by another copy of "
                     "Snipwright.", len(foreign))
        self._last_foreign_count = len(foreign)

        save_sidecar("queue.json", foreign + mine)
        # ACCUMULATE our own ids, and never record a foreign one.
        #
        # Both halves matter and both were got wrong first time. Replacing the
        # set rather than adding to it forgets the jobs this instance has
        # deleted, so the next save finds them still on disk, thinks another
        # instance added them, and puts them back. Recording a foreign id
        # claims someone else's job as ours, so the save after that treats it
        # as one we removed and deletes it - which is the very thing this
        # method exists to prevent.
        self._known_ids |= mine_ids

    # ------------------------------------------------------------------ #
    # Staging files
    # ------------------------------------------------------------------ #

    def _staged_in_use(self):
        """Every staging file ANY instance's queue still refers to.

        Read from disk as well as from `self.jobs`, because this decides what
        gets deleted and one instance's queue is not the whole queue.

        This had the same fault `save_queue()` used to have, and it showed up
        the same way: a job removed in one window had its staged project
        deleted, while the other window still held that job and later ran it
        against a file that was gone.  `read_source_filename()` returns nothing
        for a missing file, so it surfaced as "The project file has no source
        recording recorded" - which reads like a corrupt project rather than a
        deleted one.

        `sweep_staging()` uses this too, and there the stakes are higher: it
        deletes anything no job claims, so an instance starting up with a
        partial view could remove staged projects belonging to jobs another
        instance is about to run, with nobody having touched the queue at all.

        Falls back to `self.jobs` alone if the file cannot be read - which
        keeps FEWER files in use and so deletes more, but a queue.json that
        will not parse is a bigger problem than a stale staging file.
        """
        paths = {
            norm_path(j.vprj_path) for j in self.jobs
            if j.vprj_path and is_staged(j.vprj_path)
        }
        try:
            from config.loader import load_sidecar
            on_disk = load_sidecar("queue.json", default=None)
        except Exception:
            on_disk = None
        if isinstance(on_disk, list):
            for data in on_disk:
                if not isinstance(data, dict):
                    continue
                p = data.get("vprj_path")
                if p and is_staged(p):
                    paths.add(norm_path(p))
        return paths

    def _discard_staged(self, paths):
        """Delete the staging projects among `paths` that nothing still needs.

        Called whenever a job leaves the queue.  Queue to Batch writes a fresh
        time-stamped .vprj under the config folder for every job it stages, and
        until now nothing ever removed one, so the folder grew without limit
        for anyone who used the feature regularly.

        Two guards, both of which matter:

        - Only files inside the staging folder are touched, so a project the
          user added by hand from their own Videos folder is never deleted.
        - The file is only removed if no remaining job still points at it.  The
          same recording can legitimately be queued twice, and while the paths
          are time-stamped and so normally unique, a job removed while another
          referenced the same path would otherwise delete the survivor's
          project out from under the runner.
        """
        still_needed = self._staged_in_use()
        for path in paths:
            if not is_staged(path):
                continue
            if norm_path(path) in still_needed:
                continue
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            except OSError as exc:
                # Not worth troubling the user with: the sweep at the next
                # start will pick it up, and failing to tidy a scratch file is
                # no reason to make removing a job look like it failed.
                log.warning("Couldn't remove staged project %s: %s", path, exc)

    def sweep_staging(self, min_age_seconds=3600):
        """Delete staging projects no job refers to any more.

        The per-removal cleanup above covers the ordinary path, but a crash or
        a kill between writing the project and adding the job leaves a file
        behind that nothing will ever claim.  This runs once at start-up, after
        the queue has been loaded, so every file a job still needs is known.

        The age guard is for a second copy of the application running at the
        same time: it may have staged a project seconds ago and not yet saved
        the queue entry that claims it, and deleting that would break a job
        that is about to run.  An orphan older than the guard cannot be in that
        window, and anything newer is simply swept on the next start instead.
        """
        directory = staging_dir()
        if not os.path.isdir(directory):
            return 0

        import time

        keep = self._staged_in_use()
        cutoff = time.time() - min_age_seconds
        removed = 0

        try:
            names = os.listdir(directory)
        except OSError as exc:
            log.warning("Couldn't read the batch queue folder %s: %s",
                        directory, exc)
            return 0

        for name in names:
            if not name.lower().endswith((".vprj", ".swproj", ".vjr")):
                continue
            path = os.path.join(directory, name)
            if norm_path(path) in keep:
                continue
            try:
                if os.path.getmtime(path) > cutoff:
                    continue
                os.remove(path)
                removed += 1
            except FileNotFoundError:
                pass
            except OSError as exc:
                log.warning("Couldn't remove orphaned staged project %s: %s",
                            path, exc)

        if removed:
            log.info("Swept %d orphaned project file(s) from the batch queue "
                     "folder", removed)
        return removed

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
        from project.formats import read_source_filename

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

        from project.formats import read_source_filename

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
        self._tally[0] += 1
        self._maybe_all_finished()

    def _on_external_failed(self, job, message):
        self._finish_external(job, FAILED, message)
        row = self._row_of(job)
        if row >= 0:
            self.job_failed.emit(row, message)
        self.jobs_changed.emit()
        self._tally[1] += 1
        self._maybe_all_finished()

    def _maybe_all_finished(self):
        """Emit all_finished once nothing is left running, then start over."""
        if self.runner is not None or self.has_external_running():
            return
        completed, failed, held, cancelled = self._tally
        self._tally = [0, 0, 0, False]
        if completed or failed or held or cancelled:
            self.all_finished.emit(completed, failed, held, cancelled)

    def _on_external_cancelled(self, job):
        # Cancelled on the user's behalf via Remove: now the encoder has
        # actually stopped and its part-finished file is gone, the row can go
        # too.  Doing it here rather than when Remove was pressed means the row
        # never vanishes while its encoder is still shutting down.
        drop = id(job) in self._remove_when_cancelled
        self._remove_when_cancelled.discard(id(job))

        self._finish_external(job, CANCELLED)
        row = self._row_of(job)
        self._tally[3] = True

        if drop and row >= 0:
            staged = self.jobs[row].vprj_path
            del self.jobs[row]
            self.save_queue()
            self._discard_staged([staged])
            self.jobs_changed.emit()
            self._maybe_all_finished()
            return

        if row >= 0:
            self.job_failed.emit(row, "")
        self.jobs_changed.emit()
        self._maybe_all_finished()

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
        # Collected before the deletions, since the rows shift as they go.
        staged = [self.jobs[r].vprj_path for r in rows
                  if 0 <= r < len(self.jobs)]
        for r in sorted(rows, reverse=True):
            if 0 <= r < len(self.jobs):
                del self.jobs[r]
        # The runner walks this same list by index, so keep its cursor honest.
        if self.runner is not None:
            self.runner.note_removed(rows)
        self.save_queue()
        # After the list has shrunk, so a path another job still points at is
        # correctly seen as still needed.
        self._discard_staged(staged)
        self.jobs_changed.emit()

    def move(self, row, delta):
        nr = row + delta
        if 0 <= row < len(self.jobs) and 0 <= nr < len(self.jobs):
            # Never move the running job, and never swap another job past it -
            # the UI gates this too, but guard here as the source of truth.
            if self.jobs[row].status == RUNNING or \
                    self.jobs[nr].status == RUNNING:
                return row
            # Neither a finished job nor anything swapping with one may move.
            # The runner walks the list by index and never returns to a
            # position it has passed, so a queued job lifted above the block of
            # completed jobs lands where the cursor has already been and would
            # simply never run.  Send to End is the way to get a job back into
            # the current pass.
            if DONE in (self.jobs[row].status, self.jobs[nr].status):
                return row
            self.jobs[row], self.jobs[nr] = self.jobs[nr], self.jobs[row]
            self.save_queue()
            self.jobs_changed.emit()
            return nr
        return row

    def move_to_end(self, row):
        """Send a job to the back of the queue.

        For the case where a job failed or was held, the runner moved on, and
        the user has since fixed it: without this they would have to wait for
        the whole queue to drain before it could be retried.  Moving it to the
        end puts it back in the runner's path on this same pass.

        The running job stays put, and an adopted export stays put - neither is
        the caller's to shuffle.  The runner is told, so its cursor follows the
        list rather than skipping a job.
        """
        if not (0 <= row < len(self.jobs)):
            return row
        job = self.jobs[row]
        if job.status == RUNNING or job.externally_running:
            return row
        # A finished job has nothing left to do - the runner skips DONE - so
        # moving it only suggests it is about to be processed again.
        if job.status == DONE:
            return row
        if row == len(self.jobs) - 1:
            return row

        self.jobs.append(self.jobs.pop(row))
        if self.runner is not None:
            # Same adjustment removal makes: the job has left a position at or
            # before the cursor, so everything after it shifted up by one.
            # Called directly rather than wrapped in a try - a typo here would
            # silently leave the cursor pointing at the wrong job, which is far
            # worse than an exception.
            self.runner.note_removed([row])
        self.save_queue()
        self.jobs_changed.emit()
        return len(self.jobs) - 1

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
        staged = [self.jobs[r].vprj_path for r in done_rows]
        for r in sorted(done_rows, reverse=True):
            del self.jobs[r]
        if self.runner is not None:
            self.runner.note_removed(done_rows)
        self.save_queue()
        self._discard_staged(staged)
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

    def refresh_from_disk(self):
        """Take in queue changes another instance has made since we loaded.

        Adds jobs this instance has never seen, and drops ones it knew about
        that have since gone from the file - the same `_known_ids` reasoning
        `save_queue()` uses, read in the other direction.

        Two things are deliberately left alone:

        - Jobs this instance is running or has adopted from the editor. Their
          state lives in a worker here, not on disk, and the copy on disk is
          by definition the stale one.
        - Anything at all if a batch is in flight. Changing the list the runner
          is working through is not worth the risk for a refresh; it is called
          before `start()` and when the Batch Manager is opened, which covers
          the cases that matter.

        Returns True if anything changed, so a caller can refresh its view.
        """
        if self.runner is not None:
            return False
        try:
            from config.loader import load_sidecar
            on_disk = load_sidecar("queue.json", default=None)
        except Exception:
            on_disk = None
        if not isinstance(on_disk, list):
            return False

        disk_by_id = {}
        for data in on_disk:
            if isinstance(data, dict) and data.get("id"):
                disk_by_id[data["id"]] = data

        keep, changed = [], False
        for job in self.jobs:
            if job.external or job.status == RUNNING:
                keep.append(job)          # ours, in flight - disk is stale
                continue
            if job.id in disk_by_id or job.id not in self._known_ids:
                keep.append(job)
                continue
            # We knew it and the file no longer has it: removed elsewhere.
            changed = True
        added = 0
        have = {j.id for j in keep}
        for jid, data in disk_by_id.items():
            if jid in have:
                continue
            keep.append(BatchJob.from_dict(data))
            added += 1
        if added:
            changed = True
        if changed:
            self.jobs = keep
            self._known_ids |= {j.id for j in self.jobs}
            log.info("Batch queue refreshed from disk: %d job(s) now queued.",
                     len(self.jobs))
        return changed

    def start(self):
        if self.runner is not None:
            return
        # Take in what another instance has done before running anything.
        #
        # This window's list is read once at startup, so a job removed or
        # finished in another copy of Snipwright is still sitting here as
        # queued - and running it means working from a project that has since
        # been discarded.  That is exactly what happened during testing: a job
        # removed in one window failed in the other with "The project file has
        # no source recording recorded", because the staged project had gone.
        #
        # Starting a batch is the moment it matters most and the cheapest
        # place to do it: nothing is running yet, so nothing can be disturbed.
        self.refresh_from_disk()
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
        self._tally[0] += completed
        self._tally[1] += failed
        self._tally[2] += held
        self._tally[3] = self._tally[3] or bool(cancelled)
        self._maybe_all_finished()
