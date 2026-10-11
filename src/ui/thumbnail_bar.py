"""
ThumbnailBar - the strip of frame thumbnails beneath the preview.

Behaviour:
  - Thumbnails are a fixed size (~120px).  The number shown is computed from
    the available width, so the strip fills the window and re-flows on resize.
  - The count is always odd, so the cursor frame sits in the dead centre.
    Near the start/end of the file the off-the-edge slots show blank, so the
    cursor stays centred rather than drifting.
  - A pixmap cache keyed by frame index means stepping one frame only decodes
    the single newly-revealed thumbnail; the other ten are reused.  Frames are
    fetched in increasing index order so the decoder stays on its fast
    sequential path.

The bar reads frames from window.frames (the FrameSequence) exactly as before,
so it works for both the in-RAM and decode-on-demand back ends.
"""

import math

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QSizePolicy,
)

from media.renderer import render_frame
from media.scrub_worker import frame_label


# Target width per thumbnail; the real width flexes slightly so the strip
# fills the bar edge-to-edge with no gaps.
THUMB_TARGET_WIDTH = 120
THUMB_HEIGHT = 68
THUMB_SPACING = 4
THUMB_MIN_WIDTH = 80
MIN_THUMBS = 3
MAX_PIXMAP_CACHE = 400


class _Thumb(QLabel):

    # Emitted with the thumb's frame index when clicked (release inside the
    # widget).  -1 means the thumb is empty / has no frame.
    clicked = Signal(int)

    def __init__(self):
        super().__init__()

        # The frame this thumb currently shows; -1 when empty.
        self.frame_index = -1

        # Picture type letter ("I"/"P"/"B") to overlay, or "" for none.
        self.letter = ""
        # Whether this frame is inside a kept scene.  Drives the band
        # along the top edge; see _draw_scene_band().
        self.in_scene = False

        # True when the playhead sits on this frame.  Derived rather than
        # assigned: the refresh paths already keep frame_index correct, and
        # a separate flag set alongside it in seven places would be one
        # missed edit away from a stale ring.
        self.bar = None

        self.setFixedHeight(
            THUMB_HEIGHT
        )

        # Always the same width: the strip changes how many thumbnails it
        # shows, and the gaps between them, never their size.  Stretching
        # them to fill the bar made them shrink and grow with the window -
        # most visibly when the Charms bar took its width away - and the
        # user's ruling was that thumbnails always stay the same size.
        self.setFixedWidth(
            THUMB_TARGET_WIDTH
        )

        self.setAlignment(
            Qt.AlignCenter
        )

        # A pointing-hand cursor hints that thumbnails are clickable.
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(_STYLE_EMPTY)

    # Report a fixed size hint that does NOT depend on the current pixmap.
    #
    # A plain QLabel returns its pixmap's size as the size hint.  Combined with
    # the Expanding policy and _fit_to_label() (which scales each pixmap to its
    # label's current width), that formed a feedback loop: the cursor thumb's
    # 3px border made its hint a hair wider, the layout gave it more width, the
    # next refresh scaled its pixmap wider still, and it ballooned across
    # refreshes while its neighbours were squeezed toward the minimum (the
    # "4:3" thumbs).  Pinning the hint to the canonical thumbnail size decouples
    # layout width from pixmap width, so every slot shares the bar equally and
    # the pixmap is just painted (centred/scaled) within whatever width it gets.
    def sizeHint(self):
        return QSize(THUMB_TARGET_WIDTH, THUMB_HEIGHT)

    def minimumSizeHint(self):
        return QSize(THUMB_MIN_WIDTH, THUMB_HEIGHT)

    def mouseReleaseEvent(self, event):
        # Treat a left-click release inside the thumb as a request to jump to
        # that frame.  Ignore empty thumbs.
        if (
            event.button() == Qt.LeftButton
            and self.rect().contains(event.position().toPoint())
            and self.frame_index >= 0
        ):
            self.clicked.emit(self.frame_index)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        # Draw the thumbnail (pixmap + border) as usual, then overlay the
        # cursor ring and the picture-type letter.
        super().paintEvent(event)

        # Ring first, then the band inside it - see _draw_scene_band(), which
        # insets itself past the ring so the two sit side by side rather than
        # one covering the other.
        self._draw_cursor_ring()
        self._draw_scene_band()

        if not self.letter:
            return

        colour = _FRAME_TYPE_COLOURS.get(self.letter, QColor("#e0e0e0"))

        painter = QPainter(self)
        try:
            font = QFont()
            font.setPixelSize(13)
            font.setBold(True)
            painter.setFont(font)

            metrics = painter.fontMetrics()
            text_w = metrics.horizontalAdvance(self.letter)
            text_h = metrics.height()

            # A small translucent chip so the letter reads over any image.
            pad = 2
            box_w = text_w + pad * 2
            box_h = text_h
            painter.fillRect(
                3, 3, box_w, box_h, QColor(0, 0, 0, 150)
            )

            painter.setPen(colour)
            painter.drawText(
                3 + pad,
                3 + metrics.ascent(),
                self.letter,
            )
        finally:
            painter.end()

    @property
    def is_cursor(self):
        """Whether the playhead is on this thumb."""
        bar = self.bar
        if bar is None or self.frame_index < 0:
            return False
        try:
            return self.frame_index == bar.main.current_frame
        except AttributeError:
            return False

    def _draw_scene_band(self):
        """Mark a frame inside a kept scene with a band along its top edge.

        Where the boundary is, is then where the band stops - a hard edge
        between two adjacent thumbnails, which is what someone stepping
        frame-by-frame towards a cut is actually looking for.  The border
        alone left that edge one pixel wide.
        """
        if not self.in_scene:
            return

        w = self.width()
        # On the cursor frame the ring runs along this same top edge, so start
        # the band below it.  Letting the ring sit on top would eat half the
        # band on precisely the frame being looked at - the same mistake the
        # ring itself was created to fix, one layer further in.
        # Below the border normally, below the ring on the cursor frame - the
        # ring now occupies the edge, so it is the ring the band clears.
        inset = _CURSOR_RING if self.is_cursor else _OUTER_BORDER
        band = _SCENE_BAND
        if w <= 2 * inset or self.height() <= inset + band + _SCENE_BAND_EDGE:
            return

        painter = QPainter(self)
        try:
            inner_w = w - 2 * inset
            painter.fillRect(inset, inset, inner_w, band,
                             QColor(_SCENE_BAND_COLOUR))
            painter.fillRect(inset, inset + band, inner_w,
                             _SCENE_BAND_EDGE, QColor(_SCENE_BAND_EDGE_COLOUR))
        finally:
            painter.end()

    def _draw_cursor_ring(self):
        """Ring the current frame *inside* its own border, not instead of it.

        The cursor used to be a stylesheet border like every other state,
        which meant it replaced whatever the frame already showed.  The one
        frame whose scene membership matters most - the one you have just
        stepped onto - was therefore the only frame not showing it, so
        stepping through a cut you could see the boundary right up until you
        reached it, at which point the blue took over and the yellow
        vanished.  Reported by a user reviewing cut points after a repair,
        who could not tell when he had arrived at the edge.

        Drawn rather than styled because Qt style sheets give a widget one
        border, and two rings are wanted here: the outer says which scene the
        frame belongs to, the inner says the cursor is on it.  Inset by the
        outer border's width plus a pixel of breathing room, so neither
        covers the other.
        """
        if not self.is_cursor:
            return

        inset = 0                      # at the edge; see _CURSOR_RING
        ring = _CURSOR_RING
        w = self.width()
        h = self.height()
        if w <= 2 * (inset + ring) or h <= 2 * (inset + ring):
            return

        painter = QPainter(self)
        try:
            colour = QColor(_CURSOR_COLOUR)
            # Four filled rectangles rather than drawRect with a wide pen.
            # A pen is centred on the path it strokes, and for an even width
            # Qt has to put the odd half-pixel on one side: the left and top
            # edges came out flush against the border while the right and
            # bottom sat a pixel short of it.  Visible when zoomed in, and
            # exactly the sort of asymmetry that looks like a rendering
            # glitch rather than a deliberate inset.  Filling the four sides
            # explicitly leaves no geometry to interpret.
            inner_w = w - 2 * inset
            inner_h = h - 2 * inset
            painter.fillRect(inset, inset, inner_w, ring, colour)
            painter.fillRect(inset, h - inset - ring, inner_w, ring, colour)
            painter.fillRect(inset, inset, ring, inner_h, colour)
            painter.fillRect(w - inset - ring, inset, ring, inner_h, colour)
        finally:
            painter.end()


