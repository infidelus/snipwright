"""Carry DVB subtitles through a re-encoded join (item 1w).

A join of scenes that don't match is re-encoded through an ffmpeg concat
FILTER, which takes picture and sound only - so broadcast subtitles, which
are pictures on their own timeline, used to be dropped (2.9.0 at least said
so).  This puts them back: each scene's subtitles are taken from its rendered
segment, moved to that scene's place in the joined timeline, and muxed beside
the re-encoded picture and sound.

**One canvas for the whole stream.**  DVB subtitles are drawn for a canvas:
an HD broadcast declares 1920x1080 in every display set, an SD one declares
nothing and so means 720x576.  Copying both into one stream gives a stream
whose canvas changes part-way through.  mpv copes; FFmpeg's renderer does
not - it fixes its canvas at the first subtitle, and later ones drawn for a
bigger canvas fall outside it and vanish - and Jellyfin burns subtitles in
with that renderer whenever its client can't draw DVB itself (a web
browser).  Measured on a join of ITV1 SD and Channel 4 HD (2026-10-02): the
copied stream lost the HD half in Jellyfin; this module's output showed both
halves in mpv and in Jellyfin.  So a scene whose subtitles were drawn for a
different canvas from the joined video is REDRAWN: its pictures scaled and
placed exactly as the Joiner scales and places the picture beneath them,
and written out as fresh DVB data declaring the joined video's size.  A
scene already drawn for that size is copied untouched.

**Different channels use different page ids** (ITV1 SD page 2, Channel 4 HD
page 1).  A decoder follows one page and ignores the rest, so every scene is
moved to page 1.

**Colours come from the stream, not the decoder.**  PyAV hands over a
decoded subtitle's pixels but not its palette, so the colour tables (CLUT
segments) are read from the data itself, tracking regions and tables across
display sets as a decoder does.  Checked against FFmpeg's decode on both
test slices: all 113 pictures found their region and a complete table.

**Two traps, both measured.**  FFmpeg 6.1's decoder stops reading a line the
moment it reaches the region's width and then rejects the end-of-line code
("Invalid object location!"); FFmpeg 8 does not mind.  Broadcast encoders
never code a line to the edge, so neither does this: trailing transparent
pixels are left uncoded, the region is filled transparent first, and every
region gets one spare transparent column.  And a DVB subtitle stays up until
something replaces it or it times out, so each scene ends with an empty
display set - otherwise one scene's last subtitle could hang over the next.

**A disc's PGS subtitles are converted to DVB** (2.10.0).  The transport
stream the join is built in cannot hold PGS, and a scene's render has
already dropped them, so they are read from the scene's SOURCE recording over
its time range.  PGS is pictures and colour tables too: PyAV decodes the
pixels, the palette is read from the palette segments as for DVB, alpha
becomes DVB's transparency (T = 255 - alpha), and the writer below turns
them into DVB in the same single stream as the broadcasts'.  Two DVB rules
bite: a luma of 0 means "fully transparent" whatever T says, so a visible
colour is never written with Y 0; and the writer leaves trailing colour-0
pixels uncoded, so a palette whose transparent entry is not 0 is renumbered
until it is.  Measured on the user's Blu-ray slice (2026-10-03): 29
pictures, every one with a complete palette and its position as the
composition gives it.

Teletext is a different thing again; the caller reports anything left
behind.
"""

import logging
from fractions import Fraction

import av
import numpy as np

from smartcut.open_options import LEGACY_OPEN_ARGS, SOURCE_OPEN_OPTIONS

# The application's own logger, as every other module uses - a module-named
# logger never reaches Snipwright's log file.
log = logging.getLogger("snipwright")

PAGE = 1                       # the one page id every scene is moved to
# The page time-out for subtitles converted from PGS.  A DVB page time-out is
# how long a subtitle may stay up, and FFmpeg takes 0 literally - the first
# conversion wrote 0 and FFmpeg showed every disc subtitle for no time at
# all.  PGS ends each subtitle with an explicit clear, which
# is converted too, so this only has to be longer than any subtitle lasts.
PGS_TIMEOUT = 60
SD_CANVAS = (720, 576)         # what a set with no display definition means
# PyAV names the DECODER ("dvbsub"); FFmpeg's codec id is "dvb_subtitle".
DVB_CODECS = ("dvbsub", "dvb_subtitle")
PGS_CODECS = ("pgssub", "hdmv_pgs_subtitle")
# Every kind a re-encoded join can carry.
CARRIED_CODECS = DVB_CODECS + PGS_CODECS


# -- reading DVB ------------------------------------------------------------

