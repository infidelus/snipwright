"""The Charms bar - VideoReDo's column of big buttons down the right edge.

Requested by a user who missed it from VideoReDo.  It duplicates what the
menus already do, so it is OFF by default and, when off, takes no space at
all: the window looks exactly as it did before the bar existed.  Shown or
hidden from View > Show Charms Bar or Settings > Charms bar, at once, with
no restart.

Ten slots, each a function and an optional label (blank = the function's
own name).  A slot set to None is simply skipped, so the slots in use are
packed together from the top - which is how the number of buttons is
chosen, with no separate count to set.  VideoReDo has six fixed slots and
its bar used about 60% of the window's height, so ten fit comfortably.

Every function is something the menus already reach, and each button calls
the same main-window method as its menu item, so a charm can never behave
differently from the menu it stands in for.
"""

import copy

from PySide6.QtCore import QCoreApplication, QSize, Qt, QT_TRANSLATE_NOOP
from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import QApplication, QToolBar, QToolButton

from utils.icons import load_icon

CONTEXT = "Charms"

SLOTS = 10

# Smaller than a toolbar's usual 32 px icons and a step down from the
# interface font.  The first version was about twice as wide as VideoReDo's
# bar beside it, and padding turned out to be the small part of that:
# removing nearly all of it saved 3 px (92 -> 89), because the width is set
# by the longest single word - "Commercials" is 73 px of text on its own.
# The font is what moves it: 92 -> 76 px, with the icons at 24.
ICON_SIZE = 24
LABEL_SCALE = 0.85

# key: (label, main-window method).  Each function's icon is Snipwright's
# own, src/assets/icons/charms/<key>.svg, drawn by
# dev/scripts/make-charm-icons.py in the transport buttons' style and
# re-tinted to the theme the same way.  The desktop's icon theme was used
# at first; it differed on every desktop, lacked several names on some
# (Mint-Y has no view-list-details), drew different names identically on
# others, and is usually absent on Windows - so the bar looked different
# everywhere.  The user's call: one set of our own, the same on any OS.
FUNCTIONS = {
    "open_video": (QT_TRANSLATE_NOOP("Charms", "Open Video"), "open_video"),
    "save_video": (QT_TRANSLATE_NOOP("Charms", "Save Video"), "export_video"),
    "close_video": (QT_TRANSLATE_NOOP("Charms", "Close Video"), "close_video"),
    "open_project": (QT_TRANSLATE_NOOP("Charms", "Open Project"), "open_project"),
    "save_project": (QT_TRANSLATE_NOOP("Charms", "Save Project"), "save_project"),
    "save_project_as": (QT_TRANSLATE_NOOP("Charms", "Save Project As"),
                        "save_project_as"),
    "queue_to_batch": (QT_TRANSLATE_NOOP("Charms", "Queue to Batch"),
                       "queue_to_batch"),
    "add_to_joiner": (QT_TRANSLATE_NOOP("Charms", "Add to Joiner"),
                      "add_current_to_joiner"),
    "edit_joiner": (QT_TRANSLATE_NOOP("Charms", "Edit Joiner List"),
                    "edit_joiner_list"),
    "create_joiner": (QT_TRANSLATE_NOOP("Charms", "Create Joined Video"),
                      "create_joiner_video"),
    "queue_joiner": (QT_TRANSLATE_NOOP("Charms", "Queue Joiner to Batch"),
                     "queue_joiner_to_batch"),
    "batch_manager": (QT_TRANSLATE_NOOP("Charms", "Batch Manager"),
                      "open_batch_manager"),
    "detect_commercials": (QT_TRANSLATE_NOOP("Charms", "Detect Commercials"),
                           "detect_commercials"),
    "quick_stream_fix": (QT_TRANSLATE_NOOP("Charms", "Quick Stream Fix"),
                         "quick_stream_fix"),
    "program_info": (QT_TRANSLATE_NOOP("Charms", "Programme Info"),
                     "show_program_info"),
    "tv_renamer": (QT_TRANSLATE_NOOP("Charms", "TV Renamer"), "_open_renamer"),
    "film_renamer": (QT_TRANSLATE_NOOP("Charms", "Film Renamer"),
                     "_open_film_renamer"),
    "settings": (QT_TRANSLATE_NOOP("Charms", "Settings"), "open_settings"),
}


