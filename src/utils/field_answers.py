"""What the detector said, and what the user made of it, per recording.

The Watcher writes a project of the detector's cuts, and the user then
corrects it and saves over it - or sends it to the Batch Manager, whose
staged copy is pruned with the job.  Either way the detector's own answer
was lost, so how far the user had to move it could only be learned by
running detection again.  This keeps both, side by side, in one small JSON
file per recording under the settings folder, for
dev/scripts/field-report.py to compare (2026-10-24).

Nothing here may cost the user anything: every function swallows its own
errors, and the files are pruned after KEEP_DAYS.
"""

import hashlib
import json
import logging
import os
import time

log = logging.getLogger(__name__)

FOLDER = "chalkline-answers"
KEEP_DAYS = 180


def _path_for(source):
    from config.loader import CONFIG_DIR
    folder = os.path.join(str(CONFIG_DIR), FOLDER)
    base = os.path.splitext(os.path.basename(source))[0]
    tag = hashlib.sha1(os.path.abspath(source).encode()).hexdigest()[:8]
    return folder, os.path.join(folder, f"{base} [{tag}].json")


def _cuts(cuts):
    return [[round(float(a), 3), round(float(b), 3)] for a, b in cuts]


def record_detector_answer(source, project_path, cuts, duration, detector,
                           channel=None, made_with=""):
    """Keep the detector's untouched answer for `source`."""
    try:
        folder, path = _path_for(source)
        os.makedirs(folder, exist_ok=True)
        record = {
            "source": os.path.abspath(source),
            "project": os.path.abspath(project_path),
            "detector": detector,
            "channel": channel,
            "made_with": made_with,
            "written": time.time(),
            "duration": duration,
            "cuts": _cuts(cuts),
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=1)
        cutoff = time.time() - KEEP_DAYS * 86400
        for name in os.listdir(folder):
            old = os.path.join(folder, name)
            if name.endswith(".json") and os.path.getmtime(old) < cutoff:
                os.remove(old)
    except Exception:
        log.debug("Could not keep the detector's answer", exc_info=True)


def record_user_answer(source, project_path, via):
    """Add the user's cuts, read from the project just written, to the
    detector's answer for `source` - if there is one.  `via` says how it
    was saved ("save", "export", "batch"); the latest wins."""
    try:
        _folder, path = _path_for(source)
        if not os.path.exists(path):
            return
        from repair.chalkline import parse_vprj
        cuts, _duration = parse_vprj(project_path)
        with open(path, encoding="utf-8") as fh:
            record = json.load(fh)
        record["user"] = {"cuts": _cuts(cuts), "saved": time.time(),
                          "via": via}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=1)
    except Exception:
        log.debug("Could not keep the user's answer", exc_info=True)
