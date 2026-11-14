"""Joiner model - an ordered list of segments to be joined into one video.

Each entry references a saved edit (a .vprj project) or a plain media file;
title cards arrive in a later phase.  The whole list saves and loads as a
.vjr file (our own JSON format - simpler and more robust than the XML the
.vprj uses for VideoReDo compatibility).

This module is the data model and its persistence only.  Building the joined
output is a separate, later phase; nothing here touches ffmpeg or the exporter.
"""

import json
import os


# Bump if the on-disk shape ever changes in an incompatible way.
JOINER_FORMAT = "snipwright-joiner"
JOINER_VERSION = 1

# File extension for a saved joiner list.
JOINER_EXT = ".vjr"


class JoinerEntry:
    """One segment in the joiner list - a single scene from a source recording.

    A joiner entry is one scene (one kept range) from one recording, so scenes
    from different videos - or several scenes from the same video - can be freely
    reordered and interleaved.  The scene is captured in seconds, with its cut
    list (everything except this scene) stored so a .vprj can be regenerated for
    editing or rendering without a saved project.  Title cards arrive later.
    """

    KIND_SCENE = "scene"          # one scene (kept range) from a recording
    KIND_MEDIA = "media"          # a plain media file, used whole
    KIND_TITLE = "title"          # a generated title card (a later phase)

    def __init__(self, kind, source="", description="", start=0.0, end=0.0,
                 cuts=None, total_duration=0.0, fps=25.0,
                 text="", subtitle="", bg_color="#000000",
                 text_color="#FFFFFF", bg_image="", bg_scaling="fill",
                 size_mb=0.0, fade_in=0.0, fade_out=0.0):
        self.kind = kind
        self.source = source               # the underlying recording / media
        self.description = description       # the time-range / label shown
        self.start = float(start)            # scene start, seconds (display)
        self.end = float(end)                # scene end, seconds (display)
        # REMOVED regions [start_sec, end_sec] that keep only this scene; the
        # source of truth for regenerating a .vprj.  Empty means "whole file".
        self.cuts = [list(c) for c in (cuts or [])]
        self.total_duration = float(total_duration)   # source length, seconds
        self.fps = float(fps) or 25.0
        # Rough size of this scene, MB - estimated from the source file size in
        # proportion to the scene's share of it when the entry was added.  Used
        # only for the Info panel's joiner readout; 0.0 means "unknown".
        self.size_mb = float(size_mb)
        # Per-clip fade to/from black, in seconds (0 = none).  fade_in ramps up
        # from black over the first fade_in seconds; fade_out ramps down to
        # black over the last fade_out seconds.  Applied during the re-encode
        # join (which a non-zero fade forces).
        self.fade_in = max(0.0, float(fade_in))
        self.fade_out = max(0.0, float(fade_out))
        # Title-card fields (kind == KIND_TITLE).  A title's length is held in
        # `end` (start stays 0), so `duration` works for it like any entry.
        self.text = text
        self.subtitle = subtitle
        self.bg_color = bg_color or "#000000"
        self.text_color = text_color or "#FFFFFF"
        # Optional background image for a title card.  When set it replaces the
        # solid colour; `bg_scaling` decides how an odd-shaped image maps onto
        # the card's frame ("fill" = cover/crop, "fit" = letterbox, "stretch").
        self.bg_image = bg_image or ""
        self.bg_scaling = bg_scaling or "fill"

    @property
    def is_title(self):
        return self.kind == self.KIND_TITLE

    @property
    def duration(self):
        return max(0.0, self.end - self.start)

    @property
    def display_name(self):
        if self.is_title:
            return "Title card"
        return os.path.basename(self.source) if self.source else "(untitled)"

    @property
    def exists(self):
        if self.is_title:
            return True                       # generated, no file needed
        return bool(self.source) and os.path.exists(self.source)

    def to_dict(self):
        return {
            "kind": self.kind,
            "source": self.source,
            "description": self.description,
            "start": self.start,
            "end": self.end,
            "cuts": self.cuts,
            "total_duration": self.total_duration,
            "fps": self.fps,
            "text": self.text,
            "subtitle": self.subtitle,
            "bg_color": self.bg_color,
            "text_color": self.text_color,
            "bg_image": self.bg_image,
            "bg_scaling": self.bg_scaling,
            "size_mb": self.size_mb,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            kind=data.get("kind", cls.KIND_SCENE),
            source=data.get("source", "") or data.get("path", ""),
            description=data.get("description", ""),
            start=float(data.get("start", 0.0) or 0.0),
            end=float(data.get("end", 0.0) or 0.0),
            cuts=data.get("cuts", []),
            total_duration=float(data.get("total_duration", 0.0) or 0.0),
            fps=float(data.get("fps", 25.0) or 25.0),
            text=data.get("text", ""),
            subtitle=data.get("subtitle", ""),
            bg_color=data.get("bg_color", "#000000"),
            text_color=data.get("text_color", "#FFFFFF"),
            bg_image=data.get("bg_image", ""),
            bg_scaling=data.get("bg_scaling", "fill"),
            size_mb=float(data.get("size_mb", 0.0) or 0.0),
            fade_in=float(data.get("fade_in", 0.0) or 0.0),
            fade_out=float(data.get("fade_out", 0.0) or 0.0),
        )