# Picture-type badge colours: I/IDR/keyframes green, P amber, B grey-blue.
_FRAME_TYPE_COLOURS = {
    "IDR": QColor("#37d67a"),
    "I": QColor("#37d67a"),
    "P": QColor("#f5a623"),
    "B": QColor("#9bb4d4"),
}


# Every thumbnail's outer border is one pixel, and says which scene the frame
# belongs to.  The cursor ring is drawn inside that - see
# ThumbnailBarLabel._draw_cursor_ring() - so a frame can show both at once.
#
# The gap between the two started at one pixel, to stop them reading as a
# single thick band.  Set to zero once it was seen on real thumbnails: yellow
# against blue separates on colour alone, and closing the gap gives the ring
# a pixel more image to sit against, which is worth having on a dark frame
# where it competes with black.  Put it back to 1 if the two ever end up in
# similar colours.
_OUTER_BORDER = 1
# The cursor ring sits AT the thumbnail's edge again, where it started.
#
# It was moved inside the border to fix a real fault: the cursor style
# used to replace the border, so the one frame you had just stepped onto
# was the only one not showing whether it was inside a scene.  That
# reason is gone.  Scene membership is the band's job now, and the band
# is drawn separately, so the ring can cover the border without hiding
# anything.  Inset by a few pixels it just looked odd.
_CURSOR_RING = 2
_CURSOR_COLOUR = "#2f9bff"

