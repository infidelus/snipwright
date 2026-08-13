"""Caching smartcut's index of a source file.

Building a MediaContainer walks the whole file, decoding just enough of every
packet to map GOP boundaries, keyframe positions and packet timestamps.  For a
Freeview recording that is a second or two.  For a 21 GB Blu-ray on a network
share it is over three minutes, and it happens again every time the file is
exported - the same work, on a file that has not changed.

Snipwright already caches its own FrameIndex this way; this does the same for
smartcut's.  What is stored is only the computed index: lists of integers and
numpy arrays.  The live PyAV handles are rebuilt on open, which is quick,
because opening a container is not what costs the time - walking it is.

The cache key includes the file's path, size and modification time, so an
edited or replaced file gets a fresh index rather than a stale one.  The format
version is part of the file, so a change to what smartcut records invalidates
every existing entry rather than loading something subtly wrong.
"""

import hashlib
import logging
import os
import pickle
from fractions import Fraction
from pathlib import Path

import av
import numpy as np

logger = logging.getLogger("snipwright")

# Bump when the set of attributes below changes, or when a smartcut update
# alters what any of them mean.  An old entry is then ignored rather than
# loaded into a container that expects something different.
#
# 3: gop_end_times_dts changed meaning for sources that begin part-way through
#    a GOP.  Entries written before that fix hold ends shifted one GOP earlier,
#    and loading one puts the container straight back into the fault the fix
#    removes - the cache would otherwise keep the bug alive on every file
#    already opened.
CACHE_VERSION = 3

CACHE_DIR = Path.home() / ".config" / "snipwright" / "smartcut-index"

# Everything the constructor computes by walking the file.  Deliberately
# explicit: a container attribute that is not listed here will not be cached,
# which fails safe - the worst case is that it is recomputed.
# `video_frame_times` and each track's `frame_times` are deliberately absent:
# they are the pts arrays multiplied by the stream time base, they are arrays of
# Fraction objects so they store poorly (2.5x the size of the pts they derive
# from), and recomputing them takes under half a second. Storing them would
# roughly double the cache for no useful gain.
CACHED_ATTRS = (
    "video_frame_times_pts",
    "video_keyframe_indices",
    "gop_start_times_dts",
    "gop_end_times_dts",
    "gop_start_nal_types",
    "gop_leading_end_dts",
    "gop_has_rasl",
    "duration",
    "start_time",
)

# Per audio track.  `packets` is not among them - it is a lazy view built at
# open time, and caching it would defeat the point of it being lazy.
CACHED_TRACK_ATTRS = ("frame_times_pts",)


def cache_path_for(path):
    """Where this file's cached index lives, keyed so a change invalidates it."""
    st = os.stat(path)
    key = hashlib.md5(
        ("%s|%s|%s|%s" % (Path(path).resolve(), st.st_mtime_ns, st.st_size,
                          CACHE_VERSION)).encode("utf-8")
    ).hexdigest()
    return CACHE_DIR / ("%s.sci" % key)


def _encode(value):
    """Make a value picklable without losing its type.

    Fractions and numpy arrays both pickle, but going through explicit forms
    keeps the file readable by a future version that changes representation.
    """
    if isinstance(value, Fraction):
        return ("frac", (value.numerator, value.denominator))
    if isinstance(value, np.ndarray):
        if value.dtype == object:
            # An object array - smartcut's frame times are arrays of Fraction,
            # which tobytes() cannot represent (it would serialise pointers).
            # Store the elements individually instead.
            return ("npobj", [_encode(v) for v in value.tolist()])
        return ("np", (value.tobytes(), str(value.dtype), value.shape))
    if isinstance(value, list):
        return ("list", [_encode(v) for v in value])
    return ("raw", value)


def _decode(encoded):
    kind, payload = encoded
    if kind == "frac":
        return Fraction(payload[0], payload[1])
    if kind == "np":
        data, dtype, shape = payload
        # frombuffer gives a read-only view over the pickled bytes; copy it so
        # the array behaves like the one the walk produced.
        return np.frombuffer(data, dtype=dtype).reshape(shape).copy()
    if kind == "npobj":
        arr = np.empty(len(payload), dtype=object)
        for i, item in enumerate(payload):
            arr[i] = _decode(item)
        return arr
    if kind == "list":
        return [_decode(v) for v in payload]
    return payload


