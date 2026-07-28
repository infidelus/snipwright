"""The Batch Manager window.

A view onto the main window's BatchController: it shows the queued projects and
their progress, and drives the controller (add / remove / start / stop).  The
batch itself runs in the controller, so closing this window leaves a running
batch going in the background, and reopening it shows the live state.
"""

import os

from PySide6.QtCore import Qt, QT_TRANSLATE_NOOP, QCoreApplication
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QAbstractItemView,
)

from batch.job import (
    QUEUED, RUNNING, DONE, FAILED, CANCELLED, NEEDS_REVIEW,
    apply_modifier, clean_basename, build_dest_path, container_to_fmt,
)
from addons.output_profiles import load_profiles, resolve_profile
from batch.controller import norm_path
from project.vprj import read_source_filename
from utils.eta import format_seconds

# Display labels for the job phases the runner reports.
_PHASE_TEXT = {
    "qsf": QT_TRANSLATE_NOOP("BatchManager", "Repairing"),
    "index": QT_TRANSLATE_NOOP("BatchManager", "Indexing"),
    "copy": QT_TRANSLATE_NOOP("BatchManager", "Copying"),
    "encode": QT_TRANSLATE_NOOP("BatchManager", "Encoding"),
    "verify": QT_TRANSLATE_NOOP("BatchManager", "Verifying"),
    "recode_audio": QT_TRANSLATE_NOOP("BatchManager", "Recoding audio"),
    "recode_full": QT_TRANSLATE_NOOP("BatchManager", "Recoding"),
    "rebuild_audio": QT_TRANSLATE_NOOP("BatchManager", "Rebuilding audio"),
    "graft_audio": QT_TRANSLATE_NOOP("BatchManager", "Copying audio"),
    "finalise": QT_TRANSLATE_NOOP("BatchManager", "Finalising"),
    "done": QT_TRANSLATE_NOOP("BatchManager", "Finishing"),
}

_STATUS_TEXT = {
    QUEUED: QT_TRANSLATE_NOOP("BatchManager", "Queued"),
    DONE: QT_TRANSLATE_NOOP("BatchManager", "Done"),
    FAILED: QT_TRANSLATE_NOOP("BatchManager", "Failed"),
    CANCELLED: QT_TRANSLATE_NOOP("BatchManager", "Cancelled"),
    NEEDS_REVIEW: QT_TRANSLATE_NOOP("BatchManager", "Needs review"),
}

COL_PROJECT = 0
COL_PROFILE = 1
COL_OUTPUT = 2
COL_STATUS = 3
COL_EDIT = 4


