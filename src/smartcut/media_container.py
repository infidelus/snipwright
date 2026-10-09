from dataclasses import dataclass, field
from fractions import Fraction
from typing import cast

import logging
import numpy as np

from smartcut.latm import LatmError, LatmRepacketiser
from smartcut.lazy_packets import LazyAudioPackets
from smartcut.open_options import LEGACY_OPEN_ARGS, SOURCE_OPEN_OPTIONS
from smartcut.rational import q
from av import AudioStream, Packet, VideoStream
from av import open as av_open
from av import time_base as AV_TIME_BASE
from av.container.input import InputContainer
from av.stream import Stream

from smartcut.nal_tools import (
    get_h264_nal_unit_type,
    get_h265_nal_unit_type,
    is_leading_picture_nal_type,
    is_rasl_nal_type,
    is_safe_h264_keyframe_nal,
    is_safe_h265_keyframe_nal,
)


# Stand-in decode time for a packet the demuxer gave no DTS at all.
#
# In practice only the opening packets of a file lack one: until enough
# pictures have been read to absorb the reorder delay, there is no decode time
# to report.  Matroska is the common case - the first two packets of an HEVC
# recording with B-pyramids typically arrive with pts set and dts None.
#
# The same value is recorded as a GOP's start DTS when its opening packet has
# none, so `gop_start_times_dts[i] == UNKNOWN_DTS` means "GOP i begins before
# any decode time is known" - which can only be the first GOP of the file.
# The cutter relies on that reading; see VideoCutter.fetch_frame.
UNKNOWN_DTS = -100_000_000


def ts_to_time(ts: float) -> Fraction:
    return Fraction(round(ts*1000), 1000)


def _note_latm_config(track, packet) -> None:
    """Record this packet's LATM configuration if it declares a new one.

    Called for every audio packet during the index walk, so it has to be
    cheap: eight bytes off a memoryview, three comparisons and a set lookup.
    A memoryview rather than bytes(packet) matters - copying every packet of
    a two-and-a-half-hour recording is the 175 MB of churn LazyAudioPackets
    exists to avoid.

    The useSameStreamMux short circuit is kept because the format allows it,
    but do not rely on it: measured on a Channel 4 HD recording, *every* one
    of 500,483 frames carried its own StreamMuxConfig and not one reused the
    previous.  What keeps the cost down is the prefix set, not that branch.

    Bytes 3..6 are bits 24-55: the object type, sampling frequency index,
    channel configuration and the structural flags.  The window stops there
    deliberately.  latmBufferFullness sits at bits 59-66 - inside the config
    but different on nearly every frame - so a wider window stops
    identifying the configuration and starts identifying the frame.  On the
    same recording, seven bytes gave 11 distinct prefixes on the main track
    and 103 on the audio description track, against a true count of 2 and 1;
    four bytes gives exactly 2 and 1, so the full parse runs twice per file
    instead of a hundred times.
    """
    try:
        head = bytes(memoryview(packet)[:8])
    except Exception:
        return
    if len(head) < 8 or head[0] != 0x56 or (head[1] & 0xE0) != 0xE0:
        return                                # not LOAS framing
    if head[3] & 0x80:                        # useSameStreamMux
        return
    prefix = head[3:7]
    try:
        sig = track.latm_prefixes[prefix]
    except KeyError:
        try:
            rep = LatmRepacketiser(bytes(packet))
            sig = (rep.object_type, rep.sample_rate, rep.channel_config)
        except LatmError:
            # Unparsable frames are skipped by the cutter too, so an
            # unreadable config is not evidence either way about the file
            # changing.  Remember it so the parse is not retried per frame.
            sig = None
        track.latm_prefixes[prefix] = sig
    if sig is None:
        return
    # Change points, not a set: which configuration applies to a given cut
    # cannot be answered by a set, and a file that returns to a configuration
    # it used earlier must record that as a further point.
    if not track.latm_config_points or track.latm_config_points[-1][1] != sig:
        track.latm_config_points.append((len(track.packet_pts) - 1, sig))


# channelConfiguration (ISO 14496-3 table 1.19) -> ffmpeg channel layout.
# 0 means "described elsewhere in the AOT-specific config", which this parser
# does not read, so it is deliberately absent and falls back to the old
# behaviour rather than guessing.
_CHANNEL_LAYOUTS = {
    1: "mono", 2: "stereo", 3: "3.0", 4: "4.0",
    5: "5.0", 6: "5.1", 7: "7.1",
}


