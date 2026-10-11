"""Charms bar page: whether the bar shows, and what its ten buttons do.

Laid out as VideoReDo's own Charms page is - a numbered function list, a
label beside each, blank meaning the function's own name, and Restore
Defaults - so someone who used the bar there finds it where they expect.
See ui/charms.py for the bar itself.
"""

from PySide6.QtCore import QT_TRANSLATE_NOOP, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QHBoxLayout)

from ui import charms
from ui.settings_pages import SettingsPage
from ui.settings_widgets import hint


class _DragHandle(QLabel):
    """The grip at the start of each row: drag it to reorder the slots.

    Asked for in testing: putting ten slots back in order by changing each
    drop-down in turn took six edits for what is one move.  Dragging moves
    the entry live - it follows the pointer and the others shuffle along -
    so there is no drop indicator to aim at and nothing to miss.

    The row being carried is outlined in the highlight colour from the
    moment the grip is pressed until it is let go - without it there was no
    sign anything had been picked up until the pointer reached the next
    row and the entry jumped (reported in testing: no "feeling" of moving).
    """

    def __init__(self, page, index):
        super().__init__("\u2261")              # three bars, in any font
        self._page = page
        self._index = index
        self._dragging = None
        self.setCursor(Qt.OpenHandCursor)
        font = self.font()
        font.setPointSizeF(font.pointSizeF() * 1.4)
        self.setFont(font)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = self._index
            self.setCursor(Qt.ClosedHandCursor)
            self._page._mark_row(self._index)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging is None:
            return super().mouseMoveEvent(event)
        target = self._page._row_at(event.globalPosition().toPoint().y())
        if target is not None and target != self._dragging:
            self._page._move_row(self._dragging, target)
            self._dragging = target
            self._page._mark_row(target)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging is not None:
            self._dragging = None
            self.setCursor(Qt.OpenHandCursor)
            self._page._mark_row(None)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class CharmsPage(SettingsPage):
    TITLE = QT_TRANSLATE_NOOP("Settings", "Charms bar")

    def build(self):
        s = self._settings()

        self._show = QCheckBox(self.tr("Show the Charms bar"))
        self._show.setChecked(bool(s.get("show_charms", False)))
        self.add(self._show)
        self.add(hint(
            self.tr("A column of large buttons down the right-hand edge of the "
                    "window, as in VideoReDo. Each button does the same as its "
                    "menu item. Also on the View menu. Slots set to None are "
                    "left out, so the buttons in use sit together from the top.")
        ))

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.addWidget(QLabel(self.tr("Function")), 0, 2)
        grid.addWidget(QLabel(self.tr("Button label")), 0, 3)

        # (key, label) in display order; "" is None.  Sorted by the name the
        # user reads, so the list is alphabetical in German too.
        self._choices = [("", self.tr("None"))] + sorted(
            ((k, charms.function_label(k)) for k in charms.FUNCTIONS),
            key=lambda kv: kv[1].casefold())

        self._rows = []
        self._handles = []
        for i, (key, label) in enumerate(charms.slots_from_config(self._config)):
            grid.addWidget(QLabel(f"{i + 1}."), i + 1, 0)
            handle = _DragHandle(self, i)
            self._handles.append(handle)
            handle.setToolTip(self.tr("Drag to move this button up or down"))
            grid.addWidget(handle, i + 1, 1)
            combo = QComboBox()
            for k, text in self._choices:
                # The same icon the bar will show, so a slot can be picked
                # by its picture as well as its name.
                combo.addItem(charms.icon_for(k), text)
            edit = QLineEdit()
            edit.setMaxLength(40)
            combo.currentIndexChanged.connect(
                lambda _i, c=combo, e=edit: self._update_placeholder(c, e))
            grid.addWidget(combo, i + 1, 2)
            grid.addWidget(edit, i + 1, 3)
            self._rows.append((combo, edit))
            self._set_row(combo, edit, key, label)
        grid.setColumnStretch(3, 1)
        self.add_layout(grid)

        self.add(hint(self.tr("Leave a label blank to use the function's own name.")))

        row = QHBoxLayout()
        restore = QPushButton(self.tr("Restore Defaults"))
        restore.clicked.connect(self._restore_defaults)
        row.addWidget(restore)
        row.addStretch(1)
        self.add_layout(row)

    # -- reordering by drag ------------------------------------------------

    def _row_values(self):
        return [(self._choices[c.currentIndex()][0], e.text())
                for c, e in self._rows]

    def _row_at(self, global_y):
        """The slot whose row spans the pointer's height, or None."""
        for i, (combo, _edit) in enumerate(self._rows):
            top = combo.mapToGlobal(combo.rect().topLeft()).y()
            if top - 3 <= global_y <= top + combo.height() + 3:
                return i
        return None

    def _mark_row(self, index):
        """Outline the row being dragged, or clear the outline (None)."""
        for i, (handle, (combo, edit)) in enumerate(zip(self._handles, self._rows)):
            on = i == index
            handle.setStyleSheet(
                "QLabel { background: palette(highlight); "
                "color: palette(highlighted-text); border-radius: 3px; }"
                if on else "")
            frame = "border: 2px solid palette(highlight); border-radius: 3px;" if on else ""
            combo.setStyleSheet(f"QComboBox {{ {frame} }}" if on else "")
            edit.setStyleSheet(f"QLineEdit {{ {frame} }}" if on else "")

    def _move_row(self, src, dst):
        """Move slot src to dst, the slots between shuffling along by one.

        The rows stay where they are; their contents move.  So the numbers
        down the side keep counting 1 to 10, and what the user sees is the
        dragged entry travelling with the pointer.
        """
        values = self._row_values()
        values.insert(dst, values.pop(src))
        for (combo, edit), (key, label) in zip(self._rows, values):
            self._set_row(combo, edit, key, label)

    def _set_row(self, combo, edit, key, label):
        idx = next((n for n, (k, _t) in enumerate(self._choices) if k == key), 0)
        combo.setCurrentIndex(idx)
        edit.setText(label)
        self._update_placeholder(combo, edit)

    def _update_placeholder(self, combo, edit):
        key = self._choices[combo.currentIndex()][0]
        edit.setPlaceholderText(charms.default_label(key, self._config))
        edit.setEnabled(bool(key))

    def _restore_defaults(self):
        """The slots only - whether the bar is shown is left as it is."""
        for (combo, edit), item in zip(self._rows, charms.default_charms()):
            self._set_row(combo, edit, item["function"], item["label"])

    def save(self, config):
        settings = config.setdefault("settings", {})
        settings["show_charms"] = self._show.isChecked()
        settings["charms"] = [
            {"function": self._choices[combo.currentIndex()][0],
             "label": edit.text().strip()
             if self._choices[combo.currentIndex()][0] else ""}
            for combo, edit in self._rows
        ]
