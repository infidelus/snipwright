"""Read-only dialog showing the open file's programme information.

Mirrors VideoReDo's "Program Information" window: File, Video and Audio
sections, with a Copy to clipboard button.  Opened from Tools > Show Video
Programme Info or the configured shortcut (Ctrl+L by default).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QWidget,
    QFrame,
    QApplication,
)

from utils.program_info import (
    gather_program_info,
    to_plaintext,
    translate_text,
)


class ProgramInfoDialog(QDialog):

    def __init__(self, source_path, frame_count=None, fps=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(self.tr("Programme Information"))
        self._sections = gather_program_info(source_path, frame_count, fps)

        outer = QVBoxLayout(self)

        # Scrollable so a file with several audio tracks can't grow the window
        # off-screen.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        # Never scroll/stretch sideways: a long value wraps to the width instead.
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(4, 4, 4, 4)

        # Fields rendered full-width (their own wrapping row) so a long value -
        # notably the filename - wraps down the window rather than stretching it
        # sideways.  These go in their own horizontal row rather than the grid,
        # because QGridLayout mis-handles the height of a wrapped, spanned cell.
        # Section titles, labels and values are gathered in English and
        # translated for display; translate_text also handles the audio section
        # title, which is built from a pattern.
        _t = translate_text

        # Matched against the English key, which is what gather_program_info stores.
        full_width = {"Name"}

        for title, rows in self._sections:
            header = QLabel(_t(title))
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            body.addWidget(header)

            grid_rows = []
            for label, value in rows:
                if label not in full_width:
                    grid_rows.append((label, value))
                    continue

                row = QHBoxLayout()
                row.setContentsMargins(8, 0, 0, 0)
                row.setSpacing(8)
                lab = QLabel("%s:" % _t(label))
                val = QLabel(_t(value))
                val.setWordWrap(True)
                val.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                val.setTextInteractionFlags(Qt.TextSelectableByMouse)
                val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
                row.addWidget(lab, 0, Qt.AlignTop)
                row.addWidget(val, 1, Qt.AlignTop)
                body.addLayout(row)

            if not grid_rows:
                continue

            grid = QGridLayout()
            grid.setContentsMargins(8, 0, 0, 8)
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(2)
            grid.setColumnStretch(1, 1)
            grid.setColumnStretch(3, 1)

            # Two label/value pairs per row for a compact, VRD-like layout.
            for idx, (label, value) in enumerate(grid_rows):
                r = idx // 2
                c = (idx % 2) * 2

                lab = QLabel("%s:" % _t(label))
                val = QLabel(_t(value))
                val.setTextInteractionFlags(Qt.TextSelectableByMouse)

                grid.addWidget(lab, r, c, Qt.AlignLeft | Qt.AlignTop)
                grid.addWidget(val, r, c + 1, Qt.AlignLeft | Qt.AlignTop)

            body.addLayout(grid)

        body.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self._scroll = scroll
        self._content = content
        self._fitted = False

        # Buttons: Copy to clipboard (left), OK (right).
        buttons = QHBoxLayout()

        copy_button = QPushButton(self.tr("Copy to clipboard"))
        copy_button.clicked.connect(self._copy_to_clipboard)
        buttons.addWidget(copy_button)

        buttons.addStretch(1)

        ok_button = QPushButton(self.tr("OK"))
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)

        outer.addLayout(buttons)

        # The starting size; _fit_to_content() sets the real height once the
        # window is on screen and its wrapped rows can be measured.
        self.resize(560, 520)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._fitted:
            self._fitted = True
            self._fit_to_content()

    def _fit_to_content(self):
        """Open tall enough to show everything, up to 85% of the screen.

        A fixed 520 pixels showed a scroll bar for an ordinary recording with
        two audio tracks, in every theme (reported 2026-11-13).  The content's
        height is read at the width it will have with no scroll bar - its rows
        wrap, so the height depends on the width - and only content taller
        than 85% of the screen still scrolls.
        """
        layout = self._content.layout()
        layout.activate()
        viewport = self._scroll.viewport()
        width = viewport.width()
        bar = self._scroll.verticalScrollBar()
        if bar.isVisible():
            width += bar.width()
        needed = layout.totalHeightForWidth(width)
        if needed < 0:
            needed = self._content.sizeHint().height()
        height = self.height() + (needed - viewport.height())

        over = self.parentWidget().window() if self.parentWidget() else None
        screen = (over.screen() if over is not None else None) or self.screen()
        area = screen.availableGeometry() if screen is not None else None
        if area is not None:
            # The cap is on the whole window, title bar included.
            decoration = max(0, self.frameGeometry().height() - self.height())
            height = min(height, int(area.height() * 0.85) - decoration)
        height = max(height, self.minimumSizeHint().height())
        self.resize(self.width(), height)

        # Qt centred the window at its first size and keeps the top-left
        # corner on a resize, so centre it again over the editor (or the
        # screen), kept on the screen - as Remembered logos does.
        from PySide6.QtCore import QRect
        centre = (over.frameGeometry().center() if over is not None
                  else (area.center() if area is not None else None))
        if centre is not None:
            frame = QRect(self.frameGeometry())
            frame.moveCenter(centre)
            if area is not None:
                frame.moveLeft(max(area.left(), min(
                    frame.left(), area.right() - frame.width() + 1)))
                frame.moveTop(max(area.top(), min(
                    frame.top(), area.bottom() - frame.height() + 1)))
            self.move(frame.topLeft())

    def _copy_to_clipboard(self):
        # Copy what's actually on screen: the gathered sections keep English
        # keys internally, so translate the titles, labels and values before
        # rendering them, otherwise a German user would paste English text.
        _t = translate_text

        translated = [
            (_t(title), [(_t(label), _t(value)) for label, value in rows])
            for title, rows in self._sections
        ]
        QApplication.clipboard().setText(
            to_plaintext(translated)
        )
