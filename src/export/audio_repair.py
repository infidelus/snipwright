"""Make a cut's audio one channel configuration by re-encoding only the
frames that disagree.

Broadcast AAC can change channel configuration mid-programme - Channel 4 HD
runs continuity and advert breaks in stereo and the programme in 5.1.  MPEG-TS
carries the configuration in every frame so a mixed cut plays perfectly, but
MP4 and Matroska each hold ONE configuration per track, so copying such a cut
into either gives a track with the right packet count and no sound.

The blunt answer is to re-encode the whole track.  On a three-hour film that
is ten minutes of work and the loss of the 5.1 mix, to correct about two
seconds of audio: measured on a real Channel 4 recording, 83 frames out of
415,649 were the minority configuration - 0.02%.

This repairs those runs instead.  Frames in the dominant configuration are
passed through untouched, byte for byte; only the minority runs are decoded,
upmixed and re-encoded, and they are spliced back at the same frame positions
so nothing after them moves.

Two things make that safe:

  * The encoder adds one frame (1024 samples) of priming.  Measured against
    the original at a correlation of 0.9997 once dropped, so discarding the
    leading frame leaves the substitution sample-aligned and the frame count
    exactly preserved.
  * The replacement bitrate is measured from the cut's own dominant frames
    rather than guessed, so it matches what the broadcaster actually sent.

Frames are streamed rather than held: a run is buffered, repaired and written,
so peak memory is one run and not one audio track.
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile

logger = logging.getLogger("snipwright")

# channelConfiguration -> ffmpeg channel layout.
LAYOUTS = {1: "mono", 2: "stereo", 3: "3.0", 4: "4.0",
           5: "5.0", 6: "5.1", 7: "7.1"}

# Above this share of the track, surgical repair has no advantage over simply
# re-encoding, and the run buffering stops being cheap.
MAX_REPAIR_SHARE = 0.05

# 1024 samples per AAC frame.
SAMPLES_PER_FRAME = 1024


def _adts_config(head):
    """channelConfiguration from an ADTS header, or None if not ADTS."""
    if len(head) < 4 or head[0] != 0xFF or (head[1] & 0xF0) != 0xF0:
        return None
    return ((head[2] & 0x01) << 2) | ((head[3] & 0xC0) >> 6)


def _split_adts(data):
    """Split an ADTS elementary stream into frames."""
    out, i = [], 0
    while i + 7 <= len(data):
        if data[i] != 0xFF or (data[i + 1] & 0xF0) != 0xF0:
            i += 1
            continue
        length = (((data[i + 3] & 0x03) << 11) | (data[i + 4] << 3)
                  | ((data[i + 5] & 0xE0) >> 5))
        if length < 7 or i + length > len(data):
            break
        out.append(data[i:i + length])
        i += length
    return out


def survey(path, stream_index):
    """What configurations this audio track holds, and at what bitrate.

    Returns a dict, or None if the track isn't ADTS AAC.  Reads four bytes per
    packet, so it costs a pass over the file and nothing else.
    """
    import av

    try:
        container = av.open(path)
    except Exception:
        return None
    try:
        streams = [s for s in container.streams if s.type == "audio"]
        if stream_index >= len(streams):
            return None
        counts, byte_totals = {}, {}
        stream = streams[stream_index]
        sample_rate = stream.codec_context.sample_rate or 48000
        for packet in container.demux(stream):
            if packet.size < 7:
                continue
            head = bytes(memoryview(packet)[:4])
            config = _adts_config(head)
            if config is None:
                continue
            counts[config] = counts.get(config, 0) + 1
            byte_totals[config] = byte_totals.get(config, 0) + packet.size
    except Exception:
        return None
    finally:
        try:
            container.close()
        except Exception:
            pass

    if not counts:
        return None
    dominant = max(counts, key=lambda c: counts[c])
    total = sum(counts.values())
    minority = total - counts[dominant]
    seconds = counts[dominant] * SAMPLES_PER_FRAME / float(sample_rate)
    bitrate = int(byte_totals[dominant] * 8 / seconds) if seconds else 0
    return {
        "counts": counts,
        "dominant": dominant,
        "total": total,
        "minority": minority,
        "sample_rate": sample_rate,
        "bitrate": bitrate,
        "census": ", ".join(f"{c}ch x{n}" for c, n in sorted(counts.items())),
    }


# ffmpeg's layout names for the channel counts broadcast material uses.  Only
# these are named; anything else falls back to a bare count, which ffmpeg's
# aformat filter also accepts.
_LAYOUT_NAMES = {1: "mono", 2: "stereo", 3: "2.1", 6: "5.1", 8: "7.1"}


def layout_name(channels):
    """ffmpeg's name for a channel count, e.g. 6 -> '5.1'."""
    return _LAYOUT_NAMES.get(int(channels or 0), "%dc" % (channels or 2))


