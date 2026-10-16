"""Edit > Capture Frame - where the picture goes, as VideoReDo asks it.

A small dialog rather than the system's Save dialog, which on some desktops
fills most of the screen for what is usually one click: the file field
already holds a full path (the capture folder from Settings > Files plus
the recording's name and the timecode), so OK saves at once, and "…"
opens the full dialog only when wanted.  The clipboard is the other
destination - for pasting straight into a message or a bug report.
"""

import os

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from ui.settings_widgets import native_path


class CaptureFrameDialog(QDialog):

    def __init__(self, path, to_clipboard, deinterlace, interlaced,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Capture Frame"))

        layout = QVBoxLayout(self)

        dest = QGroupBox(self.tr("Destination"))
        dl = QVBoxLayout(dest)
        choice = QHBoxLayout()
        self._clipboard = QRadioButton(self.tr("Clipboard"))
        self._file = QRadioButton(self.tr("File"))
        choice.addWidget(self._clipboard)
        choice.addWidget(self._file)
        choice.addStretch(1)
        dl.addLayout(choice)
        row = QHBoxLayout()
        self._path = QLineEdit(native_path(path))
        self._path.setMinimumWidth(420)
        row.addWidget(self._path, 1)
        self._browse = QPushButton("…")
        self._browse.setToolTip(self.tr("Choose the folder and name"))
        self._browse.clicked.connect(self._on_browse)
        row.addWidget(self._browse)
        dl.addLayout(row)
        layout.addWidget(dest)

        self._deinterlace = QCheckBox(self.tr("Deinterlace"))
        self._deinterlace.setChecked(bool(deinterlace))
        tip = self.tr("Removes the comb-like lines a moving picture shows "
                      "when a broadcast is interlaced.")
        if not interlaced:
            tip += " " + self.tr("This frame is not interlaced, so it is "
                                 "saved as it is either way.")
        self._deinterlace.setToolTip(tip)
        layout.addWidget(self._deinterlace)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        (self._clipboard if to_clipboard else self._file).setChecked(True)
        self._clipboard.toggled.connect(self._sync)
        self._sync()
        self.adjustSize()

    def _sync(self):
        on = self._file.isChecked()
        self._path.setEnabled(on)
        self._browse.setEnabled(on)

    def _on_browse(self):
        png = self.tr("PNG image (*.png)")
        jpeg = self.tr("JPEG image (*.jpg *.jpeg)")
        path, chosen = QFileDialog.getSaveFileName(
            self, self.tr("Capture Frame"), self._path.text(),
            ";;".join((png, jpeg)))
        if path:
            if not os.path.splitext(path)[1]:
                path += ".jpg" if chosen == jpeg else ".png"
            self._path.setText(native_path(path))

    def to_clipboard(self):
        return self._clipboard.isChecked()

    def path(self):
        return self._path.text().strip()

    def deinterlace(self):
        return self._deinterlace.isChecked()