def save(container, path):
    """Write a container's computed index to the cache.  Best-effort."""
    try:
        blob = {
            "version": CACHE_VERSION,
            "attrs": {name: _encode(getattr(container, name))
                      for name in CACHED_ATTRS
                      if hasattr(container, name)},
            "tracks": [
                {name: _encode(getattr(track, name))
                 for name in CACHED_TRACK_ATTRS if hasattr(track, name)}
                for track in container.audio_tracks
            ],
            "n_audio": len(container.audio_tracks),
            "n_subtitle": len(container.subtitle_tracks),
            # Subtitle packets are cached in full, unlike audio.  There are
            # only a couple of thousand in a long recording and they are a few
            # bytes each, but without them the file would still have to be
            # walked to collect them - which is the very cost being avoided.
            "subtitles": [
                [(bytes(pkt), pkt.pts, pkt.dts, pkt.duration) for pkt in track]
                for track in container.subtitle_tracks
            ],
        }
        target = cache_path_for(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Write beside the target and rename, so an interrupted write cannot
        # leave a half-written index that would later load as garbage.
        tmp = target.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            pickle.dump(blob, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, target)
        return True
    except Exception:
        logger.warning("Couldn't cache the smartcut index", exc_info=True)
        return False


def load(container, path):
    """Populate a container from the cache.  True if it was used.

    The caller must have opened the file and set up streams and tracks already;
    this only fills in what walking the file would have produced.
    """
    try:
        cache = cache_path_for(path)
        if not cache.exists():
            return False
        with open(cache, "rb") as f:
            blob = pickle.load(f)

        if blob.get("version") != CACHE_VERSION:
            return False
        # A different number of tracks means this is not the same file, whatever
        # the key says - refuse rather than mismatch them.
        if blob.get("n_audio") != len(container.audio_tracks):
            return False
        if blob.get("n_subtitle") != len(container.subtitle_tracks):
            return False

        for name, encoded in blob["attrs"].items():
            setattr(container, name, _decode(encoded))
        for track, saved in zip(container.audio_tracks, blob["tracks"]):
            for name, encoded in saved.items():
                setattr(track, name, _decode(encoded))

        # Rebuild the subtitle packets against this container's own streams -
        # a Packet must belong to the stream it will be muxed from.
        saved_subs = blob.get("subtitles")
        if saved_subs is not None:
            streams = list(container.av_container.streams.subtitles)
            if len(streams) != len(saved_subs):
                return False
            for i, (stream, packets) in enumerate(zip(streams, saved_subs)):
                rebuilt = []
                for data, pts, dts, duration in packets:
                    pkt = av.Packet(data)
                    pkt.stream = stream
                    pkt.pts = pts
                    pkt.dts = dts
                    pkt.duration = duration
                    rebuilt.append(pkt)
                container.subtitle_tracks[i] = rebuilt

        try:
            os.utime(cache, None)      # keep recently-used entries alive
        except OSError:
            pass
        return True
    except Exception:
        # Worth seeing: a cache that silently never loads looks like a cache
        # that is working, only slower.
        logger.warning("Couldn't load the cached smartcut index; walking the "
                       "file instead", exc_info=True)
        return False


def clear_all():
    """Delete every cached smartcut index now, regardless of age.

    Best-effort; returns (files_removed, bytes_freed).  Snipwright keeps two
    separate caches - its own FrameIndex and this one - and someone clearing
    the cache from Settings means both, not whichever one happens to be wired
    up.  Leaving this one behind made a fixed build behave exactly like the
    broken one on every file already opened.
    """
    removed = 0
    freed = 0
    try:
        if CACHE_DIR.exists():
            for entry in CACHE_DIR.glob("*.sci"):
                try:
                    freed += entry.stat().st_size
                    entry.unlink()
                    removed += 1
                except OSError:
                    pass
    except Exception:
        pass
    return removed, freed


def prune(max_age_days):
    """Delete cached indices not used within `max_age_days`.  0 keeps them."""
    try:
        days = float(max_age_days)
    except (TypeError, ValueError):
        return 0
    if days <= 0 or not CACHE_DIR.exists():
        return 0

    import time
    cutoff = time.time() - days * 86400
    removed = 0
    for entry in CACHE_DIR.glob("*.sci"):
        try:
            if entry.stat().st_mtime < cutoff:
                entry.unlink()
                removed += 1
        except OSError:
            pass
    return removed
