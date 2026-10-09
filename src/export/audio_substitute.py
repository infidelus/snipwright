"""Timestamp-preserving payload substitution.

The previous implementation rebuilt the audio track as a bare ADTS elementary
stream and remuxed it.  An elementary stream carries no timestamps, so ffmpeg
laid a perfectly uniform grid over it - and that erased every discontinuity the
real timeline contained.

Those discontinuities are not errors.  A broadcast recording is missing audio
wherever the transmission dropped a frame, and the timestamps are what carry
that absence: measured on the recording this was written against, 72 dropouts
totalling 2,624 ms across two and a half hours.  The .ts plays in sync because
each packet says where it belongs.  Regenerating the grid closed all 72 holes,
so the audio ran progressively earlier - about 2.6 seconds by the end, which is
exactly the drift that was reported.

So nothing here regenerates a timestamp.  The container is remuxed packet by
packet with every pts, dts and duration carried across untouched, and only the
PAYLOAD of the frames that must change is substituted.  A repaired file has the
same timeline as the one it came from, hole for hole.

Measured on a five-scene cut of a real damaged recording: 1,093 ms of gaps
present before and after, every timestamp on both audio tracks identical, and
sync against a lossless .ts reference drifting 2 ms across seventeen minutes.
"""

from __future__ import annotations

import logging
import os
from smartcut.open_options import LEGACY_OPEN_ARGS
from smartcut.rational import q

logger = logging.getLogger("snipwright")


class _RepairCancelled(Exception):
    pass


def _duration_of(container):
    """The file's length in seconds, or 0.0 if it cannot be told.

    Only used to turn a packet timestamp into a fraction for the progress bar,
    so a container that will not say is not an error - the caller falls back to
    a busy indicator.
    """
    import av

    try:
        if container.duration:
            return float(container.duration) / av.time_base
    except Exception:
        pass
    return 0.0


class _Walk:
    """Turns packet timestamps into a percentage for the progress bar.

    Both passes here walk the file once from beginning to end, so how far
    through the timeline a packet sits is how far through the pass we are.

    Two things this has to get right:

    - **The clock does not start at zero.** A broadcast recording's first
      packet carries whatever timestamp the transmission was up to, so the
      first one seen is taken as the baseline. Dividing a raw PTS by the
      duration would have the bar start at some arbitrary point and run off
      the end.
    - **Only report when the whole number RISES.** Two reasons, and the second
      is not obvious. A callback per packet would cost more than the repair on
      a three-hour recording, so whole percents only; and apply_repairs
      demuxes video and audio together, whose timestamps interleave rather
      than arrive in order, so a raw reading oscillates - 52, 51, 53, 52 -
      and the bar visibly jitters backwards. Measured on the test clip: 39
      backward steps out of 180 updates. Never reporting a fall costs nothing
      and is what the user should see anyway.

    `span` maps this pass onto a slice of the overall bar, so several tracks
    and both passes advance one bar rather than each restarting it.
    """

    def __init__(self, container, progress_cb, span=(0.0, 1.0),
                 phase="repair_audio"):
        self.cb = progress_cb
        self.low, self.high = span
        self.phase = phase
        self.duration = _duration_of(container)
        self.baseline = None
        self.last = -1
        if self.cb is not None and not self.duration:
            # Nothing to count against: say so once rather than leave the bar
            # sitting at zero as though it had stalled.
            self.cb({"phase": self.phase, "percent": -1})

    def note(self, packet):
        if self.cb is None or not self.duration:
            return
        # dts by preference: it is monotonic even where B-frames reorder pts,
        # and apply_repairs walks video packets too.
        stamp = packet.dts if packet.dts is not None else packet.pts
        if stamp is None or q(packet.time_base) is None:
            return
        try:
            seconds = float(stamp * packet.time_base)
        except (TypeError, ValueError):
            return
        if self.baseline is None:
            self.baseline = seconds
        walked = (seconds - self.baseline) / self.duration
        walked = min(1.0, max(0.0, walked))
        percent = int(round((self.low + walked * (self.high - self.low)) * 100))
        if percent > self.last:
            self.last = percent
            self.cb({"phase": self.phase, "percent": percent})


