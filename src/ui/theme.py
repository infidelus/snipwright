"""Light / dark theming for Snipwright.

By default the editor follows the desktop's own colours (on Linux Mint, whatever
GTK theme is set).  These helpers let the user pin a look from Settings
instead, by switching to Qt's Fusion style with an explicit palette; **System**
restores the desktop's own style and palette exactly.

There are two families:

* **Light** and **Dark** - the classic look: Fusion with a plain palette and
  nothing else, as Snipwright has always looked.
* **Modern Light** and **Modern Dark** - the same Fusion base with a style
  sheet on top: rounded controls, more padding, flat headers, slim scroll bars
  and a single blue accent for the default button, focus and selection.
* **Modern (follow system)** - Modern Light or Modern Dark, whichever matches
  the desktop's own light or dark preference, switching when the desktop
  does.  The default for a new installation.

The timeline, thumbnail and scene bars keep their own dark video-editor colours
in every theme - that's deliberate, and conventional in editors, where a dark
work area is easier on the eyes regardless of the surrounding chrome.
"""

import os

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import (QAbstractSpinBox, QLineEdit, QListView,
                               QStyleFactory)

# Captured once at startup so "System" can restore the desktop's own look
# exactly, rather than an approximation of it.
_original_palette = None
_original_style_name = None

# Every value apply_theme() understands, in the order Settings lists them.
THEME_MODES = ("system", "light", "dark", "modern-system", "modern-light",
               "modern-dark")
_MODERN_MODES = ("modern-system", "modern-light", "modern-dark")

# What apply_theme() last applied, so a desktop switching between light and
# dark can re-apply "modern-system" with the same style wrapper.
_current = {"mode": None, "wrap_style": None}
_watching_scheme = False

# Tooltip styling per theme, kept readable on each background.
_TOOLTIP = {
    "dark": ("QToolTip { color:#f0f0f0; background-color:#2b2b2b;"
             " border:1px solid #555; padding:4px 6px; }"),
    "light": ("QToolTip { color:#202020; background-color:#ffffe1;"
              " border:1px solid #b0b0a0; padding:4px 6px; }"),
}

# The editor's Info box border.  It lives in the application's style sheet
# rather than on the widget, so the Modern themes can restyle it: a widget's
# own sheet would always win over the application's.
CLASSIC_INFO_BOX = "#infoBox { border: 1px solid #555555; }"

# The arrows drawn in Modern combo and spin boxes.  A style sheet that styles
# those boxes replaces Fusion's own arrows, so they must be supplied.
_ARROW_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "theme")
)

# The Modern colours.  "arrow" picks which set of arrow images suits the
# background.
_MODERN = {
    "light": dict(window="#f3f4f6", panel="#ffffff", base="#ffffff", alt="#f7f8fa",
                  border="#dcdfe4", border_hi="#c3c8d0", text="#1d2127",
                  muted="#646b76", accent="#2f6bd8", accent_hi="#2559b8",
                  accent_soft="#e3ecfb", hover="#eef0f3", disabled="#a3a8b0",
                  tip_bg="#1d2127", tip_fg="#f3f4f6", bright="#c42b1c",
                  arrow="light"),
    "dark": dict(window="#1d1f23", panel="#25282d", base="#181a1d", alt="#202327",
                 border="#33373e", border_hi="#454a53", text="#e4e6e9",
                 muted="#9aa0a9", accent="#4a8cf7", accent_hi="#6aa1f8",
                 accent_soft="#24344f", hover="#2d3036", disabled="#5f646c",
                 tip_bg="#e4e6e9", tip_fg="#1d1f23", bright="#ff6b5e",
                 arrow="dark"),
}


def remember_original(app):
    """Record the application's starting style and palette, once.

    Called before any theme is applied, so a later switch back to "System" can
    reinstate the desktop's own appearance rather than a guess at it.
    """
    global _original_palette, _original_style_name
    if _original_palette is None:
        _original_palette = QPalette(app.palette())
        _original_style_name = app.style().name()


