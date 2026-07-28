#!/usr/bin/env python3
"""Entry point for the standalone Snipwright Watcher (tray app).

Run it directly:

    .venv/bin/python src/watcher.py

or let it start on login via Settings → "Start the watcher automatically".

It runs as its own process, separate from the editor, so it can quietly scan
recordings in the background whether or not the editor is open.
"""

import sys
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLockFile

from watch.tray import WatcherTray
from watch.single_instance import watcher_lock_path


def main():
    # Write to a proper per-day log file (its own 'watcher' family) so a
    # background run launched from the Extras menu or autostart - with no
    # terminal attached - still leaves a trace of what it decided to do.  It
    # goes in the watcher's own config folder, alongside watch.json and the
    # processed/ignore lists, so the tray's "Open config folder" reaches it.
    # The watcher is a separate helper app, so its retention comes from its own
    # config (watch.json), not the editor's settings.
    try:
        from utils.applog import configure_logging
        from config.loader import CONFIG_DIR
        from watch.config import WatchConfig
        log_file = configure_logging(
            str(CONFIG_DIR),
            0,                       # prune by count only, not by age
            False,                   # the watcher's decision log isn't verbose
            app_tag="watcher",
            max_files=WatchConfig.load().log_max_files,
        )
        logging.getLogger("snipwright.watch").info(
            "Starting Snipwright Watcher"
        )
        if log_file is not None:
            logging.getLogger("snipwright.watch").info(
                "Logging to %s", log_file
            )
    except Exception:
        # Never let a logging problem stop the watcher starting.
        logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)
    app.setApplicationName("snipwright-watcher")
    app.setApplicationDisplayName("Snipwright Watcher")
    # Group any Watcher windows under its own launcher (snipwright-watcher.desktop)
    # rather than appearing as a stray panel icon.
    app.setDesktopFileName("snipwright-watcher")
    # A tray app must not quit when its (optional) windows close.
    app.setQuitOnLastWindowClosed(False)

    # Match the editor: apply the chosen Light/Dark theme and UI language (both
    # read from the editor's config, where those settings live) before the tray
    # is built.  System theme / English are the defaults.
    try:
        from ui.theme import apply_theme, remember_original
        from ui.i18n import install_language
        from config.loader import ensure_config
        cfg = ensure_config()

        # The watcher can be the first of the two applications to start, so it
        # may be the one that performs the migration.  It has no window to put
        # a message in, so the log is where it says so.
        from config.loader import MIGRATION_NOTE
        if MIGRATION_NOTE:
            logging.getLogger("snipwright.watch").info(MIGRATION_NOTE)
        settings = cfg.get("settings", {})
        remember_original(app)
        apply_theme(app, settings.get("theme", "system"))
        install_language(app, settings.get("language", "en"))
    except Exception:
        pass

    # Single-instance guard: refuse to start a second Watcher - two tray icons
    # and two background scanners would only fight each other.  This covers a
    # duplicate from the editor's Extras menu, autostart, or a terminal alike.
    # The lock is held for the lifetime of this process (kept alive on the
    # stack through app.exec()).
    lock = QLockFile(watcher_lock_path())
    lock.setStaleLockTime(0)
    if not lock.tryLock(100):
        logging.info("Snipwright Watcher is already running; exiting.")
        return

    tray = WatcherTray(app)        # noqa: F841 - keeps the tray alive
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
