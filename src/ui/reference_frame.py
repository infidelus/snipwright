"""Reference Frame: hold one picture beside the editor while you look for it.

Requested during testing, from a forum suggestion.  After an advert break a
channel often repeats the last few seconds of the programme, and the cut has
to land on the frame that matches the one before the break.  Avidemux users do
this by saving a still (Ctrl+E) and comparing by eye; here the still stays on
screen, and a figure says how closely the frame on screen matches it, so
stepping through the repeat shows the match rising to 100%.

The panel either sits docked at the top of the editor's right-hand column,
above the scene list (which gets shorter while it is open, so the preview
loses nothing), or floats in a small window of its own.  Docked is the
default: being part of the editor, it can never take the keyboard away from
it.  Floating, it passes on every key it does not use, so the arrow keys
still step frames after a click in it.

The match is measured on the DECODED frame, reduced to a small grey
thumbnail by area averaging - not on the preview picture.  The preview is
drawn two ways (a quick scale while scrubbing, a smooth one at rest), so one
frame could be drawn slightly differently on two visits: a reference taken
from one drawing then read 99% against the same frame in the other, and
stayed there (found in testing, before release).  The decoded frame is the same
whichever way it is drawn.  The panel notices a new frame by watching the
preview change, and asks the editor for the frame then - usually from its
cache of recent frames.  It is a guide to where to look, not a decision -
neighbouring frames of a still shot score nearly as high as the matching
one, so the last step is always by eye.
"""

import numpy as np
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# The size both pictures are reduced to before comparing.  Small enough to be
# instant, large enough that two different shots never look alike.
_SAMPLE_W, _SAMPLE_H = 64, 36

# How far apart the two thumbnails may be, on average per pixel (0-255), and
# still show green.  Measured on a BBC One HD recording, against a reference
# in a slow-moving shot: the same frame 0, one frame on 0.8, two on 1.6, five
# on 2.8, a second on 6.8, a different shot 40 or more; on a 5USA SD
# recording one frame on scored 95%, five on 86%.  So green means "this
# frame or its immediate neighbour", which is as close as a figure can get -
# the last step is by eye.  How a channel's repeated material scores against
# the original has not been measured: if it is re-encoded it will sit a
# little above 0.
_SAME = 1.5
# The difference at which the figure reaches 0%.  Anything this far apart is
# simply a different picture; the exact number below it is what matters.
_ZERO = 40.0

# The picture's width when the floating window first opens; docked, it
# takes the column's width.  Floating, it then follows the window's size.
_FLOAT_W = 400
# The smallest the floating picture may be dragged to.
_FLOAT_MIN_W = 240


def sample(frame):
    """A small greyscale copy of a decoded ``frame`` to compare, or None.

    Area averaging, so the sample is the mean of each block of the picture
    rather than whichever pixels a scaler happened to pick.
    """
    if frame is None:
        return None
    try:
        small = frame.reformat(width=_SAMPLE_W, height=_SAMPLE_H,
                               format="gray", interpolation="AREA")
        data = small.to_ndarray()
    except Exception:
        return None
    return np.asarray(data, dtype=np.float32)[:_SAMPLE_H, :_SAMPLE_W].copy()


def difference(a, b):
    """Mean absolute difference per pixel between two samples, 0-255."""
    if a is None or b is None or a.shape != b.shape:
        return None
    return float(np.abs(a - b).mean())


def match_percent(diff):
    """The difference as a match figure: 100% identical, 0% unrelated."""
    if diff is None:
        return None
    return max(0, min(100, int(round(100.0 * (1.0 - diff / _ZERO)))))


