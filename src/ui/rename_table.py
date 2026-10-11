"""Column and window sizing shared by the TV and Film Renamers.

Both dialogs show "Current name | New name | Status", and the new name is
the one the user opens the window to read: it carries the folder path the
file is moving into, so it is nearly always the longer of the two.  The
columns used to split the width evenly, which left the new name cut short
while the current name had room to spare, and the user stretched the window
every time to see what a rename would do.

So the current name gets what its longest entry needs plus a little, the
new name takes everything else, and the window remembers the size the user
gives it.
"""

from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QApplication, QHeaderView

from config.loader import save_config

# Breathing room after the longest current name, so it does not sit hard
# against the column line.
_SLACK = 24

# The most of the shared width the current name may take, so a very long
# original filename cannot squeeze the new name out of sight.  The new name
# is the column the window exists to show.
_CURRENT_MAX_SHARE = 0.45

# Width the window opens at the first time, before the user has sized it.
# 1,240 was tried first and left a typical TV rename with far too much
# empty space; the user's size is remembered after that, so this only has
# to be a sensible start.
DEFAULT_WIDTH = 1100


class _RefitOnResize(QObject):
    def __init__(self, table):
        super().__init__(table)
        self._table = table

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            fit_current_column(self._table)
        return False


def setup_columns(table):
    """Current name sized by fit_current_column(), new name stretches."""
    header = table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.Interactive)
    header.setSectionResizeMode(1, QHeaderView.Stretch)
    header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    # On the VIEWPORT, not the table: the table's own resize arrives before
    # its viewport has taken the new width, so the share cap was worked out
    # from the old width and the column never grew back.
    table.viewport().installEventFilter(_RefitOnResize(table))


def fit_current_column(table):
    """Size the current-name column to its content, within its share.

    Called after every table fill and on every resize: the cap depends on
    the table's width, and the content changes with each folder loaded.
    """
    header = table.horizontalHeader()
    # sizeHintForColumn() measures the items as drawn, check box included;
    # the header's own label sets the floor for an empty or short list.
    want = max(table.sizeHintForColumn(0), header.sectionSizeHint(0)) + _SLACK
    shared = table.viewport().width() - header.sectionSize(2)
    if shared > 0:
        want = min(want, int(shared * _CURRENT_MAX_SHARE))
    want = max(want, header.sectionSizeHint(0))
    if header.sectionSize(0) != want:
        header.resizeSection(0, want)


def open_sized(dialog, config, key, default=None):
    """Open at the size the user last left this window, and keep it.

    `default` is the (width, height) for the first opening; without one it
    is DEFAULT_WIDTH by the layout's own height.  Also used by the Batch
    Manager, whose first size is measured from its rows.

    The same idea as the main window, which restores its size from
    config["window"]: the right width depends on the user's own filenames
    and library layout, so rather than guess one, the window starts at
    DEFAULT_WIDTH and from then on remembers whatever the user makes it.
    Stored under config["dialogs"][key] and saved when the window closes,
    by any route - finished is emitted for Close, Escape and the title-bar
    button alike.  Never larger than most of the screen, so a size saved
    on a bigger monitor still opens usable on a smaller one.
    """
    saved = (config.get("dialogs") or {}).get(key) or {}
    if default is None:
        default = (DEFAULT_WIDTH, dialog.sizeHint().height())
    width = int(saved.get("width") or default[0])
    height = int(saved.get("height") or default[1])
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen is not None:
        avail = screen.availableGeometry()
        width = min(width, int(avail.width() * 0.9))
        height = min(height, int(avail.height() * 0.9))
    dialog.resize(max(width, dialog.minimumWidth()),
                  max(height, dialog.minimumHeight()))

    def _remember(_result=None):
        try:
            config.setdefault("dialogs", {})[key] = {
                "width": dialog.width(), "height": dialog.height()}
            save_config(config)
        except Exception:
            pass

    dialog.finished.connect(_remember)