def _dark_palette():
    p = QPalette()
    window = QColor(53, 53, 53)
    base = QColor(35, 35, 35)
    text = QColor(220, 220, 220)
    disabled = QColor(127, 127, 127)
    p.setColor(QPalette.Window, window)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, window)
    p.setColor(QPalette.ToolTipBase, QColor(43, 43, 43))
    p.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, window)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.BrightText, QColor(255, 80, 80))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    p.setColor(QPalette.Link, QColor(90, 160, 240))
    p.setColor(QPalette.PlaceholderText, QColor(150, 150, 150))
    for role in (QPalette.Text, QPalette.ButtonText, QPalette.WindowText):
        p.setColor(QPalette.Disabled, role, disabled)
    return p


def _light_palette():
    p = QPalette()
    window = QColor(240, 240, 240)
    base = QColor(255, 255, 255)
    text = QColor(30, 30, 30)
    disabled = QColor(160, 160, 160)
    p.setColor(QPalette.Window, window)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    p.setColor(QPalette.ToolTipBase, QColor(255, 255, 225))
    p.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, window)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.BrightText, QColor(200, 0, 0))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    p.setColor(QPalette.Link, QColor(30, 90, 200))
    p.setColor(QPalette.PlaceholderText, QColor(130, 130, 130))
    for role in (QPalette.Text, QPalette.ButtonText, QPalette.WindowText):
        p.setColor(QPalette.Disabled, role, disabled)
    return p


def _modern_palette(t):
    """The Modern palette.  Widgets that draw themselves from the palette (the
    transport time boxes, the Charms bar, the icons) follow it without knowing
    about the style sheet; Mid and Midlight are set too, as Fusion draws its
    frame lines from them."""
    p = QPalette()
    for role, key in ((QPalette.Window, "window"), (QPalette.WindowText, "text"),
                      (QPalette.Base, "base"), (QPalette.AlternateBase, "alt"),
                      (QPalette.Text, "text"), (QPalette.Button, "panel"),
                      (QPalette.ButtonText, "text"), (QPalette.Highlight, "accent"),
                      (QPalette.ToolTipBase, "tip_bg"),
                      (QPalette.ToolTipText, "tip_fg"),
                      (QPalette.PlaceholderText, "muted"), (QPalette.Link, "accent"),
                      (QPalette.BrightText, "bright"),
                      (QPalette.Mid, "border"), (QPalette.Midlight, "border"),
                      (QPalette.Dark, "border_hi"), (QPalette.Light, "panel")):
        p.setColor(role, QColor(t[key]))
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    for role in (QPalette.Text, QPalette.ButtonText, QPalette.WindowText):
        p.setColor(QPalette.Disabled, role, QColor(t["disabled"]))
    return p


def _arrow_url(name):
    # Forward slashes and quotes, so a Windows path or one with a space in it
    # still reads as a single URL in the style sheet.
    path = os.path.join(_ARROW_DIR, name + ".svg").replace("\\", "/")
    return 'url("%s")' % path