def _segments(data):
    """(type, page, body) for each segment of one PES payload."""
    i = 0
    while i + 6 <= len(data) and data[i] == 0x0F:
        typ = data[i + 1]
        page = int.from_bytes(data[i + 2:i + 4], "big")
        size = int.from_bytes(data[i + 4:i + 6], "big")
        yield typ, page, data[i + 6:i + 6 + size]
        i += 6 + size


class _State:
    """Regions, colour tables, page layout and canvas, as a decoder keeps them.

    Region and CLUT definitions persist between display sets - a set may
    redefine only what changed - so they are tracked across the whole
    stream, not read per packet.
    """

    def __init__(self):
        self.regions = {}      # id -> {"w", "h", "clut"}
        self.cluts = {}        # id -> {entry: (Y, Cr, Cb, T)}
        self.page = []         # [(region id, x, y)]
        self.canvas = SD_CANVAS
        self.declared = False  # a display definition has been seen
        self.timeout = 10

    def feed(self, data):
        for typ, _page, b in _segments(data):
            if typ == 0x10 and b:                       # page composition
                self.timeout = b[0]
                self.page = [(b[i], int.from_bytes(b[i + 2:i + 4], "big"),
                              int.from_bytes(b[i + 4:i + 6], "big"))
                             for i in range(2, len(b) - 5, 6)]
            elif typ == 0x11 and len(b) >= 8:           # region composition
                self.regions[b[0]] = {
                    "w": int.from_bytes(b[2:4], "big"),
                    "h": int.from_bytes(b[4:6], "big"),
                    "clut": b[7],
                }
            elif typ == 0x12 and b:                     # CLUT definition
                table = self.cluts.setdefault(b[0], {})
                i = 2
                while i + 2 <= len(b):
                    entry, flags = b[i], b[i + 1]
                    if flags & 0x01:                    # full range
                        if i + 6 > len(b):
                            break
                        table[entry] = tuple(b[i + 2:i + 6])
                        i += 6
                    else:                               # reduced range
                        if i + 4 > len(b):
                            break
                        v = int.from_bytes(b[i + 2:i + 4], "big")
                        table[entry] = ((v >> 10) << 2, ((v >> 6) & 0xF) << 4,
                                        ((v >> 2) & 0xF) << 4, (v & 0x3) << 6)
                        i += 4
            elif typ == 0x14 and len(b) >= 5:           # display definition
                self.canvas = (int.from_bytes(b[1:3], "big") + 1,
                               int.from_bytes(b[3:5], "big") + 1)
                self.declared = True

    def palette_for(self, rect):
        """The colour table of the region a decoded rectangle came from."""
        for rid, x, y in self.page:
            region = self.regions.get(rid)
            if region and (x, y, region["w"], region["h"]) == (
                    rect.x, rect.y, rect.width, rect.height):
                return self.cluts.get(region["clut"], {})
        return None


class _PgsState:
    """A PGS stream's palettes, current palette and canvas, as a decoder keeps
    them.  A presentation composition names the palette its objects use."""

    def __init__(self):
        self.palettes = {}     # id -> {entry: (Y, Cr, Cb, alpha)}
        self.palette_id = 0
        self.canvas = (1920, 1080)

    @staticmethod
    def _segments(data):
        i = 0
        while i + 3 <= len(data):
            typ, size = data[i], int.from_bytes(data[i + 1:i + 3], "big")
            yield typ, data[i + 3:i + 3 + size]
            i += 3 + size

    def feed(self, data):
        for typ, b in self._segments(data):
            if typ == 0x16 and len(b) >= 11:            # presentation composition
                self.canvas = (int.from_bytes(b[0:2], "big"),
                               int.from_bytes(b[2:4], "big"))
                self.palette_id = b[9]
            elif typ == 0x14 and len(b) >= 2:           # palette definition
                table = self.palettes.setdefault(b[0], {})
                for i in range(2, len(b) - 4, 5):
                    table[b[i]] = (b[i + 1], b[i + 2], b[i + 3], b[i + 4])

    def dvb_palette(self):
        """The current palette in DVB's terms, and the colour number that must
        be swapped with 0 so that 0 is transparent (None when it already is)."""
        out = {}
        for entry, (y, cr, cb, alpha) in self.palettes.get(self.palette_id, {}).items():
            if alpha:
                y = max(y, 16)          # DVB: luma 0 means transparent
            out[entry] = (y, cr, cb, 255 - alpha)
        if out.get(0, (0, 0, 0, 255))[3] == 255:
            return out, None
        clear = next((e for e, v in sorted(out.items()) if v[3] == 255), None)
        if clear is None:
            clear = next(e for e in range(256) if e not in out)
            out[clear] = (16, 128, 128, 255)
        out[0], out[clear] = out[clear], out.get(0, (16, 128, 128, 255))
        return out, clear


