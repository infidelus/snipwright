"""The in-app User Guide viewer (Help -> User Guide).

Shows the bundled HTML guide in a QTextBrowser, with a button to open the same
file in the system browser for anyone who prefers reading it there, and a Find
box (Ctrl+F) so the guide can be searched without leaving the application -
asked for 2026-11-12.
"""

import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QKeySequence,
    QShortcut,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
)

_HELP_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "help")
)
_GUIDE = os.path.join(_HELP_DIR, "user-guide.html")


def guide_path():
    """The user guide for the current interface language.

    A translated guide is a copy of the English one named
    ``user-guide_<code>.html`` (e.g. ``user-guide_de.html``) sitting beside it in
    ``assets/help``.  If there isn't one for the chosen language, the English
    guide is used, so a missing translation never leaves the reader with nothing.
    """
    try:
        from config.loader import ensure_config
        code = ensure_config().get("settings", {}).get("language", "en")
    except Exception:
        code = "en"
    if code and code != "en":
        translated = os.path.join(_HELP_DIR, "user-guide_%s.html" % code)
        if os.path.exists(translated):
            return translated
    return _GUIDE


# The guide's stylesheet is written for the dark theme, which left the help
# window stubbornly dark for anyone using the light one.  Rather than keep two
# copies of every guide in step, the dark palette is swapped for a light one
# when the guide is loaded.  One substitution table, one guide file per
# language.
_LIGHT_PALETTE = (
    ("color: #d6d6d6", "color: #202124"),           # body text
    ("background-color: #1e1e22", "background-color: #ffffff"),
    ("h1 { color: #ffffff", "h1 { color: #101114"),
    ("color: #5aa9ff", "color: #1a5fb4"),           # headings and links
    ("1px solid #34343a", "1px solid #d0d3d8"),     # h2 underline
    ("h3 { color: #cfd3d6", "h3 { color: #33383d"),
    ("background-color: #2a2a30", "background-color: #eef0f3"),
    ("color: #e6c07b", "color: #8a5a00"),           # inline code
    ("1px solid #3a3a42", "1px solid #c8ccd2"),     # table rules
    ("th { background-color: #eef0f3; color: #ffffff",
     "th { background-color: #eef0f3; color: #101114"),
    ("color: #9aa0a6", "color: #5f6368"),           # captions and lead text
    ("background-color: #26262c", "background-color: #eef3fb"),
    # The note border uses the same accent as headings and links, so it is
    # already handled by the "color: #5aa9ff" rule above - except that this one
    # is a border rather than a colour property, so it needs its own entry.
    ("3px solid #5aa9ff", "3px solid #1a5fb4"),
)


def _is_dark(widget):
    """Whether the application is currently showing a dark palette.

    Asked of the widget rather than the config, so it follows the desktop when
    the theme is set to System.
    """
    colour = widget.palette().color(widget.backgroundRole())
    # Perceived brightness; the midpoint is a good enough divider here.
    return (colour.red() * 299 + colour.green() * 587
            + colour.blue() * 114) / 1000 < 128


def _guide_html(path, dark):
    """The guide's HTML, recoloured for the light theme when needed."""
    with open(path, encoding="utf-8") as f:
        html = f.read()
    if dark:
        return html
    for old, new in _LIGHT_PALETTE:
        html = html.replace(old, new)
    return html


