import numpy as np
from PySide6.QtCore import Qt, QT_TRANSLATE_NOOP, QCoreApplication

from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QGridLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)

from utils.timecode import (
    frame_to_timecode,
    seconds_to_timecode,
)


def _real_span(index, first, last, total_frames, fps=25.0):
    """How long frames first..last play for, in seconds, from the index's
    real timestamps - the same timing the exporter gives its chapter marks.

    Not (last - first + 1) / fps: a field-coded HD recording does not space
    its frames evenly, and the count drifted a frame from where the join
    really landed in a saved 1080i test (2026-11-12).  A leap in the
    recording's clock - a recorder's own crude edit, say - is not playing
    time and counts as one frame.
    """
    if index is None:
        return (last - first + 1) / fps
    try:
        num, den = index.time_base
        stop = min(last + 2, total_frames)
        pts = np.asarray(index.pts[first:stop], dtype=np.float64)
        steps = np.diff(pts) * num / den
        if len(steps):
            frame = float(np.median(steps)) or 1.0 / fps
        else:
            frame = 1.0 / fps
        steps[steps > 1.0] = frame
        total = float(steps.sum())
        if last + 1 >= total_frames:
            total += frame          # the last frame's own length
        return total
    except Exception:
        return (last - first + 1) / fps


class InfoPanel(QWidget):

    def __init__(
            self,
            window,
    ):

        super().__init__()

        self.window = window

        #
        # Outer column: the "Info" title, then a bordered box holding the
        # figures.  The box fills the panel width - which matches the scene
        # list above it - so the border is the same width as the scene panel
        # and stays that width regardless of how wide the figures get (it used
        # to hug its contents, so it was narrower before a file was loaded).
        #

        outer = QVBoxLayout(
            self
        )

        # No horizontal margin: the box lines up with the scene list, which
        # sits flush in the same column.
        outer.setContentsMargins(
            0,
            6,
            0,
            6,
        )

        outer.setSpacing(
            6
        )

        title = QLabel(
            self.tr("Info")
        )

        title.setStyleSheet(
            "font-weight:bold;"
        )

        outer.addWidget(
            title
        )

        #
        # The bordered box.  1px #555 border to match the app's other panels
        # (transport, scene list).  It fills the width horizontally and is
        # capped to its contents vertically (so it never stretches down the
        # column).
        #
        # The border itself is in the application's style sheet (ui/theme.py,
        # keyed on the object name), not set here: a widget's own sheet always
        # wins over the application's, which stopped the Modern themes giving
        # the box their rounded border.
        #

        box = QFrame()

        box.setObjectName(
            "infoBox"
        )

        box.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum,
        )

        grid = QGridLayout(
            box
        )

        # A little inner padding so the figures aren't flush against the
        # border, plus spacing between the columns.
        grid.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        grid.setHorizontalSpacing(
            28
        )

        grid.setVerticalSpacing(
            6
        )

        # Columns 0 and 4 are empty stretch spacers; the actual content
        # (label / Time / MB in columns 1-3) is therefore centred in the box,
        # sitting a little indented from the border rather than crammed to one
        # side or spread to the edges.
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(4, 1)

        # Pin the Time and MB columns to the width of their widest possible
        # value.  Otherwise the columns shrink to fit short content - so the
        # dashes shown before a file is open ("--:--:--.--", and "0.00") made
        # the whole block narrower and shifted than once real figures appeared.
        # Fixed widths keep the layout identical whether or not a file's open.
        fm = self.fontMetrics()
        grid.setColumnMinimumWidth(
            2,
            fm.horizontalAdvance("00:00:00.00") + 6,
        )
        grid.setColumnMinimumWidth(
            3,
            fm.horizontalAdvance("99999.99") + 6,
        )

        #
        # Column headers
        #

        time_header = QLabel(self.tr("Time"))
        time_header.setAlignment(Qt.AlignCenter)
        grid.addWidget(
            time_header,
            0,
            2,
        )

        mb_header = QLabel(self.tr("MB"))
        mb_header.setAlignment(Qt.AlignCenter)
        grid.addWidget(
            mb_header,
            0,
            3,
        )

        #
        # Rows
        #

        self.rows = {}

        labels = [
            QT_TRANSLATE_NOOP("InfoPanel", "Cursor"),
            QT_TRANSLATE_NOOP("InfoPanel", "Program"),
            QT_TRANSLATE_NOOP("InfoPanel", "Selection"),
            QT_TRANSLATE_NOOP("InfoPanel", "Output"),
            # Where the selected cut's join lands in the saved video -
            # asked for by a user checking his joins in VLC (2026-11-12).
            QT_TRANSLATE_NOOP("InfoPanel", "Splice"),
            QT_TRANSLATE_NOOP("InfoPanel", "Joiner"),
        ]

        for index, name in enumerate(
                labels,
                start=1,
        ):

            label = QLabel(
                QCoreApplication.translate("InfoPanel", name) + ":"
            )

            value = QLabel(
                self.tr("--:--:--.--")
            )

            value.setAlignment(
                Qt.AlignCenter
            )

            mb = QLabel(
                self.tr("0.00")
            )

            mb.setAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )

            grid.addWidget(
                label,
                index,
                1,
            )

            grid.addWidget(
                value,
                index,
                2,
            )

            grid.addWidget(
                mb,
                index,
                3,
            )

            self.rows[name] = {
                "time": value,
                "mb": mb,
            }

            if name == "Splice":
                # No tooltip, like every other row here; the guide explains
                # it.  Never a size: a moment, not a span.
                mb.setText("")

        outer.addWidget(
            box
        )

        # Spare height collects below the box rather than stretching it.
        outer.addStretch(
            1
        )

    def update_info(self):

        window = self.window

        total_frames = (
            len(window.frames)
            if window.frames
            else 0
        )

        file_mb = getattr(
            window,
            "source_size_mb",
            0.0,
        )

        file_bytes = getattr(
            window,
            "source_size_bytes",
            0,
        )

        index = getattr(
            window,
            "index",
            None,
        )

        def mb_for(ranges, frame_count):
            """Size of the given frame ranges, in MB.

            Measured from the index's per-frame byte totals where they exist,
            so a range that runs above or below the file's average bitrate
            reports its real size.  The flat share is only the fallback for an
            index built before those totals were recorded.
            """
            if not total_frames:
                return 0.0

            if index is not None:
                return index.estimated_mb(ranges, file_bytes)

            return file_mb * (frame_count / total_frames)

        #
        # Cursor: position in time, size up to the cursor.
        #

        self.rows["Cursor"]["time"].setText(
            frame_to_timecode(window.current_frame)
        )

        # Everything before the cursor, so the figure reads as "how far into
        # the file am I" - frame 0 is therefore 0.00, not one frame's worth.
        cursor_ranges = (
            [(0, window.current_frame - 1)]
            if window.current_frame > 0
            else []
        )

        self.rows["Cursor"]["mb"].setText(
            f"{mb_for(cursor_ranges, window.current_frame):.2f}"
        )

        #
        # Selection: duration + size of what's currently selected - the marked
        # IN/OUT span, or the row highlighted in the scene list.
        #

        selection_text = "--:--:--.--"
        selection_frames = 0
        selection_ranges = []

        pending_in = window.selection.pending_in
        pending_out = window.selection.pending_out

        if pending_in is not None and pending_out is not None:

            # The markers come first: marking IN/OUT is the primary way of
            # selecting something, and this row used to sit empty through the
            # whole of it, filling in only once a scene had been added and
            # clicked in the list.  VideoReDo shows the marked span here.
            start = min(pending_in, pending_out)
            end = max(pending_in, pending_out)

            selection_frames = end - start + 1
            selection_ranges = [(start, end)]
            selection_text = frame_to_timecode(selection_frames)

        elif window.selected_scene is not None:

            # Falls back to the highlighted row for the case where the markers
            # have been cleared but a scene is still selected.  Read from the
            # scene list rather than the kept ranges, because Cut Mode lists
            # the cuts - row N there is not kept range N.
            scene_list = getattr(window, "scene_list", None)

            ranges = (
                scene_list.displayed_ranges()
                if scene_list is not None
                else window.selection.ranges
            )

            if 0 <= window.selected_scene < len(ranges):
                start, end = ranges[window.selected_scene]
                selection_frames = end - start + 1
                selection_ranges = [(start, end)]
                selection_text = frame_to_timecode(selection_frames)

        self.rows["Selection"]["time"].setText(selection_text)

        self.rows["Selection"]["mb"].setText(
            f"{mb_for(selection_ranges, selection_frames):.2f}"
        )

        #
        # Output: total kept duration + estimated size.
        #

        total_kept = 0
        kept_ranges = list(window.selection.ranges)

        for start, end in kept_ranges:
            total_kept += end - start + 1

        self.rows["Output"]["time"].setText(
            frame_to_timecode(total_kept)
        )

        self.rows["Output"]["mb"].setText(
            f"{mb_for(kept_ranges, total_kept):.2f}"
        )

        #
        # Splice: where the selected row's join lands in the saved video -
        # everything kept before it.  Cut Mode lists cuts, Scene Mode lists
        # the scenes kept; either way the join is at the row's start, and
        # there is one only with kept material both before and after it.
        #

        splice_text = "--:--:--.--"
        if window.selected_scene is not None:
            scene_list = getattr(window, "scene_list", None)
            rows = (scene_list.displayed_ranges()
                    if scene_list is not None else kept_ranges)
            # Clicking a row puts the IN/OUT markers on it, VideoReDo-style,
            # so markers on the row are expected.  Markers somewhere else
            # mean a new edit is being marked, and the row no longer speaks
            # for what is being looked at.
            on_row = (0 <= window.selected_scene < len(rows) and (
                pending_in is None or pending_out is None
                or (min(pending_in, pending_out),
                    max(pending_in, pending_out))
                == tuple(rows[window.selected_scene])))
            if on_row:
                row_start = rows[window.selected_scene][0]
                before = [(start, min(end, row_start - 1))
                          for start, end in kept_ranges if start < row_start]
                after = any(end >= row_start for _s, end in kept_ranges)
                if before and after:
                    seconds = sum(_real_span(index, a, b, total_frames)
                                  for a, b in before)
                    splice_text = seconds_to_timecode(seconds)
        self.rows["Splice"]["time"].setText(splice_text)

        #
        # Program: the whole active video's length + size.
        #

        if total_frames:
            # A duration, like Selection and Output - so a whole file kept
            # reads the same on both rows.  This used to show the last
            # frame's timecode (count - 1), which put Program one frame
            # behind Output for an uncut recording.  Cursor stays a
            # position, so at the last frame it reads one frame lower.
            self.rows["Program"]["time"].setText(
                frame_to_timecode(total_frames)
            )
            self.rows["Program"]["mb"].setText(
                f"{file_mb:.2f}"
            )
        else:
            self.rows["Program"]["time"].setText(self.tr("--:--:--.--"))
            self.rows["Program"]["mb"].setText(self.tr("0.00"))

        #
        # Joiner: combined duration (and rough size) of the joiner list.  Spans
        # whatever's queued for joining, independent of the open video.
        #

        joiner = getattr(window, "joiner_list", None)

        if joiner is not None and len(joiner):
            self.rows["Joiner"]["time"].setText(
                seconds_to_timecode(joiner.total_duration())
            )
            joiner_mb = joiner.total_size_mb()
            self.rows["Joiner"]["mb"].setText(
                f"{joiner_mb:.2f}" if joiner_mb > 0 else "--"
            )
        else:
            self.rows["Joiner"]["time"].setText(self.tr("--:--:--.--"))
            self.rows["Joiner"]["mb"].setText(self.tr("0.00"))
