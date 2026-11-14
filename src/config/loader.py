import json
import shutil

from pathlib import Path

from config.defaults import (
    DEFAULT_CONFIG,
)


APP_DIR_NAME = "snipwright"

# What the settings folder was called before the application was renamed.
# NOTE: this is deliberately the OLD name and must not be updated to match the
# current one - a bulk rename that "helpfully" changes it silently disables the
# migration, since it would then look for the folder already in use.
# Kept so an existing installation's settings, profiles, batch queue and watcher
# state come across on first run rather than the user finding an empty
# application.
LEGACY_DIR_NAMES = ("vrd-next",)

CONFIG_DIR = (

    Path.home()

    /

    ".config"

    /

    APP_DIR_NAME

)

# Set by migrate_legacy_config() when it actually copies something, so the
# editor and the watcher can tell the user rather than moving their settings
# about silently.
MIGRATION_NOTE = None

CONFIG_FILE = (

    CONFIG_DIR

    /

    "config.json"

)


def migrate_legacy_config():
    """Bring settings across from a previous name of the application.

    Copies rather than moves, deliberately.  The old folder is left exactly as
    it was, so anyone who wants to go back to an earlier version still has
    their settings waiting - at the cost of one orphaned directory, which is a
    small price for not being the reason somebody lost their profiles.

    Runs at most once: the presence of the new folder is the flag, so a user who
    deliberately clears their settings does not have the old ones reappear
    behind them.  Returns a short description of what happened, or None.
    """
    global MIGRATION_NOTE

    if CONFIG_DIR.exists():
        return None

    base = CONFIG_DIR.parent
    source = None
    for name in LEGACY_DIR_NAMES:
        candidate = base / name
        if candidate.is_dir():
            source = candidate
            break
    if source is None:
        return None

    copied = 0
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            # Logs are large, disposable and named after the old application;
            # there is nothing to gain by dragging them across.
            if item.suffix == ".log" or item.name.endswith(".log"):
                continue
            target = CONFIG_DIR / item.name
            if target.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
            copied += 1
    except OSError as exc:
        MIGRATION_NOTE = (
            "Couldn't copy your previous settings from %s: %s"
            % (source, exc)
        )
        return MIGRATION_NOTE

    if copied:
        MIGRATION_NOTE = (
            "Your settings have been copied from %s to %s. The old folder has "
            "been left alone." % (source, CONFIG_DIR)
        )
    return MIGRATION_NOTE


CONFIG_PROBLEM_FILE = "config-problem.json"


def _set_aside_unreadable_config(exc):
    """Keep an unreadable config.json, note why, and return fresh defaults."""
    import copy
    import time
    keep = CONFIG_FILE.with_name(
        "config.json.unreadable-%s" % time.strftime("%Y%m%d-%H%M%S"))
    try:
        shutil.copy2(str(CONFIG_FILE), str(keep))
    except OSError:
        keep = None
    detail = str(exc)
    try:
        _atomic_write_json(CONFIG_DIR / CONFIG_PROBLEM_FILE, {
            "kept": str(keep) if keep else "",
            "error": detail,
        })
    except Exception:
        pass
    import logging
    logging.getLogger("snipwright").warning(
        "The settings file %s could not be read (%s); starting with the "
        "default settings. The file was kept as %s.",
        CONFIG_FILE, detail, keep or "(it could not be copied)")
    defaults = copy.deepcopy(DEFAULT_CONFIG)
    if keep is not None:
        # Only once the old file is safely copied: otherwise every start would
        # meet the same broken file and report it again.  Without a copy it is
        # left alone - the defaults then apply for this session only.
        try:
            _atomic_write_json(CONFIG_FILE, defaults)
        except Exception:
            pass
    return defaults


def take_config_problem():
    """The note left by an unreadable settings file, once: {kept, error}
    or None.  Read and removed, so the editor reports it a single time."""
    path = CONFIG_DIR / CONFIG_PROBLEM_FILE
    note = load_sidecar(CONFIG_PROBLEM_FILE, default=None)
    if note is None:
        return None
    try:
        path.unlink()
    except OSError:
        pass
    return note if isinstance(note, dict) else None