class BatchManagerDialog(QDialog):

    def __init__(self, main_window, controller):
        super().__init__(main_window)
        self.main = main_window
        self.controller = controller

        self.setWindowTitle(self.tr("Batch Manager"))
        self.resize(820, 460)

        # Non-modal: the main window stays usable while a batch runs.
        self.setModal(False)
        # Destroy on close so reopening builds a fresh view bound to the
        # (possibly still-running) controller.
        self.setAttribute(Qt.WA_DeleteOnClose)

        self._build_ui()
        self._connect_controller()
        self._refresh_table()
        self._sync_running_state()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        c = self.controller
        outer = QVBoxLayout(self)

        # --- destination settings ---------------------------------------- #
        # Output folder (left) and Default profile (right) share a line; the
        # name modifier sits below.
        settings = QGridLayout()
        settings.setHorizontalSpacing(10)

        settings.addWidget(QLabel(self.tr("Output folder:")), 0, 0)
        self._folder_edit = QLineEdit(c.out_folder)
        self._folder_edit.setReadOnly(True)
        settings.addWidget(self._folder_edit, 0, 1)
        self._browse_btn = QPushButton(self.tr("Browse…"))
        self._browse_btn.clicked.connect(self._choose_folder)
        settings.addWidget(self._browse_btn, 0, 2)

        # Column 3 is a fixed gap so the two groups don't look cluttered.
        settings.addWidget(QLabel(self.tr("Default profile:")), 0, 4)
        self._default_profile = QComboBox()
        self._default_profile.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self._default_profile.setMinimumWidth(170)
        self._default_profile.setMaximumWidth(280)
        self._fill_profile_combo(self._default_profile, c.default_profile)
        self._default_profile.currentIndexChanged.connect(
            self._on_default_profile
        )
        settings.addWidget(self._default_profile, 0, 5)

        settings.addWidget(QLabel(self.tr("Name modifier:")), 1, 0)
        self._modifier_edit = QLineEdit(c.modifier)
        self._modifier_edit.setPlaceholderText(
            self.tr("optional - prefixes the name, or suffixes it if it starts with - or _")
        )
        self._modifier_edit.textChanged.connect(self._on_modifier_changed)
        settings.addWidget(self._modifier_edit, 1, 1, 1, 5)

        # The folder field takes the slack; the profile combo stays compact.
        settings.setColumnStretch(1, 1)
        settings.setColumnStretch(5, 0)
        settings.setColumnMinimumWidth(3, 24)

        outer.addLayout(settings)

        # --- job table --------------------------------------------------- #
        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(
            [self.tr("Project"), self.tr("Profile"), self.tr("Output"), self.tr("Status"), ""]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(COL_PROJECT, QHeaderView.Stretch)
        hh.setSectionResizeMode(COL_PROFILE, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(COL_OUTPUT, QHeaderView.Stretch)
        hh.setSectionResizeMode(COL_STATUS, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(COL_EDIT, QHeaderView.ResizeToContents)
        outer.addWidget(self.table, 1)

        # --- list management buttons ------------------------------------- #
        row = QHBoxLayout()
        self._add_btn = QPushButton(self.tr("Add Projects…"))
        self._add_btn.clicked.connect(self._add_projects)
        self._add_watch_btn = QPushButton(self.tr("Add from Watch Folder"))
        self._add_watch_btn.setToolTip(
            self.tr("Add new projects produced by the Snipwright Watcher (commercial "
            "detection). They arrive stopped, for you to review and Start.")
        )
        self._add_watch_btn.clicked.connect(self._add_from_watch_folder)
        self._remove_btn = QPushButton(self.tr("Remove"))
        self._remove_btn.clicked.connect(self._remove_selected)
        self._up_btn = QPushButton(self.tr("Move Up"))
        self._up_btn.clicked.connect(lambda: self._move_selected(-1))
        self._down_btn = QPushButton(self.tr("Move Down"))
        self._down_btn.clicked.connect(lambda: self._move_selected(1))
        for b in (self._add_btn, self._add_watch_btn, self._remove_btn,
                  self._up_btn, self._down_btn):
            row.addWidget(b)
        row.addStretch(1)
        self._clear_done_btn = QPushButton(self.tr("Clear Finished"))
        self._clear_done_btn.clicked.connect(self._clear_finished)
        row.addWidget(self._clear_done_btn)
        outer.addLayout(row)

        # --- selected-job info ------------------------------------------- #
        # Shows the path the highlighted job will actually work from - the QSF'd
        # /tmp copy when one was used, otherwise the original recording - so it
        # can be checked at a glance.
        self._info_label = QLabel("")
        self._info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._info_label.setStyleSheet("color: gray;")
        outer.addWidget(self._info_label)

        # --- overall progress -------------------------------------------- #
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.setFormat("")
        outer.addWidget(self._progress)

        self._status_label = QLabel("")
        outer.addWidget(self._status_label)

        # --- start / close ----------------------------------------------- #
        bottom = QHBoxLayout()
        bottom.addStretch(1)
        self._start_btn = QPushButton(self.tr("Start"))
        self._start_btn.clicked.connect(self._toggle_start)
        bottom.addWidget(self._start_btn)
        self._close_btn = QPushButton(self.tr("Close"))
        self._close_btn.clicked.connect(self.close)
        bottom.addWidget(self._close_btn)
        outer.addLayout(bottom)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    # ------------------------------------------------------------------ #
    # Controller wiring
    # ------------------------------------------------------------------ #

    def _connect_controller(self):
        c = self.controller
        c.jobs_changed.connect(self._refresh_table)
        c.job_started.connect(self._on_job_started)
        c.job_progress.connect(self._on_job_progress)
        c.job_done.connect(self._on_job_done)
        c.job_failed.connect(self._on_job_failed)
        c.job_held.connect(self._on_job_held)
        c.batch_finished.connect(self._on_batch_finished)
        c.running_changed.connect(self._on_running_changed)
        # Seed the bar from the job already running, so opening the window
        # mid-batch shows the current progress immediately rather than a blank
        # bar until the next whole-percent tick arrives.
        self._seed_progress()

    def _seed_progress(self):
        for i, job in enumerate(self._jobs()):
            if job.status == RUNNING:
                self._on_job_progress(
                    i, {"percent": job.percent, "phase": job.phase})
                return

    def _disconnect_controller(self):
        c = self.controller
        for sig, slot in (
            (c.jobs_changed, self._refresh_table),
            (c.job_started, self._on_job_started),
            (c.job_progress, self._on_job_progress),
            (c.job_done, self._on_job_done),
            (c.job_failed, self._on_job_failed),
            (c.job_held, self._on_job_held),
            (c.batch_finished, self._on_batch_finished),
            (c.running_changed, self._on_running_changed),
        ):
            try:
                sig.disconnect(slot)
            except (TypeError, RuntimeError):
                pass

    # ------------------------------------------------------------------ #
    # Settings handlers
    # ------------------------------------------------------------------ #

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Output Folder"), self.controller.out_folder
        )
        if folder:
            self.controller.out_folder = folder
            self._folder_edit.setText(folder)
            self._refresh_table()

    def _on_default_profile(self):
        self.controller.default_profile = self._default_profile.currentData()

    def _fill_profile_combo(self, combo, selected_name):
        """Populate a combo with every profile name (data == name) and select
        ``selected_name``.  A name that's no longer among the profiles (e.g. a
        profile deleted after queueing) is still added so it stays visible and
        the user can see what the job is set to."""
        names = [p.name for p in self._profiles()]
        combo.blockSignals(True)
        combo.clear()
        for n in names:
            combo.addItem(n, n)
        if selected_name and selected_name not in names:
            combo.addItem(self.tr("%s (missing)") % selected_name, selected_name)
        idx = combo.findData(selected_name)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def _on_modifier_changed(self, text):
        self.controller.modifier = text
        self._refresh_table()

    # ------------------------------------------------------------------ #
    # Queue management
    # ------------------------------------------------------------------ #

    def _add_projects(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add Projects",
            self.controller.out_folder,
            "VideoReDo Project (*.vprj *.VPRJ);;All files (*)",
        )
        if not paths:
            return

        # Anything already in the queue?  Adding a project twice is usually an
        # accidental re-pick, but is legitimate when comparing output settings,
        # so ask - and if they decline, still add the ones that are new.
        dupes = [p for p in paths if self.controller.jobs_for_path(p)]

        if dupes:
            listed = "\n".join(
                "\u2022 %s" % os.path.basename(p) for p in dupes[:5]
            )
            if len(dupes) > 5:
                listed += "\n" + self.tr("\u2026and %d more") % (len(dupes) - 5)

            answer = QMessageBox.question(
                self, self.tr("Add Projects"),
                self.tr("%d of the selected projects are already in the "
                        "queue:\n\n%s\n\nAdd them again?")
                % (len(dupes), listed)
                if len(dupes) != 1 else
                self.tr("\"%s\" is already in the queue.\n\nAdd it again?")
                % os.path.basename(dupes[0]),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if answer != QMessageBox.Yes:
                paths = [p for p in paths if p not in dupes]

        if paths:
            self.controller.add_jobs(paths)

    def _add_from_watch_folder(self):
        """Pull in any new projects the Watcher has written, as stopped jobs."""
        import glob
        from watch.config import WatchConfig

        folder = WatchConfig.load().output_dir
        if not folder or not os.path.isdir(folder):
            QMessageBox.information(
                self, self.tr("Add from Watch Folder"),
                self.tr("The watch output folder doesn't exist yet. Set it up in the "
                "Snipwright Watcher first."),
            )
            return

        found = sorted(
            glob.glob(os.path.join(folder, "*.vprj"))
            + glob.glob(os.path.join(folder, "*.VPrj"))
        )

        # A bulk add should never queue a recording that's already waiting.
        # Comparing project paths alone isn't enough: a recording edited and
        # sent over with Queue to Batch arrives as a timestamped staging file,
        # so its path never matches the watcher's copy even though both cut the
        # same recording.  Compare what each project actually points at.
        existing_projects = {
            norm_path(j.vprj_path) for j in self.controller.jobs if j.vprj_path
        }
        queued_sources = self.controller.queued_sources()

        new = []
        skipped = 0
        for path in found:
            if norm_path(path) in existing_projects:
                skipped += 1
                continue
            source = ""
            try:
                source = read_source_filename(path)
            except Exception:
                source = ""
            key = norm_path(source) if source else ""
            if key and key in queued_sources:
                skipped += 1
                continue
            new.append(path)
            if key:
                # Guard against two watcher projects for the same recording
                # within this same sweep.
                queued_sources.add(key)

        if not new:
            QMessageBox.information(
                self, self.tr("Add from Watch Folder"),
                self.tr("No new projects in the watch folder — everything there is "
                "already in the queue."),
            )
            return

        self.controller.add_jobs(new)
        message = self.tr(
            "Added %d project(s) from the watch folder. They're queued and "
            "stopped — review each with Edit, then Start."
        ) % len(new)
        if skipped:
            message += "\n\n" + self.tr(
                "Skipped %d already in the queue."
            ) % skipped
        QMessageBox.information(
            self, self.tr("Add from Watch Folder"), message,
        )

    def _selected_rows(self):
        return sorted({i.row() for i in self.table.selectedIndexes()})

    def _on_selection_changed(self):
        self._update_buttons()
        self._update_info()

    def _update_info(self):
        """Show the working path of the single selected job, if any."""
        rows = self._selected_rows()
        jobs = self._jobs()
        if len(rows) == 1 and 0 <= rows[0] < len(jobs):
            job = jobs[rows[0]]
            working = read_source_filename(job.vprj_path) or "(unknown)"
            self._info_label.setText(self.tr("Working from:  %s") % working)
        else:
            self._info_label.setText("")

    def _remove_selected(self):
        rows = self._selected_rows()
        if not rows:
            return

        jobs = self._jobs()

        # An adopted export can be stopped, unlike the job the batch runner is
        # working on - that one needs the batch stopping first.  Offer to do it,
        # since Remove is where you'd reach for anyway.
        exports = [
            r for r in rows
            if 0 <= r < len(jobs) and jobs[r].externally_running
            and not jobs[r].cancelling
        ]
        if exports:
            names = "\n".join("\u2022 %s" % jobs[r].name for r in exports[:5])
            answer = QMessageBox.question(
                self, self.tr("Stop export"),
                self.tr("%d export(s) are still being written in the "
                        "background:\n\n%s\n\nStopping now discards the "
                        "part-finished file. The rows disappear once the "
                        "encoder has actually stopped, which can take a "
                        "moment.\n\nStop them?") % (len(exports), names),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
            for r in exports:
                self.controller.cancel_export(r)
            # The rest of the selection is handled below; the cancelled rows
            # remove themselves when their workers confirm.
            rows = [r for r in rows if r not in exports]
            if not rows:
                return

        # Whatever's left: the runner's current job still can't go, and neither
        # can an export already in the middle of stopping.
        protected = self.controller.protected_rows()
        clash = [r for r in rows if r in protected]
        if clash:
            remaining = [r for r in rows if r not in protected]
            if not remaining:
                QMessageBox.information(
                    self, self.tr("Remove"),
                    self.tr("That file is being processed right now. Stop the "
                            "batch first if you want to remove it."),
                )
                return
            rows = remaining
        self.controller.remove(rows)

    def _clear_finished(self):
        self.controller.clear_finished()

    def _move_selected(self, delta):
        rows = self._selected_rows()
        if len(rows) != 1 or not self._can_move(rows[0], delta):
            return
        nr = self.controller.move(rows[0], delta)
        self.table.selectRow(nr)

    # ------------------------------------------------------------------ #
    # Table rendering
    # ------------------------------------------------------------------ #

    def _jobs(self):
        return self.controller.jobs

    def _profiles(self):
        return load_profiles(self.controller.config)

    def _profile_editable(self, job):
        """A job's profile can still be changed until it actually starts
        processing: queued (and failed/cancelled, which re-run) are editable;
        a running or finished job is not.  This holds even while the batch is
        running, so you can re-profile jobs you queue on the fly."""
        return job.status not in (RUNNING, DONE)

    def _preview_output(self, job, taken=None):
        """Best-effort output filename for display, before the job runs - named
        after the recording, with the job profile's container extension.

        `taken` carries the names earlier rows have already claimed, so the
        preview shows the ' (2)' the runner will actually add rather than
        displaying the same filename twice and leaving the user to wonder
        whether the second job is about to overwrite the first.
        """
        embedded = read_source_filename(job.vprj_path)
        base_src = embedded or job.vprj_path
        name = apply_modifier(clean_basename(base_src), self.controller.modifier)
        profile = resolve_profile(self.controller.config, job.profile_name)
        ext = profile.extension(os.path.splitext(base_src)[1] or ".ts")
        if taken is None:
            return os.path.join(self.controller.out_folder, f"{name}{ext}")
        # Same call the runner makes, so the preview and the real thing agree -
        # including the container-to-format conversion, which is why this uses
        # container_to_fmt rather than the profile's container name directly.
        return build_dest_path(
            self.controller.out_folder, self.controller.modifier,
            base_src, container_to_fmt(profile.container), taken,
        )

    def _refresh_table(self):
        jobs = self._jobs()
        self.table.setRowCount(len(jobs))
        for r, job in enumerate(jobs):
            item = QTableWidgetItem(job.name)
            item.setToolTip(job.vprj_path)
            self.table.setItem(r, COL_PROJECT, item)

            combo = self.table.cellWidget(r, COL_PROFILE)
            if not isinstance(combo, QComboBox):
                combo = QComboBox()
                combo.currentIndexChanged.connect(
                    lambda _idx, _r=r: self._on_row_profile(_r)
                )
                self.table.setCellWidget(r, COL_PROFILE, combo)
            self._fill_profile_combo(combo, job.profile_name)
            combo.setEnabled(self._profile_editable(job))


            self.table.setItem(r, COL_STATUS, QTableWidgetItem(
                self._status_for(job)
            ))

            # Edit button: opens this project in the editor so its (often
            # approximate, e.g. Comskip-detected) cut points can be adjusted
            # before the batch processes it.  Saving in the editor writes back
            # to this same .vprj, which the runner re-reads at process time.
            edit_btn = self.table.cellWidget(r, COL_EDIT)
            if not isinstance(edit_btn, QPushButton):
                edit_btn = QPushButton(self.tr("Edit…"))
                edit_btn.clicked.connect(
                    lambda _checked=False, _r=r: self._edit_row(_r)
                )
                self.table.setCellWidget(r, COL_EDIT, edit_btn)
            edit_btn.setEnabled(job.status != RUNNING)
        self._refresh_outputs()
        self._update_buttons()

    def _refresh_outputs(self):
        """Rebuild the whole Output column.

        Always the whole column, never one row: the names are claimed in order,
        so a job that would clash with an earlier one gets a ' (2)'.  Changing
        any row's profile can change its extension, which changes what clashes
        with what - so recomputing a single row in isolation would drop the
        suffix and show two rows writing to the same file.
        """
        claimed = set()
        for r, job in enumerate(self._jobs()):
            out = job.dest_path or self._preview_output(job, claimed)
            claimed.add(out)
            item = QTableWidgetItem(os.path.basename(out))
            item.setToolTip(out)
            self.table.setItem(r, COL_OUTPUT, item)

    def _on_row_profile(self, row):
        jobs = self._jobs()
        if not (0 <= row < len(jobs)):
            return
        combo = self.table.cellWidget(row, COL_PROFILE)
        if isinstance(combo, QComboBox):
            self.controller.set_job_profile(row, combo.currentData())
            self._refresh_outputs()

    def _status_for(self, job):
        if job.cancelling:
            # Asked to stop, but the encoder hasn't finished unwinding - saying
            # so is better than a percentage that has quietly stopped moving.
            return self.tr("Stopping…")
        if job.externally_running:
            # Distinguished from a batch job so it's clear where the work is
            # happening - and why Start won't touch it.
            return self.tr("Exporting… %d%%") % job.percent
        if job.status == RUNNING:
            return f"Running… {job.percent}%"
        if job.status == NEEDS_REVIEW:
            return self.tr("Needs review — Edit to repair & confirm")
        if job.status == FAILED and job.message:
            return f"Failed: {job.message.splitlines()[0]}"
        return QCoreApplication.translate(
            "BatchManager",
            _STATUS_TEXT.get(job.status, QT_TRANSLATE_NOOP("BatchManager", "Queued")),
        )

    def _set_row_status(self, row):
        jobs = self._jobs()
        if 0 <= row < len(jobs):
            self.table.setItem(row, COL_STATUS, QTableWidgetItem(
                self._status_for(jobs[row])
            ))
            # The profile combo follows the job's state - lock it once the job
            # starts or finishes, leave it editable while still pending.
            combo = self.table.cellWidget(row, COL_PROFILE)
            if isinstance(combo, QComboBox):
                combo.setEnabled(self._profile_editable(jobs[row]))
            # Edit is allowed except on the job that's actually processing.
            edit_btn = self.table.cellWidget(row, COL_EDIT)
            if isinstance(edit_btn, QPushButton):
                edit_btn.setEnabled(jobs[row].status != RUNNING)

    def _edit_row(self, row):
        """Open this row's project in the editor to adjust its scenes, and
        close the Batch Manager so focus returns to the editor.  Saving in the
        editor updates the same .vprj this row points at."""
        jobs = self._jobs()
        if not (0 <= row < len(jobs)):
            return
        job = jobs[row]
        if job.status == RUNNING:
            return
        if not os.path.isfile(job.vprj_path):
            QMessageBox.warning(
                self, self.tr("Edit"),
                f"The project file no longer exists:\n\n{job.vprj_path}",
            )
            return
        was_held = job.status == NEEDS_REVIEW
        # Only act if the editor actually started loading it (the user may
        # cancel the unsaved-changes prompt, in which case we stay put).
        if self.main.load_project_file(job.vprj_path, "Edit Project"):
            # Opening a held job for review releases it back to the queue, so
            # once you've repaired and confirmed its cuts it processes on the
            # next run.
            if was_held:
                self.controller.requeue(row)
            self.close()

    # ------------------------------------------------------------------ #
    # Running (delegated to the controller)
    # ------------------------------------------------------------------ #

    def _toggle_start(self):
        if self.controller.is_running():
            self._prompt_stop()
        else:
            self._start_batch()

    def _prompt_stop(self):
        """Ask how to stop: abandon the job that's running, or let it finish
        first and stop before the next one starts."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle(self.tr("Stop Batch"))
        box.setText(self.tr("Stop processing the queue?"))
        informative = self.tr(
            "The job that's currently running can be finished first, or stopped "
            "straight away and left unfinished."
        )
        if self.controller.has_external_running():
            # Two things are in flight, so "the job that's currently running" is
            # ambiguous and "Stop now" reads as though it stops everything.
            informative += "\n\n" + self.tr(
                "This affects the batch only. An export sent here from the "
                "editor keeps running either way - to stop that, select its row "
                "and press Remove."
            )
        box.setInformativeText(informative)
        finish_btn = box.addButton(
            self.tr("Finish current file, then stop"), QMessageBox.AcceptRole
        )
        now_btn = box.addButton(self.tr("Stop now"), QMessageBox.DestructiveRole)
        box.addButton(self.tr("Keep going"), QMessageBox.RejectRole)
        box.setDefaultButton(finish_btn)
        box.exec()

        clicked = box.clickedButton()
        if clicked is finish_btn:
            self._status_label.setText(
                self.tr("Stopping after the current file…")
            )
            self._start_btn.setEnabled(False)
            self.controller.stop(after_current=True)
        elif clicked is now_btn:
            self._status_label.setText(self.tr("Stopping…"))
            self._start_btn.setEnabled(False)
            self.controller.stop()

    def _start_batch(self):
        jobs = self._jobs()
        if not jobs:
            QMessageBox.information(
                self, self.tr("Batch Manager"), self.tr("Add at least one project first.")
            )
            return
        if not self.controller.pending_count():
            held = self.controller.held_count()
            if held:
                QMessageBox.information(
                    self, self.tr("Batch Manager"),
                    f"{held} job(s) are waiting for review. Click Edit on each "
                    "to repair and confirm the cuts, then run the batch again.",
                )
            else:
                QMessageBox.information(
                    self, self.tr("Batch Manager"),
                    self.tr("Every job is already done. Add more, or use Clear Finished."),
                )
            return
        self.controller.start()

    def _on_running_changed(self, running):
        self._start_btn.setText(self.tr("Stop") if running else self.tr("Start"))
        self._start_btn.setEnabled(True)
        self._set_controls_enabled(not running)
        if not running:
            self._progress.setRange(0, 100)
            self._progress.setValue(0)
            self._progress.setFormat("")
        self._refresh_table()

    def _sync_running_state(self):
        """Reflect the controller's current state when (re)opening the dialog."""
        running = self.controller.is_running()
        self._start_btn.setText(self.tr("Stop") if running else self.tr("Start"))
        self._set_controls_enabled(not running)
        if running:
            if self.controller.is_finishing():
                # A stop-after-current is already pending - keep showing that,
                # not the plain running message, and keep Stop disabled since
                # it's already been actioned.
                self._status_label.setText(
                    self.tr("Stopping after the current file…"))
                self._start_btn.setEnabled(False)
            else:
                self._status_label.setText(self.tr("Batch running…"))

    def _set_controls_enabled(self, on):
        # Adding more projects is always allowed (queue while it runs), and so
        # is removing ones that are still waiting - the controller refuses to
        # remove the job that's actually running.  Clear Finished is likewise
        # safe mid-run (it only drops inert DONE jobs), so it's driven by
        # whether anything is finished rather than by the run state.  Output
        # settings stay locked down during a run.
        for w in (
            self._default_profile, self._modifier_edit,
            self._browse_btn,
        ):
            w.setEnabled(on)
        self._remove_btn.setEnabled(True)
        self._clear_done_btn.setEnabled(
            any(j.status == DONE for j in self._jobs()))
        self._update_buttons()   # refresh the per-selection move gating too

    def _on_job_started(self, index):
        self._set_row_status(index)
        self.table.selectRow(index)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        jobs = self._jobs()
        if 0 <= index < len(jobs):
            self._status_label.setText(
                f"Processing {index + 1} of {len(jobs)}: {jobs[index].name}"
            )

    def _drives_progress_bar(self, index):
        """Whether this row owns the shared bar at the bottom.

        Two jobs can now be in flight at once - the batch's own, and an export
        adopted from the editor - and there's only one bar.  The batch runner's
        job wins while a batch is running; otherwise the adopted export gets
        it.  Either way each row shows its own percentage in the Status column,
        so nothing is hidden.
        """
        if self.controller.is_running():
            return index == self.controller.running_row()
        jobs = self._jobs()
        return 0 <= index < len(jobs) and jobs[index].externally_running

    def _on_job_progress(self, index, info):
        # The row's own status cell always follows its job.
        self._set_row_status(index)
        if not self._drives_progress_bar(index):
            return

        phase = info.get("phase", "")
        pct = info.get("percent")
        phase_text = QCoreApplication.translate(
            "BatchManager",
            _PHASE_TEXT.get(phase, QT_TRANSLATE_NOOP("BatchManager", "Working")),
        )

        # A negative percent means "busy, with nothing to count" - the audio
        # graft, the mux and the finalise pass all report it.  Pulse the bar
        # rather than dropping it back to zero, which looks like the job has
        # restarted.
        if isinstance(pct, (int, float)) and pct < 0:
            if self._progress.maximum() != 0:
                self._progress.setRange(0, 0)
            self._progress.setFormat(phase_text)
            return

        if self._progress.maximum() == 0:
            self._progress.setRange(0, 100)
        if isinstance(pct, (int, float)):
            self._progress.setValue(int(pct))

        # "%p" is the progress bar's own placeholder for the percentage; the
        # estimate is baked into the format string as it changes.
        text = f"{phase_text} — %p%"
        remaining = self.controller.eta_seconds(index)
        if remaining is not None:
            text += " — " + self.tr("%s left") % format_seconds(remaining)
        self._progress.setFormat(text)

    def _on_job_done(self, index, stats):
        jobs = self._jobs()
        if 0 <= index < len(jobs):
            out = jobs[index].dest_path or ""
            item = QTableWidgetItem(os.path.basename(out))
            item.setToolTip(out)
            self.table.setItem(index, COL_OUTPUT, item)
            self._set_row_status(index)
        # A job just finished, so Clear Finished may now have something to do.
        self._clear_done_btn.setEnabled(
            any(j.status == DONE for j in self._jobs()))

    def _on_job_failed(self, index, message):
        self._set_row_status(index)

    def _on_job_held(self, index, reason):
        self._set_row_status(index)

    def _on_batch_finished(self, completed, failed, held, cancelled):
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFormat("")
        verb = self.tr("Stopped") if cancelled else self.tr("Finished")
        parts = [f"{completed} done"]
        if held:
            parts.append(f"{held} need review")
        if failed:
            parts.append(f"{failed} failed")
        summary = f"{verb}. " + ", ".join(parts) + "."
        self._status_label.setText(summary)
        self._refresh_table()
        if held and not cancelled:
            QMessageBox.information(
                self, self.tr("Batch finished"),
                f"{summary}\n\n{held} file(s) need repairing before they can be "
                "cut. Click Edit on each to run Quick Stream Fix and confirm "
                "the cut points, then run the batch again.",
            )
        elif failed and not cancelled:
            QMessageBox.warning(
                self, self.tr("Batch finished"),
                f"{summary}\n\nSee the Status column for what went wrong "
                "with the failed jobs.",
            )

    # ------------------------------------------------------------------ #
    # Buttons / close
    # ------------------------------------------------------------------ #

    def _update_buttons(self):
        sel = self._selected_rows()
        # Waiting jobs can be removed even mid-run (the controller protects the
        # one actually being processed), so this depends only on the selection.
        self._remove_btn.setEnabled(bool(sel))
        # Reordering is allowed while the batch runs - you just can't move the
        # job that's currently processing, and you can't move another job past
        # it (into a slot at or before the running one).  _can_move works that
        # out per direction so, for example, the job right after the running
        # one can move down but not up.
        one = len(sel) == 1
        self._up_btn.setEnabled(one and self._can_move(sel[0], -1))
        self._down_btn.setEnabled(one and self._can_move(sel[0], 1))

    def _can_move(self, row, delta):
        """Whether the job at `row` may move by `delta` (-1 up, +1 down).

        A running job is pinned, and no job may cross it - so a move is refused
        when the job itself is running, when the target slot is out of range,
        or when the neighbour being swapped with is the running job.
        """
        jobs = self._jobs()
        target = row + delta
        if not (0 <= row < len(jobs) and 0 <= target < len(jobs)):
            return False
        if jobs[row].status == RUNNING:
            return False
        if jobs[target].status == RUNNING:
            return False
        return True

    def closeEvent(self, event):
        # Closing the window does NOT stop a running batch - it keeps going in
        # the background.  Just detach this view from the controller.
        self._disconnect_controller()
        super().closeEvent(event)
