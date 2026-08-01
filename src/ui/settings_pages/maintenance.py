"""Maintenance page: cached data, direct config editing, and reset."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSpinBox, QComboBox,
)

from ui.settings_pages import SettingsPage
from ui.settings_widgets import hint
from ui.settings_pages.files import _divider
from PySide6.QtCore import QT_TRANSLATE_NOOP


class MaintenancePage(SettingsPage):
    TITLE = QT_TRANSLATE_NOOP("Settings", "Maintenance")

    def build(self):
        s = self._settings()

        self._build_update_check()

        self.add(_divider())
        self.add(QLabel(self.tr("Quick Stream Fix working copies")))
        self._build_working_copies()

        cache_row = QHBoxLayout()
        cache_row.addWidget(QLabel(self.tr("Delete cached data older than")))
        self._cache_age = QSpinBox()
        self._cache_age.setRange(0, 3650)
        self._cache_age.setSuffix(" days")
        self._cache_age.setSpecialValueText("never")   # shown when value is 0
        self._cache_age.setValue(int(s.get("cache_max_age_days", 30)))
        cache_row.addWidget(self._cache_age)
        cache_row.addStretch(1)

        clear_btn = QPushButton(self.tr("Delete now"))
        clear_btn.clicked.connect(self._ctx.clear_cache)
        cache_row.addWidget(clear_btn)
        self.add_layout(cache_row)
        self.add(hint(
            self.tr("Cached frame indices and Quick Stream Fix records for files you "
            "haven't opened in this long are removed at startup. Set to 0 "
            "(never) to keep them indefinitely.")
        ))

        # Renamer match cache - separate age limit (it defaults to "never",
        # since renamer matches are usually worth keeping).
        rn_row = QHBoxLayout()
        rn_row.addWidget(QLabel(self.tr("Delete remembered renamer matches older than")))
        self._renamer_age = QSpinBox()
        self._renamer_age.setRange(0, 3650)
        self._renamer_age.setSuffix(" days")
        self._renamer_age.setSpecialValueText("never")
        self._renamer_age.setValue(int(s.get("renamer_cache_max_age_days", 0)))
        rn_row.addWidget(self._renamer_age)
        rn_row.addStretch(1)
        clear_rn = QPushButton(self.tr("Delete now"))
        clear_rn.clicked.connect(self._clear_renamer_cache)
        rn_row.addWidget(clear_rn)
        self.add_layout(rn_row)
        self.add(hint(
            self.tr("The TV and film renamer remember each TMDB/IMDb match so they "
            "don't look it up again. These are kept in their own file; purge "
            "old ones here, or set to 0 (never) to keep them indefinitely.")
        ))

        edit_row = QHBoxLayout()
        edit_cfg = QPushButton(self.tr("Edit config.json"))
        edit_cfg.setFocusPolicy(Qt.NoFocus)
        edit_cfg.clicked.connect(self._ctx.edit_config)
        edit_row.addWidget(edit_cfg)
        edit_row.addStretch(1)
        self.add_layout(edit_row)
        self.add(hint(
            self.tr("Edit every setting directly as text - including the keyboard "
            "shortcuts, which have no controls of their own here. Changes "
            "apply as soon as you save, and any clashing keys are flagged then.")
        ))

        restore_row = QHBoxLayout()
        restore = QPushButton(self.tr("Restore Default Settings"))
        restore.setFocusPolicy(Qt.NoFocus)
        restore.clicked.connect(self._ctx.restore_defaults)
        restore_row.addWidget(restore)
        restore_row.addStretch(1)
        self.add_layout(restore_row)
        self.add(hint(
            self.tr("Reset every setting - paths, options and keyboard shortcuts - "
            "back to its default. Your recordings and projects aren't affected.")
        ))

    def _clear_renamer_cache(self):
        from PySide6.QtWidgets import QMessageBox
        from addons.match_cache import clear as clear_renamer_cache
        clear_renamer_cache(self._config)
        QMessageBox.information(
            self, self.tr("Renamer cache cleared"),
            self.tr("The remembered renamer matches have been deleted."))

    def _build_update_check(self):
        """Whether - and how often - to ask GitHub about new releases."""
        s = self._settings()
        row = QHBoxLayout()
        row.addWidget(QLabel(self.tr("Check for new versions:")))
        self._update_check = QComboBox()
        for value, label in (("off", self.tr("Never")),
                             ("daily", self.tr("Daily")),
                             ("weekly", self.tr("Weekly")),
                             ("monthly", self.tr("Monthly"))):
            self._update_check.addItem(label, value)
        idx = self._update_check.findData(s.get("update_check", "off"))
        self._update_check.setCurrentIndex(max(0, idx))
        row.addWidget(self._update_check)
        row.addStretch(1)
        check_now = QPushButton(self.tr("Check now"))
        check_now.clicked.connect(self._check_now)
        row.addWidget(check_now)
        self.add_layout(row)
        self.add(hint(self.tr(
            "Asks GitHub whether a newer Snipwright has been released and tells "
            "you if there is one. Nothing is downloaded or installed - only the "
            "public list of releases is read. Set to Never to disable automatic "
            "checks; a manual check can always be made with the Check now "
            "button."
        )))

    def _build_working_copies(self):
        """Quick Stream Fix working copies: how much space, and how to clear it.

        Snipwright removes its own when it closes, so this is mostly for
        reassurance and for copies left behind by a crash - but on Windows,
        where the temp folder is never cleared automatically, being able to see
        the figure matters.
        """
        from utils.qsf_temp import temp_dir

        row = QHBoxLayout()
        self._qsf_label = QLabel()
        row.addWidget(self._qsf_label)
        row.addStretch(1)
        open_btn = QPushButton(self.tr("Open folder"))
        open_btn.setToolTip(temp_dir())
        open_btn.clicked.connect(self._open_temp_folder)
        row.addWidget(open_btn)
        del_btn = QPushButton(self.tr("Delete now"))
        del_btn.clicked.connect(self._delete_working_copies)
        row.addWidget(del_btn)
        self.add_layout(row)
        self.add(hint(self.tr(
            "Repairing a recording with Quick Stream Fix writes a working copy "
            "to the system temporary folder, and the editor cuts that copy. "
            "They are kept so you can come back to a recording later, and "
            "deleted once they reach the age below."
        )))

        age_row = QHBoxLayout()
        age_row.addWidget(QLabel(self.tr("Delete leftovers older than")))
        self._qsf_age = QSpinBox()
        self._qsf_age.setRange(0, 365)
        self._qsf_age.setSuffix(self.tr(" days"))
        self._qsf_age.setSpecialValueText(self.tr("never"))
        self._qsf_age.setValue(
            int(self._settings().get("qsf_temp_max_age_days", 7)))
        self._qsf_age.setToolTip(self.tr(
            "Checked at startup. Anything still in use is never deleted - open "
            "in the editor, being exported, or referenced by a job in the batch "
            "queue."
        ))
        age_row.addWidget(self._qsf_age)
        age_row.addStretch(1)
        self.add_layout(age_row)

        self._refresh_working_copies()

    def _refresh_working_copies(self):
        from utils.qsf_temp import list_working_copies, human_size
        rows = list_working_copies()
        if not rows:
            self._qsf_label.setText(self.tr("No working copies on disk."))
            return
        total = sum(r[1] for r in rows)
        self._qsf_label.setText(
            self.tr("%d working copy/copies using %s")
            % (len(rows), human_size(total))
        )

    def _open_temp_folder(self):
        from utils.qsf_temp import temp_dir
        from utils.open_path import open_path
        open_path(temp_dir())

    def _delete_working_copies(self):
        from PySide6.QtWidgets import QMessageBox
        from utils.qsf_temp import (list_working_copies, delete, human_size)

        rows = list_working_copies()
        if not rows:
            QMessageBox.information(
                self, self.tr("Working copies"),
                self.tr("There are no working copies to delete."))
            return
        total = sum(r[1] for r in rows)
        if QMessageBox.question(
                self, self.tr("Working copies"),
                self.tr("Delete %d working copy/copies, freeing %s?\n\n"
                        "Anything still in use is skipped - open in the editor, "
                        "being exported, or needed by a queued batch job.")
                % (len(rows), human_size(total)),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No) != QMessageBox.Yes:
            return

        # Protect exactly what the automatic sweep protects: the open
        # recording, anything a background export is reading, and anything a
        # queued batch job points at.
        keep = []
        from PySide6.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            getter = getattr(w, "_in_use_paths", None)
            if callable(getter):
                try:
                    keep.extend(getter())
                except Exception:
                    pass

        gone, freed = delete([r[0] for r in rows], keep=keep)
        self._refresh_working_copies()
        QMessageBox.information(
            self, self.tr("Working copies"),
            self.tr("Deleted %d file(s), freeing %s.") % (gone, human_size(freed)))

    def _check_now(self):
        win = self.window()
        parent = win.parent() if win is not None else None
        target = parent if hasattr(parent, "check_for_updates") else None
        if target is None:
            from PySide6.QtWidgets import QApplication
            for w in QApplication.topLevelWidgets():
                if hasattr(w, "check_for_updates"):
                    target = w
                    break
        if target is not None:
            target.check_for_updates(manual=True)

    def save(self, config):
        settings = config.setdefault("settings", {})
        settings["update_check"] = self._update_check.currentData()
        settings["qsf_temp_max_age_days"] = self._qsf_age.value()
        settings["cache_max_age_days"] = self._cache_age.value()
        settings["renamer_cache_max_age_days"] = self._renamer_age.value()
