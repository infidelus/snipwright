from PySide6.QtCore import (
    Qt,
    QPoint,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QFont,
)
from PySide6.QtWidgets import (
    QWidget,
)


class SceneBar(QWidget):

    def __init__(
            self,
            window,
    ):

        super().__init__()

        self.window = window

        self.scrubbing = False

        self.setFixedHeight(
            18
        )

    def paintEvent(
            self,
            event,
    ):

        from PySide6.QtGui import (
            QPainter,
            QColor,
            QPen,
        )

        painter = QPainter(self)

        w = self.width()
        h = self.height()

        total = max(
            1,
            len(self.window.frames)
        )

        #
        # Base bar (delete area)
        #

        painter.fillRect(
            0,
            0,
            w,
            h,
            # Slightly lighter than the old #702020 so the cut regions read
            # more clearly, while staying well behind the green kept scenes and
            # keeping the white markers legible.
            QColor("#8a2a2a")
        )

        #
        # Selection (keep area)
        #

        selection = getattr(
            self.window,
            "selection",
            None
        )

        if selection is None:
            painter.end()
            return

        mode = getattr(
            self.window,
            "_edit_mode",
            lambda: "scene",
        )()

        for index, (
                start,
                end,
        ) in enumerate(
            selection.ranges
        ):

            x1 = int(
                start
                /
                total
                *
                w
            )

            x2 = int(
                end
                /
                total
                *
                w
            )

            colour = QColor(
                "#2f8f3c"
            )

            # In Scene Mode the list rows are these kept scenes, so the
            # selected row highlights here.  In Cut Mode the rows are the cuts
            # instead, and the highlight is drawn after this loop.
            if (
                    mode != "cut"
                    and
                    self.window.selected_scene
                    ==
                    index
            ):
                colour = QColor(
                    "#d0b000"
                )

            painter.fillRect(
                x1,
                0,
                max(
                    2,
                    x2 - x1
                ),
                h,
                colour
            )

        #
        # Cut Mode: highlight the selected cut - a red section - since that's
        # what the list is showing.
        #

        if mode == "cut" and self.window.selected_scene is not None:

            frames = getattr(self.window, "frames", None)

            if frames:

                cuts = selection.cut_ranges(
                    len(frames) - 1
                )

                if 0 <= self.window.selected_scene < len(cuts):

                    start, end = cuts[
                        self.window.selected_scene
                    ]

                    x1 = int(
                        start
                        /
                        total
                        *
                        w
                    )

                    x2 = int(
                        end
                        /
                        total
                        *
                        w
                    )

                    painter.fillRect(
                        x1,
                        0,
                        max(
                            2,
                            x2 - x1
                        ),
                        h,
                        QColor(
                            "#d0b000"
                        )
                    )

        #
        # Scene markers
        #

        scene_markers = (
            self.window.scenes.markers
        )

        marker_colour = QColor(
            "#00d8ff"
        )

        painter.setPen(
            QPen(
                marker_colour,
                1,
            )
        )

        painter.setBrush(
            marker_colour
        )

        for frame in scene_markers:
            x = int(
                frame
                /
                total
                *
                w
            )

            #
            # Vertical marker line
            #

            painter.drawLine(
                x,
                5,
                x,
                h,
            )

            #
            # Top triangle
            #

            painter.drawPolygon([
                QPoint(x - 4, 0),
                QPoint(x + 4, 0),
                QPoint(x, 5),
            ])

        #
        # Current frame
        #

        current_frame = getattr(
            self.window,
            "current_frame",
            0
        )

        current_x = int(
            current_frame
            /
            total
            *
            w
        )

        painter.setPen(
            QPen(
                QColor("#ffffff"),
                3,
            )
        )

        painter.drawLine(
            current_x,
            0,
            current_x,
            h,
        )

        #
        # Top cursor tab
        #

        painter.fillRect(
            current_x - 2,
            0,
            5,
            6,
            QColor("#ffffff")
        )

        #
        # Active unfinished selection markers
        #
        # Drawn as a dark line inside a light one.  A single pale colour was
        # used here, which disappeared against the yellow of a highlighted
        # scene; a single dark colour would disappear against the dark red of
        # the cut areas instead.  The pair reads on every colour the bar can
        # draw - red, green, yellow, and the white playhead.
        #

        if selection.pending_in is not None:
            self._draw_pending_bracket(
                painter,
                int(selection.pending_in / total * w),
                h,
                arm=5,
            )

        #
        # Pending OUT marker
        #

        if selection.pending_out is not None:
            self._draw_pending_bracket(
                painter,
                int(selection.pending_out / total * w),
                h,
                arm=-5,
            )

        painter.end()

    def _draw_pending_bracket(
            self,
            painter,
            x,
            h,
            arm,
    ):
        """Draw one IN/OUT bracket at `x`.

        `arm` is how far the top and bottom arms reach, and which way: positive
        turns the bracket right (IN), negative turns it left (OUT).
        """
        from PySide6.QtGui import QColor, QPen

        def bracket(colour, width):
            painter.setPen(QPen(QColor(colour), width))

            painter.drawLine(x, 0, x, h)

            painter.drawLine(x, 0, x + arm, 0)

            painter.drawLine(x, h - 1, x + arm, h - 1)

        # Light halo first, dark line over it.
        bracket("#f0f0f0", 3)
        bracket("#101010", 1)

    def seek_from_x(
            self,
            x,
    ):

        if not self.window.frames:
            return

        total = len(
            self.window.frames
        )

        x = max(
            0,
            min(
                self.width(),
                x,
            )
        )

        frame = int(
            (
                    x
                    /
                    self.width()
            )
            *
            total
        )

        frame = max(
            0,
            min(
                total - 1,
                frame,
            )
        )

        self.window.current_frame = frame

        self.window.scrub_to(frame)

    def mousePressEvent(
            self,
            event,
    ):

        if event.button() != Qt.LeftButton:
            return

        # Clicking the timeline means "take me here", which is no longer the
        # highlighted scene - leaving the yellow highlight on a row you have
        # navigated away from is just a distraction.  The IN/OUT markers stay
        # put: they are the edit in progress, not a highlight.
        clear = getattr(self.window, "clear_scene_selection", None)

        if clear is not None:
            clear()

        self.scrubbing = True

        self.seek_from_x(
            event.position().x()
        )

        self.window.setFocus()

    def mouseMoveEvent(
            self,
            event,
    ):

        if not self.scrubbing:
            return

        self.seek_from_x(
            event.position().x()
        )

    def mouseReleaseEvent(
            self,
            event,
    ):

        if event.button() == Qt.LeftButton:
            self.scrubbing = False

            #
            # Lock in the exact frame and refresh thumbnails / scene list.
            #

            self.window.scrub_finish()