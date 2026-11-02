"""DVB teletext in a transport stream, which PyAV can carry but not describe.

PyAV's own FFmpeg is built without libzvbi, so it has no teletext decoder and
a teletext stream comes back with no codec context at all.  Everything that
asks a subtitle stream for its codec, or copies one with
add_stream_from_template(), then fails - a .ts save of a recording carrying
teletext stopped with "template stream of type subtitle has no codec
context" (reported 2026-10-27, a recording from outside the UK; Freeview
carries none).

The packets themselves need no decoder: they are copied as they are.  What
is lost is the stream's description - the PMT's teletext descriptor, which
says which page holds the subtitles (888 is usual).  FFmpeg keeps it as the
stream's extradata, PyAV cannot set extradata without a codec context, and
the muxer then writes "initial page 100" for every language: the subtitles
are still there, but a player no longer knows where.  So the source's
descriptors are read from its PMT here and written back into the output's
once it is closed.

The PID is the link between the two: PyAV's Stream.id is the stream's PID in
a transport stream.
"""

import logging

logger = logging.getLogger("snipwright")

TS_PACKET = 188
# Teletext descriptor (EN 300 468 6.2.43); the ES carrying it is teletext.
TELETEXT_TAG = 0x56
# How far into a file to look for the PMT.  Broadcasters repeat it every
# 100 ms or so; ten megabytes is several seconds of even an HD recording.
_SCAN_BYTES = 10 * 1024 * 1024


def _crc32(data):
    crc = 0xFFFFFFFF
    for b in data:
        crc ^= b << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) if crc & 0x80000000 else crc << 1
            crc &= 0xFFFFFFFF
    return crc


def _section_start(p):
    """Offset of a section in a packet that starts one, else None."""
    if p[0] != 0x47 or not p[1] & 0x40:
        return None
    afc = (p[3] >> 4) & 3
    if not afc & 1:
        return None
    i = 4 + (1 + p[4] if afc & 2 else 0)
    if i >= TS_PACKET:
        return None
    i += 1 + p[i]          # pointer field
    return i if i < TS_PACKET - 3 else None


def _pid(p):
    return ((p[1] & 0x1F) << 8) | p[2]


def _pmt_streams(sec):
    """[(stream_type, pid, descriptors bytes)] from a whole PMT section."""
    length = ((sec[1] & 0x0F) << 8) | sec[2]
    end = 3 + length - 4
    j = 12 + (((sec[10] & 0x0F) << 8) | sec[11])
    out = []
    while j + 5 <= end:
        es_len = ((sec[j + 3] & 0x0F) << 8) | sec[j + 4]
        out.append((sec[j], ((sec[j + 1] & 0x1F) << 8) | sec[j + 2],
                    bytes(sec[j + 5:j + 5 + es_len])))
        j += 5 + es_len
    return out


def _descriptor(descs, tag):
    k = 0
    while k + 2 <= len(descs):
        if descs[k] == tag:
            return bytes(descs[k:k + 2 + descs[k + 1]])
        k += 2 + descs[k + 1]
    return None


def _pmt_pids(p, at):
    """PMT PIDs from a PAT section starting at `at`, or None."""
    if p[at] != 0x00:
        return None
    length = ((p[at + 1] & 0x0F) << 8) | p[at + 2]
    pids = set()
    for j in range(at + 8, min(at + 3 + length - 4, TS_PACKET - 3), 4):
        if (p[j] << 8) | p[j + 1]:
            pids.add(((p[j + 2] & 0x1F) << 8) | p[j + 3])
    return pids


