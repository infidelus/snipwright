"""
FrameIndex - a lightweight, frame-exact index of a video stream.

Built by demuxing packets (no pixel decoding), so it is fast even on long
recordings.  It records, in display (PTS) order:

  - every frame's PTS                (so frame N  <->  index N, exactly)
  - which PTS values are keyframes   (so we can seek reliably)
  - a running total of video packet bytes up to each frame (so the Info
    panel can report the real size of a range rather than assuming a flat
    bitrate across the file)
  - the source fps, dimensions, codec, time_base, start PTS, interlaced flag
    (so nothing is hard-coded to 25fps / PAL)

The index is cached to disk keyed by the file's path + mtime + size, so
re-opening the same recording is instant.

Building runs on a worker thread (FrameIndexBuilder) so the UI never blocks.
"""

import bisect
import hashlib
import json
import os
import struct
import time
from array import array
from itertools import accumulate
from pathlib import Path

import av

from PySide6.QtCore import (
    QThread,
    Signal,
)


CACHE_DIR = (
    Path.home()
    / ".cache"
    / "snipwright"
    / "index"
)

# 4 added the cumulative video byte totals used for size estimates.  A bump
# invalidates every cached index, so each file is re-scanned once.
# Bump whenever the contents of a cached index could differ from one built by
# the current code, or an old entry is loaded in place of a corrected one.
#
# 5: the field-pair collapse changed for 2.4.0 (a recording could be indexed at
#    half its length), and the interlaced flag stopped being decided by a
#    single decoded frame.  Entries written before those fixes hold the wrong
#    frame count and the wrong flag, and loading one puts the fix back out of
#    reach - which is exactly what happened during development, where exports
#    were compared against each other for several builds while every one of
#    them quietly used an index from before the collapse was fixed.
CACHE_VERSION = 5