# -- writing DVB ------------------------------------------------------------

class _Writer:
    """Builds display sets; version numbers advance as a stream's must."""

    def __init__(self, canvas):
        self.canvas = canvas
        self._page_version = 0
        self._object_version = 0

    @staticmethod
    def _segment(typ, body):
        return (bytes([0x0F, typ]) + PAGE.to_bytes(2, "big")
                + len(body).to_bytes(2, "big") + body)

    def _display_definition(self):
        w, h = self.canvas
        return self._segment(0x14, bytes([0x00]) + (w - 1).to_bytes(2, "big")
                             + (h - 1).to_bytes(2, "big"))

    def _next_page_version(self):
        self._page_version = (self._page_version + 1) % 16
        return self._page_version

    @staticmethod
    def _code_line(row):
        """One line as an 8-bit/pixel code string - never to the edge."""
        nonzero = np.nonzero(row)[0]
        n = int(nonzero[-1]) + 1 if len(nonzero) else 0
        out = bytearray([0x12])
        i = 0
        while i < n:
            p = int(row[i])
            j = i
            while j < n and row[j] == p and j - i < 127:
                j += 1
            run = j - i
            if p == 0:
                out += bytes([0x00, run])               # run of colour 0
            elif run >= 3:
                out += bytes([0x00, 0x80 | run, p])     # run of colour p
            else:
                out += bytes([p]) * run
            i = j
        out += bytes([0x00, 0x00, 0xF0])               # end string, end line
        return bytes(out)

    def display(self, pictures, timeout):
        """A complete display set (mode change) showing `pictures`:
        (x, y, pixels[h][w] of colour numbers, {entry: (Y, Cr, Cb, T)})."""
        version = self._next_page_version()
        page = bytearray([timeout, (version << 4) | (0x2 << 2) | 0x3])
        for i, (x, y, _pix, _pal) in enumerate(pictures):
            page += bytes([i, 0xFF]) + x.to_bytes(2, "big") + y.to_bytes(2, "big")
        parts = [self._display_definition(), self._segment(0x10, bytes(page))]
        for i, (_x, _y, pix, pal) in enumerate(pictures):
            pix = np.pad(pix, ((0, 0), (0, 1)))         # spare transparent column
            h, w = pix.shape
            region = (bytes([i, (version << 4) | 0x0F])  # fill flag set
                      + w.to_bytes(2, "big") + h.to_bytes(2, "big")
                      + bytes([0x6F, i, 0x00, 0x03])     # 8-bit, CLUT i
                      + i.to_bytes(2, "big") + bytes([0x00, 0x00, 0xF0, 0x00]))
            parts.append(self._segment(0x11, region))
            clut = bytearray([i, (version << 4) | 0x0F])
            for entry, (yy, cr, cb, t) in sorted(pal.items()):
                clut += bytes([entry, 0x3F, yy, cr, cb, t])   # 8-bit, full range
            parts.append(self._segment(0x12, bytes(clut)))
            top = b"".join(self._code_line(r) for r in pix[0::2])
            bottom = b"".join(self._code_line(r) for r in pix[1::2])
            self._object_version = (self._object_version + 1) % 16
            obj = (i.to_bytes(2, "big") + bytes([(self._object_version << 4) | 0x01])
                   + len(top).to_bytes(2, "big") + len(bottom).to_bytes(2, "big")
                   + top + bottom)
            parts.append(self._segment(0x13, obj))
        parts.append(self._segment(0x80, b""))
        return b"".join(parts)

    def clear(self):
        """An empty display set: whatever was shown goes."""
        version = self._next_page_version()
        return (self._display_definition()
                + self._segment(0x10, bytes([0, (version << 4) | (0x2 << 2) | 0x3]))
                + self._segment(0x80, b""))

    def renumber(self, data):
        """A display set as it was, moved to the common page."""
        return b"".join(self._segment(t, b) for t, _p, b in _segments(data))


# -- the join ---------------------------------------------------------------

def _picture_area(video_stream, target):
    """Where a scene's picture sits on the joined frame.

    The same arithmetic as the Joiner's filter: un-anamorphic to the display
    width (scale=trunc(iw*sar/2)*2:ih), fit inside the target keeping the
    aspect, centred on padding.
    """
    tw, th = target
    sar = video_stream.sample_aspect_ratio or Fraction(1)
    dw = int(video_stream.width * sar / 2) * 2 or video_stream.width
    dh = video_stream.height
    f = min(tw / dw, th / dh)
    pw = int(round(dw * f / 2)) * 2
    ph = int(round(dh * f / 2)) * 2
    return (tw - pw) // 2, (th - ph) // 2, pw, ph