def _modern_sheet(t):
    """The Modern style sheet, filled in from one set of colours."""
    down = _arrow_url("down-" + t["arrow"])
    up = _arrow_url("up-" + t["arrow"])
    c = dict(t, down=down, up=up)
    return """
QWidget {{ outline: 0; }}
QToolTip {{ color:{tip_fg}; background:{tip_bg}; border:none; border-radius:6px;
            padding:5px 8px; }}

QMenuBar {{ background:{window}; border-bottom:1px solid {border}; padding:2px 4px; }}
QMenuBar::item {{ padding:5px 10px; border-radius:6px; background:transparent; }}
QMenuBar::item:selected {{ background:{hover}; }}
QMenu {{ background:{panel}; border:1px solid {border}; border-radius:8px; padding:5px; }}
QMenu::item {{ padding:6px 22px 6px 12px; border-radius:5px; }}
QMenu::item:selected {{ background:{accent_soft}; color:{text}; }}
QMenu::item:disabled {{ color:{disabled}; }}
QMenu::separator {{ height:1px; background:{border}; margin:5px 8px; }}

QToolBar {{ background:{window}; border:none; spacing:4px; padding:4px 6px; }}
QToolBar::separator {{ width:1px; background:{border}; margin:6px 6px; }}
QToolButton {{ border:1px solid transparent; border-radius:6px; padding:4px;
               background:transparent; }}
QToolButton:hover {{ background:{hover}; border-color:{border}; }}
QToolButton:pressed, QToolButton:checked {{ background:{accent_soft};
                                            border-color:{accent}; }}

QStatusBar {{ background:{window}; border-top:1px solid {border}; color:{muted}; }}
QStatusBar::item {{ border:none; }}

QPushButton {{ background:{panel}; border:1px solid {border_hi}; border-radius:6px;
               padding:5px 14px; min-height:18px; }}
QPushButton:hover {{ background:{hover}; }}
QPushButton:pressed {{ background:{accent_soft}; }}
QPushButton:default {{ background:{accent}; color:#ffffff; border-color:{accent}; }}
QPushButton:default:hover {{ background:{accent_hi}; border-color:{accent_hi}; }}
QPushButton:disabled {{ color:{disabled}; border-color:{border}; }}
QPushButton:default:disabled {{ background:{panel}; color:{disabled};
                                border-color:{border}; }}
QPushButton:checked {{ background:{accent_soft}; border-color:{accent}; }}
QPushButton:flat {{ background:transparent; border:none; padding:2px; }}
QPushButton:flat:hover {{ background:{hover}; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTimeEdit, QDateEdit,
QPlainTextEdit, QTextEdit {{
    background:{base}; border:1px solid {border_hi}; border-radius:6px;
    padding:4px 8px; selection-background-color:{accent}; selection-color:#ffffff; }}
/* The 8px left padding (plus the border) is _SPIN_TEXT_LEFT for number boxes. */
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus,
QTimeEdit:focus, QDateEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border:1px solid {accent}; }}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled,
QTimeEdit:disabled, QDateEdit:disabled {{
    color:{disabled}; background:{alt}; border-color:{border}; }}
QLineEdit:read-only {{ background:{alt}; }}
QComboBox {{ padding-right:24px; }}
QComboBox::drop-down {{ border:none; width:22px; subcontrol-origin:padding;
                        subcontrol-position:center right; }}
QComboBox::down-arrow {{ image:{down}; width:10px; height:6px; }}
QComboBox QAbstractItemView {{ background:{panel}; border:1px solid {border};
    border-radius:6px; padding:4px; selection-background-color:{accent_soft};
    selection-color:{text}; }}
QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit {{ padding-right:20px; }}
QSpinBox::up-button, QDoubleSpinBox::up-button, QTimeEdit::up-button,
QDateEdit::up-button {{
    subcontrol-origin:border; subcontrol-position:top right; width:18px;
    border:none; background:transparent; margin:2px 2px 0 0; }}
QSpinBox::down-button, QDoubleSpinBox::down-button, QTimeEdit::down-button,
QDateEdit::down-button {{
    subcontrol-origin:border; subcontrol-position:bottom right; width:18px;
    border:none; background:transparent; margin:0 2px 2px 0; }}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow, QTimeEdit::up-arrow,
QDateEdit::up-arrow {{ image:{up}; width:9px; height:5px; }}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow, QTimeEdit::down-arrow,
QDateEdit::down-arrow {{ image:{down}; width:9px; height:5px; }}

QGroupBox {{ background:{panel}; border:1px solid {border}; border-radius:8px;
             margin-top:22px; padding:12px 10px 10px 10px; }}
QGroupBox::title {{ subcontrol-origin:margin; subcontrol-position:top left; left:4px;
                    top:2px; padding:0 2px; color:{muted}; font-weight:600; }}

QTabWidget::pane {{ border:1px solid {border}; border-radius:8px; background:{panel};
                    top:-1px; }}
QTabBar::tab {{ background:transparent; border:none; border-bottom:2px solid transparent;
                padding:7px 14px; margin-right:2px; color:{muted}; }}
QTabBar::tab:selected {{ color:{text}; border-bottom:2px solid {accent}; }}
QTabBar::tab:hover:!selected {{ color:{text}; }}

QTableView, QTreeView, QListView, QTableWidget, QListWidget, QTreeWidget {{
    background:{base}; alternate-background-color:{alt}; border:1px solid {border};
    border-radius:8px; gridline-color:{border};
    selection-background-color:{accent_soft}; selection-color:{text}; }}
QListWidget::item, QListView::item {{ padding:6px 10px; border-radius:6px;
                                      margin:1px 4px; }}
QListWidget::item:selected, QListView::item:selected {{ background:{accent_soft};
                                                        color:{text}; }}
QListWidget::item:hover:!selected, QListView::item:hover:!selected {{
    background:{hover}; }}
QHeaderView {{ background:transparent; }}
QHeaderView::section {{ background:{alt}; color:{muted}; border:none;
    border-bottom:1px solid {border}; padding:6px 8px; font-weight:600; }}
QTableCornerButton::section {{ background:{alt}; border:none; }}

QScrollBar:vertical {{ background:transparent; width:10px; margin:2px; }}
QScrollBar:horizontal {{ background:transparent; height:10px; margin:2px; }}
QScrollBar::handle {{ background:{border_hi}; border-radius:3px; min-height:30px;
                      min-width:30px; }}
QScrollBar::handle:hover {{ background:{muted}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width:0; height:0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background:transparent; }}

QSlider:horizontal {{ min-height:20px; }}
QSlider::groove:horizontal {{ height:4px; background:{border}; border-radius:2px; }}
QSlider::sub-page:horizontal {{ background:{accent}; border-radius:2px; }}
QSlider::handle:horizontal {{ background:{panel}; border:2px solid {accent};
    width:12px; height:12px; margin:-6px 0; border-radius:8px; }}

QProgressBar {{ background:{alt}; border:1px solid {border}; border-radius:6px;
                text-align:center; min-height:16px; }}
QProgressBar::chunk {{ background:{accent}; border-radius:5px; }}

QSplitter::handle {{ background:{window}; }}
QDialogButtonBox {{ padding-top:6px; }}

QFrame#infoBox {{ background:{panel}; border:1px solid {border}; border-radius:8px; }}
""".format(**c)