def latm_configs_in_ranges(track, ranges):
    """Which LATM configurations the kept ranges actually contain.

    Returns (configs, packet_index): the distinct configurations present, in
    the order they first appear, and the index of a packet carrying the first
    of them - which is the packet the output stream should be described from.

    The output stream used to be built from track.packets[0] regardless.  On a
    Channel 4 HD film that is a stereo continuity packet from before the
    programme started, while 84% of the recording is 5.1, so the header
    described the wrong thing for almost the whole file.  Cutting the advert
    breaks out of such a recording leaves every kept range in one
    configuration, and it is that one the output must declare.

    `ranges` are on the source's own clock, as track.frame_times is.
    """
    points = getattr(track, "latm_config_points", None)
    if not points:
        return [], 0
    times = track.frame_times
    if times is None or len(times) == 0:
        return [sig for _, sig in points], points[0][0]

    configs = []
    first_index = None
    for i, (idx, sig) in enumerate(points):
        # A configuration runs from its own packet until the next change; the
        # first one also covers anything before it that the walk did not see.
        span_start = times[idx] if i else None
        span_end = times[points[i + 1][0]] if i + 1 < len(points) else None
        for (r_start, r_end) in ranges:
            if span_start is not None and span_start >= r_end:
                continue
            if span_end is not None and span_end <= r_start:
                continue
            if sig not in configs:
                configs.append(sig)
                if first_index is None:
                    first_index = idx
            break
    if first_index is None:
        # No range overlapped anything - fall back to the file's first.
        return [points[0][1]], points[0][0]
    return configs, first_index


def _multiply_array_by_fraction(args: tuple[np.ndarray, Fraction]) -> np.ndarray:
    """Helper for parallel Fraction array multiplication (must be at module level for pickling)."""
    arr, time_base = args
    return arr * time_base


@dataclass
class AudioTrack:
    media_container: "MediaContainer"
    av_stream: AudioStream
    path: str
    index: int

    packets: object = field(default_factory=lambda: [])
    # Timestamps gathered during the index pass; `packets` is built from these
    # once the file has been walked.
    packet_pts: list = field(default_factory=lambda: [])
    # Distinct LATM StreamMuxConfig signatures seen while walking the file.
    # Broadcast AAC can change configuration mid-programme - Channel 4 HD runs
    # continuity and advert breaks in stereo and the programme in 5.1 - and the
    # output stream is built from one packet, so a file with more than one
    # entry here cannot be described by a single container-level header.
    # Cached, because the walk that fills it is skipped on a cache hit.
    # Change points as (packet_index, (object_type, sample_rate,
    # channel_config)), so a cut can be asked which configurations IT spans
    # rather than only which the file contains.
    latm_config_points: list = field(default_factory=lambda: [])
    # Raw config-byte prefix -> parsed signature (or None if unparsable), so
    # the full parse runs once per distinct configuration rather than once per
    # config-carrying frame.  Not cached: a working set for the walk, not a
    # result of it.
    latm_prefixes: dict = field(default_factory=lambda: {})
    frame_times_pts: np.ndarray = field(default_factory = lambda: np.empty(()))
    frame_times: np.ndarray = field(default_factory = lambda: np.empty(()))

