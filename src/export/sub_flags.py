"""Keep subtitle tracks' default/forced flags exactly as the input has them.

The ffmpeg command-line tool, when an output has two or more tracks of one
kind and none of them is marked default, marks the FIRST one default by
itself - unless any -disposition is given on the command line, which turns
that guessing off.  In Matroska a default subtitle track is shown by the
player, so a Blu-ray rip with three subtitle tracks, all off, came out of an
HEVC re-encode with the first one switched on.  A rip with one subtitle
track was untouched, which is why one season of a series was affected and
the season before it was not (found 2026-10-14 on Stargate Universe; checked
with plain ffmpeg 6.1: three tracks -> first default, one track -> none).

subtitle_flags(path) states every subtitle track's flags explicitly, copied
from the input, so nothing is guessed and a FORCED track - which a disc uses
for foreign-language dialogue - stays forced.  Add its arguments to any
ffmpeg command that copies input 0's subtitles, in order, to an output that
keeps track flags (Matroska).  MPEG-TS has no such flags, so it is left
alone there.
"""

import json
import logging
import subprocess

logger = logging.getLogger(__name__)

# The flags worth carrying for a subtitle track.  "default" is the one that
# matters here; the others are kept so a track means the same thing after.
_FLAGS = ("default", "forced", "hearing_impaired", "visual_impaired",
          "comment", "descriptions")


def subtitle_flags(path, out_path=None):
    """ffmpeg arguments restating each subtitle track's flags from `path`.

    Returns [] when `out_path` is given and is not Matroska, when the input
    has no subtitles, or when it cannot be probed - in which case ffmpeg
    behaves exactly as it did before.
    """
    if out_path is not None and not str(out_path).lower().endswith(
            (".mkv", ".mka", ".mks", ".webm")):
        return []
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "s",
             "-show_entries", "stream=index:stream_disposition=" + ",".join(_FLAGS),
             "-of", "json", path],
            capture_output=True, text=True, timeout=60,
        ).stdout
        streams = json.loads(out or "{}").get("streams", [])
    except (OSError, ValueError, subprocess.SubprocessError):
        logger.debug("Could not read subtitle flags from %s", path,
                     exc_info=True)
        return []
    args = []
    for n, s in enumerate(streams):
        disp = s.get("disposition") or {}
        on = [f for f in _FLAGS if disp.get(f)]
        # "0" clears every flag; ffmpeg joins several with "+".
        args += ["-disposition:s:%d" % n, "+".join(on) if on else "0"]
    return args
