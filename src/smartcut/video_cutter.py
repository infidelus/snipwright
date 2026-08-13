import heapq
from collections.abc import Generator
from dataclasses import dataclass
from fractions import Fraction
from typing import cast

import av
import av.bitstream
from av import VideoCodecContext, VideoStream
from av.codec.context import CodecContext
from av.container.input import InputContainer
from av.container.output import OutputContainer
from av.packet import Packet
from av.stream import Disposition
from av.video.frame import PictureType, VideoFrame

from smartcut.media_container import UNKNOWN_DTS, MediaContainer
from smartcut.media_utils import VideoExportMode, VideoExportQuality, get_crf_for_quality
from smartcut.misc_data import CutSegment
from smartcut.nal_tools import get_h265_nal_unit_type, is_leading_picture_nal_type
from smartcut.poc_rewrite import HevcPocRewriter


@dataclass
class FrameHeapItem:
    """Wrapper for frames in the heap, sorted by PTS"""
    pts: int | None
    frame: VideoFrame

    def __lt__(self, other: 'FrameHeapItem') -> bool:
        # Handle None PTS values by treating them as -1 (earliest)
        self_pts = self.pts if self.pts is not None else -1
        other_pts = other.pts if other.pts is not None else -1
        return self_pts < other_pts

def is_annexb(packet: Packet | bytes | None) -> bool:
        if packet is None:
            return False
        data = bytes(packet)
        return data[:3] == b'\0\0\x01' or data[:4] == b'\0\0\0\x01'

def copy_packet(p: Packet) -> Packet:
    # return p
    packet = Packet(bytes(p))
    packet.pts = p.pts
    packet.dts = p.dts
    packet.duration = p.duration
    # packet.pos = p.pos
    packet.time_base = p.time_base
    packet.stream = p.stream
    packet.is_keyframe = p.is_keyframe
    for side_data in p.iter_sidedata():
        packet.set_sidedata(side_data)
    # packet.is_discard = p.is_discard

    return packet


@dataclass
class VideoSettings:
    mode: VideoExportMode
    quality: VideoExportQuality
    codec_override: str = 'copy'
    # Whether the source stream is interlaced (e.g. 1080i MBAFF, 576i MPEG-2).
    # True: open boundary encoders in interlaced mode - MBAFF codes any
    # progressive stretches as frame macroblocks, so mixed content is handled
    # correctly.  False: never.  None: decide from the first recoded frame.
    source_interlaced: bool | None = None


@dataclass
class VideoStreamSetup:
    """Result of creating a video output stream, used to initialize VideoCutter."""
    out_stream: VideoStream
    codec_name: str
    is_full_recode: bool  # True if VideoExportMode.RECODE with codec override


def create_video_output_stream(
    media_container: MediaContainer,
    output_av_container: OutputContainer,
    video_settings: VideoSettings,
) -> VideoStreamSetup:
    """
    Create output video stream from source media container.

    Separated from VideoCutter to allow reuse in joining operations where
    multiple input files write to the same output stream.
    """
    in_stream = cast(VideoStream, media_container.video_stream)
    assert in_stream.time_base is not None, "Video stream must have a time_base"

    if video_settings.mode == VideoExportMode.RECODE and video_settings.codec_override != 'copy':
        # Full recode mode with explicit codec
        out_stream = cast(VideoStream, output_av_container.add_stream(
            video_settings.codec_override,
            rate=in_stream.guessed_rate,
            options={'x265-params': 'log_level=error'}
        ))
        out_stream.width = in_stream.width
        out_stream.height = in_stream.height
        if in_stream.sample_aspect_ratio is not None:
            out_stream.sample_aspect_ratio = in_stream.sample_aspect_ratio
        out_stream.metadata.update(in_stream.metadata)
        out_stream.disposition = cast(Disposition, in_stream.disposition.value)
        out_stream.time_base = in_stream.time_base
        codec_name = video_settings.codec_override
        is_full_recode = True
    else:
        # Smartcut/copy mode - preserve codec from input
        original_codec_name = in_stream.codec_context.name

        codec_mapping = {
            'libdav1d': 'libaom-av1',  # AV1 decoder to encoder
        }
        mapped_codec_name = codec_mapping.get(original_codec_name, original_codec_name)

        if mapped_codec_name != original_codec_name:
            # Need to create stream with mapped codec name
            out_stream = cast(VideoStream, output_av_container.add_stream(
                mapped_codec_name,
                rate=in_stream.guessed_rate
            ))
            out_stream.width = in_stream.width
            out_stream.height = in_stream.height
            if in_stream.sample_aspect_ratio is not None:
                out_stream.sample_aspect_ratio = in_stream.sample_aspect_ratio
            out_stream.metadata.update(in_stream.metadata)
            out_stream.disposition = cast(Disposition, in_stream.disposition.value)
            out_stream.time_base = in_stream.time_base
            codec_name = mapped_codec_name
        else:
            # Copy the stream if no mapping needed
            out_stream = output_av_container.add_stream_from_template(
                in_stream,
                options={'x265-params': 'log_level=error'}
            )
            out_stream.metadata.update(in_stream.metadata)
            out_stream.disposition = cast(Disposition, in_stream.disposition.value)
            out_stream.time_base = in_stream.time_base
            codec_name = original_codec_name

        is_full_recode = False

    # Note: Codec tag normalization is done in VideoCutter.__init__ after bitstream filter setup

    assert out_stream.time_base is not None, "Output stream must have a time_base"

    return VideoStreamSetup(
        out_stream=out_stream,
        codec_name=codec_name,
        is_full_recode=is_full_recode,
    )