def plan_repairs(path, stream_index, info, cancel_cb=None,
                 progress_cb=None, span=(0.0, 1.0)):
    """Work out which packets need replacing, and with what.

    Returns {ordinal: replacement_bytes} for the target audio stream, where
    ordinal counts non-empty packets of that stream from zero.  Only the
    minority-configuration frames appear; everything else is left alone.

    Returns None if any run could not be re-encoded to exactly the length it
    replaced, because a length change is a sync change.
    """
    import av

    from export.audio_repair import _adts_config, _reencode_run

    dominant = info["dominant"]
    replacements = {}
    try:
        container = av.open(path, **LEGACY_OPEN_ARGS)
    except Exception:
        return None
    try:
        stream = [s for s in container.streams
                  if s.type == "audio"][stream_index]
        walk = _Walk(container, progress_cb, span)
        ordinal = -1
        run, run_start = [], None
        for packet in container.demux(stream):
            if cancel_cb is not None and cancel_cb():
                raise _RepairCancelled()
            walk.note(packet)
            if not packet.size:
                continue
            ordinal += 1
            data = bytes(packet)
            config = _adts_config(data[:4]) if len(data) >= 7 else None
            if config is not None and config != dominant:
                if run_start is None:
                    run_start = ordinal
                run.append(data)
                continue
            if run:
                fixed = _reencode_run(run, dominant, info["bitrate"],
                                      info["sample_rate"])
                if fixed is None or len(fixed) != len(run):
                    logger.warning(
                        "Audio run at packet %d came back as %s frame(s) "
                        "instead of %d; abandoning the repair.",
                        run_start,
                        "none" if fixed is None else len(fixed), len(run),
                    )
                    return None
                for offset, payload in enumerate(fixed):
                    replacements[run_start + offset] = payload
                run, run_start = [], None
        if run:
            fixed = _reencode_run(run, dominant, info["bitrate"],
                                  info["sample_rate"])
            if fixed is None or len(fixed) != len(run):
                return None
            for offset, payload in enumerate(fixed):
                replacements[run_start + offset] = payload
    except _RepairCancelled:
        raise
    except Exception as exc:
        logger.warning("Could not plan the audio repair: %s", exc)
        return None
    finally:
        try:
            container.close()
        except Exception:
            pass
    return replacements


def apply_repairs(src, dst, stream_index, replacements, cancel_cb=None,
                  progress_cb=None, span=(0.0, 1.0)):
    """Remux src to dst, substituting payloads and preserving every timestamp.

    Returns True on success.  Video, the other audio tracks and subtitles are
    copied packet for packet; a data stream (the EPG PID) is dropped, as the
    export has always dropped it.
    """
    import av

    try:
        inp = av.open(src, **LEGACY_OPEN_ARGS)
    except Exception as exc:
        logger.warning("Could not open the cut for repair: %s", exc)
        return False

    out = None
    try:
        audio_streams = [s for s in inp.streams if s.type == "audio"]
        target = audio_streams[stream_index]
        out = av.open(dst, "w", format="mpegts")
        mapping = {}
        for s in inp.streams:
            if s.type not in ("video", "audio", "subtitle"):
                continue                      # EPG and other data PIDs
            if s.codec_context is None:
                continue
            try:
                new_stream = out.add_stream_from_template(s)
                # add_stream_from_template carries codec parameters but NOT
                # the stream metadata, so the language tag ("eng") was lost
                # and players showed the tracks as bare numbers instead of
                # naming the language.  Carry it, and the dispositions that
                # mark which track is the audio description.
                try:
                    new_stream.metadata.update(dict(s.metadata))
                except Exception:
                    pass
                try:
                    new_stream.disposition = s.disposition
                except Exception:
                    pass
                mapping[s.index] = new_stream
            except Exception as exc:
                logger.warning("Could not carry stream %d across: %s",
                               s.index, exc)
                return False

        wanted = [s for s in inp.streams if s.index in mapping]
        walk = _Walk(inp, progress_cb, span)
        ordinal = -1
        substituted = 0
        for packet in inp.demux(wanted):
            if cancel_cb is not None and cancel_cb():
                raise _RepairCancelled()
            walk.note(packet)
            if packet.dts is None and packet.pts is None:
                continue                      # flush packet
            if not packet.size:
                continue
            out_stream = mapping.get(packet.stream.index)
            if out_stream is None:
                continue

            if packet.stream.index == target.index:
                ordinal += 1
                payload = replacements.get(ordinal)
                if payload is not None:
                    # A new packet carrying the repaired payload, wearing the
                    # original's timestamps exactly.  This is the whole point:
                    # the timeline must not move.
                    new = av.Packet(payload)
                    new.pts = packet.pts
                    new.dts = packet.dts
                    new.time_base = packet.time_base
                    new.duration = packet.duration
                    new.stream = out_stream
                    out.mux(new)
                    substituted += 1
                    continue

            packet.stream = out_stream
            out.mux(packet)

        if substituted != len(replacements):
            logger.warning(
                "Repair substituted %d packet(s) of %d planned; abandoning.",
                substituted, len(replacements),
            )
            return False
    except _RepairCancelled:
        raise
    except Exception as exc:
        logger.warning("Audio repair remux failed: %s", exc)
        return False
    finally:
        for handle in (out, inp):
            try:
                if handle is not None:
                    handle.close()
            except Exception:
                pass
    return os.path.exists(dst) and os.path.getsize(dst) > 0
