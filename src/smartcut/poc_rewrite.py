"""Renumber HEVC picture order counts across a splice.

Why this exists
---------------

Smartcut builds its output from two kinds of material: segments copied
straight from the source, and short stretches re-encoded at each cut
boundary.  The copied packets are byte-for-byte the source's, which means
they keep the source's own ``slice_pic_order_cnt_lsb``.

That is wrong as soon as the pieces are put in a different order.  A
picture's POC identifies it inside a coded video sequence, and two segments
taken from different points in the source will happily bring the same POC
with them.  Measured on a 10-bit HDR10 cut: two pictures both claiming POC
44, twenty-five pictures apart, one of them lost on decode.

It went unnoticed for a long time because it is normally masked.  The
boundary encoder writes its own SPS, which differs from the source's, so a
decoder re-initialises at every switch between copied and re-encoded
material and clears the earlier picture out of the DPB before the colliding
one arrives.  Give the encoder the source's colour description and x265
reproduces the source's SPS exactly - the stream becomes *more* correct -
the parameter sets stop differing, nothing re-initialises, and the
collision surfaces.  So the colour fix and this one have to land together.

What it does
------------

Each contiguous run of output pictures gets one constant POC offset, chosen
so the run clears the highest POC that could still be in the decoder's DPB.
The offset is constant across the run because the reference picture sets in
the slice headers are expressed as *deltas*: shift every picture in a run by
the same amount and every reference still points where it did.

Two rules govern where a run begins:

- An IDR always begins one, with offset zero.  An IDR empties the DPB, so it
  can never collide with anything before it - and it cannot be shifted even
  if we wanted to, because an IDR carries no ``slice_pic_order_cnt_lsb`` at
  all and a decoder fixes its POC at 0 regardless of what we write.  An
  early version of this shifted IDR runs along with the rest and turned one
  fault into another: `Could not find ref with POC 116`, the IDR sitting at
  0 while its own trailing pictures referenced 0+offset.
- A change of origin begins one - copied material giving way to re-encoded
  or the reverse, or two copied segments that are not adjacent in the
  source.  ``VideoCutter`` knows these outright and passes a run id in.

Sources whose keyframes are IDR (many commercial encodes) come out of this
unchanged, because every run then starts with an IDR and every offset is
zero.  Sources whose keyframes are CRA - DVB broadcast, and x265 with
open-GOP, which includes the project's own synthetic test files - are the
ones that need it.

Anything the parser is not certain of turns the rewriter off for the rest of
the export and the packets pass through untouched, which is exactly what
2.3.0 shipped.  Being wrong here corrupts a stream; doing nothing only
leaves it as it already was.
"""

import logging
import math

logger = logging.getLogger(__name__)

# NAL unit types (see nal_tools for the wider list).
_VCL = range(0, 22)
_IDR = (19, 20)
_IRAP = range(16, 22)
_SPS = 33
_PPS = 34
# Sub-layer non-reference and leading pictures never become prevTid0Pic.
_NOT_PREV_TID0 = (0, 2, 4, 6, 7, 8, 9)   # TRAIL_N, TSA_N, STSA_N, RADL_*, RASL_*