def _normalize_output_codec_tag(
    out_stream: VideoStream,
    output_av_container: OutputContainer,
    in_stream: VideoStream,
) -> None:
    """Ensure codec tags are compatible with output container format."""
    container_name = output_av_container.format.name.lower() if output_av_container.format.name else ''
    out_codec_ctx = cast(CodecContext, out_stream.codec_context)
    in_codec_ctx = in_stream.codec_context
    in_codec_name = in_codec_ctx.name

    is_mp4_mov_mkv = any(name in container_name for name in ('mp4', 'mov', 'matroska', 'webm'))
    is_mp4_or_mov = any(name in container_name for name in ('mp4', 'mov'))

    # Normalize MPEG-TS codec tags for MP4/MOV/MKV containers
    # Check INPUT stream's codec_tag since output may not have been populated yet
    if is_mp4_mov_mkv and in_codec_name == 'h264' and _is_mpegts_h264_tag(in_codec_ctx.codec_tag):
        out_codec_ctx.codec_tag = 'avc1'

    # For HEVC in MP4/MOV: use hev1 to keep VPS/SPS/PPS inline
    if is_mp4_or_mov and in_codec_name in ('hevc', 'h265'):
        out_codec_ctx.codec_tag = 'hev1'
    elif is_mp4_mov_mkv and in_codec_name in ('hevc', 'h265') and _is_mpegts_hevc_tag(in_codec_ctx.codec_tag):
        out_codec_ctx.codec_tag = 'hvc1'


def _apply_source_colour(enc_codec, src_codec_ctx) -> None:
    """Carry the source's colour description onto an encoder.

    Without this the frames re-encoded at each cut are written with their
    colour unspecified while the rest of the stream declares BT.2020/PQ -
    measured on one 10-bit HDR10 cut as 199 frames tagged and 78 tagged
    nothing - and an HDR display shows a flash at every join.

    Setting it also makes x265 reproduce the source's SPS byte for byte,
    which is what smartcut's extradata matching is reaching for anyway.  That
    is why this cannot ship on its own: two differing SPS were making a
    decoder re-initialise at every segment switch, and that was hiding a POC
    collision between spliced segments.  See smartcut.poc_rewrite.
    """
    if src_codec_ctx is None:
        return
    for attr in ('color_primaries', 'color_trc', 'colorspace', 'color_range'):
        try:
            value = getattr(src_codec_ctx, attr)
        except Exception:
            continue
        if value is None:
            continue
        try:
            setattr(enc_codec, attr, value)
        except Exception:
            # An encoder that will not accept one of these is no worse off
            # than before; the others are still worth setting.
            pass


def _is_mpegts_h264_tag(codec_tag: str) -> bool:
    """Check if codec tag is MPEG-TS style H.264 tag."""
    return codec_tag == '\x1b\x00\x00\x00'


def _is_mpegts_hevc_tag(codec_tag: str) -> bool:
    """Check if codec tag is MPEG-TS style HEVC tag."""
    return codec_tag in ('HEVC', '\x24\x00\x00\x00')