class _ScaledPicture(QLabel):
    """The reference picture, redrawn to fit whatever size it is given -
    but never above its own full size, where enlarging would only blur it."""

    def __init__(self):
        super().__init__()
        self._image = None
        self._hint = QSize(_FLOAT_W, _FLOAT_W * 9 // 16)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: black;")

    def set_image(self, image):
        self._image = image
        self._redraw()

    def set_hint(self, width, height):
        self._hint = QSize(width, height)
        self.updateGeometry()

    def sizeHint(self):
        return self._hint

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._redraw()

    def _redraw(self):
        if self._image is None or self._image.isNull():
            return
        width = min(self.width(), self._image.width())
        height = min(self.height(), self._image.height())
        if width <= 0 or height <= 0:
            return
        self.setPixmap(QPixmap.fromImage(self._image).scaled(
            width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))


class _FloatingWindow(QDialog):
    """The window the panel lives in while floating.

    Hands every key it receives to the editor.  A click in the window makes
    it the active one, and without this the arrow keys would then go nowhere
    useful - which is what happened before it was added.
    """

    def __init__(self, editor, panel):
        super().__init__(editor)
        self._editor = editor
        self._panel = panel
        self.setWindowTitle(panel.tr("Reference Frame"))
        # A tool window stays above the editor and is not a separate entry
        # in the task bar.
        self.setWindowFlag(Qt.Tool, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        QVBoxLayout(self).setContentsMargins(6, 6, 6, 6)

    def keyPressEvent(self, event):
        # Every key, Escape included - the editor already gives Escape a
        # meaning, and two different ones depending on which window has the
        # focus would be a trap.
        self._editor.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self._editor.keyReleaseEvent(event)

    def closeEvent(self, event):
        # The title bar's close button closes the panel, not just its window.
        self._panel.close_panel(from_window=True)
        super().closeEvent(event)


class ReferenceFramePanel(QWidget):
    """The reference picture, its timecode, the match figure and buttons."""

    def __init__(self, editor, dock_slot):
        super().__init__()
        self._editor = editor
        self._slot = dock_slot          # the layout it sits in when docked
        self._window = None             # the floating window, made on demand
        self._docked = True
        self._closing = False

        self._frame = None              # frame number of the reference
        self._image = None              # the full reference picture
        self._sample = None             # what it is compared by
        self._last_key = None           # the preview pixmap last compared

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(4)
        self._picture = _ScaledPicture()
        # Floating, the picture takes whatever room the window is given.
        layout.addWidget(self._picture, 1)

        self._caption = QLabel()
        self._caption.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._caption)

        self._match = QLabel()
        self._match.setAlignment(Qt.AlignCenter)
        font = self._match.font()
        font.setPointSizeF(font.pointSizeF() * 1.3)
        font.setBold(True)
        self._match.setFont(font)
        self._match.setToolTip(self.tr(
            "How closely the frame in the editor matches this one. Step "
            "through the part repeated after an advert break and the figure "
            "rises to 100% on the matching frame.<br><br>Frames next to each "
            "other in a still shot score almost as high, so check the last "
            "step by eye."
        ))
        layout.addWidget(self._match)

        # Two rows of two, so the buttons fit the 280-pixel column in German
        # as well as English.  None of them takes the keyboard focus: a
        # focused button would swallow the arrow keys meant for the editor.
        buttons = QGridLayout()
        buttons.setSpacing(4)
        self._goto = QPushButton(self.tr("Go to Reference"))
        self._goto.setToolTip(self.tr("Move the editor to the reference frame."))
        self._goto.clicked.connect(self._go_to_reference)
        self._replace = QPushButton(self.tr("Use Current Frame"))
        self._replace.setToolTip(self.tr(
            "Make the frame in the editor the reference instead."))
        self._replace.clicked.connect(self._editor.set_reference_frame)
        self._dock_btn = QPushButton()
        self._dock_btn.clicked.connect(self._toggle_docked)
        close = QPushButton(self.tr("Close"))
        close.clicked.connect(self.close_panel)
        for i, button in enumerate((self._goto, self._replace,
                                    self._dock_btn, close)):
            button.setFocusPolicy(Qt.NoFocus)
            buttons.addWidget(button, i // 2, i % 2)
        layout.addLayout(buttons)

        # Watch the editor's preview rather than hooking every place that
        # draws it: there are several, and a new one added later would
        # otherwise silently stop the figure updating.
        self._timer = QTimer(self)
        self._timer.setInterval(120)
        self._timer.timeout.connect(self._compare)

        self.hide()

    # -- where it lives ------------------------------------------------------
    def is_open(self):
        return self._frame is not None and (
            self.isVisible() or (self._window is not None
                                 and self._window.isVisible()))

    def is_docked(self):
        return self._docked

    def open_panel(self, docked):
        """Show the panel, docked in the column or in its own window."""
        self._docked = bool(docked)
        if self._docked:
            if self._window is not None:
                self._window.hide()
            self.setParent(None)
            self._slot.addWidget(self)
            self._dock_btn.setText(self.tr("Float"))
            self._dock_btn.setToolTip(self.tr(
                "Move the reference into a window of its own, which can be "
                "placed anywhere."))
        else:
            if self._window is None:
                self._window = _FloatingWindow(self._editor, self)
            self._slot.removeWidget(self)
            self._window.layout().addWidget(self)
            self._dock_btn.setText(self.tr("Dock"))
            self._dock_btn.setToolTip(self.tr(
                "Put the reference back above the scene list."))
        self._fit_picture()
        self.show()
        if not self._docked:
            if not self._window.isVisible():
                # Sized to fit only the first time; after that it reopens at
                # whatever size the user dragged it to.
                if not getattr(self, "_placed", False):
                    self._window.adjustSize()
                self._place_window()
                self._window.show()
            self._window.raise_()
        self._timer.start()
        self._last_key = None
        self._compare()
        self._editor.reference_panel_changed()

    def _place_window(self):
        # Over the editor's right-hand column the first time - where the
        # docked panel sits - and wherever the user left it after that.
        if getattr(self, "_placed", False):
            return
        geo = self._editor.frameGeometry()
        self._window.move(max(0, geo.right() - self._window.width() - 80),
                          geo.top() + 80)
        self._placed = True

    def _toggle_docked(self):
        self.open_panel(not self._docked)
        self._editor.remember_reference_docked(self._docked)

    def close_panel(self, from_window=False):
        if self._closing:
            return
        self._closing = True
        try:
            self._timer.stop()
            self.hide()
            if self._window is not None and not from_window:
                self._window.hide()
            self._editor.reference_panel_changed()
        finally:
            self._closing = False

    def discard(self):
        """Forget the reference and remove the panel (a new recording)."""
        self.close_panel()
        self._slot.removeWidget(self)
        if self._window is not None:
            self._window.deleteLater()
            self._window = None
        self.deleteLater()

    # -- the reference ---------------------------------------------------------
    def set_reference(self, frame, image, timecode, decoded):
        """Hold ``image`` (the full picture) as frame ``frame``, comparing by
        ``decoded``, the decoded frame itself."""
        self._frame = frame
        self._image = image
        self._sample = sample(decoded)
        self._caption.setText(self.tr("Reference: %s") % timecode)
        self._last_key = None
        self._fit_picture()
        self._compare()

    def reference_frame(self):
        return self._frame

    def _fit_picture(self):
        if self._image is None:
            return
        picture = self._picture
        if self._docked:
            # The column's width, which the scene list fixes.
            width = max(160, self._editor.scene_list.width())
            height = int(round(width * 9 / 16))
            picture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            picture.setFixedSize(width, height)
        else:
            # Follows the window, from a small floor up to the picture's own
            # full size - never enlarged beyond 100%.
            picture.setSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
            picture.setMinimumSize(_FLOAT_MIN_W, _FLOAT_MIN_W * 9 // 16)
            picture.setMaximumSize(
                max(_FLOAT_MIN_W, self._image.width()),
                max(_FLOAT_MIN_W * 9 // 16, self._image.height()))
            picture.set_hint(_FLOAT_W, _FLOAT_W * 9 // 16)
        picture.set_image(self._image)

    # -- comparing -------------------------------------------------------------
    def _compare(self):
        pixmap = self._editor.preview.pixmap()
        if pixmap is None or pixmap.isNull() or self._sample is None:
            self._match.setText("")
            return
        # Not while playing: the figure means nothing at 25 frames a second,
        # and asking for each frame would add decoding to the playback.
        if getattr(self._editor, "_playing", False):
            return
        key = pixmap.cacheKey()
        if key == self._last_key:
            return
        self._last_key = key
        diff = difference(self._sample,
                          sample(self._editor.reference_compare_frame()))
        pct = match_percent(diff)
        if pct is None:
            self._match.setText("")
            return
        self._match.setText(self.tr("Match: %d%%") % pct)
        colour = "#3cb371" if diff <= _SAME else (
            "#d4a017" if pct >= 75 else "gray")
        self._match.setStyleSheet("color: %s;" % colour)

    def _go_to_reference(self):
        if self._frame is not None:
            self._editor.goto_frame(self._frame)