def _rendered_length(path):
    """A rendered scene's picture length - what the concat filter consumed."""
    try:
        with av.open(path) as c:
            v = c.streams.video[0]
            if v.duration:
                return float(v.duration * v.time_base)
            if v.frames and v.average_rate:
                return float(v.frames / v.average_rate)
    except Exception:
        pass
    return None


def subtitle_kinds(path):
    """The codec of each subtitle stream in a file - [] if it can't be read."""
    try:
        with av.open(path) as c:
            return [s.codec_context.name for s in c.streams.subtitles]
    except Exception:
        return []


def _scene_sets(path, offset, length, writer):
    """One scene's subtitle display sets, moved to `offset` in the join.

    Returns (sets, redrawn, language): sets is [(seconds, payload)].
    """
    with av.open(path) as c:
        dvb = [s for s in c.streams.subtitles
               if s.codec_context.name in DVB_CODECS]
        if not dvb or not c.streams.video:
            return [], False, ""
        sub, video = dvb[0], c.streams.video[0]
        language = sub.metadata.get("language", "") or ""
        vstart = float((video.start_time or 0) * video.time_base)
        px, py, pw, ph = _picture_area(video, writer.canvas)
        state = _State()
        sets = []
        redraw = None
        for packet in c.demux(sub):
            if packet.pts is None:
                continue
            data = bytes(packet)
            state.feed(data)
            if redraw is None:
                # Decided on the first set, once its canvas is known.
                redraw = not (state.canvas == writer.canvas
                              and (px, py, pw, ph) == (0, 0) + writer.canvas)
            pictures = [r for r in packet.decode() if getattr(r, "width", 0)]
            rel = float(packet.pts * sub.time_base) - vstart
            if not 0 <= rel < length:
                continue
            if not redraw:
                sets.append((offset + rel, writer.renumber(data)))
                continue
            sx = pw / state.canvas[0]
            sy = ph / state.canvas[1]
            drawn = []
            for r in pictures:
                palette = state.palette_for(r)
                if palette is None:
                    log.warning("Subtitles: a picture in %s matched no region; "
                                "it is left out.", path)
                    continue
                stride = r.planes[0].buffer_size // max(1, r.height)
                src = np.frombuffer(bytes(r.planes[0]), np.uint8)
                src = src.reshape(r.height, stride)[:, :r.width]
                nw = max(1, round(r.width * sx))
                nh = max(1, round(r.height * sy))
                rows = np.minimum((np.arange(nh) / sy).astype(int), r.height - 1)
                cols = np.minimum((np.arange(nw) / sx).astype(int), r.width - 1)
                drawn.append((px + round(r.x * sx), py + round(r.y * sy),
                              src[rows][:, cols], palette))
            sets.append((offset + rel,
                         writer.display(drawn, state.timeout) if drawn
                         else writer.clear()))
        sets.append((offset + length, writer.clear()))
        return sets, bool(redraw), language


def _scene_sets_pgs(path, start, offset, length, writer):
    """A disc scene's PGS subtitles, converted to DVB and moved to `offset`.

    Read from the SOURCE recording between `start` and `start + length` -
    the rendered scene no longer has them.  The demuxer is put just before
    the scene first: a Blu-ray rip runs to gigabytes, and reading it from the
    top for one scene near its end would cost minutes.
    """
    with av.open(path) as c:
        pgs = [s for s in c.streams.subtitles
               if s.codec_context.name in PGS_CODECS]
        if not pgs or not c.streams.video:
            return [], ""
        sub, video = pgs[0], c.streams.video[0]
        language = sub.metadata.get("language", "") or ""
        vstart = float((video.start_time or 0) * video.time_base)
        try:
            c.seek(int(max(0.0, vstart + start - 30.0) * 1_000_000))
        except Exception:
            pass                       # read from the top instead
        px, py, pw, ph = _picture_area(video, writer.canvas)
        state = _PgsState()
        sets = []
        for packet in c.demux(sub):
            if packet.pts is None:
                continue
            state.feed(bytes(packet))
            pictures = [r for r in packet.decode() if getattr(r, "width", 0)]
            rel = float(packet.pts * sub.time_base) - vstart - start
            if rel >= length:
                break
            if rel < 0:
                continue
            palette, swap = state.dvb_palette()
            sx, sy = pw / state.canvas[0], ph / state.canvas[1]
            drawn = []
            for r in pictures:
                stride = r.planes[0].buffer_size // max(1, r.height)
                src = np.frombuffer(bytes(r.planes[0]), np.uint8)
                src = src.reshape(r.height, stride)[:, :r.width].copy()
                if swap is not None:
                    zero, other = src == 0, src == swap
                    src[zero], src[other] = swap, 0
                nw, nh = max(1, round(r.width * sx)), max(1, round(r.height * sy))
                rows = np.minimum((np.arange(nh) / sy).astype(int), r.height - 1)
                cols = np.minimum((np.arange(nw) / sx).astype(int), r.width - 1)
                drawn.append((px + round(r.x * sx), py + round(r.y * sy),
                              src[rows][:, cols], palette))
            sets.append((offset + rel,
                         writer.display(drawn, PGS_TIMEOUT) if drawn
                         else writer.clear()))
        sets.append((offset + length, writer.clear()))
        return sets, language


