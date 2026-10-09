"""The extension an output file should carry, given its source's.

"Match Source" keeps the source's own extension, which is right for a .ts, a
.mkv or a .mp4.  It is wrong for a recording with an extension FFmpeg cannot
write to.  Tvheadend, for one, sometimes names a recording .bin - when the
channel was not yet broadcasting as the recording began, so it could not tell
what kind of stream it was about to save.  The contents are an ordinary MPEG
transport stream, and FFmpeg reads them happily because it looks at the data,
but when it writes it goes by the extension, and it has no idea what a .bin is:

    Unable to choose an output format for 'x.bin'

so every save failed.  Anything outside the list below is therefore written
as .ts, which is what an unrecognised broadcast recording almost always is,
and what every intermediate in the exporter uses anyway.
"""

import os

# Extensions FFmpeg can pick a muxer for, and that Snipwright writes.
WRITABLE_EXTS = {
    ".ts", ".m2ts", ".mts", ".mkv", ".mp4", ".m4v", ".mov", ".avi",
    ".mpg", ".mpeg", ".vob", ".wmv",
}


def writable_extension(ext):
    """`ext` (with its dot) if FFmpeg can write to it, otherwise ".ts".

    The case is kept, so a ".TS" source still gives ".TS".
    """
    if ext and ext.lower() in WRITABLE_EXTS:
        return ext
    return ".ts"


def output_extension(path):
    """The writable extension for a file made from `path`."""
    return writable_extension(os.path.splitext(path or "")[1])