# Where a Modern number box's text starts: the sheet's 1px border plus its
# 8px left padding (QSpinBox etc. in _modern_sheet - change both together).
_SPIN_TEXT_LEFT = 9


def _pad_spin_box(box):
    """Keep a number box's text off its left edge, whatever Qt does.

    PySide6 6.11.3 stopped applying the style sheet's padding to the text
    field inside a spin box: it is placed at x=0, so the text sat against the
    border (found comparing grabs of every window under 6.11.2 and 6.11.3,
    2026-11-14).  6.11.2 places it at the padding, x=9.  Measuring where Qt
    put the field and making up only the difference gives the same picture
    under both, and adds nothing where Qt already got it right.
    """
    edit = box.findChild(QLineEdit)
    if edit is None:
        return
    short = max(0, _SPIN_TEXT_LEFT - edit.geometry().x())
    margins = edit.textMargins()
    if margins.left() != short:
        edit.setTextMargins(short, margins.top(), margins.right(),
                            margins.bottom())
        edit.setProperty("_modern_padded", bool(short))


def _unpad_spin_box(box):
    edit = box.findChild(QLineEdit)
    if edit is not None and edit.property("_modern_padded"):
        margins = edit.textMargins()
        edit.setTextMargins(0, margins.top(), margins.right(), margins.bottom())
        edit.setProperty("_modern_padded", False)


class _ListRelayout(QObject):
    """Corrections the Modern style sheet needs once a widget is on screen.

    Lists: a list filled before it is first shown - the Settings page list is
    the one that showed it - works out its rows before the style sheet has
    polished it, so the rows keep their unpadded height while the padding is
    still drawn: the text of each row overlapped the next.  Found on the
    desktop only; offscreen the rows came out right, which is why the
    mock-ups looked fine.  Laying the view out again once it is on screen
    picks up the padded size.

    Number boxes: see _pad_spin_box().

    Only Show events are looked at, and only while a Modern theme is in use.
    """

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show:
            if isinstance(obj, QListView):
                QTimer.singleShot(0, obj, obj.doItemsLayout)
            elif isinstance(obj, QAbstractSpinBox):
                QTimer.singleShot(0, obj, lambda b=obj: _pad_spin_box(b))
        return False


