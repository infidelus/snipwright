"""Joiner render - turn a joiner list into one video.

Each scene entry is rendered with the exporter's smartcut engine to its own
temporary .ts, the pieces are joined with ffmpeg's concat demuxer, and the
joined .ts is finally written out in the chosen format (Match source / MKV /
MP4) using the same conversion the normal exporter uses.

The join itself is a plain stream copy, so it works when every entry shares the
same codec, resolution and frame rate - several recordings off the same
channel, the normal case.  Mixed formats need re-encoding to a common format,
which is a later phase; if the join step fails for that reason the error says
so.  (The final MKV/MP4 step is independent of that - it converts the single
joined file.)
"""

import os
import json
import shutil
import subprocess

import logging

from media.pixfmt import for_output as pixfmt_for_output

from utils.proc import popen_progress, read_stderr
import tempfile

from PySide6.QtCore import (
    QT_TRANSLATE_NOOP, QCoreApplication, QObject, QThread, Signal,
)

logger = logging.getLogger("snipwright")

from media.frame_index import build_index_sync
from export.exporter import (
    export_ranges,
    format_completion_summary,
    _write_mkv_chapters,
    _transcode_to_mp4,
    _count_output_frames,
    _audio_frame_count,
    _audio_track_info,
    _Cancelled as _ExporterCancelled,
    probe_subtitle_tracks,
    _NOTE_SUBS_LOST,
    _SUBTITLE_NAMES,
)
from utils.note_text import NoteText, counted, translate_note
from export.dvb_subtitles import (
    CARRIED_CODECS,
    DVB_CODECS,
    PGS_CODECS,
    carry_dvb_subtitles,
    subtitle_kinds,
)


# Progress labels used in more than one place.  Marked for translation; the
# worker translates each label in _report() before it is emitted.
_RENDERING_SCENE = QT_TRANSLATE_NOOP("ExportNotes", "Rendering scene %d of %d…")
_REENCODING_JOIN = QT_TRANSLATE_NOOP("ExportNotes", "Re-encoding and joining scenes…")
_APPLYING_PROFILE = QT_TRANSLATE_NOOP("ExportNotes", "Applying profile…")
_WRITING_MKV = QT_TRANSLATE_NOOP("ExportNotes", "Writing MKV…")
_CONVERTING_MP4 = QT_TRANSLATE_NOOP("ExportNotes", "Converting to MP4…")

def _joiner_pix_fmt(segments):
    """Pixel format for a joined render, taken from the first clip.

    A joiner run can mix sources and one output format has to serve them all,
    so the first clip is the reference: if it is 10-bit the output stays
    10-bit, and an 8-bit clip joined into it is carried at the higher depth,
    which costs a little size but loses nothing.
    """
    for path in (segments or []):
        if isinstance(path, str) and path:
            return pixfmt_for_output(path)
    return "yuv420p"


def _find_font(bold=False):
    """Return a usable .ttf path, preferring DejaVu Sans (present on Mint)."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def _ffmpeg_colour(hex_colour, default="0x000000"):
    """Convert a '#RRGGBB' colour to ffmpeg's '0xRRGGBB' form."""
    value = (hex_colour or "").strip()
    if value.startswith("#") and len(value) == 7:
        return "0x" + value[1:]
    return default


class _Cancelled(Exception):
    """Raised internally to unwind cleanly when the user cancels."""


# Friendly names for the codecs we see on UK broadcast streams.
_VCODEC_NAMES = {"h264": "H.264", "hevc": "HEVC", "mpeg2video": "MPEG-2"}
_ACODEC_NAMES = {
    "aac": "AAC", "aac_latm": "AAC", "mp2": "MP2", "mp3": "MP3",
    "ac3": "AC-3", "eac3": "E-AC-3",
}


def _source_signature(path):
    """(video_codec, width, height, audio_codec) for the first video/audio
    streams - the things that must match for a straight-copy join to work."""
    try:
        data = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_type,codec_name,width,height", "-of", "json", path],
            capture_output=True, text=True).stdout)
    except Exception:
        return (None, 0, 0, None)

    vcodec = acodec = None
    width = height = 0
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and vcodec is None:
            vcodec = stream.get("codec_name")
            width = stream.get("width") or 0
            height = stream.get("height") or 0
        elif stream.get("codec_type") == "audio" and acodec is None:
            acodec = stream.get("codec_name")
    return (vcodec, width, height, acodec)


def _describe_signature(sig):
    vcodec, width, height, acodec = sig
    video = _VCODEC_NAMES.get(vcodec, vcodec or "unknown video")
    audio = _ACODEC_NAMES.get(acodec, acodec or "no") + " audio"
    if width and height:
        return "%s %d×%d, %s" % (video, width, height, audio)
    return "%s, %s" % (video, audio)


def scan_join_compatibility(entries):
    """Quick header-only probe of each distinct source.  Returns
    (ok, formats_text): ok is False when the sources don't share one format (so
    a straight-copy join won't work), and formats_text is a bulleted list of
    the distinct formats found, for the caller to present."""
    distinct = {}
    for entry in entries:
        src = entry.source
        if not src or not os.path.exists(src):
            continue
        sig = _source_signature(src)
        distinct.setdefault(sig, os.path.basename(src))

    if len(distinct) <= 1:
        return True, ""

    lines = ["• %s — e.g. %s" % (_describe_signature(sig), name)
             for sig, name in distinct.items()]
    return False, "\n".join(lines)


def _probe_dims_fps(path):
    """(display_width, height, fps_rounded) for the first video stream.

    The width is the *display* width - the stored width adjusted by the sample
    aspect ratio - so anamorphic broadcast SD (e.g. 544x576 or 720x576 stored
    but 16:9 on screen) is handled by its true on-screen shape rather than its
    stored pixel grid.  Square-pixel sources are returned unchanged.
    """
    try:
        data = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries",
             "stream=width,height,avg_frame_rate,r_frame_rate,"
             "sample_aspect_ratio",
             "-of", "json", path], capture_output=True, text=True).stdout)
        stream = data.get("streams", [{}])[0]
    except Exception:
        return (0, 0, 0)
    width = stream.get("width") or 0
    height = stream.get("height") or 0
    rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
    try:
        num, den = rate.split("/")
        fps = round(float(num) / float(den)) if float(den) else 0
    except (ValueError, ZeroDivisionError):
        fps = 0

    # Fold in the sample aspect ratio so the width reflects the on-screen shape.
    # A non-square SAR (e.g. 32:17 on UK SD) means the picture is wider than its
    # stored width; using the stored width here is what made anamorphic joins
    # come out squashed and letterboxed.
    sar = stream.get("sample_aspect_ratio") or "1:1"
    try:
        sar_n, sar_d = (int(x) for x in sar.split(":"))
        if sar_n > 0 and sar_d > 0 and sar_n != sar_d:
            width = int(round(width * sar_n / sar_d))
    except (ValueError, ZeroDivisionError):
        pass
    if width % 2:                       # keep an even width for yuv420p
        width += 1
    return (width, height, fps)