class _BitReader:
    __slots__ = ('d', 'pos')

    def __init__(self, data):
        self.d = data
        self.pos = 0

    def u(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | ((self.d[self.pos >> 3] >> (7 - (self.pos & 7))) & 1)
            self.pos += 1
        return v

    def ue(self):
        lz = 0
        while self.u(1) == 0:
            lz += 1
            if lz > 32:
                raise ValueError('malformed exp-Golomb code')
        return 0 if lz == 0 else (1 << lz) - 1 + self.u(lz)

    def se(self):
        k = self.ue()
        return (k + 1) // 2 if k % 2 else -(k // 2)


def _unescape(data):
    """Remove emulation prevention bytes (00 00 03 -> 00 00)."""
    if b'\x00\x00\x03' not in data:
        return data
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if i + 2 < n and data[i] == 0 and data[i + 1] == 0 and data[i + 2] == 3:
            out += b'\x00\x00'
            i += 3
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


def _escape(data):
    """Re-insert emulation prevention bytes."""
    out = bytearray()
    zeros = 0
    for b in data:
        if zeros >= 2 and b <= 3:
            out.append(3)
            zeros = 0
        out.append(b)
        zeros = zeros + 1 if b == 0 else 0
    return bytes(out)


def _split_nals(stream):
    """Yield (start, end) of each NAL unit payload in an Annex B stream."""
    starts = []
    i = 0
    while True:
        j = stream.find(b'\x00\x00\x01', i)
        if j < 0:
            break
        starts.append(j + 3)
        i = j + 3
    n = len(stream)
    for k, s in enumerate(starts):
        e = n if k + 1 == len(starts) else starts[k + 1] - 3
        # A four-byte start code borrows its leading zero from the previous
        # unit's tail; give it back so payloads do not overlap.
        while e > s and stream[e - 1] == 0:
            e -= 1
        yield s, e


def _parse_ptl(r, max_sub_layers):
    r.u(2); r.u(1); r.u(5); r.u(32)
    r.u(1); r.u(1); r.u(1); r.u(1)
    r.u(32); r.u(12); r.u(8)
    sub_profile, sub_level = [], []
    for _ in range(max_sub_layers - 1):
        sub_profile.append(r.u(1))
        sub_level.append(r.u(1))
    if max_sub_layers > 1:
        for _ in range(max_sub_layers - 1, 8):
            r.u(2)
    for i in range(max_sub_layers - 1):
        if sub_profile[i]:
            r.u(2); r.u(1); r.u(5); r.u(32)
            r.u(1); r.u(1); r.u(1); r.u(1)
            r.u(32); r.u(12)
        if sub_level[i]:
            r.u(8)


def _parse_scaling_list(r):
    for size_id in range(4):
        step = 3 if size_id == 3 else 1
        for _ in range(0, 6, step):
            if not r.u(1):
                r.ue()
            else:
                if size_id > 1:
                    r.se()
                for _ in range(min(64, 1 << (4 + (size_id << 1)))):
                    r.se()


def _parse_st_rps(r, idx, sets, num_sets):
    """One short_term_ref_pic_set, fully derived (clause 7.3.7).

    The inter-prediction branch has to be derived properly rather than
    approximated: getting NumDeltaPocs wrong by one desynchronises every
    later bit of the SPS.  An approximate version read x265's small SPS
    correctly and could not read a broadcast one at all.
    """
    if idx != 0 and r.u(1):
        delta_idx_minus1 = r.ue() if idx == num_sets else 0
        delta_rps = (1 - 2 * r.u(1)) * (r.ue() + 1)
        ref = sets[idx - (delta_idx_minus1 + 1)]
        n_ref = len(ref['s0']) + len(ref['s1'])
        used, use_delta = [], []
        for _ in range(n_ref + 1):
            u = r.u(1)
            used.append(u)
            use_delta.append(1 if u else r.u(1))

        s0, u0 = [], []
        for j in range(len(ref['s1']) - 1, -1, -1):
            d = ref['s1'][j] + delta_rps
            if d < 0 and use_delta[len(ref['s0']) + j]:
                s0.append(d); u0.append(used[len(ref['s0']) + j])
        if delta_rps < 0 and use_delta[n_ref]:
            s0.append(delta_rps); u0.append(used[n_ref])
        for j in range(len(ref['s0'])):
            d = ref['s0'][j] + delta_rps
            if d < 0 and use_delta[j]:
                s0.append(d); u0.append(used[j])

        s1, u1 = [], []
        for j in range(len(ref['s0']) - 1, -1, -1):
            d = ref['s0'][j] + delta_rps
            if d > 0 and use_delta[j]:
                s1.append(d); u1.append(used[j])
        if delta_rps > 0 and use_delta[n_ref]:
            s1.append(delta_rps); u1.append(used[n_ref])
        for j in range(len(ref['s1'])):
            d = ref['s1'][j] + delta_rps
            if d > 0 and use_delta[len(ref['s0']) + j]:
                s1.append(d); u1.append(used[len(ref['s0']) + j])
        return {'s0': s0, 's1': s1}

    neg, pos = r.ue(), r.ue()
    s0, s1 = [], []
    prev = 0
    for _ in range(neg):
        prev -= r.ue() + 1
        s0.append(prev)
        r.u(1)
    prev = 0
    for _ in range(pos):
        prev += r.ue() + 1
        s1.append(prev)
        r.u(1)
    return {'s0': s0, 's1': s1}


def _parse_sps(payload):
    r = _BitReader(_unescape(payload[2:]))
    sps = {}
    r.u(4)
    max_sub = r.u(3)
    r.u(1)
    _parse_ptl(r, max_sub + 1)
    sps['id'] = r.ue()
    chroma = r.ue()
    sps['separate_colour_plane'] = r.u(1) if chroma == 3 else 0
    width, height = r.ue(), r.ue()
    if r.u(1):
        r.ue(); r.ue(); r.ue(); r.ue()
    r.ue(); r.ue()
    sps['log2_max_poc_lsb'] = r.ue() + 4
    ordering = r.u(1)
    for _ in range(0 if ordering else max_sub, max_sub + 1):
        r.ue(); r.ue(); r.ue()
    min_cb_log2 = r.ue() + 3
    ctb_log2 = min_cb_log2 + r.ue()
    r.ue(); r.ue(); r.ue(); r.ue()
    if r.u(1) and r.u(1):
        _parse_scaling_list(r)
    r.u(1)
    r.u(1)
    if r.u(1):
        r.u(4); r.u(4); r.ue(); r.ue(); r.u(1)
    num_st = r.ue()
    sets = []
    for i in range(num_st):
        sets.append(_parse_st_rps(r, i, sets, num_st))
    sps['long_term_ref_pics_present'] = r.u(1)

    ctb = 1 << ctb_log2
    pic_size_in_ctbs = (-(-width // ctb)) * (-(-height // ctb))
    sps['slice_address_bits'] = (
        max(1, math.ceil(math.log2(pic_size_in_ctbs)))
        if pic_size_in_ctbs > 1 else 0)
    return sps


def _parse_pps(payload):
    r = _BitReader(_unescape(payload[2:]))
    return {
        'id': r.ue(),
        'sps_id': r.ue(),
        'dependent_slice_segments_enabled': r.u(1),
        'output_flag_present': r.u(1),
        'num_extra_slice_header_bits': r.u(3),
    }


class HevcPocRewriter:
    """Rewrites slice POCs so a spliced stream carries one coherent numbering.

    Feed it every video packet in output order, with a run id that changes
    whenever the origin of the material changes.  It returns the packet's
    bytes, rewritten where needed.
    """

    def __init__(self):
        self._sps = {}
        self._pps = {}
        self.enabled = True
        self.reason = None
        # Highest POC written since the last DPB flush, and the offset in
        # force for the run being written.
        self._ceiling = -1
        self._offset = 0
        self._run = None
        self._prev_tid0 = 0
        self._have_prev = False
        self.pictures = 0
        self.shifted = 0

    def _disable(self, reason):
        if self.enabled:
            self.enabled = False
            self.reason = reason
            # Always logged, not only under verbose: a silent fallback here
            # means a stream that looks fine but is latently wrong, and the
            # reason is the only clue to which stream it was.
            logger.warning('POC renumbering off for the rest of this export '
                           '(%s); output is as 2.3.0 produced it', reason)

    def rewrite(self, data, run_id):
        """Return `data` with POCs renumbered for the run `run_id`.

        Never raises: any surprise disables the rewriter and returns the
        packet untouched, leaving the stream exactly as 2.3.0 produced it.
        """
        if not self.enabled or not data:
            return data
        try:
            return self._rewrite(data, run_id)
        except Exception as exc:                      # noqa: BLE001
            self._disable(f'{type(exc).__name__}: {exc}')
            return data

    def _rewrite(self, data, run_id):
        if data[:3] != b'\x00\x00\x01' and data[:4] != b'\x00\x00\x00\x01':
            self._disable('packet is not Annex B')
            return data

        out = None
        for start, end in _split_nals(data):
            if end - start < 2:
                continue
            payload = data[start:end]
            nal_type = (payload[0] >> 1) & 0x3F
            if nal_type == _SPS:
                sps = _parse_sps(payload)
                if sps['long_term_ref_pics_present']:
                    # poc_lsb_lt[] in a slice header is an absolute POC lsb,
                    # so a constant run offset would have to be applied there
                    # too.  Not seen in any test material; refuse rather than
                    # corrupt a stream on a guess.
                    self._disable('stream uses long-term reference pictures')
                    return data
                if sps['separate_colour_plane']:
                    self._disable('stream uses separate colour planes')
                    return data
                self._sps[sps['id']] = sps
                continue
            if nal_type == _PPS:
                pps = _parse_pps(payload)
                self._pps[pps['id']] = pps
                continue
            if nal_type not in _VCL:
                continue

            new_payload = self._rewrite_slice(payload, nal_type, run_id)
            if new_payload is None:
                continue
            if out is None:
                out = bytearray(data)
            if len(new_payload) == len(payload):
                out[start:end] = new_payload
            else:
                # Re-escaping can add a byte.  Rebuild rather than patch in
                # place, since every later offset would move.
                return self._rebuild(data, run_id)
        return bytes(out) if out is not None else data

    def _rebuild(self, data, run_id):
        """Slow path for when a rewritten NAL changes length."""
        out = bytearray()
        pos = 0
        for start, end in _split_nals(data):
            if end - start < 2:
                continue
            payload = data[start:end]
            nal_type = (payload[0] >> 1) & 0x3F
            if nal_type not in _VCL:
                continue
            new_payload = self._rewrite_slice(payload, nal_type, run_id,
                                              already_counted=True)
            if new_payload is None:
                continue
            out += data[pos:start]
            out += new_payload
            pos = end
        out += data[pos:]
        return bytes(out)

    def _rewrite_slice(self, payload, nal_type, run_id, already_counted=False):
        """Return the slice segment with its POC renumbered, or None."""
        rbsp = _unescape(payload[2:])
        r = _BitReader(rbsp)
        first_slice = r.u(1)
        if nal_type in _IRAP:
            r.u(1)                        # no_output_of_prior_pics_flag
        pps = self._pps.get(r.ue())
        if pps is None:
            raise ValueError('slice references an unseen PPS')
        sps = self._sps.get(pps['sps_id'])
        if sps is None:
            raise ValueError('slice references an unseen SPS')

        dependent = 0
        if not first_slice:
            if pps['dependent_slice_segments_enabled']:
                dependent = r.u(1)
            r.u(sps['slice_address_bits'])
        if dependent:
            # A dependent slice segment inherits the header before it, POC
            # included, so there is nothing here to change.
            return None

        for _ in range(pps['num_extra_slice_header_bits']):
            r.u(1)
        r.ue()                            # slice_type
        if pps['output_flag_present']:
            r.u(1)                        # pic_output_flag

        is_idr = nal_type in _IDR
        if first_slice and not already_counted:
            self.pictures += 1

        if is_idr:
            # An IDR flushes the DPB and its POC is fixed at 0 by the
            # decoder, so it begins a run of its own at offset zero and
            # there is no field in its header to rewrite.
            self._run = run_id
            self._offset = 0
            self._ceiling = 0
            self._prev_tid0 = 0
            self._have_prev = True
            return None

        bit_off = r.pos
        n_bits = sps['log2_max_poc_lsb']
        lsb = r.u(n_bits)
        max_lsb = 1 << n_bits

        if run_id != self._run or not self._have_prev:
            # First picture of a run.  Its own lsb is taken at face value -
            # the msb base is arbitrary, because the offset that follows
            # absorbs it - and the run is then placed clear of whatever is
            # still in the DPB.
            poc = lsb
            self._run = run_id
            self._offset = (self._ceiling + 1 - poc) if self._ceiling >= 0 else 0
            self._have_prev = True
        else:
            prev_lsb = self._prev_tid0 & (max_lsb - 1)
            prev_msb = self._prev_tid0 - prev_lsb
            if lsb < prev_lsb and (prev_lsb - lsb) >= max_lsb // 2:
                msb = prev_msb + max_lsb
            elif lsb > prev_lsb and (lsb - prev_lsb) > max_lsb // 2:
                msb = prev_msb - max_lsb
            else:
                msb = prev_msb
            poc = msb + lsb

        temporal_id = (payload[1] & 0x07) - 1
        if temporal_id == 0 and nal_type not in _NOT_PREV_TID0:
            self._prev_tid0 = poc

        new_poc = poc + self._offset
        if new_poc > self._ceiling:
            self._ceiling = new_poc
        if self._offset == 0:
            return None

        if first_slice:
            self.shifted += 1
        buf = bytearray(rbsp)
        value = new_poc & (max_lsb - 1)
        for i in range(n_bits):
            pos = bit_off + i
            mask = 1 << (7 - (pos & 7))
            if (value >> (n_bits - 1 - i)) & 1:
                buf[pos >> 3] |= mask
            else:
                buf[pos >> 3] &= ~mask & 0xFF
        return payload[:2] + _escape(bytes(buf))