class MediaContainer:
    av_container: InputContainer
    video_stream: VideoStream | None
    path: str

    video_frame_times_pts: np.ndarray
    video_frame_times: np.ndarray
    video_keyframe_indices: list[int]
    gop_start_times_pts_s: list[int] # Smallest pts in a GOP, in seconds

    gop_start_times_dts: list[int]
    gop_end_times_dts: list[int]
    gop_start_nal_types: list[int | None]  # NAL type of first picture frame after each GOP boundary
    gop_leading_end_dts: list[int | None]  # DTS of first non-leading picture in GOP (None if no leading pics)
    gop_has_rasl: list[bool]  # True if GOP has RASL frames (need priming/hybrid recode)

    audio_tracks: list[AudioTrack]
    subtitle_tracks: list

    duration: Fraction
    start_time: Fraction

    def __init__(self, path: str) -> None:
        self.path = path

        frame_pts = []
        self.video_keyframe_indices = []

        self.av_container = av_container = av_open(
            path, 'r', options=SOURCE_OPEN_OPTIONS, **LEGACY_OPEN_ARGS)

        self.chat_url = None
        self.chat_history = None
        self.chat_visualize = True
        self.start_time = Fraction(av_container.start_time, AV_TIME_BASE) if av_container.start_time is not None else Fraction(0)
        manual_duration_calc = av_container.duration is None
        self.duration = Fraction(av_container.duration , AV_TIME_BASE) if av_container.duration is not None else Fraction(0)

        is_h264 = False
        is_h265 = False

        streams: list[Stream]

        if len(av_container.streams.video) == 0:
            self.video_stream = None
            streams = [*av_container.streams.audio]
        else:
            self.video_stream = av_container.streams.video[0]
            self.video_stream.thread_type = "FRAME"
            streams = [self.video_stream, *av_container.streams.audio]

            if self.video_stream.codec_context.name == 'hevc':
                is_h265 = True
            if self.video_stream.codec_context.name == 'h264':
                is_h264 = True

        self.audio_tracks = []
        stream_index_to_audio_track = {}
        for i, audio_stream in enumerate(av_container.streams.audio):
            if q(audio_stream.time_base) is None:
                continue
            audio_stream.codec_context.thread_type = "FRAME"
            track = AudioTrack(self, audio_stream, path, i)
            self.audio_tracks.append(track)
            stream_index_to_audio_track[audio_stream.index] = track

        self.subtitle_tracks = []
        stream_index_to_subtitle_track = {}
        for i, s in enumerate(av_container.streams.subtitles):
            streams.append(s)
            stream_index_to_subtitle_track[s.index] = i
            self.subtitle_tracks.append([])

        first_keyframe = True  # Always allow the first keyframe regardless of NAL type

        # Track max packet end PTS per stream (integer domain) for manual duration calc
        # Converting to Fraction once at end is much faster than per-packet Fraction math
        max_end_pts_by_stream: dict[int, int] = {}

        self.gop_start_times_dts = []
        self.gop_end_times_dts = []
        self.gop_start_nal_types = []
        self.gop_leading_end_dts = []
        self.gop_has_rasl = []
        last_seen_video_dts = None
        # Track leading pictures in current CRA GOP
        tracking_leading_in_cra = False
        current_gop_has_leading = False
        current_gop_has_rasl = False

        # A cached index means the file has been walked before and has not
        # changed since.  Walking it again reads every packet - three and a
        # half minutes for a Blu-ray on a network share - to arrive at exactly
        # the same numbers.
        self._from_cache = False
        try:
            from smartcut import index_cache
            if index_cache.load(self, path):
                self._from_cache = True
        except Exception:
            logging.getLogger("snipwright").debug(
                "Cached smartcut index unavailable", exc_info=True)

        if self._from_cache:
            # Walking the file is what teaches ffmpeg the parameters of a
            # stream whose container header does not declare them - some
            # broadcast audio-description tracks report 0 channels at 0 Hz
            # until packets have actually been parsed.  Skipping the walk
            # leaves those streams unknown, and an output stream copied from
            # such a template is rejected by the muxer: avformat_write_header
            # returns EINVAL and the export falls back to primary audio only,
            # silently losing the track.
            #
            # It only bites on the *second* export of a file, because the
            # first one populates the cache that the next one then loads -
            # which is why exporting to .ts worked and the .mkv straight after
            # it did not.
            #
            # It must read a FEW packets, not one.  FFmpeg fills in the
            # stream's own parameters - what an output stream is copied from -
            # on the SECOND packet of the track; decoding the first fills in
            # only the decoder's.  This used to stop after the first decoded
            # frame, so it never fixed the template: a 5USA recording's sparse
            # MP2 audio-description track (2026-10-04) still copied as 0 Hz /
            # 0 channels, and every export after the first lost the track,
            # .ts included.  Measured: the copy carries 48 kHz mono after two
            # packets, by demuxing alone or with decoding.  WARM_PACKETS is
            # a wide margin; the packets are a few hundred bytes each, and
            # this runs only on a cached load, only for a track the header
            # does not describe.
            WARM_PACKETS = 25
            for track in self.audio_tracks:
                stream = track.av_stream
                cc = stream.codec_context
                if getattr(cc, "sample_rate", 0) and getattr(cc, "channels", 0):
                    continue
                try:
                    seen = 0
                    for packet in av_container.demux(stream):
                        seen += 1
                        try:
                            for _frame in packet.decode():
                                break
                        except Exception:
                            pass          # one bad packet does not end it
                        if seen >= WARM_PACKETS:
                            break
                except Exception:
                    logging.getLogger("snipwright").debug(
                        "Could not determine parameters for audio stream %s",
                        getattr(stream, "index", "?"), exc_info=True)
                finally:
                    # The demux above consumed part of the file; rewind so the
                    # cut that follows starts from the beginning as usual.
                    try:
                        av_container.seek(0)
                    except Exception:
                        pass

        for packet in () if self._from_cache else av_container.demux(streams):
            if packet.pts is None:
                continue

            if manual_duration_calc and (packet.pts is not None and packet.duration is not None):
                stream_idx = packet.stream_index
                end_pts = packet.pts + packet.duration
                if stream_idx not in max_end_pts_by_stream or end_pts > max_end_pts_by_stream[stream_idx]:
                    max_end_pts_by_stream[stream_idx] = end_pts
            if packet.stream.type == 'video' and self.video_stream:

                if packet.is_keyframe:
                    nal_type = None
                    if is_h265:
                        nal_type = get_h265_nal_unit_type(bytes(packet))
                    elif is_h264:
                        nal_type = get_h264_nal_unit_type(bytes(packet))

                    # Always allow the first keyframe regardless of NAL type (may be SEI, parameter sets, etc.)
                    is_safe_keyframe = True
                    if first_keyframe:
                        first_keyframe = False  # Only apply to the very first keyframe
                    # Use centralized helper functions for NAL type safety checks
                    elif is_h265:
                        is_safe_keyframe = is_safe_h265_keyframe_nal(nal_type)
                    elif is_h264:
                        is_safe_keyframe = is_safe_h264_keyframe_nal(nal_type)
                    if is_safe_keyframe:
                        # Finalize previous GOP's leading picture tracking
                        if tracking_leading_in_cra:
                            # Previous GOP was CRA but we never found non-leading picture
                            # This means all frames after CRA were leading (unusual but possible)
                            self.gop_leading_end_dts.append(None if not current_gop_has_leading else last_seen_video_dts)
                            self.gop_has_rasl.append(current_gop_has_rasl)

                        self.video_keyframe_indices.append(len(frame_pts))
                        dts = packet.dts if packet.dts is not None else UNKNOWN_DTS
                        first_gop = not self.gop_start_times_dts
                        self.gop_start_times_dts.append(dts)
                        self.gop_start_nal_types.append(nal_type)

                        # Each keyframe closes the GOP before it.  Only if
                        # there was one: a recording that begins part-way
                        # through a GOP - which is normal off a tuner, and
                        # what any byte-copied excerpt of one looks like - has
                        # video packets before its first keyframe, and those
                        # belong to no GOP at all.
                        #
                        # Recording an end for them shifted the whole array by
                        # one, so gop_end_times_dts[i] held the end of the
                        # packets *preceding* GOP i.  Every GOP then ran from
                        # its start to a DTS 1800 ticks earlier, no packet
                        # could fall inside one, and the cut produced a file
                        # with a video stream and no video packets in it -
                        # reported as "Export produced no readable video".
                        # Running Quick Stream Fix appeared to be the cure
                        # because the repaired copy starts on a keyframe.
                        if last_seen_video_dts is not None and not first_gop:
                            self.gop_end_times_dts.append(last_seen_video_dts)

                        # Start tracking leading pictures if this is a CRA GOP
                        if is_h265 and nal_type == 21:  # CRA frame
                            tracking_leading_in_cra = True
                            current_gop_has_leading = False
                            current_gop_has_rasl = False
                        else:
                            # Not a CRA, no leading pictures to track
                            tracking_leading_in_cra = False
                            current_gop_has_leading = False
                            current_gop_has_rasl = False
                            self.gop_leading_end_dts.append(None)
                            self.gop_has_rasl.append(False)

                elif tracking_leading_in_cra and is_h265:
                    # Check if this non-keyframe packet is a leading picture
                    packet_nal_type = get_h265_nal_unit_type(bytes(packet))
                    if is_leading_picture_nal_type(packet_nal_type):
                        current_gop_has_leading = True
                        if is_rasl_nal_type(packet_nal_type):
                            current_gop_has_rasl = True
                    else:
                        # Found first non-leading picture
                        if current_gop_has_leading:
                            # Record boundary only if there were actual leading pictures
                            dts = packet.dts if packet.dts is not None else UNKNOWN_DTS
                            self.gop_leading_end_dts.append(dts)
                        else:
                            # No leading pictures in this CRA GOP
                            self.gop_leading_end_dts.append(None)
                        self.gop_has_rasl.append(current_gop_has_rasl)
                        tracking_leading_in_cra = False

                # Use PTS as fallback when DTS is None (common in exported segments)
                last_seen_video_dts = packet.dts if packet.dts is not None else packet.pts
                frame_pts.append(packet.pts)
            elif packet.stream.type == 'audio':
                track = stream_index_to_audio_track[packet.stream_index]
                track.last_packet = packet

                # Record only the timestamp, not the packet.  Keeping every
                # packet here held the entire compressed audio in RAM - about
                # 250 MB per track on a Blu-ray, and six tracks is most of a
                # 15 GB working set.  The cutter needs random access to the
                # packets, but it can have that lazily; see LazyAudioPackets.
                track.packet_pts.append(packet.pts)
                _note_latm_config(track, packet)
            elif packet.stream.type == 'subtitle':
                self.subtitle_tracks[stream_index_to_subtitle_track[packet.stream_index]].append(packet)

        # Finalize manual duration calculation - convert from PTS to Fraction once
        if manual_duration_calc and max_end_pts_by_stream:
            for stream_idx, max_pts in max_end_pts_by_stream.items():
                stream = av_container.streams[stream_idx]
                if q(stream.time_base) is None:
                    continue
                stream_duration = Fraction(max_pts) * stream.time_base
                if stream_duration > self.duration:
                    self.duration = stream_duration

        if self.video_stream is not None and not self._from_cache:
            # Finalize last GOP's leading picture tracking if still active
            if tracking_leading_in_cra:
                self.gop_leading_end_dts.append(None if not current_gop_has_leading else last_seen_video_dts)
                self.gop_has_rasl.append(current_gop_has_rasl)
            # Ensure gop_end_times_dts has the same length as gop_start_times_dts.
            # This is needed because make_cut_segments uses zip() which truncates to
            # shortest length. When all packets have dts=None (can happen in short
            # exported segments), last_seen_video_dts stays None, so we use the
            # same sentinel value used for gop_start_times_dts when DTS is missing.
            if len(self.gop_end_times_dts) < len(self.gop_start_times_dts):
                fallback_dts = last_seen_video_dts if last_seen_video_dts is not None else UNKNOWN_DTS
                self.gop_end_times_dts.append(fallback_dts)
            assert len(self.gop_start_times_dts) == len(self.gop_end_times_dts), \
                f"GOP DTS array length mismatch: start={len(self.gop_start_times_dts)}, end={len(self.gop_end_times_dts)}"
            frame_pts_sorted = np.sort(np.array(frame_pts))
            self.video_frame_times_pts = frame_pts_sorted

        # Collect PTS arrays for audio tracks, and give each track a lazy view
        # over its packets rather than the packets themselves.
        for t in self.audio_tracks:
            if not self._from_cache:
                t.frame_times_pts = np.array(t.packet_pts)
            try:
                t.packets = LazyAudioPackets(
                    # On a cache hit packet_pts is empty - the count comes from
                    # the cached timestamp array instead.
                    self.path, t.av_stream.index, len(t.frame_times_pts)
                )
            except Exception:
                # If anything about the lazy reader does not suit this file,
                # fall back to an empty list rather than failing the cut: the
                # audio cutter treats an empty packet list as "nothing to
                # copy", which is wrong but survivable, and the log will say.
                logging.getLogger("snipwright").exception(
                    "Lazy audio reader unavailable for stream %s",
                    getattr(t.av_stream, "index", "?"))
                t.packets = []
            # The pts list has served its purpose; the numpy array replaces it.
            t.packet_pts = []

        # Parallelize Fraction array multiplication (expensive due to per-element
        # Fraction creation).  Runs whether the index came from the cache or from
        # walking the file: these arrays are derived, and recomputing them is
        # cheaper than storing arrays of Fraction objects.
        from concurrent.futures import ThreadPoolExecutor
        tasks: list[tuple[np.ndarray, Fraction]] = []

        # Run for a cached index too: frame_times is derived from the pts array
        # and the time base, and recomputing it costs a fraction of a second -
        # far less than the space storing an array of Fractions would take.
        if self.video_stream is not None and q(self.video_stream.time_base) is not None:
            tasks.append((self.video_frame_times_pts, q(self.video_stream.time_base)))
        for t in self.audio_tracks:
            if q(t.av_stream.time_base) is not None:
                tasks.append((t.frame_times_pts, q(t.av_stream.time_base)))

        if tasks:
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(_multiply_array_by_fraction, tasks))

            result_idx = 0
            if self.video_stream is not None and q(self.video_stream.time_base) is not None:
                self.video_frame_times = results[result_idx]
                self.gop_start_times_pts_s = list(self.video_frame_times[self.video_keyframe_indices])
                result_idx += 1
            for t in self.audio_tracks:
                if q(t.av_stream.time_base) is not None:
                    t.frame_times = results[result_idx]
                    result_idx += 1

        # Store what the walk produced, so the next export of this file skips
        # it.  Only when it was actually computed - re-saving a cache hit would
        # just rewrite the same file.
        if not self._from_cache:
            try:
                from smartcut import index_cache
                index_cache.save(self, path)
            except Exception:
                logging.getLogger("snipwright").debug(
                    "Couldn't cache the smartcut index", exc_info=True)

    def close(self) -> None:
        self.av_container.close()

    def get_next_frame_time(self, t: Fraction) -> Fraction:
        assert self.video_stream is not None
        t += self.start_time
        # Convert to PTS for searching
        t_pts = round(t / cast(Fraction, q(self.video_stream.time_base)))
        idx = np.searchsorted(self.video_frame_times_pts, t_pts)
        if idx == len(self.video_frame_times_pts):
            return self.duration
        elif idx == 0:
            return self.video_frame_times[0] - self.start_time
        # Otherwise, find the closest of the two possible candidates: arr[idx-1] and arr[idx]
        else:
            prev_val = self.video_frame_times[idx - 1]
            next_val = self.video_frame_times[idx]
            if t - prev_val <= next_val - t:
                return prev_val - self.start_time
            else:
                return next_val - self.start_time

    def get_frame_time_at_or_before(self, t: Fraction) -> Fraction:
        """Get frame time at or before the given time (snap down).

        For video files: uses video frame times.
        For audio-only files: uses first audio track's frame times.

        Args:
            t: Time in seconds (relative to start_time=0)

        Returns:
            Frame time at or before t, or 0 if t is before first frame.
        """
        t_absolute = t + self.start_time

        if self.video_stream is not None:
            frame_times = self.video_frame_times
            frame_times_pts = self.video_frame_times_pts
            time_base = cast(Fraction, q(self.video_stream.time_base))
        elif self.audio_tracks:
            track = self.audio_tracks[0]
            frame_times = track.frame_times
            frame_times_pts = track.frame_times_pts
            time_base = cast(Fraction, q(track.av_stream.time_base))
        else:
            return t  # No frames to snap to

        t_pts = round(t_absolute / time_base)
        # side='right' ensures we get index after t if t is exactly on a frame boundary
        idx = int(np.searchsorted(frame_times_pts, t_pts, side='right')) - 1
        idx = max(0, idx)
        return frame_times[idx] - self.start_time

    def get_frame_time_at_or_after(self, t: Fraction) -> Fraction:
        """Get frame time at or after the given time (snap up).

        For video files: uses video frame times.
        For audio-only files: uses first audio track's frame times.

        Args:
            t: Time in seconds (relative to start_time=0)

        Returns:
            Frame time at or after t, or duration if t is past last frame.
        """
        t_absolute = t + self.start_time

        if self.video_stream is not None:
            frame_times = self.video_frame_times
            frame_times_pts = self.video_frame_times_pts
            time_base = cast(Fraction, q(self.video_stream.time_base))
        elif self.audio_tracks:
            track = self.audio_tracks[0]
            frame_times = track.frame_times
            frame_times_pts = track.frame_times_pts
            time_base = cast(Fraction, q(track.av_stream.time_base))
        else:
            return t  # No frames to snap to

        t_pts = round(t_absolute / time_base)
        # side='left' ensures we get index of frame at or after t
        idx = int(np.searchsorted(frame_times_pts, t_pts, side='left'))
        if idx >= len(frame_times):
            return self.duration
        return frame_times[idx] - self.start_time