class FrameIndex:

    def __init__(
            self,
            pts,
            keyframe_pts,
            fps,
            width,
            height,
            codec,
            time_base,
            start_pts,
            interlaced,
            cum_bytes=None,
    ):

        # Display-ordered frame PTS as a packed int64 array.
        self.pts = pts

        # Running total of video packet bytes, inclusive: cum_bytes[i] is the
        # number of bytes of coded video from the start of the file up to and
        # including frame i.  Optional - an index from an older cache, or one
        # built by a caller that did not collect sizes, leaves it None and the
        # size estimates fall back to a flat share of the file.
        self.cum_bytes = cum_bytes

        # Sorted list of keyframe PTS.
        self.keyframe_pts = keyframe_pts

        self.fps = fps
        self.width = width
        self.height = height
        self.codec = codec

        # (numerator, denominator) of the stream time_base.
        self.time_base = time_base

        self.start_pts = start_pts
        self.interlaced = interlaced

        # Median keyframe spacing in PTS units - used to size the seek margin.
        gaps = [
            keyframe_pts[i + 1] - keyframe_pts[i]
            for i in range(len(keyframe_pts) - 1)
        ]

        gaps.sort()

        self.median_gop_pts = (
            gaps[len(gaps) // 2]
            if gaps
            else 0
        )

    @property
    def frame_count(self):
        return len(self.pts)

    def pts_of(self, index):
        return self.pts[index]

    def index_of_pts(self, pts):
        """Nearest frame index for a given PTS."""
        i = bisect.bisect_left(self.pts, pts)

        if i >= len(self.pts):
            return len(self.pts) - 1

        if i > 0 and (pts - self.pts[i - 1]) <= (self.pts[i] - pts):
            return i - 1

        return i

    def seconds_of(self, index):
        """Container-relative time of a frame, in seconds."""
        num, den = self.time_base

        return (self.pts[index] - self.start_pts) * num / den

    def index_of_seconds(self, seconds):
        """Nearest frame index for a container-relative time in seconds.

        The inverse of seconds_of().  Used to re-map scene boundaries onto a
        differently-indexed copy of the same content (e.g. after a Quick
        Stream Fix renumbers the timestamps): convert each boundary to seconds
        on the old index, then back to a frame number on the new index, so the
        same moment in the video is kept rather than the same frame number.
        """
        num, den = self.time_base
        target_pts = self.start_pts + round(seconds * den / num)
        return self.index_of_pts(target_pts)

    # ------------------------------------------------------------------ #
    # Size estimates
    # ------------------------------------------------------------------ #

    @property
    def total_video_bytes(self):
        """Bytes of coded video across the whole file, or 0 if not recorded."""
        if not self.cum_bytes:
            return 0
        return int(self.cum_bytes[-1])

    def video_bytes_between(self, start, end):
        """Bytes of coded video in frames start..end, inclusive.

        Returns 0 when byte totals were not recorded (an index restored from
        an older cache), which callers treat as "fall back to a flat share".
        """
        if not self.cum_bytes:
            return 0

        last = len(self.cum_bytes) - 1

        start = max(0, min(int(start), last))
        end = max(0, min(int(end), last))

        if end < start:
            return 0

        before = self.cum_bytes[start - 1] if start > 0 else 0

        return int(self.cum_bytes[end] - before)

    def estimated_bytes(self, ranges, file_size):
        """Best estimate of the bytes that frame `ranges` occupy in the source.

        `ranges` is a list of inclusive (start, end) frame pairs.

        The video is measured exactly, from the byte totals collected while
        indexing.  Everything else in the container - audio, subtitles, PSI,
        transport padding - is spread evenly across the file's running time,
        which is close enough because those streams are near constant rate.

        This replaced a flat "share of the file by frame count", which was out
        by 5.7% on a Top Gear recording (2172 MB predicted, 2297 MB written):
        the kept programme ran above the file's average bitrate, and a purely
        proportional estimate cannot see that.
        """
        try:
            file_size = int(file_size or 0)
        except (TypeError, ValueError):
            file_size = 0

        total_frames = self.frame_count

        if not total_frames or file_size <= 0:
            return 0

        kept_frames = 0
        kept_video = 0

        for start, end in ranges or []:
            if end < start:
                continue
            kept_frames += end - start + 1
            kept_video += self.video_bytes_between(start, end)

        if kept_frames <= 0:
            return 0

        video_total = self.total_video_bytes

        # No byte totals (older cached index): the old flat estimate is all
        # that is available.
        if video_total <= 0:
            return file_size * (kept_frames / total_frames)

        # Guard against a source whose video bytes exceed the file size - it
        # should not happen, but a bad estimate is better than a negative one.
        other_bytes = max(0, file_size - video_total)

        return kept_video + other_bytes * (kept_frames / total_frames)

    def estimated_mb(self, ranges, file_size):
        """estimated_bytes() expressed in MB, as the Info panel shows it."""
        return self.estimated_bytes(ranges, file_size) / (1024 * 1024)

    # ------------------------------------------------------------------ #
    # Disk cache
    # ------------------------------------------------------------------ #

    def save(self, path):

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        header = {
            "version": CACHE_VERSION,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "codec": self.codec,
            "time_base": list(self.time_base),
            "start_pts": self.start_pts,
            "interlaced": self.interlaced,
            "n_pts": len(self.pts),
            "n_kf": len(self.keyframe_pts),
            "n_bytes": len(self.cum_bytes) if self.cum_bytes else 0,
        }

        with open(path, "wb") as f:

            blob = json.dumps(header).encode("utf-8")

            f.write(
                struct.pack("<I", len(blob))
            )

            f.write(blob)

            array("q", self.pts).tofile(f)

            array("q", self.keyframe_pts).tofile(f)

            if self.cum_bytes:
                array("q", self.cum_bytes).tofile(f)

    @staticmethod
    def load(path):

        with open(path, "rb") as f:

            (length,) = struct.unpack(
                "<I",
                f.read(4),
            )

            header = json.loads(
                f.read(length).decode("utf-8")
            )

            if header.get("version") != CACHE_VERSION:
                raise ValueError("cache version mismatch")

            pts = array("q")
            pts.fromfile(f, header["n_pts"])

            kf = array("q")
            kf.fromfile(f, header["n_kf"])

            n_bytes = header.get("n_bytes") or 0

            if n_bytes:
                cum_bytes = array("q")
                cum_bytes.fromfile(f, n_bytes)
            else:
                cum_bytes = None

        return FrameIndex(
            pts=pts,
            keyframe_pts=list(kf),
            fps=header["fps"],
            width=header["width"],
            height=header["height"],
            codec=header["codec"],
            time_base=tuple(header["time_base"]),
            start_pts=header["start_pts"],
            interlaced=header["interlaced"],
            cum_bytes=cum_bytes,
        )


# ---------------------------------------------------------------------- #
# Building
# ---------------------------------------------------------------------- #

def read_chapters(path):
    """Chapter start times in a container, in seconds, earliest first.

    Recordings that have been through an encoder often carry chapters - the
    upscaling and HEVC workflows both produce MKVs with them, and so does
    Snipwright's own export, which writes the scene markers out as chapters.
    Reading them back means a file exported from Snipwright, or produced by any
    other tool, reopens with its marks already on the timeline instead of
    having to be inspected elsewhere and re-entered by hand.

    Returns [] for a container with no chapters - MPEG-TS off a tuner never
    has any - and for anything that cannot be read, because chapters are a
    convenience and must never stop a file opening.  Only the start of each
    chapter is used: Snipwright's marks are points on the timeline, not spans.
    """
    try:
        container = av.open(str(path))
        try:
            # chapters() is a recent PyAV addition; older versions simply do
            # not have it, and a missing convenience must not break opening.
            getter = getattr(container, "chapters", None)
            raw = getter() if callable(getter) else (getter or [])

            seconds = []
            for chapter in raw:
                try:
                    if isinstance(chapter, dict):
                        start = chapter["start"]
                        time_base = chapter["time_base"]
                    else:
                        start = chapter.start
                        time_base = chapter.time_base
                    if start is None or not time_base:
                        continue
                    seconds.append(float(start * time_base))
                except Exception:
                    continue        # one bad chapter shouldn't lose the rest
        finally:
            container.close()

        return sorted(s for s in seconds if s >= 0)

    except Exception:
        # Deliberately silent: this module has no logger, and a file whose
        # chapters cannot be read still opens perfectly well without them.
        return []


def _probe_interlaced(path, max_frames=300):
    """Decode a sample of frames to learn whether the stream is interlaced.

    This used to decode exactly one frame - the first - and let it speak for
    the whole recording.  Broadcast material is routinely mixed: a Channel 4 HD
    recording opened on a progressive frame and was therefore treated as
    progressive throughout, even though 326 of the 686 frames later handed to
    the boundary encoder were field-coded.  Film-sourced programmes especially
    tend to open on progressive frames and switch to interlaced for adverts,
    trailers and continuity.

    So sample a run of frames and report True if any of them is field-coded.
    A few hundred is enough to catch a mixed stream while staying quick; it is
    also only half the picture, which is why build_frame_index combines this
    with the field-pair evidence from the packet walk.
    """
    try:
        container = av.open(str(path))
        stream = container.streams.video[0]

        seen = 0
        for frame in container.decode(stream):
            if getattr(frame, "interlaced_frame", False):
                container.close()
                return True
            seen += 1
            if seen >= max_frames:
                break

        container.close()

    except Exception:
        pass

    return False


def build_frame_index(
        path,
        progress_cb=None,
        cancel_cb=None,
):
    """
    Build a FrameIndex by demuxing packets (no pixel decode).

    progress_cb(frame_count) is called periodically.
    cancel_cb() -> bool lets a worker abort early.
    """
    container = av.open(str(path))
    stream = container.streams.video[0]

    pts_list = []
    size_list = []
    keyframe_pts = []

    # Bytes from packets the demuxer gave no PTS for.  They still occupy space
    # in the file, so they are carried on to the next frame that does have one
    # rather than being lost from the running total.
    pending_bytes = 0

    for packet in container.demux(stream):

        if cancel_cb is not None and cancel_cb():
            container.close()
            return None

        packet_bytes = int(getattr(packet, "size", 0) or 0)

        if packet.pts is None:
            pending_bytes += packet_bytes
            continue

        pts_list.append(packet.pts)
        size_list.append(packet_bytes + pending_bytes)
        pending_bytes = 0

        if packet.is_keyframe:
            keyframe_pts.append(packet.pts)

        if (
                progress_cb is not None
                and len(pts_list) % 2000 == 0
        ):
            progress_cb(len(pts_list))

    fps = (
        float(stream.average_rate)
        if stream.average_rate
        else 25.0
    )

    cc = stream.codec_context

    time_base = (
        stream.time_base.numerator,
        stream.time_base.denominator,
    )

    start_pts = (
        stream.start_time
        if stream.start_time is not None
        else (pts_list[0] if pts_list else 0)
    )

    width = cc.width
    height = cc.height
    codec = cc.name

    container.close()

    # Sort PTS and sizes together: the sizes are only meaningful while they
    # stay attached to the frame they came from.
    if pts_list:
        ordered = sorted(
            zip(pts_list, size_list),
            key=lambda pair: pair[0],
        )
        pts_list = [pair[0] for pair in ordered]
        size_list = [pair[1] for pair in ordered]

    keyframe_pts = sorted(set(keyframe_pts))

    # --- Field-coded (PAFF) detection and collapse ---------------------- #
    #
    # Some broadcast H.264 is field-coded: each displayable frame is split
    # into two field-pictures with separate PTS ~half a frame apart, so the
    # demuxer emits ~2x as many packets as there are frames.  Indexing those
    # as frames doubles the count and makes duration, the timeline scale and
    # thumbnails all wrong (e.g. a 42:50 file reported as 59:27).
    #
    # The stream's average_rate is the authoritative *displayable* rate, so we
    # collapse PTS onto that frame grid: keep one entry per frame-period slot.
    # Guarded - only applied when the raw count clearly exceeds what the
    # duration at the declared rate implies (i.e. field-coding is present),
    # so normal progressive files are never altered.
    # Bound before the guard below, because the interlace decision consults it
    # whether or not that block runs.
    has_field_pairs = False
    if pts_list and fps and time_base[1]:
        tb_num, tb_den = time_base
        ticks_per_frame = (tb_den / tb_num) / float(fps)

        # Decide whether to collapse by looking for field-pairs directly: any
        # consecutive PTS closer together than ~3/4 of a frame period means two
        # field-pictures share a frame slot.  This is robust where the old
        # global "raw count vs duration" ratio failed:
        #   - PTS discontinuities (ad breaks) inflated the duration estimate and
        #     suppressed the collapse, leaving the count (and reported length)
        #     too high - e.g. a 73-min file reported as 82 min.
        #   - Partially field-coded files (only some sections interlaced) never
        #     reached the old 20%-excess threshold and so were left uncollapsed.
        # The merge itself is correct for progressive streams too (nothing is
        # ever close enough to pair), but we still gate on field-pair presence
        # so a genuinely progressive file is never touched.
        if ticks_per_frame:
            near = ticks_per_frame * 0.75
            has_field_pairs = any(
                0 < (pts_list[i] - pts_list[i - 1]) < near
                for i in range(1, len(pts_list))
            )
        else:
            has_field_pairs = False

        if has_field_pairs:
            # Merge each packet into the previous frame when it sits less than
            # a field period after it.  Purely local: the gap to the previous
            # *kept* frame is what decides, so nothing depends on where the
            # stream's timestamps happen to sit.
            #
            # This used to place every packet on a global grid, slot =
            # round((pts - first_pts) / ticks_per_frame), and keep one packet
            # per slot.  That silently lost half of a recording whenever the
            # stream ended up half a frame period off that grid.  A field pair
            # is two 1800-tick gaps, which returns the stream to the grid, so
            # pairs normally cancel out - but an odd number of them anywhere in
            # the file leaves everything after it sitting on x.5 slots, and
            # round() then maps consecutive frames onto the same slot
            # (0.5 and 1.5 -> 0 and 2, 2.5 and 3.5 -> 2 and 4, ...) because
            # Python rounds halves to even.  A 2h38m film indexed as 1h19m,
            # with the timeline scale and every reported timing halved.
            #
            # Found on a raw Freeview recording with 2027 field-pair gaps - an
            # odd number - where the same file after Quick Stream Fix had 2004
            # and indexed correctly.  Whether the count came out odd or even
            # was the only difference between a good index and a ruined one.
            collapsed = [pts_list[0]]
            collapsed_sizes = [size_list[0]]
            for p, size in zip(pts_list[1:], size_list[1:]):
                if 0 <= p - collapsed[-1] < near:
                    # Second field of the frame already kept: its bytes belong
                    # to that frame, or the file's total would come out short
                    # by half on field-coded sources.
                    collapsed_sizes[-1] += size
                else:
                    collapsed.append(p)
                    collapsed_sizes.append(size)
            pts_list = collapsed
            size_list = collapsed_sizes
            # Keep only keyframes that survive in the collapsed set.
            kf = set(keyframe_pts)
            keyframe_pts = [p for p in pts_list if p in kf]

    # Field pairs found during the packet walk are proof of field coding
    # (PAFF), and they cost nothing extra to consult.  Decoding cannot be
    # dropped in their favour though: MBAFF codes interlaced content as single
    # frames carrying the field flag, with no pairs to find.  Each catches what
    # the other misses, so take either as evidence.
    interlaced = bool(has_field_pairs) or _probe_interlaced(path)

    # Running total, so a range's size is one subtraction rather than a walk.
    cum_bytes = array("q", accumulate(size_list))

    return FrameIndex(
        pts=array("q", pts_list),
        keyframe_pts=keyframe_pts,
        cum_bytes=cum_bytes,
        fps=fps,
        width=width,
        height=height,
        codec=codec,
        time_base=time_base,
        start_pts=start_pts,
        interlaced=interlaced,
    )


def _cache_path_for(src):
    st = os.stat(src)

    key = hashlib.md5(
        f"{Path(src).resolve()}|{st.st_mtime_ns}|{st.st_size}".encode("utf-8")
    ).hexdigest()

    return CACHE_DIR / f"{key}.idx"


def prune_index_cache(max_age_days):
    """Delete cached .idx files not used within max_age_days.

    "Used" means loaded - get_or_build_index touches the file on every cache
    hit, so an index for a file you still open regularly stays alive and only
    genuinely-stale ones expire.  A value <= 0 means keep forever.  Best-effort;
    returns the number of files removed.
    """
    try:
        if not max_age_days or max_age_days <= 0:
            return 0

        cutoff = time.time() - max_age_days * 86400
        removed = 0

        if CACHE_DIR.exists():
            for p in CACHE_DIR.glob("*.idx"):
                try:
                    if p.stat().st_mtime < cutoff:
                        p.unlink()
                        removed += 1
                except OSError:
                    pass

        return removed

    except Exception:
        return 0


def clear_index_cache():
    """Delete every cached .idx file now, regardless of age.  Best-effort;
    returns (files_removed, bytes_freed)."""
    removed = 0
    freed = 0
    try:
        if CACHE_DIR.exists():
            for p in CACHE_DIR.glob("*.idx"):
                try:
                    freed += p.stat().st_size
                    p.unlink()
                    removed += 1
                except OSError:
                    pass
    except Exception:
        pass
    return removed, freed


class FrameIndexBuilder(QThread):

    # Note: named to avoid clashing with QThread.finished.
    progress = Signal(int)
    finished_index = Signal(object)
    failed = Signal(str)

    def __init__(
            self,
            path,
            parent=None,
    ):
        super().__init__(parent)

        self.path = path
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            index = build_frame_index(
                self.path,
                progress_cb=self.progress.emit,
                cancel_cb=lambda: self._cancel,
            )

            if index is not None and not self._cancel:
                self.finished_index.emit(index)

        except Exception as exc:
            self.failed.emit(str(exc))


def get_or_build_index(
        path,
        parent=None,
):
    """
    Return (index, None) if a valid cached index loads.
    Return (None, builder) if it must be built - caller connects the
    builder's signals and calls builder.start().

    The builder auto-saves the finished index to cache.
    """
    cache = _cache_path_for(path)

    if cache.exists():
        try:
            index = FrameIndex.load(cache)
            # Mark the cache file as freshly used so age-based pruning keeps
            # indices for files you actually open and only expires stale ones.
            try:
                os.utime(cache, None)
            except OSError:
                pass
            return index, None
        except Exception:
            pass    # stale/corrupt - rebuild

    builder = FrameIndexBuilder(path, parent)

    def _autosave(index):
        try:
            index.save(cache)
        except Exception:
            pass

    builder.finished_index.connect(_autosave)

    return None, builder


def build_index_sync(path):
    """Synchronously return a FrameIndex for `path`, using the on-disk cache
    when valid and saving a freshly built index back to it.  This is the
    blocking equivalent of get_or_build_index, for callers that already run on
    a worker thread (the batch manager) and don't want the QThread builder.
    """
    cache = _cache_path_for(path)

    if cache.exists():
        try:
            index = FrameIndex.load(cache)
            try:
                os.utime(cache, None)
            except OSError:
                pass
            return index
        except Exception:
            pass    # stale/corrupt - rebuild

    index = build_frame_index(path)
    try:
        index.save(cache)
    except Exception:
        pass
    return index