def default_charms():
    """The ten slots as stored in config["settings"]["charms"].

    Kept in config/defaults.py, with the reasoning, so a new install, the
    config merge and Restore Defaults all read the same list.
    """
    from config.defaults import DEFAULT_CONFIG
    return copy.deepcopy(DEFAULT_CONFIG["settings"]["charms"])


def function_label(key):
    """The function's own name, in the user's language."""
    entry = FUNCTIONS.get(key)
    return QCoreApplication.translate(CONTEXT, entry[0]) if entry else ""


def slots_from_config(config):
    """Ten (function, label) pairs, whatever the config holds.

    A hand-edited config may have fewer slots, more, or a function this
    version does not know (one from a newer release, say) - each is read as
    far as it makes sense and the rest are empty, rather than refusing the
    whole bar.
    """
    raw = (config.get("settings") or {}).get("charms")
    if not isinstance(raw, list):
        raw = default_charms()
    out = []
    for i in range(SLOTS):
        item = raw[i] if i < len(raw) and isinstance(raw[i], dict) else {}
        key = item.get("function") or ""
        out.append((key if key in FUNCTIONS else "",
                    str(item.get("label") or "")))
    return out


def icon_for(key):
    """The function's own icon, tinted to the current theme."""
    return load_icon("charms/" + key) if key in FUNCTIONS else QIcon()


def _two_lines(text):
    """Break a label at the space nearest its middle, as VideoReDo does.

    "Open Video" becomes "Open / Video", "Create Joined Video" "Create /
    Joined Video", so the bar stays narrow without the text being cut off.
    A single word is left alone.
    """
    words = text.split()
    if len(words) < 2:
        return text
    best, best_gap = 1, None
    for k in range(1, len(words)):
        gap = abs(len(" ".join(words[:k])) - len(" ".join(words[k:])))
        if best_gap is None or gap < best_gap:
            best, best_gap = k, gap
    return " ".join(words[:best]) + "\n" + " ".join(words[best:])


def default_label(key, config):
    """What a slot shows when its label is left blank.

    The function's own name, except for advert detection, which is named
    after the detector it will actually run: "Chalkline", or "Comskip" for
    anyone who chose that instead.  Shorter than "Detect Commercials", whose
    one long word set the width of the whole bar, and more accurate - the
    user's suggestion, with Comskip covered.  Both are names, so they are
    not translated.
    """
    if key == "detect_commercials":
        detector = str((config.get("settings") or {}).get(
            "ad_detector", "chalkline")).lower()
        return "Comskip" if detector == "comskip" else "Chalkline"
    return function_label(key)


def _bar_style(palette):
    """Style sheet for the bar and its buttons, from the current palette.

    Colours are worked out here rather than named as palette roles in the
    sheet: Snipwright's light and dark palettes do not set Midlight or Mid,
    so "palette(midlight)" came out the same grey in both, which in the
    light theme looked like a patch of the dark one.

    The line down the bar's left edge matches the one Fusion draws under
    the menu bar - the window colour darkened by about a tenth, measured
    from a grab of each theme (#f0f0f0 -> #d8d8d8, #353535 -> #2f2f2f) -
    instead of the toolbar's own two-tone bevel, which stood out in dark.
    """
    window = palette.color(QPalette.Window)
    light = window.lightness() > 128
    line = window.darker(111)
    hover = window.darker(112) if light else window.lighter(140)
    pressed = window.darker(125) if light else window.lighter(170)
    return (f"QToolBar {{ border: none; border-left: 1px solid {line.name()}; "
            f"background: {window.name()}; padding: 0px; spacing: 2px; }} "
            "QToolButton { padding: 0px; margin: 0px; border: none; "
            "border-radius: 3px; } "
            f"QToolButton:hover {{ background: {hover.name()}; }} "
            f"QToolButton:pressed {{ background: {pressed.name()}; }}")