# A band along the top edge of every frame that is inside a kept scene,
# drawn over the picture rather than above it.
#
# The 1px border was already saying this, and was reported twice as too
# hard to see - once against a dark scene, once on a bright one where the
# picture and the border were a similar colour.  A single pixel competing
# with arbitrary picture content is a losing proposition whatever colour
# it is, and a strip of hundreds of thumbnails is exactly where it has to
# read at a glance.
#
# Inside the frame, not above it: the user who asked for this pointed at
# another editor that puts a line above each thumbnail, and noted himself
# that it costs vertical space.  Overlaying the top few pixels of the
# picture costs none.
#
# The dark hairline under the band is what makes it survive a pale frame.
# Yellow on white is nearly invisible; yellow with a dark edge under it
# is not.
_SCENE_BAND = 4
_SCENE_BAND_EDGE = 1
_SCENE_BAND_COLOUR = "#e6c200"
_SCENE_BAND_EDGE_COLOUR = "#1a1400"

_STYLE_EMPTY = (
    "background:#081420; border:1px solid #222;"
)

# Kept for the cursor's darker backing, which still reads as "you are here"
# underneath the ring.  The border is the plain one: the border now always
# belongs to the scene state, so the ring never erases it.
_STYLE_CURSOR = (
    "background:#001026; border:1px solid #222;"
)

_STYLE_MARKER = (
    "background:#06121c; border:1px solid #19c3c3;"
)

# No yellow edge any more - the band along the top says "inside a scene"
# on its own, and a border repeating it only added a boxed-in look.  It
# also hurt the frame that matters most: sandwiched between the yellow
# border outside it and the yellow band inside it, the blue cursor ring
# read as a muddy line between two yellows rather than as blue.
#
# The darker background stays, so the edges still differ a little where
# the picture does not reach.  Scene MARKERS keep their cyan border:
# that is a different state with no band of its own, so there the border
# is carrying the meaning rather than duplicating it.
_STYLE_SELECTED = (
    "background:#203000; border:1px solid #222;"
)

_STYLE_NORMAL = (
    "background:#081420; border:1px solid #222;"
)