def recommended_target(entries):
    """Choose a common (width, height, fps) for a re-encode join: the largest
    frame size present and the highest (rounded) frame rate, so higher-quality
    scenes are preserved and lower ones upscaled to match."""
    best_w = best_h = 0
    best_pixels = -1
    fps = 0
    seen = set()
    for entry in entries:
        src = entry.source
        if not src or src in seen or not os.path.exists(src):
            continue
        seen.add(src)
        width, height, rate = _probe_dims_fps(src)
        if width * height > best_pixels:
            best_pixels = width * height
            best_w, best_h = width, height
        fps = max(fps, rate)
    return (best_w or 1920, best_h or 1080, fps or 25)


def _probe_video(path):
    """Return (codec_name, interlaced) for the first video stream."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name,field_order",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True).stdout.split()
    codec = out[0] if out else ""
    field_order = out[1] if len(out) > 1 else ""
    interlaced = field_order in ("tt", "bb", "tb", "bt")
    return codec, interlaced


class JoinerRenderWorker(QThread):
    """Renders every joiner entry and joins them into one output file."""

    progress = Signal(int, str)        # overall percent, status label
    finished_ok = Signal(str)          # output path
    failed = Signal(str)               # message ("Cancelled." if cancelled)

    def __init__(self, entries, out_path, profile=None,
                 reencode_target=None, parent=None):
        super().__init__(parent)
        self._entries = list(entries)
        self._out = out_path
        # The full output profile chosen in the Save Video dialogue (the same
        # dialogue used everywhere else).  It carries container, video mode
        # (copy/HEVC), crop, aspect and audio settings, and is applied to the
        # joined result exactly as Save Video applies it to a single cut.
        # None falls back to a plain lossless copy to a .ts.
        self._profile = profile
        self._out_format = profile.container if profile is not None else "match"
        # "Match Source" means the container the destination was given, and
        # must be resolved to a real one here, exactly as export_ranges()
        # resolves it for a single cut.  The joiner took "match" to mean
        # MPEG-TS whatever the name, so joining scenes from Blu-ray .mkv rips
        # wrote a transport stream under an .mkv name - playable, but
        # mislabelled and with no chapters, because the chapters are written
        # by the Matroska mux that never ran (found 2026-10-09).
        if self._out_format == "match":
            by_ext = {".mkv": "mkv", ".mp4": "mp4", ".m4v": "mp4",
                      ".mov": "mp4"}
            resolved = by_ext.get(os.path.splitext(out_path)[1].lower())
            if resolved:
                logger.info("Joiner: Match Source writes %s to suit the "
                            "destination's %s extension.", resolved.upper(),
                            os.path.splitext(out_path)[1])
                self._out_format = resolved
        # None -> lossless stream-copy join (same-format scenes).
        # (width, height, fps) -> re-encode every scene to that and join.
        self._reencode_target = reencode_target
        self._cancel = False
        # (short label, full explanation) pairs for the completion dialog,
        # filled in as the run goes.  A join can quietly normalise several
        # recordings into one shape, so what it did is worth reporting rather
        # than leaving to the log.
        self._notes = []
        # The current stage's high-water mark, which stage it is, and when
        # that stage began; see _report.
        self._last_percent = 0
        self._stage = None
        self._stage_started = None
        # Populated just before finished_ok is emitted; read by the caller in
        # its slot.
        self.stats = {}

    def _profile_is_lossless_copy(self):
        """True when the profile asks for nothing beyond a possible container
        change - so the proven lossless join + finalize path can be used and
        the output stays byte-for-byte the source video.

        Any of HEVC, crop, an aspect override, or AAC re-encode means the
        joined stream has to be processed, which we do in one whole-file pass
        (below), identical to how Save Video handles the same profile."""
        p = self._profile
        if p is None:
            return True
        return (
            getattr(p, "video", "copy") == "copy"
            and getattr(p, "crop_mode", "none") == "none"
            and getattr(p, "aspect", "source") == "source"
            and getattr(p, "audio", "copy") == "copy"
        )

    def cancel(self):
        self._cancel = True

    def _check_cancel(self):
        if self._cancel:
            raise _Cancelled()

    def _report(self, percent, label, stage=None):
        """Emit progress for the current stage, never backwards within it.

        A join is not one job, it is several: cutting each scene, joining
        them, then writing the result in the requested format.  Squeezing all
        of that onto one 0-100 bar meant the last stage - which re-encodes,
        and is the slowest thing in the run - got a sliver at the top, and the
        bar sat at 99% while the real work happened.

        So each stage gets the whole bar, the same way a normal export does:
        the bar fills, the label changes, and it fills again.  `stage` is any
        token that identifies the current one; passing a new one resets the
        bar to the beginning.

        Within a stage the value never falls, because the exporter reports
        each of ITS phases as a fresh 0-100 and passing those through
        unfiltered is what made the bar bounce backwards on every scene.
        """
        if stage is not None and stage != self._stage:
            self._stage = stage
            self._last_percent = 0
            self._stage_started = None

        percent = max(0, min(100, int(percent)))
        if percent < self._last_percent:
            percent = self._last_percent
        self._last_percent = percent
        # Translated here because the signal carries a plain str: a
        # NoteText would arrive as its English text.  The Joiner's progress
        # lines stayed English in the German interface until this.
        self.progress.emit(percent, translate_note(
            self._with_eta(percent, label), QCoreApplication.translate))

    def _with_eta(self, percent, label):
        """The status label with a time estimate appended, once one is sound.

        The estimate lives in the LABEL, not the bar: the bar has room for a
        percentage and nothing else, and the label is already a full line of
        text sitting under it.

        Deliberately plain arithmetic - elapsed time scaled by how much is
        left - rather than the exporter's EtaTracker. That tracker times each
        recode phase separately because a phase change means the rate changes;
        here there is one bar covering scene renders and a whole-file pass,
        and the honest thing to report is the average so far.

        Nothing is shown below 5% or in the first few seconds, because an
        estimate drawn from almost no data is worse than no estimate: it swings
        wildly and people watch it instead of the bar.
        """
        import time

        # Timed from the START OF THIS STAGE, not the run.  The stages do
        # wildly different work - a stream copy then a whole-file encode - so
        # an average across them would predict the encode from the copy's rate
        # and be badly wrong in the direction that matters.
        if self._stage_started is None:
            self._stage_started = time.time()

        if percent < 5 or percent >= 100:
            return label

        elapsed = time.time() - self._stage_started
        if elapsed < 5.0:
            return label

        remaining = elapsed * (100.0 - percent) / percent
        if remaining < 1.0:
            return label

        from utils.eta import format_seconds
        return NoteText(QT_TRANSLATE_NOOP("ExportNotes", "%s  (about %s left)"),
                        label, format_seconds(remaining))

    def _completion_stats(self, started, durations):
        """The figures ExportCompleteDialog shows, measured from the output.

        The joiner used to finish with a one-line "Joined video created" box
        while a plain export got the full summary.  That is the wrong way
        round: a join is the operation where you most want to see what came
        out, because it is the one that can silently re-encode several
        recordings into one and normalise them to a common shape.

        Every figure here is read back off the finished file rather than
        totted up from what we intended to write, so it reports what is
        actually on disk.
        """
        import time

        stats = {
            "out_path": self._out,
            "scenes": len(self._entries),
            "duration_secs": sum(durations),
            "processing_secs": max(0.0, time.time() - started),
            "errors": [],
            "notes": list(self._notes),
        }

        try:
            stats["out_size"] = os.path.getsize(self._out)
        except OSError:
            stats["out_size"] = 0
        # What the joined file kept, read off it - for the log and the window.
        stats["subtitle_tracks"] = probe_subtitle_tracks(self._out)

        try:
            stats["video_frames"] = _count_output_frames(self._out)
        except Exception:
            stats["video_frames"] = 0

        try:
            frames = _audio_frame_count(self._out)
            stats["audio_frames"] = frames or 0
        except Exception:
            stats["audio_frames"] = 0

        try:
            out = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a",
                 "-show_entries", "stream=index", "-of", "csv=p=0",
                 self._out],
                capture_output=True, text=True, timeout=30,
            ).stdout
            # A SET of indexes, not a line count.  ffprobe lists an MPEG-TS
            # stream once per program, so a single-audio recording came back
            # as two tracks - the same trap that once had the exporter mapping
            # streams that did not exist.
            stats["audio_tracks"] = len(
                {line.strip() for line in out.splitlines() if line.strip()})
        except Exception:
            stats["audio_tracks"] = 0

        elapsed = stats["processing_secs"]
        stats["fps"] = (stats["video_frames"] / elapsed) if elapsed else 0.0

        seconds = stats["duration_secs"]
        stats["video_bitrate"] = (
            int(stats["out_size"] * 8 / seconds) if seconds else 0)

        return stats

    def run(self):
        import time

        started = time.time()
        self._started_at = started
        tmpdir = tempfile.mkdtemp(prefix="snipwright-joiner-")
        index_cache = {}
        segments = []
        durations = []
        try:
            n = len(self._entries)
            if n == 0:
                raise RuntimeError("The joiner list is empty.")

            # The scene renders are one stage and own the whole bar
            # between them; the join and the format pass are stages of their
            # own.  Trying to fit everything on one bar meant whichever stage
            # came last got whatever was left, which was a sliver.
            slots = n

            for i, entry in enumerate(self._entries):
                self._check_cancel()

                # A title card is generated, not cut from a source.  It needs
                # the re-encode join (it can't stream-copy alongside broadcast),
                # which the caller guarantees by setting a target when a title
                # is present.
                if entry.is_title:
                    self._report(i * 100 / slots,
                                 NoteText(QT_TRANSLATE_NOOP(
                                 "ExportNotes", "Building title card %d of %d…"),
                                 i + 1, n),
                                 stage="scenes")
                    target = self._reencode_target or (1920, 1080, 25)
                    seg = self._make_title(entry, i, tmpdir, target)
                    segments.append(seg)
                    durations.append(entry.duration)
                    continue

                src = entry.source
                if not src or not os.path.exists(src):
                    raise RuntimeError("File not found:\n%s" % (src,))

                self._report(i * 100 / slots,
                             NoteText(_RENDERING_SCENE, i + 1, n),
                             stage="scenes")

                # Build (or reuse) the source's frame index, then map the
                # scene's seconds onto frame numbers for the exporter.
                if src not in index_cache:
                    index_cache[src] = build_index_sync(src)
                index = index_cache[src]

                start_f = index.index_of_seconds(entry.start)
                end_f = index.index_of_seconds(entry.end)
                if end_f < start_f:
                    start_f, end_f = end_f, start_f

                seg = os.path.join(tmpdir, "seg_%04d.ts" % i)

                def _cb(data, base=i):
                    pct = data.get("percent", 0) if isinstance(data, dict) else 0
                    # A phase that reports -1 is a busy indicator, not a
                    # position; hold where we are rather than snapping to the
                    # start of the scene's slot.
                    if pct < 0:
                        pct = 0
                    self._report((base + pct / 100.0) * 100 / slots,
                                 NoteText(_RENDERING_SCENE, base + 1, n),
                                 stage="scenes")

                # Always render the intermediate pieces as .ts; the chosen
                # output format is applied once, to the joined file.
                export_ranges(
                    src, seg, [(start_f, end_f)], index,
                    out_format="match",
                    progress_cb=_cb,
                    cancel_cb=lambda: self._cancel,
                    # Not "Export complete": this is an intermediate piece,
                    # and one per scene made a single join look like several
                    # finished exports in the log.  Compact for the same
                    # reason - a scene is only worth reading when something
                    # went wrong, and the full block buried the summary that
                    # matters under five that do not.
                    summary_label="Joiner: scene %d of %d rendered:" % (
                        i + 1, n),
                    summary_compact=True,
                )
                self._check_cancel()
                segments.append(seg)
                durations.append(entry.duration)

            self._report(0,
                         QT_TRANSLATE_NOOP("ExportNotes", "Joining scenes…")
                         if not self._reencode_target
                         else _REENCODING_JOIN,
                         stage="join")
            if self._reencode_target:
                fades = [
                    (float(getattr(e, "fade_in", 0.0) or 0.0),
                     float(getattr(e, "fade_out", 0.0) or 0.0))
                    for e in self._entries
                ]
                joined_ts = self._join_reencode(
                    segments, tmpdir, self._reencode_target, durations, fades)
            else:
                joined_ts = self._join(segments, tmpdir)
                self._carry_copy_join_subtitles(
                    joined_ts, segments, durations, tmpdir)
            self._check_cancel()

            # Apply the chosen output profile to the joined stream.  A plain
            # lossless-copy profile takes the proven fast path (container
            # change only, per-scene MKV chapters preserved); anything that
            # processes the picture or audio (HEVC, crop, aspect, AAC) is
            # applied in a single whole-file pass, so the result matches Save
            # Video for the same profile and no per-scene seams are re-encoded
            # independently (which would risk header mismatches at the joins).
            if self._profile_is_lossless_copy():
                self._finalize(joined_ts, durations)
            else:
                self._report(0, _APPLYING_PROFILE, stage="finish")
                self._apply_profile(joined_ts, 0)
            self._check_cancel()

            self._report(100, QT_TRANSLATE_NOOP("ExportNotes", "Done"),
                         stage="done")
            # Populated before finished_ok so the caller can read it in the
            # slot, matching how chalkline_worker hands back its own extras.
            self.stats = self._completion_stats(started, durations)
            # ...and logged here, which it never was.  The figures went only
            # to ExportCompleteDialog, so a join left a block in the log for
            # every intermediate scene and nothing at all for the file it
            # actually produced.  Same formatter as a plain export, so the
            # two cannot drift.
            logger.info("\n".join(format_completion_summary(
                "Joined video complete:", self.stats, notes=self._notes)))
            self.finished_ok.emit(self._out)

        except (_Cancelled, _ExporterCancelled):
            # Ours, or the exporter's own (raised when the user aborts while a
            # scene render or the profile pass is inside export_ranges) - both
            # mean the same thing: a deliberate stop, not an error.
            self._discard_output()
            self.failed.emit("Cancelled.")
        except Exception as exc:                    # noqa: BLE001 - reported
            self._discard_output()
            if self._cancel:
                # The abort can also surface as an ordinary error from the
                # teardown (smartcut removes its output and returns, and the
                # pipeline then reports the missing video).  The user pressed
                # Cancel, so that's the answer - not the wreckage's shape.
                self.failed.emit("Cancelled.")
            else:
                self.failed.emit(str(exc))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _discard_output(self):
        try:
            if os.path.exists(self._out):
                os.remove(self._out)
        except OSError:
            pass

    def _join(self, segments, tmpdir):
        """Concatenate the rendered .ts segments into one .ts; returns its
        path."""
        if not segments:
            raise RuntimeError("Nothing to join.")

        joined = os.path.join(tmpdir, "joined.ts")
        if len(segments) == 1:
            shutil.copyfile(segments[0], joined)
            return joined

        list_path = os.path.join(tmpdir, "concat.txt")
        with open(list_path, "w", encoding="utf-8") as handle:
            for seg in segments:
                # concat-demuxer quoting: wrap in single quotes, escape any.
                handle.write("file '%s'\n" % seg.replace("'", "'\\''"))

        cmd = [
            "ffmpeg", "-hide_banner", "-y",
            "-f", "concat", "-safe", "0", "-i", list_path,
            # -map 0 or ffmpeg keeps ONE audio track and throws the rest away.
            #
            # Without it ffmpeg applies its default stream selection, which
            # picks a single stream of each type - the "best" one - and
            # discards the others.  Every join therefore lost every audio
            # track but the first, silently: the scenes were rendered with
            # both ("smartcut: finished OK (2 audio tracks written)") and the
            # joined file came out with one.  Found on a BBC ONE South
            # recording whose audio description track carried real audio and
            # simply vanished.  Subtitles would go the same way.
            #
            # -map 0 takes every stream from the input in its original order,
            # which is what a lossless join is supposed to mean.
            "-map", "0",
            "-c", "copy", joined,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(joined):
            tail = "\n".join((result.stderr or "").strip().splitlines()[-6:])
            raise RuntimeError(
                "Joining the scenes failed.  The clips may not share the same "
                "format (codec, resolution or frame rate); mixed formats will "
                "be supported in a later build.\n\n" + tail)

        # Count what came out against what went in.
        #
        # The exporter has done this for a long time - see "Audio tracks in
        # finished file" in export_ranges() - and the joiner did not, which is
        # why it lost every audio track but the first for as long as it has
        # existed and said nothing.  The scenes each reported writing two
        # tracks and the joined file held one, and nothing compared the two
        # numbers.  A count is cheap next to a join and turns a silent loss
        # into a line in the log.
        try:
            before = len(_audio_track_info(segments[0]))
            after = len(_audio_track_info(joined))
        except Exception:
            before = after = 0
        if before and after and after < before:
            logger.warning(
                "Joiner: the joined file has %d audio track(s) but the scenes "
                "had %d - %d lost in the join.",
                after, before, before - after)
        return joined

    def _join_reencode(self, segments, tmpdir, target, durations, fades=None):
        """Join scenes that don't share a format by re-encoding them all to a
        common target (width, height, fps) in one ffmpeg concat-filter pass.

        Each scene is deinterlaced, scaled (preserving aspect, padded), set to
        the target frame rate and pixel format; audio is resampled to 48 kHz
        stereo AAC.  Lower-resolution scenes are upscaled to match the highest.

        fades, if given, is a per-segment list of (fade_in, fade_out) seconds -
        a fade to/from black applied to that clip's picture only (the audio is
        left at full level).
        """
        if not segments:
            raise RuntimeError("Nothing to join.")

        width, height, fps = target
        joined = os.path.join(tmpdir, "joined.ts")

        # concat needs one layout and one sample rate across every input, so
        # the segments have to be normalised to something.  That something was
        # hardcoded to stereo, which flattened a 5.1 recording every time the
        # joiner had to re-encode - and the bitrate was pinned at 192k, which
        # is a stereo figure being spent on six channels.
        #
        # Normalise to the WIDEST layout present instead.  Upmixing a stereo
        # segment puts its content in the front pair and silence elsewhere,
        # which loses nothing; downmixing a 5.1 one to match a stereo title
        # card would throw the surround away, which is the mistake this
        # replaces.
        from export.audio_repair import layout_name, source_profile

        # How many audio tracks can be carried through.
        #
        # concat needs every input to contribute the same number of audio
        # streams, so the most that can be carried is the FEWEST any segment
        # has.  This used to take `[%d:a:0]` from each and concatenate with
        # `a=1`, so a join that had to re-encode came out with one audio track
        # however many went in - an audio description or second language was
        # dropped without a word.  The lossless path lost them too until
        # 2.7.2; this is the same fault in the other half.
        counts = [len(_audio_track_info(seg)) for seg in segments]
        tracks = min(counts) if counts else 0
        if tracks and min(counts) != max(counts):
            logger.warning(
                "Joiner: the scenes have different numbers of audio tracks "
                "(%s); carrying %d, which is all they have in common.",
                ", ".join(str(c) for c in counts), tracks,
            )
            self._notes.append((
                QT_TRANSLATE_NOOP(
                    "ExportNotes", "some audio tracks could not be carried through"),
                "The scenes do not all have the same number of audio tracks "
                "(%s), and joining by re-encoding can only carry the ones "
                "they share. %d track(s) were kept."
                % (", ".join(str(c) for c in counts), tracks),
            ))

        # Subtitles cannot go through the concat filter below - broadcast
        # subtitles are pictures on their own timeline - so DVB subtitles are
        # carried round it instead and added once the picture and sound are
        # joined (item 1w; see export/dvb_subtitles.py, which also explains
        # why some scenes' subtitles are redrawn).  Anything else - a disc's
        # PGS subtitles, which a transport stream cannot hold - still cannot
        # be carried, and says so: that used to be SILENT for every kind.
        #
        # What is CARRIED is read from the rendered scenes; what is LOST must
        # be read from the SOURCE recordings.  A scene is rendered to a
        # transport stream, and a Blu-ray's PGS subtitles are already dropped
        # at that step - so judging by the rendered scenes, as this check
        # first did, found nothing to report and said nothing (the user's join of
        # an HD, an SD and a Blu-ray recording, 2026-10-03).  Every entry,
        # title cards included, renders exactly one segment, in order.
        # A disc's PGS is converted to DVB from the source (2.10.0), so it
        # counts as carried; teletext and anything else is still lost.
        kinds = [subtitle_kinds(seg) for seg in segments]
        lost, sources = [], []
        for entry in self._entries[:len(segments)]:
            source = [] if entry.is_title else subtitle_kinds(entry.source)
            lost.append([x for x in source if x not in CARRIED_CODECS])
            sources.append((entry.source, entry.start)
                           if any(x in PGS_CODECS for x in source) else None)
        dvb_scenes = sum(1 for k, src in zip(kinds, sources)
                         if src or any(x in DVB_CODECS for x in k))
        other_scenes = sum(1 for k in lost if k)
        if other_scenes:
            logger.warning(
                "Joiner: %d of %d scene(s) have subtitles of a kind a "
                "re-encoded join cannot carry (%s); the joined video does "
                "not have them.", other_scenes, len(segments),
                ", ".join(sorted({x for k in lost for x in k})))
            self._notes.append((
                QT_TRANSLATE_NOOP(
                    "ExportNotes", "some subtitles could not be carried through"),
                "%d of the %d scenes had subtitles of a kind that cannot be "
                "carried through a join that has to be re-encoded (such as "
                "teletext), so the joined video does not have them. A join "
                "of scenes that all share one format is not re-encoded, and "
                "keeps them." % (other_scenes, len(segments)),
            ))
        if tracks == 0:
            logger.warning("Joiner: no audio track common to every scene.")

        # Per TRACK, not once for the whole file: a 5.1 main track and a
        # stereo audio-description track want different layouts, and forcing
        # both to the widest would inflate the AD track to six channels of
        # mostly silence.
        track_layouts, track_rates = [], []
        for k in range(tracks):
            profiles = [source_profile(seg, k) for seg in segments]
            ch = max([c for c, _b in profiles if c] or [2])
            br = [b for _c, b in profiles if b]
            track_layouts.append(layout_name(ch))
            track_rates.append(max(br) if br else None)
            logger.info(
                "Joiner: re-encoding audio track %d as %s (%d channel(s)) "
                "at %s.", k + 1, layout_name(ch), ch,
                ("%d kbps" % (max(br) // 1000)) if br
                else "the encoder's own rate",
            )

        shape = "; ".join(
            "track %d as %s at %s"
            % (k + 1, track_layouts[k],
               ("%d kbps" % (track_rates[k] // 1000)) if track_rates[k]
               else "the encoder's own rate")
            for k in range(tracks)
        ) or "no audio"
        self._notes.append((
            QT_TRANSLATE_NOOP(
                "ExportNotes", "the scenes were re-encoded to join them"),
            "These scenes did not match closely enough to be joined without "
            "re-encoding, so the picture was re-encoded and the audio was "
            "brought to a common shape: %s. Scenes that "
            "match can be joined losslessly instead."
            % (shape,),
        ))

        inputs = []
        filters = []
        labels = []
        for i, seg in enumerate(segments):
            inputs += ["-i", seg]

            # Optional fade to/from black for this clip's picture.  Clamp to the
            # clip length so a too-long fade can't run past the clip.
            fade = ""
            if fades and i < len(fades):
                dur = max(0.001, durations[i] if i < len(durations) else 0.0)
                fi = max(0.0, min(fades[i][0], dur))
                fo = max(0.0, min(fades[i][1], dur - fi))
                if fi > 0:
                    fade += ",fade=t=in:st=0:d=%.3f" % fi
                if fo > 0:
                    fade += ",fade=t=out:st=%.3f:d=%.3f" % (dur - fo, fo)

            filters.append(
                "[%d:v:0]yadif=deint=interlaced,"
                # Un-anamorphic first: resample by the sample aspect ratio to
                # square pixels at the true display width (UK SD is 544/720x576
                # stored but 16:9 on screen), so the fit below uses the real
                # picture shape instead of the stored pixel grid.
                "scale=trunc(iw*sar/2)*2:ih,setsar=1,"
                "scale=%d:%d:force_original_aspect_ratio=decrease,"
                "pad=%d:%d:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=%d,"
                "format=yuv420p%s[v%d]"
                % (i, width, height, width, height, fps, fade, i))
            # One audio chain per track, each brought to ITS OWN layout.
            for k in range(tracks):
                filters.append(
                    "[%d:a:%d]aresample=48000,"
                    "aformat=sample_fmts=fltp:channel_layouts=%s[a%d_%d]"
                    % (i, k, track_layouts[k], i, k))
            labels.append("[v%d]%s" % (
                i, "".join("[a%d_%d]" % (i, k) for k in range(tracks))))

        outs = "".join("[outa%d]" % k for k in range(tracks))
        filters.append("%sconcat=n=%d:v=1:a=%d[outv]%s"
                       % ("".join(labels), len(segments), tracks, outs))

        total = max(0.001, sum(durations))
        cmd = [
            "ffmpeg", "-hide_banner", "-nostats", "-y",
            *inputs,
            "-filter_complex", ";".join(filters),
            "-map", "[outv]",
        ]
        for k in range(tracks):
            cmd += ["-map", "[outa%d]" % k]
        cmd += [
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            # Keep the source bit depth; see media/pixfmt.py.
            "-pix_fmt", _joiner_pix_fmt(segments),
            "-c:a", "aac",
        ]
        # Per-track bitrate, and none at all where the source rate could not
        # be read: the encoder's own default scales with the channel count,
        # which is closer to right than any figure invented here.
        for k in range(tracks):
            if track_rates[k]:
                cmd += ["-b:a:%d" % k, "%dk" % (track_rates[k] // 1000)]
        cmd += ["-progress", "pipe:1", joined]
        self._run_with_progress(cmd, total, _REENCODING_JOIN)
        if not os.path.exists(joined):
            raise RuntimeError("Re-encoding the joined video failed.")
        if dvb_scenes:
            self._carry_subtitles(joined, segments, durations, tmpdir, sources)
        return joined

    def _carry_copy_join_subtitles(self, joined, segments, durations, tmpdir):
        """Give a COPY join the subtitles its scenes' sources carry.

        A copy join renders each scene to a transport stream and concatenates
        them.  A broadcast's DVB subtitles come through that untouched, but a
        disc's PGS subtitles cannot go in a transport stream at all, so every
        join of Blu-ray scenes that did not need re-encoding came out with no
        subtitles and nothing said - found joining four scenes of one Blu-ray
        rip (2026-10-09).  The re-encoded join has converted PGS to DVB from
        the source recording since 2.10.0; this sends a copy join down the
        same path whenever a scene's source has PGS, and names anything that
        still cannot be carried (a file's SubRip or ASS, say).
        """
        lost, sources = [], []
        for entry in self._entries[:len(segments)]:
            source = [] if entry.is_title else subtitle_kinds(entry.source)
            # Teletext and DVB survive the .ts pieces and the concat as they
            # are; PGS is converted below; anything else is lost.
            lost.append([x for x in source if x not in CARRIED_CODECS
                         and "teletext" not in x])
            sources.append((entry.source, entry.start)
                           if any(x in PGS_CODECS for x in source) else None)
        other_scenes = sum(1 for k in lost if k)
        if other_scenes:
            kinds = ", ".join(sorted({_SUBTITLE_NAMES.get(x, x)
                                      for k in lost for x in k}))
            logger.warning(
                "Joiner: %d of %d scene(s) have %s subtitles, which a joined "
                "video cannot carry; it does not have them.",
                other_scenes, len(segments), kinds)
            self._notes.append((
                QT_TRANSLATE_NOOP(
                    "ExportNotes", "some subtitles could not be carried through"),
                "%d of the %d scenes had %s subtitles, which a joined video "
                "cannot carry, so it does not have them. Exporting those "
                "scenes on their own to .mkv keeps them."
                % (other_scenes, len(segments), kinds),
            ))
        if any(sources):
            self._carry_subtitles(joined, segments, durations, tmpdir,
                                  sources)

    def _carry_subtitles(self, joined, segments, durations, tmpdir,
                         sources=None):
        """Add the scenes' DVB subtitles to the joined video, in place.

        A failure here must never cost the join itself: the picture and sound
        are done and good, so it is logged, reported, and the join goes on
        without subtitles - exactly what every re-encoded join did before.
        """
        self._check_cancel()
        self._report(self._last_percent,
                     QT_TRANSLATE_NOOP("ExportNotes", "Adding subtitles…"))
        with_subs = os.path.join(tmpdir, "joined-subtitles.ts")
        try:
            summary = carry_dvb_subtitles(joined, with_subs, segments,
                                          durations, sources)
        except Exception:
            logger.exception("Joiner: carrying the subtitles through failed; "
                             "the joined video is written without them.")
            self._notes.append((
                QT_TRANSLATE_NOOP(
                    "ExportNotes", "subtitles could not be carried through"),
                "The scenes had subtitles, but adding them to the re-encoded "
                "join failed, so the joined video was written without them. "
                "The log has the details.",
            ))
            return
        if not summary:
            return
        os.replace(with_subs, joined)
        if summary.get("converted"):
            self._notes.append((
                QT_TRANSLATE_NOOP(
                    "ExportNotes", "disc subtitles were converted"),
                "%d scene(s) came from a disc, whose subtitles cannot be "
                "carried into a joined broadcast video as they are, so they "
                "were converted to broadcast (DVB) subtitles - the words, "
                "colours and positions are unchanged."
                % summary["converted"],
            ))
        if summary["redrawn"]:
            self._notes.append((
                QT_TRANSLATE_NOOP(
                    "ExportNotes", "subtitles were redrawn to fit"),
                "%d scene(s) had subtitles drawn for a different picture "
                "size from the joined video, so they were redrawn to match "
                "it - the words and colours are unchanged. That keeps them "
                "showing in every player, including ones that cannot cope "
                "with subtitles changing size part-way through."
                % summary["redrawn"],
            ))

    def _run_with_progress(self, cmd, total_seconds, label):
        """Run an ffmpeg command that emits -progress, moving the bar via the
        out_time it reports.  The final slot of the overall bar (90-99%) tracks
        the encode."""
        # stderr to a temp file, never a pipe - see utils/proc.py.
        proc, err_file = popen_progress(cmd)
        try:
            for line in proc.stdout:
                if self._cancel:
                    proc.terminate()
                    break
                line = line.strip()
                if line.startswith("out_time_ms="):
                    try:
                        secs = int(line.split("=", 1)[1]) / 1_000_000.0
                        pct = min(99, int(100 * secs / total_seconds))
                        self._report(pct, label, stage="join")
                    except (ValueError, ZeroDivisionError):
                        pass
        finally:
            proc.wait()
        err_text = read_stderr(err_file)
        if self._cancel:
            raise _Cancelled()
        if proc.returncode != 0:
            err = (err_text or "").strip().splitlines()[-6:]
            raise RuntimeError(
                "Re-encoding the joined video failed.\n\n" + "\n".join(err))

    def _make_title(self, entry, idx, tmpdir, target):
        """Generate a title-card clip (text on a coloured background, silent
        audio) at the target format, returned as a .ts segment.

        Text is passed via textfile= so any characters (colons, quotes,
        percent signs) are safe without escaping.
        """
        width, height, fps = target
        duration = max(0.5, entry.duration)
        out = os.path.join(tmpdir, "title_%04d.ts" % idx)

        bg = _ffmpeg_colour(entry.bg_color, "0x000000")
        fg = _ffmpeg_colour(entry.text_color, "0xFFFFFF")
        font_bold = _find_font(bold=True)
        font = _find_font(bold=False)

        title_size = max(16, int(height * 0.075))
        sub_size = max(12, int(height * 0.040))
        has_sub = bool((entry.subtitle or "").strip())

        draws = []
        # Title text file.
        title_path = os.path.join(tmpdir, "title_%04d_main.txt" % idx)
        with open(title_path, "w", encoding="utf-8") as handle:
            handle.write(entry.text or "")
        title_y = "(h-text_h)/2-(h*0.06)" if has_sub else "(h-text_h)/2"
        draws.append(
            "drawtext=textfile=%s:fontfile=%s:fontcolor=%s:fontsize=%d:"
            "x=(w-text_w)/2:y=%s"
            % (title_path, font_bold, fg, title_size, title_y))

        if has_sub:
            sub_path = os.path.join(tmpdir, "title_%04d_sub.txt" % idx)
            with open(sub_path, "w", encoding="utf-8") as handle:
                handle.write(entry.subtitle or "")
            draws.append(
                "drawtext=textfile=%s:fontfile=%s:fontcolor=%s:fontsize=%d:"
                "x=(w-text_w)/2:y=(h-text_h)/2+(h*0.06)"
                % (sub_path, font, fg, sub_size))

        draws.append("format=yuv420p")

        # Background layer: a user-supplied image scaled onto the card's frame,
        # or (the default) a solid colour.  If the image path has gone missing
        # we quietly fall back to the colour rather than failing the render.
        bg_image = getattr(entry, "bg_image", "") or ""
        scaling = getattr(entry, "bg_scaling", "fill") or "fill"
        use_image = bool(bg_image) and os.path.exists(bg_image)

        if use_image:
            if scaling == "stretch":
                # Scale to the exact frame, ignoring aspect ratio (may distort).
                bg_filter = "scale=%d:%d,setsar=1" % (width, height)
            elif scaling == "fit":
                # Whole image visible, letterboxed with the background colour.
                bg_filter = (
                    "scale=%d:%d:force_original_aspect_ratio=decrease,"
                    "pad=%d:%d:(%d-iw)/2:(%d-ih)/2:color=%s,setsar=1"
                    % (width, height, width, height, width, height, bg))
            else:
                # "fill": cover the frame keeping aspect ratio, cropping overflow.
                bg_filter = (
                    "scale=%d:%d:force_original_aspect_ratio=increase,"
                    "crop=%d:%d,setsar=1" % (width, height, width, height))
            vf = ",".join([bg_filter] + draws)
            video_input = [
                "-loop", "1", "-framerate", "%d" % fps,
                "-t", "%.3f" % duration, "-i", bg_image,
            ]
        else:
            vf = ",".join(draws)
            video_input = [
                "-f", "lavfi",
                "-i", "color=c=%s:s=%dx%d:r=%d:d=%.3f"
                % (bg, width, height, fps, duration),
            ]

        cmd = [
            "ffmpeg", "-hide_banner", "-nostats", "-y",
            *video_input,
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-r", "%d" % fps,
            # A title card is generated, not decoded from anything, so there is
            # no source depth to preserve - 8-bit is right and universally safe.
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", "%.3f" % duration, out,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(out):
            tail = "\n".join((result.stderr or "").strip().splitlines()[-6:])
            raise RuntimeError("Building the title card failed.\n\n" + tail)
        return out

    def _apply_profile(self, joined_ts, base=90):
        """Apply a processing profile (HEVC / crop / aspect / AAC) to the
        joined stream in one whole-file pass, writing the final output.

        The joined .ts is indexed and handed to the very same exporter Save
        Video uses, with a single range covering the whole file, so the join
        honours the profile identically to a normal save.  ``base`` is where
        the overall progress bar stands as this stage begins; the exporter's
        own 0-100 is mapped onto the remaining span (this is the slow stage
        when the profile re-encodes, so it deserves the real range rather
        than a crawl through the last few percent).
        """
        p = self._profile
        index = build_index_sync(joined_ts)
        last = max(0, index.frame_count - 1)

        span = max(1, 99 - base)

        # The exporter reports phased progress, each phase counting 0-100 on
        # its own - and its "done" marker arrives *before* a trailing heavy
        # encode phase, so it can't be taken at face value.  For the joiner's
        # single overall bar each phase gets a weighted slice of the span
        # (the HEVC/crop encode dominates a profile pass; the stream-copy cut
        # and audio work are quick), the floor ratchets at each phase change,
        # and the emitted value never moves backwards.  run() emits the real
        # 100 when everything has finished.
        weights = {"copy": 0.10, "verify": 0.02, "graft_audio": 0.05,
                   "recode_audio": 0.15, "rebuild_audio": 0.15,
                   "encode": 0.75}
        state = {"phase": None, "floor": base, "ceil": base + span, "last": base}

        def _cb(data):
            if not isinstance(data, dict):
                return
            phase = data.get("phase") or ""
            if phase == "done":
                return                          # internal marker, not the end
            pct = data.get("percent", 0)
            if phase != state["phase"]:
                state["phase"] = phase
                state["floor"] = state["last"]
                width = int(span * weights.get(phase, 0.15))
                state["ceil"] = min(base + span, state["floor"] + max(1, width))
            if pct is None or pct < 0:
                value = state["last"]          # indeterminate pulse: hold
            else:
                pct = max(0, min(100, int(pct)))
                value = state["floor"] + (
                    (state["ceil"] - state["floor"]) * pct // 100)
            value = max(state["last"], min(99, value))
            state["last"] = value
            self._report(value, _APPLYING_PROFILE)

        export_ranges(
            joined_ts,
            self._out,
            [(0, last)],
            index,
            out_format=self._out_format,
            progress_cb=_cb,
            cancel_cb=lambda: self._cancel,
            audio_mode=getattr(p, "audio", "copy"),
            audio_bitrate=getattr(p, "audio_bitrate", 0),
            aspect=getattr(p, "aspect", "source"),
            crop_mode=getattr(p, "crop_mode", "none"),
            crop=getattr(p, "crop", (0, 0, 0, 0)),
            video_mode=getattr(p, "video", "copy"),
            encoder_preset=getattr(p, "preset", "faster"),
            encoder_crf=(p.effective_crf()
                         if hasattr(p, "effective_crf") else None),
            audio_sync_ms=getattr(p, "audio_sync_ms", 0),
            downmix=getattr(p, "downmix", "keep"),
            level_mode=getattr(p, "level_mode", "none"),
            level_value=getattr(p, "level_value", 0.0),
            encoder_gop_seconds=(p.effective_gop_seconds()
                                 if hasattr(p, "effective_gop_seconds")
                                 else None),
        )

    def _finalize(self, joined_ts, durations):
        """Write the joined .ts out in the requested format.

        This is a stage in its own right, with the whole bar, because for MP4
        it is a full re-encode and by far the longest part of the run.  It
        used to report a flat 99 before starting and then map its own progress
        onto 90-99, so it sat pinned at the top for minutes with nothing
        moving.

        cancel_cb is passed through.  Without it, Cancel during the MP4
        conversion did nothing at all: the dialog hid itself, the next
        progress update brought it back, and the encode ran to completion.
        """
        if self._out_format == "mkv":
            self._report(0, _WRITING_MKV, stage="finish")

            # Keyed on the exporter's phase, not a fixed token, so the rare
            # reference-decode pass restarts the bar instead of being clamped
            # flat at the top by the never-backwards rule.  Its label says so
            # too: a second bar with the same caption reads as a stall.
            labels = {
                "verify": QT_TRANSLATE_NOOP("ExportNotes", "Checking MKV audio…"),
                "verify_reference": QT_TRANSLATE_NOOP("ExportNotes", "Comparing against the source audio…"),
                "rebuild_audio": QT_TRANSLATE_NOOP("ExportNotes", "Rebuilding MKV audio…"),
            }

            def _mkv_cb(data):
                if not isinstance(data, dict):
                    return
                phase = data.get("phase") or "finalise_mkv"
                pct = data.get("percent", 0)
                if pct is None or pct < 0:
                    return                      # busy pulse, not a position
                self._report(pct, labels.get(phase, _WRITING_MKV),
                             stage="finish:%s" % phase)

            _write_mkv_chapters(
                joined_ts, self._out, durations,
                cancel_cb=lambda: self._cancel, progress_cb=_mkv_cb)
            self._check_cancel()
        elif self._out_format == "mp4":
            self._report(0, _CONVERTING_MP4, stage="finish")
            codec, interlaced = _probe_video(joined_ts)

            def _cb(data):
                pct = data.get("percent", 0) if isinstance(data, dict) else 0
                if pct is None or pct < 0:
                    return                      # busy pulse, not a position
                self._report(pct, _CONVERTING_MP4, stage="finish")

            _transcode_to_mp4(
                joined_ts, self._out, codec, interlaced,
                total_seconds=sum(durations), progress_cb=_cb,
                cancel_cb=lambda: self._cancel)
            self._check_cancel()
            # An .mp4 has no place for DVB subtitles or teletext.  The
            # exporter says so for an ordinary export; this conversion is the
            # joiner's own, and said nothing.
            subs = subtitle_kinds(joined_ts)
            if subs:
                kinds = ", ".join(sorted({_SUBTITLE_NAMES.get(x, x)
                                          for x in subs}))
                logger.warning(
                    "MP4 cannot carry the joined video's %s subtitle(s); "
                    "they are not in the output.", kinds)
                self._notes.append((
                    counted(len(subs), *_NOTE_SUBS_LOST),
                    "The joined video carries %s subtitles, which an .mp4 "
                    "file has no place for. Save it as .mkv or .ts instead "
                    "and they are kept." % kinds,
                ))
        else:
            # Match source (.ts) - the joined file is the output.
            shutil.move(joined_ts, self._out)


class JoinExportAdapter(QObject):
    """Makes a running join look like an editor export to whoever watches it.

    The export progress window and the Batch Manager's adopted-export rows
    both expect an export worker's signals: progress as a dictionary, a stats
    dictionary when finished, and a separate "cancelled".  The Joiner's worker
    reports a percentage and a line of text, the output path, and cancelling
    as a failure whose message is "Cancelled.".  This translates, so a join
    gets the same window as an export - Abort and Send to Batch included -
    and can be handed to the Batch Manager while it runs, exactly as an
    export can.  Nothing about the render itself changes.
    """
    progress = Signal(dict)
    finished_ok = Signal(dict)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.source_path = ""       # several sources; none to protect singly
        worker.progress.connect(self._on_progress)
        worker.finished_ok.connect(self._on_finished)
        worker.failed.connect(self._on_failed)

    def _on_progress(self, percent, label):
        self.progress.emit({"phase": "join", "percent": int(percent),
                            "label": label})

    def _on_finished(self, path):
        stats = dict(getattr(self.worker, "stats", None) or {})
        stats.setdefault("out_path", path)
        self.finished_ok.emit(stats)

    def _on_failed(self, message):
        if message == "Cancelled.":
            self.cancelled.emit()
        else:
            self.failed.emit(message)

    # The controller cancels and waits on an adopted worker.
    def cancel(self):
        self.worker.cancel()

    def wait(self, ms=None):
        return self.worker.wait(ms) if ms is not None else self.worker.wait()

    def isRunning(self):
        return self.worker.isRunning()

    def start(self):
        self.worker.start()
