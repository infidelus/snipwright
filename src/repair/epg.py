"""The broadcaster's own "now and next" (DVB EIT present/following).

Item 1ac.  A recording's tail is the end of its programme followed by
continuity and the next programme - and the next programme carries the
channel's logo, so the detector, which reads the logo, sees "programme" and
stops trimming.  Across the corpus it found the programme's end within a few
seconds on most recordings and then left 400-600 s uncut after it.

The recording says where the next programme begins, in its own words.  A
DVB transport stream carries the EPG's present/following table (EIT p/f,
PID 0x12, table 0x4E): which programme is on now, and which is next.  When
the broadcaster switches "now" from this programme to the next one, what
follows is, by the broadcaster's own account, not this programme.  Measured
over 26 corpus recordings that carry it, that switch came AFTER the user's
corrected programme end on every one - from +1 s to +410 s, median +163 s:
broadcasters switch on the schedule, and programmes run a little short of
their slot.  So it is a safe outer limit for the programme, never inside it.

Not every recorder keeps the table.  Tvheadend does; the corpus's other
recorder (broadcast service numbers, no service name, SCTE-35 streams)
records none, and those recordings come out of this with nothing - which
leaves detection exactly as it was.

Reading it costs one pass over the file with numpy and no decoding: only the
EIT PID's packets are reassembled, and only sections of table 0x4E for this
recording's service are CRC-checked and parsed, which is what keeps it quick
(the first measuring script checked every EIT section, schedule tables and
all - 650,000 of them in a 700 MB file).
"""

import numpy as np

_CHUNK = 188 * 400_000

# Video stream types in a PMT: MPEG-2, MPEG-2 (11172), H.264, HEVC.
_VIDEO_TYPES = (0x01, 0x02, 0x1B, 0x24)


def _payload(row):
    afc = (row[3] >> 4) & 3
    p = 4
    if afc & 2:
        p = 5 + row[4]
    return bytes(row[p:188]) if afc & 1 and p < 188 else b""


def _crc32_mpeg(data):
    crc = 0xFFFFFFFF
    for b in data:
        crc ^= b << 24
        for _ in range(8):
            crc = (((crc << 1) ^ 0x04C11DB7) if crc & 0x80000000
                   else (crc << 1)) & 0xFFFFFFFF
    return crc


def _bcd(b):
    return (b >> 4) * 10 + (b & 0xF)


def _sync_offset(fh):
    head = fh.read(188 * 2000)
    off = head.find(b"\x47")
    while 0 <= off and off + 188 < len(head) and head[off + 188] != 0x47:
        off = head.find(b"\x47", off + 1)
    return max(off, 0)


def _programme_ids(path, off):
    """(service_id, video_pid) from the first PAT and its PMT, or Nones.

    Read BEFORE the main pass on purpose: learning them during it meant the
    first block of the file - about ten minutes of a recording - took no
    timestamps, and every time came out that much early.
    """
    service = pmt_pid = None
    with open(path, "rb") as fh:
        fh.seek(off)
        for _ in range(200):
            raw = fh.read(188 * 10000)
            if len(raw) < 188:
                break
            for k in range(0, len(raw) - 187, 188):
                row = raw[k:k + 188]
                if row[0] != 0x47 or not row[1] & 0x40:
                    continue
                pid = ((row[1] & 0x1F) << 8) | row[2]
                pl = _payload(row)
                if not pl or 1 + pl[0] >= len(pl):
                    continue
                s = pl[1 + pl[0]:]
                if len(s) < 13:
                    continue
                if pid == 0 and service is None:
                    end = 3 + (((s[1] & 0xF) << 8) | s[2]) - 4
                    for j in range(8, min(end, len(s) - 3), 4):
                        prog = s[j] << 8 | s[j + 1]
                        if prog:
                            service = prog
                            pmt_pid = ((s[j + 2] & 0x1F) << 8) | s[j + 3]
                            break
                elif pmt_pid is not None and pid == pmt_pid:
                    end = 3 + (((s[1] & 0xF) << 8) | s[2]) - 4
                    j = 12 + (((s[10] & 0xF) << 8) | s[11])
                    while j + 4 < min(end, len(s)):
                        ep = ((s[j + 1] & 0x1F) << 8) | s[j + 2]
                        if s[j] in _VIDEO_TYPES:
                            return service, ep
                        j += 5 + (((s[j + 3] & 0xF) << 8) | s[j + 4])
    return service, None