# The strip's own background, in BOTH themes.
#
# theme.py already says the timeline, thumbnail and scene bars keep dark
# video-editor colours whatever the theme is, and the timeline and scene bars
# do - they fill their whole area, so nothing of the window shows through.
# This bar never set a background at all, so in light mode the gaps around the
# thumbnails came out #f0f0f0 and the strip sat on a bright panel.
#
# That is not cosmetic.  The thumbnails themselves are pixel-identical in the
# two themes - border, scene band and cursor ring all the same colours - yet
# the strip was reported as markedly clearer in dark mode.  The whole of that
# difference was the surround: a yellow band against a bright background has
# far less to separate it than the same band against a dark one.  The user who
# asked for clearer cut marks works in light mode, so he had the worse of it.
#
# Matched to what the dark theme was already producing, so dark mode is
# unchanged and light mode gains what it should always have had.
_STRIP_BACKGROUND = "#333339"


class ThumbnailBar(QWidget):

    def __init__(self, window):
        super().__init__()

        # Scoped to this class so it styles the strip itself and does not
        # cascade into the thumbnails, which set their own.
        #
        # WA_StyledBackground is REQUIRED, not belt and braces.  A direct
        # QWidget subclass ignores a style sheet background entirely unless
        # either this attribute is set or paintEvent draws PE_Widget itself -
        # Qt paints backgrounds for the widgets it knows about, and a plain
        # QWidget subclass is not one of them.  Without it the style sheet
        # below is accepted, applies to nothing, and the strip quietly keeps
        # the window's own colour.  Shipped once exactly like that.
        #
        # Not setAutoFillBackground(): that fills from the PALETTE, which is
        # the light colour in light mode - the very thing being overridden
        # here.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "ThumbnailBar { background:%s; }" % _STRIP_BACKGROUND
        )

        # The MainWindow.  Named 'main' to avoid shadowing QWidget.window().
        self.main = window

        self._labels = []
        self._count = 0

        # frame_index -> rendered QPixmap (content only; borders set per refresh)
        self._pixmap_cache = {}
        self._cache_order = []

        # frame_index -> picture-type letter ("I"/"P"/"B"); kept in step with
        # the pixmap cache.  Whether it's actually drawn depends on the setting.
        self._letters = {}
        self._show_frame_type = False

        # No layout: the thumbs are placed by hand in _place(), at a fixed
        # width and spacing, centred on the cursor's frame, with the ones at
        # either end cut off by the bar's edge.  A layout can only share the
        # width out - stretching the thumbs, or (tried in a test build)
        # widening the gaps - and the user's ruling is thumbs of one size
        # with the old narrow gap, the strip always full, at any width.
        #
        # The bar must still NOT report a large minimum width back up to the
        # window: when maximised it holds many thumbs, and if they counted
        # the window's minimum width would balloon and refuse to shrink on
        # un-maximise (the stuck-size trap the preview avoids).  With no
        # layout nothing is reported; the Ignored policy and the zero-width
        # minimumSizeHint() below make sure of it.
        self.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Fixed,
        )

        self.setFixedHeight(
            THUMB_HEIGHT + 32
        )

        self._rebuild_labels()

    def minimumSizeHint(self):
        # Zero width: the bar never forces the window wider (see __init__).
        return QSize(0, THUMB_HEIGHT + 32)

    # ------------------------------------------------------------------ #
    # Layout / sizing
    # ------------------------------------------------------------------ #

    def _fit_count(self):
        """Enough thumbs to fill the bar from the middle out, as an odd number.

        The cursor's thumb sits in the centre; each side then needs enough
        whole-or-partial thumbs to reach its edge, and the outermost are cut
        off where the bar ends.
        """
        width = self.width()

        if width <= 0:
            return MIN_THUMBS

        side = max(0.0, (width - THUMB_TARGET_WIDTH) / 2)
        per_side = math.ceil(side / (THUMB_TARGET_WIDTH + THUMB_SPACING))

        return max(MIN_THUMBS, 2 * per_side + 1)

    def _place(self):
        """Put each thumb at its fixed place, centred on the middle one.

        Thumbs past either edge are simply clipped by the bar, as child
        widgets are.
        """
        n = len(self._labels)
        if not n:
            return
        pitch = THUMB_TARGET_WIDTH + THUMB_SPACING
        first_x = (self.width() - THUMB_TARGET_WIDTH) // 2 - (n // 2) * pitch
        y = (self.height() - THUMB_HEIGHT) // 2
        for i, label in enumerate(self._labels):
            label.setGeometry(first_x + i * pitch, y,
                              THUMB_TARGET_WIDTH, THUMB_HEIGHT)

    def _rebuild_labels(self):
        """(Re)create the thumb labels when the fitting count changes."""
        n = self._fit_count()

        if n == self._count and self._labels:
            return

        for label in self._labels:
            label.hide()
            label.deleteLater()

        self._labels = []

        for _ in range(n):
            label = _Thumb()
            # So the thumb can tell whether the playhead is on it without
            # every refresh path having to remember to say so - frame_index
            # is already maintained everywhere, and current_frame is the
            # single source of truth for where the cursor is.
            label.bar = self
            label.clicked.connect(self._on_thumb_clicked)
            label.setParent(self)
            label.show()
            self._labels.append(label)

        self._count = n

        self._place()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._rebuild_labels()
        self._place()

        # Re-render to the new thumb width so the strip stays filled.
        self.refresh()

    # ------------------------------------------------------------------ #
    # Cache
    # ------------------------------------------------------------------ #

    def clear_cache(self):
        self._pixmap_cache.clear()
        self._cache_order.clear()
        self._letters.clear()

    def set_frame_type_display(self, mode):
        """Update whether the I/P/B badge is shown on thumbnails.

        mode is the config value ("none"/"thumbnails"/"preview"/"both"); the
        badge shows for "thumbnails" and "both".
        """
        show = mode in ("thumbnails", "both")
        if show == self._show_frame_type:
            return
        self._show_frame_type = show
        for label in self._labels:
            self._apply_letter(label, label.frame_index)
            label.update()

    def _apply_letter(self, label, frame_index):
        """Set a label's overlay letter from the cache, honouring the setting."""
        if self._show_frame_type and frame_index >= 0:
            label.letter = self._letters.get(frame_index, "")
        else:
            label.letter = ""

    def _cached_pixmap(self, frame_index):
        """Return the cached pixmap for a frame, or None.

        Cached at a single canonical width (THUMB_TARGET_WIDTH) and keyed by
        frame index alone, so a frame stays cached as it shifts between slots
        whose pixel widths differ by a pixel or two.  The tiny rescale to the
        actual slot width happens on display and is free (no decode).
        """
        return self._pixmap_cache.get(frame_index)

    def _store_pixmap(self, frame_index, pixmap):
        if frame_index not in self._pixmap_cache:
            self._cache_order.append(frame_index)

        self._pixmap_cache[frame_index] = pixmap

        while len(self._cache_order) > MAX_PIXMAP_CACHE:
            old = self._cache_order.pop(0)
            self._pixmap_cache.pop(old, None)
            self._letters.pop(old, None)

    def _fit_to_label(self, pixmap, label):
        """Scale a canonical-width cached pixmap to a label's exact width.

        A cheap pixmap scale (no decode); the difference is usually 1-2px.
        """
        w = label.width() or THUMB_TARGET_WIDTH
        if pixmap.width() == w:
            return pixmap
        return pixmap.scaledToWidth(w, Qt.SmoothTransformation)

    # ------------------------------------------------------------------ #
    # Drawing
    # ------------------------------------------------------------------ #

    def set_center_from_image(self, frame_index, image, letter=""):
        """Cache the cursor frame (from the scrub worker's preview image) at
        the canonical thumbnail width, then refresh so it's sized by the same
        path as every other thumbnail.  Guarantees the centre thumbnail matches
        the preview without a separate, inconsistently-sized render.
        """
        from PySide6.QtGui import QPixmap

        if frame_index not in self._pixmap_cache:
            pixmap = QPixmap.fromImage(image).scaledToWidth(
                THUMB_TARGET_WIDTH, Qt.SmoothTransformation
            )
            self._store_pixmap(frame_index, pixmap)
        if letter:
            self._letters[frame_index] = letter

        # Place it via the normal refresh so all slots size consistently.
        if frame_index == self.main.current_frame:
            self.refresh()

    def set_center_from_frame(self, frame_index, frame, container):
        """Cache the cursor frame (already decoded for the preview) at the
        canonical thumbnail width, then refresh.  Same single sizing path as
        all other thumbnails - no special-case rendering that could mis-size.
        """
        if frame is None:
            return

        if frame_index not in self._pixmap_cache:
            pixmap = render_frame(
                frame,
                container,
                THUMB_TARGET_WIDTH,
                THUMB_HEIGHT,
            )
            self._store_pixmap(frame_index, pixmap)
        self._letters[frame_index] = frame_label(
            frame, getattr(self.main, "fetcher", None), frame_index
        )

    def refresh_sync(self):
        """Refresh the strip decoding any uncached thumbnails inline.

        Used during frame-stepping, where the user watches the strip to find
        a cut point so it must stay exactly in sync.  Stepping shifts the
        strip by one frame, so at most one thumbnail is uncached and the
        decode is a cheap sequential frame - fast enough to do on the spot.
        """
        # Hidden from the View menu: decode nothing for a strip nobody can
        # see.  Showing it again calls refresh(), which catches up.
        if self.isHidden():
            return

        window = self.main

        if not self._labels:
            return

        frames = window.frames
        total = len(frames)

        if not total:
            for label in self._labels:
                label.frame_index = -1
                label.letter = ""
                label.clear()
                label.in_scene = False   # or a cleared slot keeps a stale band
                label.setStyleSheet(_STYLE_EMPTY)
            return

        count = self._count
        half = count // 2

        start = window.current_frame - half
        max_start = max(0, total - count)
        start = max(0, min(start, max_start))

        self._wanted = {}

        for i, label in enumerate(self._labels):
            frame_index = start + i

            if frame_index < 0 or frame_index >= total:
                label.frame_index = -1
                label.letter = ""
                label.clear()
                label.in_scene = False   # or a cleared slot keeps a stale band
                label.setStyleSheet(_STYLE_EMPTY)
                continue

            label.frame_index = frame_index
            self._wanted[frame_index] = label

            pixmap = self._cached_pixmap(frame_index)

            if pixmap is None:
                # Decode this one inline (cheap: a sequential fast-path frame).
                frame = frames[frame_index]
                if frame is not None:
                    pixmap = render_frame(
                        frame,
                        window.container,
                        THUMB_TARGET_WIDTH,
                        THUMB_HEIGHT,
                    )
                    self._store_pixmap(frame_index, pixmap)
                    self._letters[frame_index] = frame_label(
            frame, getattr(self.main, "fetcher", None), frame_index
        )

            if pixmap is not None:
                label.setPixmap(self._fit_to_label(pixmap, label))

            self._apply_letter(label, frame_index)
            self._apply_style(label, frame_index)

    def refresh(self):
        # Hidden from the View menu: decode nothing for a strip nobody can
        # see.  Showing it again calls refresh(), which catches up.
        if self.isHidden():
            return

        window = self.main

        if not self._labels:
            return

        frames = window.frames
        total = len(frames)

        count = self._count
        half = count // 2

        if not total:
            for label in self._labels:
                label.frame_index = -1
                label.letter = ""
                label.clear()
                label.in_scene = False   # or a cleared slot keeps a stale band
                label.setStyleSheet(_STYLE_EMPTY)
            return

        # Cursor centred in general, but clamp at the file ends so the bar
        # stays full (frames fall off the side rather than showing blanks).
        start = window.current_frame - half

        max_start = max(0, total - count)

        start = max(0, min(start, max_start))

        # Map of which frame each visible label wants, so a thumbnail decoded
        # later (off-thread) can be matched to the right label and stale
        # deliveries (from a previous strip) can be ignored.
        self._wanted = {}

        to_decode = []

        for i, label in enumerate(self._labels):

            frame_index = start + i

            # Only short files leave trailing slots empty.
            if frame_index < 0 or frame_index >= total:
                label.frame_index = -1
                label.letter = ""
                label.clear()
                label.in_scene = False   # or a cleared slot keeps a stale band
                label.setStyleSheet(_STYLE_EMPTY)
                continue

            label.frame_index = frame_index
            self._wanted[frame_index] = label

            pixmap = self._cached_pixmap(frame_index)

            if pixmap is not None:
                # Cached - scale to this slot (cheap) and show immediately.
                label.setPixmap(self._fit_to_label(pixmap, label))
            else:
                # Not cached: leave the current pixmap in place for now (avoids
                # a distracting flash to blank) and ask the worker to decode it
                # at the canonical width.
                to_decode.append(
                    (frame_index, THUMB_TARGET_WIDTH, THUMB_HEIGHT)
                )

            # Apply the badge from the letter cache.  For an uncached frame the
            # letter isn't known yet; set_thumb_image() will apply it when the
            # worker delivers the thumbnail.
            self._apply_letter(label, frame_index)

            self._apply_style(label, frame_index)

        # Hand the uncached thumbnails to the background worker.  Decode them
        # in left-to-right order so the strip fills like a normal load rather
        # than visibly radiating outwards from the centre.
        if to_decode:
            to_decode.sort(key=lambda t: t[0])
            worker = getattr(window, "thumb_worker", None)
            if worker is not None:
                worker.request(to_decode)

    def set_thumb_image(self, frame_index, width, image, letter=""):
        """Receive a thumbnail decoded off the UI thread and place it.

        Ignores deliveries that no longer match a visible label (the user has
        navigated away since the request).
        """
        from PySide6.QtGui import QPixmap

        wanted = getattr(self, "_wanted", None)
        if not wanted:
            return

        label = wanted.get(frame_index)
        if label is None:
            return    # stale - this frame isn't on the strip any more

        pixmap = QPixmap.fromImage(image)
        self._store_pixmap(frame_index, pixmap)
        if letter:
            self._letters[frame_index] = letter

        # Only set it if the label is still showing this frame.
        if label.frame_index == frame_index:
            label.setPixmap(self._fit_to_label(pixmap, label))
            self._apply_letter(label, frame_index)
            self._apply_style(label, frame_index)

    def _on_thumb_clicked(self, frame_index):
        # Jump the main window's cursor to the clicked thumbnail's frame.
        self.main.goto_frame(frame_index)

    def _apply_style(self, label, frame_index):
        """Give a label its border style AND its scene flag, together.

        One method rather than three call sites setting both, because the
        band along the top edge is painted while the border is styled: they
        are two mechanisms describing the same fact, and the way to keep them
        agreeing is to have one place set them.
        """
        style, in_scene = self._style_for(frame_index)
        label.in_scene = in_scene
        label.setStyleSheet(style)

    def _style_for(self, frame_index):
        """(style, in_scene) for a frame: which scene it belongs to.

        The cursor is deliberately not returned here.  It used to be checked
        first and to win, which meant the frame under the cursor was the one
        frame not showing its scene membership - the opposite of useful when
        the question is "have I reached the edge of this cut yet?".  It is
        drawn as a ring inside this border instead, so both show at once.

        The cursor keeps its darker background, which still reads as "you are
        here" underneath the ring.
        """
        window = self.main
        cursor = frame_index == window.current_frame

        in_scene = any(a <= frame_index <= b
                       for a, b in window.selection.ranges)

        if window.scenes.has_marker(frame_index):
            style = _STYLE_MARKER
        elif in_scene:
            style = _STYLE_SELECTED
        else:
            style = _STYLE_NORMAL

        if cursor:
            # Swap only the background, keeping whichever border the frame's
            # scene state earned.
            style = style.replace("background:#081420", "background:#001026")
            style = style.replace("background:#203000", "background:#12240a")
            style = style.replace("background:#06121c", "background:#001026")
        return style, in_scene