class UserGuideDialog(QDialog):
    """A simple HTML viewer for the bundled user guide."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Snipwright User Guide"))
        self.resize(900, 720)

        layout = QVBoxLayout(self)

        self._guide = guide_path()
        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)     # http links open in the browser
        dark = _is_dark(self)
        self._browser.setStyleSheet(
            "QTextBrowser { background-color: %s; }"
            % ("#1e1e22" if dark else "#ffffff")
        )
        if os.path.exists(self._guide):
            # setHtml rather than setSource, so the light palette can be
            # substituted first.  The base URL keeps the guide's images and
            # internal anchors working exactly as before.
            self._browser.setSearchPaths([os.path.dirname(self._guide)])
            self._browser.document().setBaseUrl(
                QUrl.fromLocalFile(os.path.dirname(self._guide) + os.sep)
            )
            try:
                self._browser.setHtml(_guide_html(self._guide, dark))
            except OSError:
                self._browser.setSource(QUrl.fromLocalFile(self._guide))
        else:
            self._browser.setHtml(
                "<h2>%s</h2><p>%s</p>" % (
                    self.tr("User guide not found"),
                    self.tr("The guide file appears to be missing from this "
                            "installation."),
                )
            )
        layout.addWidget(self._browser)

        row = QHBoxLayout()
        # Find: always on show rather than a bar that appears, so it can be
        # seen to exist; Ctrl+F goes to it.  Every match is highlighted, the
        # current one selected, and the count says how many there are.
        self._find = QLineEdit()
        self._find.setPlaceholderText(self.tr("Find in the guide (Ctrl+F)"))
        self._find.setClearButtonEnabled(True)
        self._find.setMinimumWidth(240)
        self._find.textChanged.connect(self._search)
        self._find.installEventFilter(self)
        self._prev_btn = QToolButton()
        self._prev_btn.setArrowType(Qt.UpArrow)
        self._prev_btn.setToolTip(self.tr("Previous match (Shift+F3)"))
        self._prev_btn.clicked.connect(self._find_previous)
        self._next_btn = QToolButton()
        self._next_btn.setArrowType(Qt.DownArrow)
        self._next_btn.setToolTip(self.tr("Next match (F3)"))
        self._next_btn.clicked.connect(self._find_next)
        self._count = QLabel()
        self._count.setMinimumWidth(90)
        row.addWidget(self._find)
        row.addWidget(self._prev_btn)
        row.addWidget(self._next_btn)
        row.addWidget(self._count)
        self._matches = []           # QTextCursor for each match
        self._current = -1
        for keys, slot in ((QKeySequence.Find, self._focus_find),
                           (QKeySequence("F3"), self._find_next),
                           (QKeySequence("Shift+F3"), self._find_previous)):
            QShortcut(keys, self, slot)
        self._enable_nav()

        open_btn = QPushButton(self.tr("Open in Browser"))
        open_btn.setAutoDefault(False)
        open_btn.clicked.connect(self._open_in_browser)
        row.addWidget(open_btn)
        row.addStretch(1)
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        row.addWidget(close_btn)
        layout.addLayout(row)

    # -- Find ------------------------------------------------------------------
    def _focus_find(self):
        self._find.setFocus()
        self._find.selectAll()

    def eventFilter(self, obj, event):
        # Esc in the Find box clears the search first; only an Esc with
        # nothing to clear closes the guide, as it always has.
        if (obj is self._find and event.type() == event.Type.KeyPress
                and event.key() == Qt.Key_Escape and self._find.text()):
            self._find.clear()
            return True
        # Enter is taken here rather than through returnPressed: a line edit
        # passes Enter on to the dialog after emitting that, which pressed
        # Open in Browser as the default button.
        if (obj is self._find and event.type() == event.Type.KeyPress
                and event.key() in (Qt.Key_Return, Qt.Key_Enter)):
            if event.modifiers() & Qt.ShiftModifier:
                self._find_previous()
            else:
                self._find_next()
            return True
        return super().eventFilter(obj, event)

    def _search(self, text):
        """Find every match of `text` (any case) and highlight them all."""
        self._matches = []
        self._current = -1
        doc = self._browser.document()
        if text:
            cursor = QTextCursor(doc)
            while True:
                cursor = doc.find(text, cursor)
                if cursor.isNull():
                    break
                self._matches.append(QTextCursor(cursor))
        if self._matches:
            # Start from the first match at or after what is on screen, so a
            # search does not throw the reader back to the top of the guide.
            top = self._browser.cursorForPosition(
                self._browser.viewport().rect().topLeft()).position()
            self._current = next(
                (i for i, c in enumerate(self._matches)
                 if c.selectionStart() >= top), 0)
        self._show_current()

    def _find_next(self):
        if self._matches:
            self._current = (self._current + 1) % len(self._matches)
            self._show_current()

    def _find_previous(self):
        if self._matches:
            self._current = (self._current - 1) % len(self._matches)
            self._show_current()

    def _show_current(self):
        dark = _is_dark(self)
        every = QTextCharFormat()
        every.setBackground(QColor("#6b5a00" if dark else "#fff3a0"))
        this = QTextCharFormat()
        this.setBackground(QColor("#d08a00" if dark else "#ffb000"))
        this.setForeground(QColor("#000000"))
        selections = []
        for i, cursor in enumerate(self._matches):
            sel = QTextEdit.ExtraSelection()
            sel.cursor = cursor
            sel.format = this if i == self._current else every
            selections.append(sel)
        self._browser.setExtraSelections(selections)
        if self._current >= 0:
            shown = QTextCursor(self._matches[self._current])
            shown.clearSelection()
            self._browser.setTextCursor(shown)
            self._browser.ensureCursorVisible()
            self._count.setText(self.tr("%(n)d of %(total)d") % {
                "n": self._current + 1, "total": len(self._matches)})
        else:
            self._count.setText(self.tr("No matches")
                                if self._find.text() else "")
        self._enable_nav()

    def _enable_nav(self):
        many = len(self._matches) > 1
        self._prev_btn.setEnabled(many)
        self._next_btn.setEnabled(many)

    def _open_in_browser(self):
        if os.path.exists(self._guide):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._guide))
