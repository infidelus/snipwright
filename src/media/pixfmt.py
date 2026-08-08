"""Choosing an output pixel format that keeps what the source had.

Every re-encode path used to pass `-pix_fmt yuv420p`, which is 8-bit.  For the
broadcast recordings Snipwright was built around that is exactly right - they
are 8-bit already, and naming it explicitly avoids ffmpeg picking something a
player might not handle.

It is wrong for anything 10-bit.  A 10-bit source re-encoded through Snipwright
came out 8-bit with no warning: banding in skies and gradients, and no way to
get the detail back.  Nobody asked for that, and nothing said it had happened.

So: keep the source's bit depth, and keep the chroma subsampling at 4:2:0 unless
the source has more.
"""

import logging
import subprocess

logger = logging.getLogger("snipwright")

# Output formats we are prepared to ask for, by (bit depth, chroma).  Anything
# not listed falls back to 8-bit 4:2:0, which every encoder and player handles.
_TARGETS = {
    (8, "420"): "yuv420p",
    (10, "420"): "yuv420p10le",
    (12, "420"): "yuv420p12le",
    (8, "422"): "yuv422p",
    (10, "422"): "yuv422p10le",
    (8, "444"): "yuv444p",
    (10, "444"): "yuv444p10le",
}

DEFAULT = "yuv420p"


def source_pix_fmt(path):
    """The first video stream's pixel format, or "" if it can't be read."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=pix_fmt",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True,
        ).stdout.strip()
    except OSError:
        return ""
    return out.splitlines()[0].strip() if out else ""


def describe(pix_fmt):
    """(bit depth, chroma) for a pixel format name, e.g. ("10", "420")."""
    name = (pix_fmt or "").lower()
    if not name.startswith("yuv"):
        return None
    chroma = None
    for c in ("420", "422", "444", "411", "410"):
        if c in name:
            chroma = c
            break
    if chroma is None:
        return None
    depth = 8
    for d in (16, 14, 12, 10, 9):
        if "p%d" % d in name:
            depth = d
            break
    return depth, chroma


def for_output(source_path, codec=""):
    """The pixel format to encode with, preserving the source's bit depth.

    `codec` is the encoder that will be used - it matters because 10-bit H.264
    means the High 10 profile, which a good many hardware players refuse even
    though software players handle it happily.  We still preserve the depth
    rather than quietly discarding it, but say so, because "my file won't play
    on the telly" is a support question worth pre-empting.
    """
    src = source_pix_fmt(source_path)
    parsed = describe(src)
    if not parsed:
        return DEFAULT

    depth, chroma = parsed
    if depth <= 8:
        return DEFAULT

    # 4:2:0 unless the source genuinely carries more; broadcast and Blu-ray are
    # 4:2:0, and upsampling chroma gains nothing but size.
    if chroma not in ("420", "422", "444"):
        chroma = "420"

    target = _TARGETS.get((depth, chroma))
    if target is None:
        # An unusual depth: step down to the nearest we are sure of.
        target = _TARGETS.get((10, chroma)) or DEFAULT

    if "264" in (codec or "").lower():
        logger.info(
            "Keeping the source's %d-bit video (%s -> %s). Note that 10-bit "
            "H.264 is the High 10 profile, which some hardware players won't "
            "decode; HEVC is the safer choice for 10-bit.",
            depth, src, target,
        )
    else:
        logger.info("Keeping the source's %d-bit video (%s -> %s).",
                    depth, src, target)
    return target