def present_events(path, cancel_cb=None):
    """Each change of the EPG's "now" event, as (seconds, event_id, duration).

    Seconds are from the recording's FIRST VIDEO FRAME, read from the video's
    own timestamps.  Empty when the recording carries no EIT, no PAT/PMT the
    reader understands, or no video timestamps - in every such case the
    caller simply has nothing to go on.
    """
    try:
        with open(path, "rb") as fh:
            off = _sync_offset(fh)
        service, vpid = _programme_ids(path, off)
    except OSError:
        return []
    if vpid is None:
        return []

    marks_i, marks_pts = [], []
    sections = []                      # (packet index, section bytes)
    buf = None                         # EIT section being reassembled
    buf_at = 0
    idx0 = 0
    with open(path, "rb") as fh:
        fh.seek(off)
        while True:
            if cancel_cb is not None and cancel_cb():
                return []
            at = fh.tell()
            raw = fh.read(_CHUNK)
            if len(raw) < 188:
                break
            n = len(raw) // 188
            a = np.frombuffer(raw[:n * 188], dtype=np.uint8).reshape(n, 188)
            sync = a[:, 0] == 0x47
            if not sync.all():
                # A damaged packet: keep what came before it and re-find the
                # sync pattern - without this the reader lost alignment and
                # silently stopped part-way through the file.
                bad = int(np.argmin(sync))
                a = a[:bad]
                k = bad * 188 + 1
                while k + 188 < len(raw) and not (raw[k] == 0x47
                                                  and raw[k + 188] == 0x47):
                    k += 1
                fh.seek(at + k)
                n = bad
            pid = ((a[:, 1].astype(np.int32) & 0x1F) << 8) | a[:, 2]
            pusi = (a[:, 1] & 0x40) != 0
            # Video timestamps, about one a second, to place a packet in time.
            for i in np.where((pid == vpid) & pusi)[0][::25]:
                pl = _payload(a[i])
                if (len(pl) > 14 and pl[:3] == b"\x00\x00\x01"
                        and pl[7] & 0x80):
                    q = pl[9:14]
                    marks_i.append(idx0 + int(i))
                    marks_pts.append(((q[0] >> 1) & 7) << 30 | q[1] << 22
                                     | (q[2] >> 1) << 15 | q[3] << 7
                                     | q[4] >> 1)
            for i in np.where(pid == 0x12)[0]:
                pl = _payload(a[i])
                if not pl:
                    continue
                if pusi[i]:
                    ptr = pl[0]
                    if buf is not None:
                        buf += pl[1:1 + ptr]
                        sections.append((buf_at, bytes(buf)))
                        buf = None
                    rest = pl[1 + ptr:]
                    # Only table 0x4E (present/following, this transport) is
                    # worth reassembling; the schedule tables that make up
                    # nearly all EIT traffic are skipped at the first byte.
                    if rest and rest[0] == 0x4E:
                        buf = bytearray(rest)
                        buf_at = idx0 + int(i)
                elif buf is not None:
                    buf += pl
            idx0 += n
    if len(marks_i) < 2:
        return []

    pts = np.unwrap(np.array(marks_pts, dtype=np.float64), period=2 ** 33)
    secs = (pts - pts.min()) / 90000.0
    pos = np.array(marks_i, dtype=np.float64)

    changes, last = [], None
    for i, raw in sections:
        if len(raw) < 3:
            continue
        ln = (((raw[1] & 0x0F) << 8) | raw[2]) + 3
        sec = raw[:ln]
        if len(sec) < ln or sec[0] != 0x4E or len(sec) < 30:
            continue
        sid = sec[3] << 8 | sec[4]
        if (service and sid != service) or sec[6] != 0:   # section 0 = "now"
            continue
        if _crc32_mpeg(sec) != 0:
            continue
        j = 14
        eid = sec[j] << 8 | sec[j + 1]
        dur = (_bcd(sec[j + 7]) * 3600 + _bcd(sec[j + 8]) * 60
               + _bcd(sec[j + 9]))
        key = (eid, bytes(sec[j + 2:j + 7]), dur)
        if key != last:
            t = float(np.interp(i, pos, secs))
            changes.append((t, eid, dur))
            last = key
    return changes


def programme_switch_out(changes, duration):
    """When the recording's programme gives way to the next, or None.

    The programme is the event that is "now" for the longest stretch of the
    recording - which needs nothing from the user's corrections, and picked
    the same event as the corrections did on all 26 corpus recordings.  The
    answer is the first later sighting of a DIFFERENT event.
    """
    spans = []
    for k, (t, eid, _d) in enumerate(changes):
        nxt = next((c[0] for c in changes[k + 1:] if c[1] != eid), duration)
        spans.append((nxt - t, k))
    if not spans:
        return None
    k = max(spans)[1]
    eid = changes[k][1]
    return next((c[0] for c in changes[k + 1:] if c[1] != eid), None)


# How close a detected break must come to the trim before it is joined to
# it.  Measured on run 43's breaks against the corrections: 10 s joined every
# break that belonged to the tail and cut no programme anywhere; 30 s cut
# 10 s of programme on more4-2, where a genuine break sits 30 s from the end.
EPG_TAIL_JOIN = 10.0

# A switch this close to the end leaves nothing worth trimming.
EPG_TAIL_MIN = 2.0


def epg_tail(breaks, switch_out, duration):
    """Trim from the EPG switch to the end, joined to breaks that reach it.

    Returns (breaks, info) where info is None when nothing changed, else
    (trim_start, switch_out, seconds_added).  Never moves the start of a
    break that already exists, and never starts a trim before the switch
    except by joining a break detection found - so it can only remove what
    the broadcaster says is not this programme, plus material detection
    already removes.
    """
    if switch_out is None or not duration:
        return breaks, None
    if switch_out >= duration - EPG_TAIL_MIN:
        return breaks, None
    start = switch_out
    for _ in range(len(breaks) + 1):
        moved = False
        for a, b in breaks:
            if a < start and b >= start - EPG_TAIL_JOIN:
                start, moved = a, True
        if not moved:
            break
    # Once the join has settled, every break starting before the trim ends
    # more than EPG_TAIL_JOIN before it; every other break is inside it.
    kept = [(a, b) for a, b in breaks if a < start]
    result = sorted(kept + [(start, duration)])
    added = (duration - start) - sum(min(b, duration) - max(a, start)
                                     for a, b in breaks if b > start)
    if added <= 0.5:
        return breaks, None
    return result, (start, switch_out, added)
