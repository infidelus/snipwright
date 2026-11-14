"""One way in to every project format.

Snipwright reads and writes three kinds of project: its own (.swproj), a
VideoReDo project (.vprj) and a plain EDL cut list (.edl). The first two can
name their own recording and so work anywhere a project is used - Save
Project, the Watcher, the batch queue, opening from a file manager. An EDL
cannot, so it stays an Import and Save As choice only, never the default.

Callers go through this module rather than project.vprj or project.swproj
directly, so each place that handles a project changes by a line rather than
learning about every format itself. The format is decided by the file's
extension on the way in, and by the user's setting (or the extension they
chose) on the way out.
"""
import os

from project import swproj, vprj

SWPROJ = swproj.EXTENSION          # ".swproj"
VPRJ = ".vprj"

# Extensions that name a project which can find its own recording.
PROJECT_EXTENSIONS = (SWPROJ, VPRJ)

# The two a user can choose as the default. An upgrade from before this
# setting existed keeps VPRJ; a new installation starts on SWPROJ - see
# config/loader.py, which tells the two apart.
FORMATS = ("swproj", "vprj")


def _ext(path):
    return os.path.splitext(path or "")[1].lower()


def default_extension(config):
    """The extension Save Project writes when nothing else decides it."""
    chosen = str((config or {}).get("paths", {}).get("project_format", "vprj"))
    return SWPROJ if chosen.lower() == "swproj" else VPRJ


def is_queued_join(path):
    """Whether `path` is a Joiner list queued as a batch job (.vjr)."""
    from project.joiner import JOINER_EXT
    return _ext(path) == JOINER_EXT


def read_source_filename(path):
    """The recording a project refers to, without needing a FrameIndex.

    A queued join has several recordings; for it this returns the name its
    output will take ("<first recording> - Joined"), which is what every
    caller - output naming, the "working from" line, the duplicate check -
    actually needs. See project.joiner.queued_name_path().
    """
    if is_queued_join(path):
        from project.joiner import queued_name_path
        return queued_name_path(path)
    if _ext(path) == SWPROJ:
        return swproj.read_source_filename(path)
    return vprj.read_source_filename(path)


def load_project(path, index):
    """Load a .swproj or .vprj onto `index`.

    Both return an object with keep_ranges, markers and source_filename; a
    .swproj's also carries the recording check (source_matches, used_frames)
    and provenance, which callers can use where they exist.
    """
    if _ext(path) == SWPROJ:
        return swproj.load_swproj(path, index)
    return vprj.load_vprj(path, index)


def save_project(path, keep_ranges, markers, source_filename, index, *,
                 made_by="person", made_with=""):
    """Write the edit in whichever format `path`'s extension names.

    `made_by` records who found the cuts - "person" for anything saved from
    the editor, or the detector ("chalkline", "comskip") whose results
    Snipwright is saving. A .vprj has nowhere to put it and ignores it.
    """
    if _ext(path) == SWPROJ:
        return swproj.save_swproj(path, keep_ranges, markers,
                                  source_filename, index,
                                  made_by=made_by, made_with=made_with)
    return vprj.save_vprj(path, keep_ranges, markers, source_filename, index)


def save_project_from_cuts(path, source_filename, cut_ranges_seconds,
                           duration_seconds=0.0, *, made_by="unknown",
                           made_with=""):
    """The Watcher's way in: cut regions in seconds, no FrameIndex.

    Writes whichever format `path`'s extension names. A .swproj records that
    the detector found these cuts and nobody has reviewed them; a .vprj has
    nowhere to say so.
    """
    if _ext(path) == SWPROJ:
        return swproj.save_swproj_from_cuts(
            path, source_filename, cut_ranges_seconds, duration_seconds,
            made_by=made_by, made_with=made_with)
    return vprj.save_vprj_from_cuts(path, source_filename, cut_ranges_seconds,
                                    duration_seconds=duration_seconds)