def source_profile(path, stream_index=0):
    """(channels, bitrate) as the recording actually is, or (None, None).

    ffprobe first, for the codec and the container's own figures, and then
    survey() to refine them ONLY when the codec really is AAC.

    That order matters and the other way round is wrong.  survey() reads ADTS
    headers, and an MPEG audio frame begins with the same 0xFFF sync word, so
    pointed at an MP2 track it parses the bits after the sync as though they
    were an ADTS header and returns a confident answer made of nothing: on a
    stereo 256 kbps MP2 recording it reported three channels at 287 kbps.

    Where the codec IS AAC, survey() is worth having, because it reports what
    the frames carry rather than what the header claims - a broadcast track
    whose container header says stereo can be 5.1 for its whole length, and
    ffprobe reports the header.

    Returning (None, None) rather than a default is deliberate: the caller
    should leave the encoder to its own devices rather than impose a figure
    nobody measured.
    """
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error",
             "-select_streams", "a:%d" % stream_index,
             "-show_entries", "stream=codec_name,channels,bit_rate",
             "-of", "default=noprint_wrappers=1", path],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except Exception:
        return None, None

    codec = ""
    channels = bitrate = None
    for line in out.splitlines():
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key == "codec_name":
            codec = value.lower()
        elif value.isdigit():         # ffprobe writes "N/A" when it can't tell
            if key == "channels":
                channels = int(value)
            elif key == "bit_rate":
                bitrate = int(value)

    if codec in ("aac", "aac_latm"):
        try:
            info = survey(path, stream_index)
        except Exception:
            info = None
        if info and info.get("dominant"):
            measured = info.get("bitrate") or 0
            return int(info["dominant"]), (measured or bitrate)

    return channels, bitrate


def _reencode_run(run, target_config, bitrate, sample_rate):
    """Re-encode one run to target_config, returning exactly len(run) frames."""
    want = len(run)
    layout = LAYOUTS.get(target_config)
    if not layout:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "run.aac")
        dst = os.path.join(tmp, "fixed.aac")
        with open(src, "wb") as fh:
            fh.write(b"".join(run))
        cmd = [
            "ffmpeg", "-hide_banner", "-v", "error", "-y",
            "-i", src,
            "-ac", str(target_config), "-channel_layout", layout,
            "-ar", str(sample_rate),
            "-c:a", "aac", "-b:a", f"{max(96000, bitrate)}",
            "-f", "adts", dst,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(dst):
            logger.warning("Audio run re-encode failed: %s",
                           (result.stderr or "").strip()[:200])
            return None
        produced = _split_adts(open(dst, "rb").read())

    if not produced:
        return None
    # Drop the encoder's priming frames from the front, then take exactly the
    # number we replaced so nothing downstream shifts.
    if len(produced) > want:
        produced = produced[len(produced) - want:]
    while len(produced) < want:
        produced.append(produced[-1])
    return produced


class _RepairCancelled(Exception):
    pass