def carry_dvb_subtitles(joined, out_path, segments, durations, sources=None):
    """Write `joined` to `out_path` with its scenes' DVB subtitles added.

    `segments` are the rendered scenes in join order and `durations` the
    length each was meant to have.  Each scene's place in the join is worked
    out from what was actually RENDERED where that can be read - the concat
    filter joins the frames it was given, and a difference of a frame or two
    per scene would add up across a long join and leave later subtitles out
    of step - and from `durations` otherwise.  `sources` gives, per scene,
    (source recording, start in seconds) or None: a scene whose rendered
    segment has no DVB but whose source has PGS has its subtitles converted
    from the source.  Returns a summary dict, or None when no scene had
    subtitles to carry (and nothing was written).
    """
    with av.open(joined) as probe:
        v = probe.streams.video[0]
        canvas = (v.width, v.height)
        base = float((v.start_time or 0) * v.time_base)
    writer = _Writer(canvas)
    sets, carried, redrawn, converted, language = [], 0, 0, 0, ""
    offset = 0.0
    sources = sources or [None] * len(segments)
    for seg, planned, source in zip(segments, durations, sources):
        length = _rendered_length(seg) or planned
        got, was_redrawn, lang = _scene_sets(seg, base + offset, length, writer)
        if not got and source:
            got, lang = _scene_sets_pgs(source[0], source[1], base + offset,
                                        length, writer)
            converted += bool(got)
        if got:
            sets += got
            carried += 1
            redrawn += was_redrawn
            language = language or lang
        offset += length
    if not carried:
        return None

    # Opened with the deep probe every source open uses.  A sparse
    # audio-description track - sent only while the narrator speaks - can
    # have its first packet well into the join, and a default probe gives up
    # before then: the track reads 0 Hz, 0 channels, the stream copied from it
    # is refused when the header is written (EINVAL), and the join was saved
    # without its subtitles.  Seen joining a U&Drama SD scene to a BBC Three HD
    # one, on PyAV 18 and 19 alike.
    src = av.open(joined, options=SOURCE_OPEN_OPTIONS, **LEGACY_OPEN_ARGS)
    dst = av.open(out_path, "w", format="mpegts")
    try:
        mapping = {}
        for stream in src.streams:
            if stream.type in ("video", "audio"):
                mapping[stream.index] = dst.add_stream_from_template(stream)
        out_sub = dst.add_stream("dvbsub")
        # Composition and ancillary page, then subtitling type 0x10: what the
        # PMT's subtitling descriptor is built from.
        out_sub.codec_context.extradata = PAGE.to_bytes(2, "big") * 2 + bytes([0x10])
        if language:
            out_sub.metadata["language"] = language
        items = [(float(p.dts * p.time_base), mapping[p.stream.index], p)
                 for p in src.demux(*[src.streams[i] for i in mapping])
                 if p.dts is not None]
        for when, payload in sets:
            p = av.Packet(payload)
            p.time_base = Fraction(1, 90000)
            p.pts = p.dts = int(round(when * 90000))
            items.append((when, out_sub, p))
        items.sort(key=lambda item: item[0])
        for _when, stream, packet in items:
            packet.stream = stream
            dst.mux(packet)
    finally:
        dst.close()
        src.close()
    log.info("Subtitles: carried %d scene(s) through the join "
             "(%d redrawn for %dx%d, %d converted from PGS), %d display set(s).",
             carried, redrawn, canvas[0], canvas[1], converted, len(sets))
    return {"carried": carried, "redrawn": redrawn, "converted": converted,
            "sets": len(sets), "canvas": canvas}