_list_relayout = None


def _relayout_lists(app, modern):
    """Install or remove the list re-layout filter, and re-lay out the lists
    already open so a live switch takes effect at once in both directions."""
    global _list_relayout
    if modern and _list_relayout is None:
        _list_relayout = _ListRelayout()
        app.installEventFilter(_list_relayout)
    elif not modern and _list_relayout is not None:
        app.removeEventFilter(_list_relayout)
        _list_relayout = None
    for w in app.allWidgets():
        if isinstance(w, QListView) and w.isVisible():
            QTimer.singleShot(0, w, w.doItemsLayout)
        elif isinstance(w, QAbstractSpinBox):
            if not modern:
                _unpad_spin_box(w)
            elif w.isVisible():
                QTimer.singleShot(0, w, lambda b=w: _pad_spin_box(b))


def _desktop_is_dark(app):
    """Whether the desktop prefers a dark look.

    Qt's own reading of the desktop's colour scheme first (on Linux Mint it
    follows the Cinnamon theme - Mint-Y-Dark reads Dark); when Qt cannot
    tell, the desktop's original window colour decides.
    """
    from PySide6.QtCore import Qt
    try:
        scheme = app.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return True
        if scheme == Qt.ColorScheme.Light:
            return False
    except AttributeError:
        pass
    palette = _original_palette or app.palette()
    return palette.color(QPalette.Window).lightness() < 128


def _on_scheme_changed(*_args):
    """The desktop switched between light and dark: follow it, if asked to."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None or _current["mode"] != "modern-system":
        return
    apply_theme(app, "modern-system", wrap_style=_current["wrap_style"])
    # Icons were drawn in the old colours; redraw them as a live switch from
    # Settings does.
    try:
        from utils.icons import clear_cache
        clear_cache()
    except Exception:
        pass
    for widget in app.allWidgets():
        refresh = getattr(widget, "refresh_theme", None)
        if callable(refresh):
            try:
                refresh()
            except Exception:
                pass


def _watch_scheme(app):
    global _watching_scheme
    if _watching_scheme:
        return
    try:
        app.styleHints().colorSchemeChanged.connect(_on_scheme_changed)
        _watching_scheme = True
    except AttributeError:
        pass


def apply_theme(app, mode, wrap_style=None):
    """Apply ``mode`` (one of ``THEME_MODES``) to the running application.

    ``wrap_style`` optionally wraps the chosen QStyle before it's installed -
    Snipwright passes its slow-tooltip proxy so the hover delay is preserved.
    ``remember_original`` is called first, so "system" always has the desktop's
    original look to restore.
    """
    remember_original(app)

    if mode == "dark":
        style_name, palette = "Fusion", _dark_palette()
        sheet = _TOOLTIP["dark"] + "\n" + CLASSIC_INFO_BOX
    elif mode == "light":
        style_name, palette = "Fusion", _light_palette()
        sheet = _TOOLTIP["light"] + "\n" + CLASSIC_INFO_BOX
    elif mode in _MODERN_MODES:
        if mode == "modern-system":
            colours = _MODERN["dark" if _desktop_is_dark(app) else "light"]
            _watch_scheme(app)
        else:
            colours = _MODERN[mode.split("-", 1)[1]]
        style_name, palette = "Fusion", _modern_palette(colours)
        sheet = _modern_sheet(colours)
    else:                                       # "system" (or anything unknown)
        style_name = _original_style_name
        palette = _original_palette
        sheet = _TOOLTIP["dark"] + "\n" + CLASSIC_INFO_BOX

    base = QStyleFactory.create(style_name) if style_name else None
    if base is not None:
        app.setStyle(wrap_style(base) if wrap_style is not None else base)
    if palette is not None:
        app.setPalette(palette)
    app.setStyleSheet(sheet)
    _relayout_lists(app, mode in _MODERN_MODES)
    _current["mode"] = mode
    _current["wrap_style"] = wrap_style