class JoinerList:
    """Ordered collection of JoinerEntry, with reordering and persistence."""

    def __init__(self):
        self.entries = []
        self.path = None              # the .vjr this list came from / saved to

    # -- list management ---------------------------------------------------

    def __len__(self):
        return len(self.entries)

    def add(self, entry):
        self.entries.append(entry)

    def remove(self, index):
        if 0 <= index < len(self.entries):
            del self.entries[index]

    def move(self, index, delta):
        """Move the entry at `index` by `delta` (-1 up, +1 down).  Returns the
        entry's new index (unchanged if the move wasn't possible)."""
        target = index + delta
        if 0 <= index < len(self.entries) and 0 <= target < len(self.entries):
            self.entries[index], self.entries[target] = (
                self.entries[target], self.entries[index]
            )
            return target
        return index

    def clear(self):
        self.entries = []

    def total_duration(self):
        return sum(e.duration for e in self.entries)

    def total_size_mb(self):
        """Best-effort total size of the joined output, MB.  Entries added
        before sizes were recorded (or loaded from an older list) contribute
        0.0, so this can under-read; it's only an estimate for the Info panel."""
        return sum(getattr(e, "size_mb", 0.0) for e in self.entries)

    # -- persistence -------------------------------------------------------

    def to_dict(self):
        return {
            "format": JOINER_FORMAT,
            "version": JOINER_VERSION,
            "entries": [e.to_dict() for e in self.entries],
        }

    def save(self, path):
        # Swapped in, never written in place - see config/loader.py.
        from config.loader import write_json_atomic
        write_json_atomic(path, self.to_dict(), indent=2)
        self.path = path

    @staticmethod
    def _read_entries(path):
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        return [JoinerEntry.from_dict(d) for d in data.get("entries", [])]

    def load_into(self, path, append=False):
        """Load entries from `path`, either replacing the current list or
        appending to it.  Returns the number of entries loaded."""
        loaded = self._read_entries(path)
        if append:
            self.entries.extend(loaded)
        else:
            self.entries = loaded
            self.path = path
        return len(loaded)

    @classmethod
    def load(cls, path):
        joiner = cls()
        joiner.load_into(path, append=False)
        return joiner


# --------------------------------------------------------------------------- #
# A Joiner list queued as a batch job
# --------------------------------------------------------------------------- #
#
# "Queue to batch" from the Joiner writes the list, as it stands, into the
# batch queue's staging folder - the same file format as Save list, plus a
# "batch" section recording the choice the user made when queueing (whether
# the join must be re-encoded, and to what), so the batch never has to ask.
# The batch runner recognises the job by its extension and hands it to the
# Joiner's own renderer.

def joined_stem(entries):
    """The name a joined video is given: the first scene's recording name
    with " - Joined", as Create Video suggests; "Joined Video" if the list
    holds only title cards."""
    for entry in entries:
        if entry.kind != JoinerEntry.KIND_TITLE and entry.source:
            return "%s - Joined" % (
                os.path.splitext(os.path.basename(entry.source))[0],)
    return "Joined Video"


def first_scene_source(entries):
    """The first real recording in the list, or "" if there is none."""
    for entry in entries:
        if entry.kind != JoinerEntry.KIND_TITLE and entry.source:
            return entry.source
    return ""


def save_queued(path, joiner_list, reencode_target=None):
    """Write `joiner_list` as a queued batch job, with the re-encode decision
    made when it was queued: None for a lossless join, or (w, h, fps)."""
    data = joiner_list.to_dict()
    data["batch"] = {
        "reencode_target": list(reencode_target) if reencode_target else None,
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    os.replace(tmp, path)


def read_queued(path):
    """(entries, reencode_target) from a queued join."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    entries = [JoinerEntry.from_dict(d) for d in data.get("entries", [])]
    target = (data.get("batch") or {}).get("reencode_target")
    if target and len(target) == 3:
        target = (int(target[0]), int(target[1]), float(target[2]))
    else:
        target = None
    return entries, target


def queued_name_path(path):
    """A path that NAMES a queued join, for the batch's output naming and
    display: "<first recording> - Joined" beside the first recording, with
    its extension. It is not a file and is never opened.

    The batch finds "the recording a job is for" in several places - to name
    the output, to show where it is working from, and to spot a recording
    queued twice. A join has several recordings, so this gives those places
    one sensible answer: named like Create Video would name it, and never
    equal to a real recording, so it cannot be mistaken for a duplicate."""
    try:
        entries, _ = read_queued(path)
    except (OSError, ValueError):
        return ""
    first = first_scene_source(entries)
    ext = os.path.splitext(first)[1] if first else ".ts"
    folder = os.path.dirname(first) if first else os.path.dirname(path)
    return os.path.join(folder, joined_stem(entries) + (ext or ".ts"))