class VideoCutter:
    def __init__(
        self,
        media_container: MediaContainer,
        stream_setup: VideoStreamSetup,
        output_av_container: OutputContainer,
        video_settings: VideoSettings,
        log_level: str | None,
        initial_position: Fraction = Fraction(0),
        initial_last_dts: int = UNKNOWN_DTS,
    ) -> None:
        self.media_container = media_container
        self.log_level = log_level
        self.encoder_inited = False
        self.video_settings = video_settings

        self.enc_codec = None
        # Set once, from the first frame handed to the boundary encoder: if
        # the source is interlaced the encoder must be opened in interlaced
        # mode (see _configure_interlace).
        self._interlace_done = False

        self.in_stream = cast(VideoStream, media_container.video_stream)
        # Assert time_base is not None once at initialization
        assert self.in_stream.time_base is not None, "Video stream must have a time_base"
        self.in_time_base: Fraction = self.in_stream.time_base

        # Open another container because seeking to beginning of the file is unreliable...
        self.input_av_container: InputContainer = av.open(media_container.path, 'r', metadata_errors='ignore')

        self.demux_iter = self.input_av_container.demux(self.in_stream)
        self.demux_saved_packet = None

        # Frame buffering for fetch_frame (using heap for efficient PTS ordering)
        self.frame_buffer: list[FrameHeapItem] = []
        self.frame_buffer_gop_dts = -1
        self.decoder = self.in_stream.codec_context
        # Decode boundary GOPs on one thread.  This used to use every core
        # (thread_type FRAME, thread_count = cpu_count), and that made exports
        # unreproducible: the same project exported twice gave files whose
        # re-encoded segments differed, while every copied segment was
        # identical.
        #
        # Frame-threaded H.264 decoding of this recording's field-coded
        # pictures does not return the same pixels every time when the machine
        # is busy.  Measured on a Channel 4 HD recording with the application
        # playing in the background: 10 of 686 frames handed to the boundary
        # encoder decoded differently across five exports, every one of them
        # a field-coded picture, and no progressive frame ever varied.  One
        # such frame is enough to change every packet to the end of its
        # re-encoded run - a single bad frame moved 125 of them - because the
        # encoder's references change with it.
        #
        # It only shows under load, which is why it was once wrongly ruled out:
        # an idle machine decodes the same file the same way for run after run,
        # so a test that does not load the machine passes whatever the thread
        # count is.
        #
        # The cost is small and bounded.  Only the GOPs at cut points are
        # decoded at all - 833 frames for a five-minute recording with six
        # re-encoded segments, around 6% of export time - so this is a few
        # seconds, not a proportional slowdown.  Playback and indexing are
        # unaffected; they are decoded elsewhere and do not reach the output.
        try:
            self.decoder.thread_type = "FRAME"
            self.decoder.thread_count = 1
        except Exception:
            pass

        # Use pre-created output stream from stream_setup
        self.out_stream = stream_setup.out_stream
        self.codec_name = stream_setup.codec_name

        if stream_setup.is_full_recode:
            # Full recode mode - initialize encoder immediately
            self.init_encoder()
            self.enc_codec = self.out_stream.codec_context
            self.enc_codec.options.update(self.encoding_options)
            self.enc_codec.time_base = self.in_time_base
            self.enc_codec.thread_type = "FRAME"
            self.enc_last_pts = -1
        else:
            # Smartcut mode - set up bitstream filter for remuxing
            self.remux_bitstream_filter = av.bitstream.BitStreamFilterContext('null', self.in_stream, self.out_stream)
            if self.in_stream.codec_context.name == 'h264' and not is_annexb(self.in_stream.codec_context.extradata):
                self.remux_bitstream_filter = av.bitstream.BitStreamFilterContext('h264_mp4toannexb', self.in_stream, self.out_stream)
            elif self.in_stream.codec_context.name == 'hevc' and not is_annexb(self.in_stream.codec_context.extradata):
                self.remux_bitstream_filter = av.bitstream.BitStreamFilterContext('hevc_mp4toannexb', self.in_stream, self.out_stream)
            # MPEG-4 Visual family: optional filters for robustness (ASF/AVI tend to need this)
            elif self.in_stream.codec_context.name in {'mpeg4', 'msmpeg4v3', 'msmpeg4v2', 'msmpeg4v1'}:
                self.remux_bitstream_filter = av.bitstream.BitStreamFilterContext('dump_extra', self.in_stream, self.out_stream)

        # Normalize codec tags for container compatibility (must be done after bitstream filter setup)
        _normalize_output_codec_tag(self.out_stream, output_av_container, self.in_stream)

        # Assert out_stream time_base is not None once at initialization
        assert self.out_stream.time_base is not None, "Output stream must have a time_base"
        self.out_time_base: Fraction = self.out_stream.time_base

        # Track typical frame duration for fixing missing/zero durations
        # MP4 muxer uses duration to calculate edit list boundaries, so
        # packets without proper duration cause last-frame discard issues
        self.typical_frame_duration: int | None = None

        # Output position state - can be set for joining multiple files
        self.last_dts = initial_last_dts
        self.segment_start_in_output = initial_position

        # Track stream continuity for hybrid CRA recoding
        self.last_remuxed_segment_gop_index = None
        self.is_first_remuxed_segment = True
        # Track decoder continuity between GOPs: last GOP end DTS consumed
        self._last_fetch_end_dts: int | None = None

        # Renumber picture order counts across splices.  Copied packets carry
        # the source's own POCs, which collide once segments from different
        # points in the source are put next to each other - see
        # smartcut.poc_rewrite.  Only HEVC: H.264 numbers pictures by a
        # different scheme entirely and is not touched here.
        self._poc = (HevcPocRewriter() if self.codec_name == 'hevc'
                     and not stream_setup.is_full_recode else None)
        self._poc_run = 0
        self._poc_enc_run = 0

    def init_encoder(self) -> None:
        self.encoder_inited = True
        # v_codec = self.in_stream.codec_context
        profile = self.out_stream.codec_context.profile

        codec_name = self.codec_name or ''
        if 'av1' in codec_name:
            self.codec_name = 'av1'
            profile = None
        if self.codec_name == 'vp9':
            if profile is not None:
                profile = profile[-1:]
                if int(profile) > 1:
                    raise ValueError("VP9 Profile 2 and Profile 3 are not supported by the encoder. Please select cutting on keyframes mode.")
        elif profile is not None:
            if 'Baseline' in profile:
                profile = 'baseline'
            elif 'High 4:4:4' in profile:
                profile = 'high444'
            elif 'Rext' in profile or 'Simple' in profile: # This is some sort of h265 extension. This might be the source of some issues I've had?
                profile = None
            else:
                profile = profile.lower().replace(':', '').replace(' ', '')

        # Get CRF value for quality setting
        crf_value = get_crf_for_quality(self.video_settings.quality)

        # Adjust CRF for newer codecs that are more efficient
        if self.codec_name in ['hevc', 'av1', 'vp9']:
            crf_value += 4
        if self.video_settings.quality == VideoExportQuality.LOSSLESS:
            crf_value = 0

        self.encoding_options = {'crf': str(crf_value)}
        if self.codec_name == 'vp9' and self.video_settings.quality == VideoExportQuality.LOSSLESS:
            self.encoding_options['lossless'] = '1'
        # encoding_options = {}
        if profile is not None:
            self.encoding_options['profile'] = profile

        if self.codec_name == 'h264':
            # sps-id = 3. We try to avoid collisions with the existing SPS ids.
            # Particularly 0 is very commonly used. Technically we should probably try
            # to dynamically set this to a safe number, but it can be difficult to know
            # our detection is robust / correct.
            self.encoding_options['x264-params'] = 'sps-id=3'

        elif self.codec_name == 'hevc':
            # Get the encoder settings from input stream extradata.
            # In theory this should not work. The stuff in extradata is technically just comments set by the encoder.
            # Another issue is that the extradata format is going to be different depending on the encoder.
            # So this will likely only work if the input stream is encoded with x265 ¯\_(ツ)_/¯
            # However, this does make the testcases from fails -> passes.
            # And I've tested that it works on some real videos as well.
            # Maybe there is some option that I'm not setting correctly and there is a better way to get the correct value?

            assert self.in_stream is not None
            assert self.in_stream.codec_context is not None
            extradata = self.in_stream.codec_context.extradata
            x265_params = []
            try:
                if extradata is None:
                    raise ValueError("No extradata")
                options_str = str(extradata.split(b'options: ')[1][:-1], 'ascii')
                x265_params = options_str.split(' ')
                for i, o in enumerate(x265_params):
                    if ':' in o:
                        x265_params[i] = o.replace(':', ',')
                    if '=' not in o:
                        x265_params[i] = o + '=1'
            except Exception:
                pass

            # Repeat headers. This should be the same as `global_headers = False`,
            # but for some reason setting this explicitly is necessary with x265.
            x265_params.append('repeat-headers=1')

            # Disable encoder info SEI. Since smartcut only re-encodes frames at cut points,
            # having x265 write its encoding settings would be misleading - it doesn't
            # represent the original video's settings.
            x265_params.append('info=0')

            if self.log_level is not None:
                x265_params.append(f'log_level={self.log_level}')

            if self.video_settings.quality == VideoExportQuality.LOSSLESS:
                x265_params.append('lossless=1')

            self.encoding_options['x265-params'] = ':'.join(x265_params)


    def _configure_interlace(self, frame: VideoFrame) -> None:
        """Open the boundary encoder in interlaced mode when the source is.

        Decoded frames from interlaced broadcasts (1080i H.264 MBAFF, 576i
        MPEG-2) carry their field flags, but the encoder ignores them unless
        it is opened for interlaced coding - without this, the re-encoded
        frames at each cut boundary come out progressive-flagged with the
        woven fields coded as-is, so players skip deinterlacing and show
        combing on motion until the copied stream resumes.

        Called with every frame about to be encoded, and decided once per
        encoder - that is, once per re-encoded run - because each run opens a
        new encoder and the flags have to be set before its first encode().
        It must not be decided once per export: a run's frames are not
        necessarily like the first run's, and broadcast material mixes the two
        freely.

        Content that is progressive (including progressive-coded stretches of
        an MBAFF stream, common on film-sourced material) is left exactly as
        before.
        """
        if self._interlace_done:
            return
        self._interlace_done = True
        hint = self.video_settings.source_interlaced
        if hint is False:
            return
        if not getattr(frame, 'interlaced_frame', False):
            # The frame that opens this run must itself be interlaced, even
            # when the stream-level hint says the recording is.
            #
            # Field order comes from the opening frame: ffmpeg sets x264's
            # b_tff from its top-field-first flag, and a progressive frame
            # carries none, so the encoder opens bottom-field-first.  On a
            # Channel 4 HD recording whose interlaced frames are all top-field
            # first, enabling interlaced coding off a progressive opening
            # frame produced a stream marked bff - inverted field order, which
            # judders on playback and is worse than the combing this exists to
            # prevent.
            #
            # So a run that opens progressive stays progressive.  Runs that
            # open interlaced get interlaced coding with the field order their
            # own frames declare.
            return
        if self.codec_name not in ('h264', 'mpeg2video'):
            return   # x265's interlace support is poor; HEVC broadcast is progressive
        assert self.enc_codec is not None
        if getattr(self.enc_codec, 'is_open', False):
            return   # too late to change; first frame normally decides in time
        existing = self.enc_codec.options.get('flags', '')
        self.enc_codec.options['flags'] = existing + '+ildct+ilme'

    def _fix_packet_timestamps(self, packet: Packet) -> None:
        """Fix packet DTS/PTS to ensure monotonic increase and PTS >= DTS."""
        packet.stream = self.out_stream
        packet.time_base = self.out_time_base

        # Treat garbage DTS values as None (can occur during encoder flush due to PyAV
        # reading uninitialized memory when frame is None during flush)
        # See: https://github.com/PyAV-Org/PyAV/issues/397
        #      https://github.com/PyAV-Org/PyAV/discussions/933
        if packet.dts is not None and (packet.dts < -900_000 or packet.dts > 1_000_000_000_000):
            packet.dts = None

        if packet.dts is not None:
            if packet.dts <= self.last_dts:
                packet.dts = self.last_dts + 1
            # Ensure PTS >= DTS (required by all container formats)
            # This check is separate from the monotonicity check above because
            # remux_segment may produce packets with DTS > PTS when adjusting
            # for B-frame delays after an encoded segment.
            if packet.pts is not None and packet.pts < packet.dts:
                packet.pts = packet.dts
            self.last_dts = packet.dts
        if packet.dts is None:
            # When DTS is None, use PTS as fallback (common for keyframes without B-frame reordering)
            # Ensure we don't use the sentinel value to avoid extremely negative DTS
            pts_value = packet.pts if packet.pts is not None else 0
            if self.last_dts < 0:
                # First packet with None DTS, use PTS
                packet.dts = pts_value
            else:
                # Subsequent packets, ensure monotonic increase
                # Don't jump DTS up to match PTS - just increment minimally to preserve PTS >= DTS
                packet.dts = self.last_dts + 1
            # The same PTS >= DTS guard as the branch above.  Its absence here
            # was why a misplaced packet left this method with pts=-8480 and
            # dts=1241 and killed the export, rather than merely being clamped:
            # the invented DTS is a position in the output, and a PTS earlier
            # than it is meaningless.
            if packet.pts is not None and packet.pts < packet.dts:
                packet.pts = packet.dts
            self.last_dts = packet.dts

        # Fix packet duration - needed by MP4 muxer to output valid frames
        # Track typical duration from valid packets, use it when duration is missing/zero
        if packet.duration is not None and packet.duration > 0:
            self.typical_frame_duration = packet.duration
        elif self.typical_frame_duration is not None:
            packet.duration = self.typical_frame_duration

    def _ensure_enc_codec(self) -> None:
        """Initialize enc_codec if not already set."""
        if self.enc_codec is not None:
            return

        muxing_codec = self.out_stream.codec_context
        enc_codec = cast(VideoCodecContext, CodecContext.create(self.codec_name, 'w'))

        if muxing_codec.rate is not None:
            enc_codec.rate = muxing_codec.rate
        enc_codec.options.update(self.encoding_options)

        # Leaving this here for future consideration: manually setting the bframe count seems to make sense in principle.
        # But atleast in the test suite, it seemed to cause more issues that in solves.
        # metadata_b_frames = max(self.in_stream.codec_context.max_b_frames, 1 if self.in_stream.codec_context.has_b_frames else 0)
        # enc_codec.max_b_frames = metadata_b_frames

        enc_codec.width = muxing_codec.width
        enc_codec.height = muxing_codec.height
        enc_codec.pix_fmt = muxing_codec.pix_fmt

        if muxing_codec.sample_aspect_ratio is not None:
            enc_codec.sample_aspect_ratio = muxing_codec.sample_aspect_ratio
        if self.codec_name == 'mpeg2video':
            enc_codec.time_base = Fraction(1, muxing_codec.rate)
        else:
            enc_codec.time_base = self.out_time_base

        if muxing_codec.bit_rate is not None:
            enc_codec.bit_rate = muxing_codec.bit_rate
        if muxing_codec.bit_rate_tolerance is not None:
            enc_codec.bit_rate_tolerance = muxing_codec.bit_rate_tolerance
        _apply_source_colour(enc_codec, self.in_stream.codec_context)
        # A new encoder restarts its own POC numbering from zero, so its
        # output is a run of its own.
        self._poc_run += 1
        self._poc_enc_run = self._poc_run

        enc_codec.codec_tag = muxing_codec.codec_tag
        enc_codec.thread_type = "FRAME"
        # Use all available cores for the boundary re-encode.  Must be set
        # before the codec is opened (the first encode() call opens it).
        try:
            import os
            enc_codec.thread_count = os.cpu_count() or 0
        except Exception:
            pass
        self.enc_last_pts = -1
        self.enc_codec = enc_codec
        # Each re-encoded run gets a brand-new encoder, and interlace mode has
        # to be set on it before its first encode() opens it.  This used to be
        # decided once per export, so only the very first run was ever
        # configured and every later one came out progressive whatever it
        # contained - on one Channel 4 HD recording that left 326 field-coded
        # frames coded as progressive across three runs.  Its own options dict
        # is fresh (populated from self.encoding_options above), so a decision
        # made for one run cannot leak into the next.
        self._interlace_done = False

    def _copy_run(self, s: CutSegment) -> int:
        """Run id for copied packets from segment `s`.

        Consecutive GOPs copied from the source keep the source's own POC
        numbering, which stays coherent as long as they were adjacent there.
        A gap means material was cut out, so the numbering restarts.
        """
        contiguous = (
            not self.is_first_remuxed_segment
            and self.last_remuxed_segment_gop_index is not None
            and s.gop_index == self.last_remuxed_segment_gop_index + 1
        )
        if not contiguous:
            self._poc_run += 1
        return self._poc_run

    def _renumber(self, packets: list[Packet], run_id: int) -> list[Packet]:
        """Rewrite POCs in `packets`, which must be in output order."""
        if self._poc is None or not self._poc.enabled:
            return packets
        result = []
        for p in packets:
            data = bytes(p)
            new_data = self._poc.rewrite(data, run_id)
            if new_data is data or new_data == data:
                result.append(p)
                continue
            packet = Packet(new_data)
            packet.pts = p.pts
            packet.dts = p.dts
            packet.duration = p.duration
            # A packet straight out of a bitstream filter has no stream and
            # may have no time base; assigning None to either raises.
            # _fix_packet_timestamps sets both afterwards in any case.
            if p.time_base is not None:
                packet.time_base = p.time_base
            if p.stream is not None:
                packet.stream = p.stream
            packet.is_keyframe = p.is_keyframe
            for side_data in p.iter_sidedata():
                packet.set_sidedata(side_data)
            result.append(packet)
        return result

    def segment(self, cut_segment: CutSegment) -> list[Packet]:
        if cut_segment.require_recode:
            packets = self.recode_segment(cut_segment)
        elif self._should_hybrid_recode_cra(cut_segment):
            # CRA GOP with leading pictures: recode leading pics, remux rest
            # Don't flush encoder - leading frames continue into existing encoder
            packets = self.hybrid_recode_cra_segment(cut_segment)
            # Update tracking variables (same as remux path)
            self.last_remuxed_segment_gop_index = cut_segment.gop_index
            self.is_first_remuxed_segment = False
        else:
            packets = self.flush_encoder()
            packets.extend(self.remux_segment(cut_segment))
            # Update tracking variables for hybrid CRA recoding
            self.last_remuxed_segment_gop_index = cut_segment.gop_index
            self.is_first_remuxed_segment = False

        self.segment_start_in_output += cut_segment.end_time - cut_segment.start_time

        for packet in packets:
            self._fix_packet_timestamps(packet)

        return packets

    def finish(self) -> list[Packet]:
        packets = self.flush_encoder()
        for packet in packets:
            self._fix_packet_timestamps(packet)

        self.input_av_container.close()

        return packets

    def recode_segment(self, s: CutSegment) -> list[Packet]:
        if not self.encoder_inited:
            self.init_encoder()
        result_packets = []

        self._ensure_enc_codec()
        assert self.enc_codec is not None

        # Prime decoder from previous GOP if this GOP has RASL frames
        # (RASL frames reference frames from before the CRA, so decoder needs previous GOP)
        decoder_priming_dts = None
        if (
            s.gop_index > 0
            and s.gop_index < len(self.media_container.gop_has_rasl)
            and self.media_container.gop_has_rasl[s.gop_index]
        ):
            decoder_priming_dts = self.media_container.gop_start_times_dts[s.gop_index - 1]

        for frame in self.fetch_frame(s.gop_start_dts, s.gop_end_dts, s.end_time, decoder_priming_dts):
            assert frame.pts is not None, "Frame pts should not be None after decoding"
            in_tb = frame.time_base if frame.time_base is not None else self.in_time_base
            if frame.pts * in_tb < s.start_time:
                continue
            if frame.pts * in_tb >= s.end_time:
                break

            out_tb = self.out_time_base if self.codec_name != 'mpeg2video' else self.enc_codec.time_base

            frame.pts = int(frame.pts - s.start_time / in_tb)

            frame.pts = int(frame.pts * in_tb / out_tb)
            frame.time_base = out_tb
            frame.pts = int(frame.pts + self.segment_start_in_output / out_tb)

            if frame.pts <= self.enc_last_pts:
                frame.pts = int(self.enc_last_pts + 1)
            self.enc_last_pts = frame.pts

            frame.pict_type = PictureType.NONE
            frame = self._scale_frame_if_needed(frame)
            self._configure_interlace(frame)
            result_packets.extend(self.enc_codec.encode(frame))

        if self.codec_name == 'mpeg2video':
            for p in result_packets:
                p.pts = p.pts * p.time_base / self.out_time_base
                p.dts = p.dts * p.time_base / self.out_time_base
                p.time_base = self.out_time_base
        return self._renumber(result_packets, self._poc_enc_run)

    def remux_segment(self, s: CutSegment) -> list[Packet]:
        result_packets = []
        # Decide the run before segment() updates the tracking fields this
        # reads, or every copied segment looks contiguous with itself.
        copy_run = self._copy_run(s)
        segment_start_pts = int(s.start_time / self.in_time_base)

        for packet in self.fetch_packet(s.gop_start_dts, s.gop_end_dts):
            # Apply timing adjustments
            segment_start_offset = self.segment_start_in_output / self.out_time_base
            # See the note in the hybrid path below: a truthiness test here
            # turns a missing timestamp into a time at the start of the file.
            if packet.pts is not None:
                pts = packet.pts
            elif packet.dts is not None:
                pts = packet.dts
            else:
                pts = segment_start_pts
            packet.pts = int((pts - segment_start_pts) * self.in_time_base / self.out_time_base + segment_start_offset)
            if packet.dts is not None:
                packet.dts = int((packet.dts - segment_start_pts) * self.in_time_base / self.out_time_base + segment_start_offset)

            result_packets.extend(self.remux_bitstream_filter.filter(packet))

        result_packets.extend(self.remux_bitstream_filter.filter(None))

        self.remux_bitstream_filter.flush()
        return self._renumber(result_packets, copy_run)

    def _should_hybrid_recode_cra(self, s: CutSegment) -> bool:
        """
        Check if this segment should use hybrid recode (recode leading pictures only).
        This is needed when:
        1. GOP has RASL frames (they reference frames before the CRA)
        2. There's discontinuity before this point (content was skipped/cut)
        """
        # Check 1: GOP must have RASL frames
        if s.gop_index < 0 or s.gop_index >= len(self.media_container.gop_has_rasl):
            return False
        if not self.media_container.gop_has_rasl[s.gop_index]:
            return False

        # Check 2: Must have discontinuity before this point
        has_discontinuity = (
            (self.is_first_remuxed_segment and s.gop_index > 0) or
            (self.last_remuxed_segment_gop_index is not None and s.gop_index > self.last_remuxed_segment_gop_index + 1)
        )
        return has_discontinuity

    def hybrid_recode_cra_segment(self, s: CutSegment) -> list[Packet]:
        """
        Hybrid recode for CRA GOPs: recode only leading pictures (RASL/RADL),
        remux CRA + trailing pictures unchanged.
        """
        if not self.encoder_inited:
            self.init_encoder()

        result_packets: list[Packet] = []

        # Decide the copy run before segment() updates the tracking fields
        # _copy_run reads, as in remux_segment.
        copy_run = self._copy_run(s)

        # Same reference point as remux_segment
        segment_start_pts = int(s.start_time / self.in_time_base)
        segment_start_offset = self.segment_start_in_output / self.out_time_base

        # Get leading boundary
        leading_end_dts = self.media_container.gop_leading_end_dts[s.gop_index]
        assert leading_end_dts is not None, "hybrid_recode_cra_segment called without leading pictures"

        self._ensure_enc_codec()
        assert self.enc_codec is not None

        # Decoder priming for RASL reference frames
        decoder_priming_dts = None
        if s.gop_index > 0:
            decoder_priming_dts = self.media_container.gop_start_times_dts[s.gop_index - 1]

        # Decode leading + CRA frames, collect packets for later remux
        collected_packets: list[Packet] = []
        all_frames: list[VideoFrame] = []

        for frame in self.fetch_frame(s.gop_start_dts, leading_end_dts, s.end_time,
                                       decoder_priming_dts, collected_packets):
            if frame.pts is not None:
                all_frames.append(frame)

        # Get GOP start time to filter out priming frames from previous GOPs
        gop_start_time = self.media_container.gop_start_times_pts_s[s.gop_index]

        # Find the CRA: the keyframe that opens *this* GOP.
        #
        # Taking collected_packets[0] on trust was how a stray packet from the
        # head of the file came to be read as the CRA.  Its pts was 0, so every
        # leading picture failed the `pts < cra_pts` test below, none were
        # re-encoded, and the stray packets were remuxed into a segment they
        # did not belong to.  Identify it by its keyframe flag and by sitting
        # inside this GOP, so a misplaced packet cannot stand in for it.
        cra_pts = None
        for p in collected_packets:
            if p.pts is None or not p.is_keyframe:
                continue
            if p.pts * self.in_time_base >= gop_start_time:
                cra_pts = p.pts
                break
        assert cra_pts is not None, "No CRA packet found in GOP"

        # Leading frames: PTS >= GOP start AND PTS < CRA PTS (will be encoded)
        # Filter by GOP start to exclude priming frames from previous GOPs
        leading_frames = [
            f for f in all_frames
            if f.pts is not None
            and f.pts * (f.time_base if f.time_base is not None else self.in_time_base) >= gop_start_time
            and f.pts < cra_pts
        ]
        leading_frames.sort(key=lambda f: f.pts if f.pts is not None else 0)

        # Encode leading frames with same timing formula as remux_segment
        encoded_packets: list[Packet] = []
        for frame in leading_frames:
            assert frame.pts is not None
            # Same formula as remux_segment
            frame.pts = int((frame.pts - segment_start_pts) * self.in_time_base / self.out_time_base + segment_start_offset)
            frame.time_base = self.out_time_base

            if frame.pts <= self.enc_last_pts:
                frame.pts = int(self.enc_last_pts + 1)
            self.enc_last_pts = frame.pts

            frame.pict_type = PictureType.NONE
            self._configure_interlace(frame)
            encoded_packets.extend(self.enc_codec.encode(frame))

        # Renumber the encoded leading pictures before flushing: the
        # rewriter carries state forward and must see packets in the order
        # they will be written, and flush_encoder renumbers its own.
        result_packets.extend(self._renumber(encoded_packets,
                                             self._poc_enc_run))
        result_packets.extend(self.flush_encoder())

        # Fix encoder DTS
        for p in result_packets:
            if p.dts is None or p.dts > 1_000_000_000_000:
                p.dts = p.pts

        # Remux: collected packets (CRA, leading already filtered in fetch_frame) + trailing
        # Handle in one loop with same timing as remux_segment
        remux_packets = list(collected_packets)
        remux_packets.extend(self.fetch_packet(leading_end_dts, s.gop_end_dts))
        copied_packets: list[Packet] = []

        for packet in remux_packets:
            # A packet with no presentation time has nothing to rebase.  The
            # old test was `packet.pts if packet.pts else 0`, which is a
            # truthiness test on a number: it turned a missing timestamp into
            # 0, and 0 was then rebased as though it were a real time at the
            # very start of the file - giving a large negative pts that the
            # muxer refuses.  Fall back to the decode time, which is the
            # closest thing to the truth, and only then to the segment start.
            if packet.pts is not None:
                pts = packet.pts
            elif packet.dts is not None:
                pts = packet.dts
            else:
                pts = segment_start_pts

            packet.pts = int((pts - segment_start_pts) * self.in_time_base / self.out_time_base + segment_start_offset)
            if packet.dts is not None:
                packet.dts = int((packet.dts - segment_start_pts) * self.in_time_base / self.out_time_base + segment_start_offset)
            copied_packets.extend(self.remux_bitstream_filter.filter(packet))

        copied_packets.extend(self.remux_bitstream_filter.filter(None))
        self.remux_bitstream_filter.flush()
        result_packets.extend(self._renumber(copied_packets, copy_run))

        return result_packets

    def flush_encoder(self) -> list[Packet]:
        if self.enc_codec is None:
            return []

        result_packets = self.enc_codec.encode()

        if self.codec_name == 'mpeg2video':
            for p in result_packets:
                if p.time_base is not None:
                    if p.pts is not None:
                        p.pts = int(p.pts * p.time_base / self.out_time_base)
                    if p.dts is not None:
                        p.dts = int(p.dts * p.time_base / self.out_time_base)
                p.time_base = self.out_time_base

        self.enc_codec = None
        return self._renumber(result_packets, self._poc_enc_run)

    def _scale_frame_if_needed(self, frame: VideoFrame) -> VideoFrame:
        """Scale frame to encoder dimensions if needed, using bilinear interpolation.

        Stays in the same pixel format (no YUV->RGB conversion).
        """
        if self.enc_codec is None:
            return frame

        if frame.width == self.enc_codec.width and frame.height == self.enc_codec.height:
            return frame

        # reformat() preserves pts/time_base and keeps pixel format unchanged
        return frame.reformat(
            width=self.enc_codec.width,
            height=self.enc_codec.height,
            interpolation='BILINEAR'
        )

    def fetch_packet(self, target_dts: int, end_dts: int) -> Generator[Packet, None, None]:
        # First, check if we have a saved packet from previous call
        if self.demux_saved_packet is not None:
            saved_dts = self.demux_saved_packet.dts if self.demux_saved_packet.dts is not None else UNKNOWN_DTS
            if saved_dts >= target_dts:
                if saved_dts <= end_dts:
                    packet = self.demux_saved_packet
                    self.demux_saved_packet = None
                    yield packet
                else:
                    # Saved packet is beyond our end range, don't yield it
                    return
            else:
                # Saved packet is before our target, clear it
                self.demux_saved_packet = None

        for packet in self.demux_iter:
            in_dts = packet.dts if packet.dts is not None else UNKNOWN_DTS

            # Skip packets before target_dts
            if packet.pts is None or in_dts < target_dts:
                diff = (target_dts - in_dts) * self.in_time_base
                if in_dts > 0 and diff > 120:
                    t = int(target_dts - 30 / self.in_time_base)
                    # print(f"Seeking to skip a gap: {float(t * tb)}")
                    self.input_av_container.seek(t, stream = self.in_stream)
                    # Clear saved packet after seek since iterator position changed
                    self.demux_saved_packet = None
                continue

            # Check if packet exceeds end_dts
            if in_dts > end_dts:
                # Save this packet for next call and stop iteration
                # Save a COPY, not the live packet.  The caller rebases the
                # packets it is given in place, so holding on to the original
                # meant that when this one was handed to the next segment it
                # was rebased a second time - pts 120 became -8520, which the
                # muxer refuses outright and the export died with "Invalid
                # argument".  It only bit when a segment boundary happened to
                # land on a saved packet, which is why it depended on exactly
                # where the scenes were placed.
                self.demux_saved_packet = copy_packet(packet)
                return

            # Packet is in our target range, yield it
            yield packet

    def fetch_frame(self, gop_start_dts: int, gop_end_dts: int, end_time: Fraction, decoder_priming_dts: int | None = None, collect_packets: list[Packet] | None = None) -> Generator[VideoFrame, None, None]:
        # Check if previous iteration consumed exactly to this GOP start
        continuous = self._last_fetch_end_dts is not None and (self._last_fetch_end_dts in (gop_end_dts, gop_start_dts))
        self._last_fetch_end_dts = gop_end_dts

        # Choose actual start DTS. Allow priming from previous GOP unless we're either still in the same GOP or continuing to the next one.
        start_dts = gop_start_dts if continuous else (decoder_priming_dts if decoder_priming_dts is not None else gop_start_dts)

        # Initialize or reset for new GOP boundary unless continuous
        if self.frame_buffer_gop_dts != gop_start_dts and not continuous:
            self.frame_buffer = []
            self.frame_buffer_gop_dts = gop_start_dts
            self.decoder.flush_buffers()

        # If asked to start earlier than GOP, seek and clear state (skip if continuous)
        if start_dts < gop_start_dts and not continuous:
            try:
                self.decoder.flush_buffers()
                self.frame_buffer = []
                self.input_av_container.seek(start_dts, stream=self.in_stream)
                self.demux_saved_packet = None
              # Recreate demux iterator after an explicit seek to ensure position is honored
                self.demux_iter = self.input_av_container.demux(self.in_stream)

            except Exception:
                pass

        # Process packets and yield frames when safe
        current_dts = gop_start_dts

        for packet in self.fetch_packet(start_dts, gop_end_dts):
            current_dts = packet.dts if packet.dts is not None else current_dts

            # Collect packets for remuxing if requested (hybrid recode path)
            # Skip: priming packets (dts < gop_start_dts), leading pictures (RASL/RADL)
            if collect_packets is not None:
                if packet.dts is not None:
                    should_collect = packet.dts >= gop_start_dts  # Skip priming packets
                else:
                    # No decode time at all.  The old fallback here was
                    # `current_dts`, which starts out equal to gop_start_dts -
                    # so a packet with no DTS was presumed to be inside this
                    # GOP.  That is exactly backwards.  Only the opening
                    # packets of a file lack a DTS, and this loop reaches them
                    # when we have deliberately seeked back to the head of the
                    # file to prime the decoder for a much later GOP's RASL
                    # pictures.  Collecting them dragged the first two packets
                    # of the recording into a segment ten seconds in, where
                    # rebasing their timestamps gave a large negative pts and
                    # the MPEG-TS muxer refused them outright.
                    #
                    # A packet with no DTS can only belong to this GOP if this
                    # GOP itself begins before any decode time is known - that
                    # is, if it is the first GOP of the file.
                    should_collect = gop_start_dts <= UNKNOWN_DTS
                if should_collect and self.codec_name == 'hevc':
                    nal_type = get_h265_nal_unit_type(bytes(packet))
                    if is_leading_picture_nal_type(nal_type):
                        should_collect = False
                if should_collect:
                    collect_packets.append(copy_packet(packet))

            # Decode packet and add frames to buffer
            for frame in self.decoder.decode(packet):
                heap_item = FrameHeapItem(frame.pts, frame)
                heapq.heappush(self.frame_buffer, heap_item)

            # Release frames that are safe (buffer_lowest_pts <= current_dts)
            BUFFERED_FRAMES_COUNT = 15 # We need this to be quite high, b/c GENPTS is on and we can't know if the pts values are real or fake
            while len(self.frame_buffer) > BUFFERED_FRAMES_COUNT:
                lowest_heap_item = self.frame_buffer[0]  # Peek at heap minimum
                frame = lowest_heap_item.frame
                frame_pts = lowest_heap_item.pts if lowest_heap_item.pts is not None else -1
                frame_time_base = frame.time_base if frame.time_base is not None else self.in_time_base

                # Only process frames that are safe to release (frame_pts <= current_dts)
                if frame_pts <= current_dts:
                    if frame_pts * frame_time_base < end_time:
                        heapq.heappop(self.frame_buffer)  # Remove from heap
                        yield frame
                    else:
                        # Safe frame is beyond end_time - we're done since all frames from now would be beyond end time
                       return
                else:
                    break

        # Final flush of the decoder
        try:
            for frame in self.decoder.decode(None):
                heap_item = FrameHeapItem(frame.pts, frame)
                heapq.heappush(self.frame_buffer, heap_item)
        except Exception:
            pass

        # Yield remaining frames within time range
        while self.frame_buffer:
            # Peek at the next frame without popping it
            next_frame = self.frame_buffer[0]
            frame = next_frame.frame
            frame_time_base = frame.time_base if frame.time_base is not None else self.in_time_base

            if (next_frame.pts is not None and
                next_frame.pts * frame_time_base < end_time):
                # Frame is within time range, pop and yield it
                heapq.heappop(self.frame_buffer)
                yield frame
            else:
                # Frame is outside time range, stop processing (leave it in buffer)
                break