def ensure_config():

    migrate_legacy_config()


    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Whether this is an existing installation. Decided BEFORE the defaults
    # are written, because a setting that must differ between a new install
    # and an upgrade (the project format) cannot be told apart afterwards.
    existing_install = CONFIG_FILE.exists()

    if not CONFIG_FILE.exists():

        CONFIG_FILE.write_text(

            json.dumps(

                DEFAULT_CONFIG,

                indent=4,

            )

        )

    try:
        with open(
                CONFIG_FILE,
                encoding="utf-8",
        ) as f:
            config = json.load(
                f
            )
        if not isinstance(config, dict):
            raise ValueError("the file does not hold a settings object")
    except (ValueError, UnicodeDecodeError) as exc:
        # A settings file that will not read - a stray comma after editing
        # the shortcuts by hand is enough.  It used to stop the editor
        # starting at all, with the error only on a terminal nobody sees
        # when it is launched from the menu (code scan, 2026-11-13).  Keep
        # the file as it is, carry on with the defaults, and leave a note the
        # editor shows once its window is up - the Watcher usually starts
        # first, and would otherwise put the defaults in place with nobody
        # told.
        config = _set_aside_unreadable_config(exc)
        # Fresh defaults would also give an existing installation the
        # new-install theme; keep the look it had while its file is sorted.
        if existing_install and isinstance(config.get("settings"), dict):
            config["settings"]["theme"] = "system"

    #
    # Merge in any keys added in newer versions that an older config file on
    # disk won't have (e.g. the settings section).
    #

    changed = False

    # An installation from before the native project format existed keeps
    # writing .vprj until its owner chooses otherwise. Without this, the merge
    # below would hand it the NEW-install default and switch format silently
    # on upgrade. A new install already has "swproj" from the defaults.
    paths = config.get("paths")
    if (existing_install and isinstance(paths, dict)
            and "project_format" not in paths):
        paths["project_format"] = "vprj"
        changed = True

    # The same for the theme.  New installations start in Modern, following
    # the desktop's light or dark preference (since 2.17.0); an installation from before then has no "theme" saved unless
    # its owner opened Settings, and must keep the desktop's own look it has
    # always had rather than change appearance on upgrade.
    settings = config.get("settings")
    if (existing_install and isinstance(settings, dict)
            and "theme" not in settings):
        settings["theme"] = "system"
        changed = True

    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
            changed = True
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if sub_key not in config[key]:
                    config[key][sub_key] = sub_value
                    changed = True

    # One-time migrations, gated on a stored schema version so each runs at
    # most once.  This is what lets a user later choose any of these bindings
    # for themselves (e.g. put Add Selection back on Return, or Mark In on I)
    # without the next load reverting it.  A missing version means "never
    # migrated" (a pre-versioning config); a config built fresh from the
    # defaults already holds the new values, so the moves below find nothing to
    # do.
    CONFIG_VERSION = 2
    version = config.get("config_version", 0)
    sc = config.get("shortcuts")

    if isinstance(sc, dict):
        if version < 1:
            # save_project was split into save_project (Ctrl+P, overwrite) and
            # save_project_as (Ctrl+Shift+P); move older configs off the old
            # combined binding so save_project_as can take Ctrl+Shift+P.
            if sc.get("save_project") == "Ctrl+Shift+P":
                sc["save_project"] = "Ctrl+P"
                changed = True

        if version < 2:
            # Selection shortcuts moved to a VRD-style scheme - Mark In/Out to
            # F3/F4 and Add Selection to Insert (freeing Return).  Only a config
            # still on the previous defaults is moved; a customised binding is
            # left alone.
            for action, (old, new) in (
                ("mark_in", ("I", "F3")),
                ("mark_out", ("O", "F4")),
                ("commit_selection", ("Return", "Insert")),
            ):
                if sc.get(action) == old:
                    sc[action] = new
                    changed = True

    if version < CONFIG_VERSION:
        config["config_version"] = CONFIG_VERSION
        changed = True

    if changed:
        save_config(config)

    return config


def write_text_atomic(path, text):
    """Write `text` to `path` the same safe way as the JSON files: beside it,
    then swapped in, so a reader never meets half a file and a write cut
    short leaves the old one whole."""
    import os
    import tempfile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json_atomic(path, obj, indent=4):
    """Public name for the safe JSON writer below, for files outside the
    config folder.  `indent` keeps each file's existing layout."""
    _atomic_write_json(path, obj, indent=indent)


def _atomic_write_json(path, obj, indent=4):
    """Write ``obj`` as JSON to ``path`` atomically (temp file + rename).

    Shared by the main config and the sidecar cache files so all of them get
    the same protection: a reader always sees either the old file or the
    complete new one, never a truncated half-write.
    """
    import os
    import tempfile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, indent=indent)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_sidecar(name, default=None):
    """Load a sidecar JSON file (e.g. the renamer cache) from the config dir.

    Kept separate from the main config so bulky, disposable data doesn't bloat
    settings.json.  Returns ``default`` if the file is missing or unreadable -
    note ``default`` is returned as given (including ``None``), so a caller can
    pass ``default=None`` to tell "file absent" apart from "file present but
    empty", which matters for one-time migrations.  A corrupt cache should
    never stop the app.
    """
    p = CONFIG_DIR / name
    try:
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        pass
    return default


def save_sidecar(name, obj):
    """Atomically write a sidecar JSON file to the config dir."""
    try:
        _atomic_write_json(CONFIG_DIR / name, obj)
    except Exception:
        pass


def save_config(config):
    _atomic_write_json(CONFIG_FILE, config)