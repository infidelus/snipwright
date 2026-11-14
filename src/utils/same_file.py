"""Is this output the very file we are reading from?

Nothing used to ask.  Saving a video under its own recording's name - pick
the recording in the Save dialog, answer Yes to "Overwrite?" - opened the
recording as the output, which empties it, while the cut was still reading
it.  The cut then failed on the empty file, and the failure clean-up deleted
"the half-written output": the recording itself.  Reproduced on a throwaway
copy during the code scan (2026-11-13).

The comparison is of the files, not the strings: a symlink, a second mount
of the same share or a different spelling of the path must not slip past.
"""

import os


def is_same_file(a, b):
    """True if paths `a` and `b` name the same file.

    os.path.samefile when both exist (it compares device and inode, so links
    and differently-spelt paths are caught); otherwise the fully resolved
    paths, compared as the platform compares them.  A path that cannot be
    examined is not the same as anything - this guards a save, and must not
    refuse one on a hiccup.
    """
    if not a or not b:
        return False
    try:
        if os.path.exists(a) and os.path.exists(b):
            return os.path.samefile(a, b)
        return (os.path.normcase(os.path.realpath(a))
                == os.path.normcase(os.path.realpath(b)))
    except (OSError, ValueError):
        return False


def any_same_file(path, others):
    """True if `path` is the same file as any of `others`."""
    return any(is_same_file(path, other) for other in (others or ()))