# Room either side of the widest line of a label.
_SIDE = 3


class _CharmButton(QToolButton):
    """A tool button only as wide as its label needs.

    QToolButton's own size hint for text under an icon adds about 9 px of
    margin beside the text whatever the style sheet says, which on a column
    this narrow is a sixth of its width.  The label is centred, so a hint
    sized to the text itself loses nothing.
    """

    def sizeHint(self):
        hint = super().sizeHint()
        fm = self.fontMetrics()
        text_w = max((fm.horizontalAdvance(line)
                      for line in self.text().split("\n")), default=0)
        width = max(text_w, self.iconSize().width()) + 2 * _SIDE
        return QSize(min(width, hint.width()), hint.height())

    def minimumSizeHint(self):
        return self.sizeHint()


class CharmsBar(QToolBar):
    """The bar itself.  rebuild() whenever the slots or the language change.

    A toolbar docked to the window's right edge rather than a widget in the
    content layout, as VideoReDo's is.  Inside the layout it paid the
    layout's spacing on one side and the window's margin on the other -
    15 px of a 89 px strip - before its buttons drew anything.  Not
    movable or floatable, and kept out of the window's right-click menu,
    so the View menu and Settings stay the only ways to show or hide it.
    """

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main = main_window
        self.setObjectName("charms_bar")
        self.setMovable(False)
        self.setFloatable(False)
        self.setOrientation(Qt.Vertical)
        self.toggleViewAction().setVisible(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.layout().setContentsMargins(1, 0, 1, 0)
        self.layout().setSpacing(2)
        self.buttons = []

    def rebuild(self, config):
        # Hidden at once: deleteLater() waits for the event loop, and until
        # then the old button still paints, on top of its replacement.
        for b in self.buttons:
            b.hide()
            b.deleteLater()
        self.buttons = []
        self.clear()
        self.setStyleSheet(_bar_style(QApplication.instance().palette()))

        for key, label in slots_from_config(config):
            if not key:
                continue
            method = getattr(self.main, FUNCTIONS[key][1], None)
            if not callable(method):
                continue
            text = label.strip() or default_label(key, config)
            b = _CharmButton(self)
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            b.setIcon(icon_for(key))
            b.charm_key = key
            b.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            font = b.font()
            font.setPointSizeF(font.pointSizeF() * LABEL_SCALE)
            b.setFont(font)
            b.setText(_two_lines(text))
            b.setToolTip(text)
            b.setAutoRaise(True)
            b.setFocusPolicy(Qt.NoFocus)
            # The menu items are connected the same way: triggered with no
            # arguments, so a method with optional parameters is not handed
            # the button's checked flag by mistake.
            b.clicked.connect(lambda _checked=False, m=method: m())
            self.addWidget(b)
            self.buttons.append(b)
        # One width for the whole column, from its widest label: German's
        # "Video / zusammenfügen" is far wider than "Open / Video", and a
        # fixed width cut it off.  Equal widths keep the buttons in a tidy
        # column, as VideoReDo's are.
        if self.buttons:
            width = max(b.sizeHint().width() for b in self.buttons)
            for b in self.buttons:
                b.setFixedWidth(width)

    def refresh_theme(self):
        """Re-tint the icons after a theme switch.

        main._apply_theme() clears the icon cache and calls this on every
        widget that has it, as it does for the transport buttons.
        """
        self.setStyleSheet(_bar_style(QApplication.instance().palette()))
        for b in self.buttons:
            b.setIcon(icon_for(b.charm_key))