def teletext_streams(path):
    """{pid: whole teletext descriptor} for every teletext stream in a .ts.

    Empty for anything else, or if the PMT cannot be found or read.
    """
    try:
        with open(path, "rb") as f:
            data = f.read(_SCAN_BYTES)
    except OSError:
        return {}
    # Find the packet grid: a sync byte that repeats every 188 bytes.
    start = next((o for o in range(min(TS_PACKET, len(data)))
                  if all(data[o + k * TS_PACKET:o + k * TS_PACKET + 1] == b"\x47"
                         for k in range(5))), None)
    if start is None:
        return {}
    pmt_pids = set()
    for off in range(start, len(data) - TS_PACKET + 1, TS_PACKET):
        p = data[off:off + TS_PACKET]
        at = _section_start(p)
        if at is None:
            continue
        pid = _pid(p)
        if pid == 0:
            pmt_pids |= _pmt_pids(p, at) or set()
            continue
        if pid not in pmt_pids or p[at] != 0x02:
            continue
        length = ((p[at + 1] & 0x0F) << 8) | p[at + 2]
        if at + 3 + length > TS_PACKET:
            continue        # a PMT spread over several packets: not here
        found = {}
        for _type, es_pid, descs in _pmt_streams(p[at:at + 3 + length]):
            d = _descriptor(descs, TELETEXT_TAG)
            if d is not None:
                found[es_pid] = d
        return found
    return {}


def restore_descriptors(path, wanted):
    """Put the source's teletext descriptors back into a written .ts.

    `wanted` is the list of whole descriptors, in the order the teletext
    streams were added to the output - which is also their order in its PMT.
    Rewrites every PMT packet in place; the section changes length only if a
    descriptor does, and a PMT that would outgrow its packet is left alone.
    Returns True when the PMT was rewritten.
    """
    if not wanted:
        return False
    cache = {}
    pmt_pids = set()
    changed = 0
    try:
        with open(path, "r+b") as f:
            pos = 0
            while True:
                f.seek(pos)
                chunk = bytearray(f.read(TS_PACKET * 8192))
                if len(chunk) < TS_PACKET:
                    break
                dirty = False
                for off in range(0, len(chunk) - TS_PACKET + 1, TS_PACKET):
                    p = chunk[off:off + TS_PACKET]
                    at = _section_start(p)
                    if at is None:
                        continue
                    pid = _pid(p)
                    if pid == 0:
                        pmt_pids |= _pmt_pids(p, at) or set()
                        continue
                    if pid not in pmt_pids or p[at] != 0x02:
                        continue
                    length = ((p[at + 1] & 0x0F) << 8) | p[at + 2]
                    if at + 3 + length > TS_PACKET:
                        continue
                    sec = bytes(p[at:at + 3 + length])
                    new = cache.get(sec)
                    if new is None:
                        new = _rewrite_pmt(sec, wanted)
                        cache[sec] = new
                    if new == sec or at + len(new) > TS_PACKET:
                        continue
                    p[at:at + len(new)] = new
                    p[at + len(new):] = b"\xff" * (TS_PACKET - at - len(new))
                    chunk[off:off + TS_PACKET] = p
                    dirty = True
                    changed += 1
                if dirty:
                    f.seek(pos)
                    f.write(chunk)
                pos += len(chunk) - len(chunk) % TS_PACKET
    except OSError as e:
        logger.warning("Teletext: could not restore its page details in %s: %s",
                       path, e)
        return False
    if changed:
        logger.debug("Teletext: page details restored in %d PMT packet(s)",
                     changed)
    return bool(changed)


def _rewrite_pmt(sec, wanted):
    """A PMT section with its teletext descriptors replaced by `wanted`."""
    pil = ((sec[10] & 0x0F) << 8) | sec[11]
    body = bytearray(sec[3:12 + pil])
    queue = list(wanted)
    for st, pid, descs in _pmt_streams(sec):
        out = bytearray()
        k = 0
        while k + 2 <= len(descs):
            tag, dl = descs[k], descs[k + 1]
            if tag == TELETEXT_TAG and queue:
                out += queue.pop(0)
            else:
                out += descs[k:k + 2 + dl]
            k += 2 + dl
        body += bytes([st, 0xE0 | (pid >> 8), pid & 0xFF,
                       0xF0 | (len(out) >> 8), len(out) & 0xFF]) + out
    seclen = len(body) + 4
    whole = bytes([sec[0], (sec[1] & 0xF0) | (seclen >> 8), seclen & 0xFF]) \
        + bytes(body)
    return whole + _crc32(whole).to_bytes(4, "big")
