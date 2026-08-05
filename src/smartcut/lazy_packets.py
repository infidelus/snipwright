"""Reading a track's audio packets without holding the whole file in memory.

The original code collected every audio packet up front, with a candid note
saying so:

    # NOTE: storing the audio packets like this keeps the whole compressed
    # audio loaded in RAM

For a Freeview recording that is a few hundred megabytes and nobody notices.
For a Blu-ray with six DTS tracks it is 3.5 GB of payload plus a PyAV packet
object for each of some two and a half million packets, which together account
for most of the 15 GB working set observed while cutting one.

This replaces that list with something that looks like a list to its callers -
`packets[i]`, `packets[a:b]`, `len(packets)` - but fetches from the file on
demand and keeps only a bounded window.

The access pattern makes that practical: cut segments are processed in
ascending time order, so a reader that streams forward and keeps a modest
window satisfies almost every request without re-reading.  A request that falls
behind the window seeks and refills, which is correct if slower, and a request
that cannot be satisfied at all falls back to reading the track from the start
- slow, but never wrong.
"""

import av


class LazyAudioPackets:
    """Sequence-like lazy view over one audio stream's packets.

    Deliberately not a subclass of list: the point is that it never holds the
    whole file, and inheriting would invite code to treat it as though it did.
    """

    # How many packets to keep either side of the current position.  Audio
    # packets are small - a DTS frame is a couple of kilobytes - so a few
    # thousand is a handful of megabytes and covers any plausible segment.
    WINDOW = 4096

    def __init__(self, path, stream_index, count):
        self._path = path
        self._stream_index = stream_index
        self._count = count

        # The window: packets [_base, _base + len(_cache)) of the stream.
        self._cache = []
        self._base = 0

        self._container = None
        self._demux = None
        self._next_index = 0        # stream index of the next packet to arrive

    def __len__(self):
        return self._count

    def _open(self):
        if self._container is None:
            self._container = av.open(self._path)
            # Match on the stream's own index rather than its position in the
            # list: an MPEG-TS file's stream indices are not contiguous, so
            # streams[1] is not necessarily the stream whose index is 1.
            self._stream = None
            for st in self._container.streams:
                if st.index == self._stream_index:
                    self._stream = st
                    break
            if self._stream is None:
                raise IndexError(
                    "stream %d not found in %s"
                    % (self._stream_index, self._path)
                )
            self._demux = self._container.demux(self._stream)
            self._next_index = 0
            self._cache = []
            self._base = 0

    def close(self):
        if self._container is not None:
            try:
                self._container.close()
            except Exception:
                pass
        self._container = None
        self._demux = None

    def _rewind(self):
        """Start again from the beginning of the stream."""
        self.close()
        self._open()

    def _read_until(self, index):
        """Ensure the window covers `index`, reading forward as needed."""
        self._open()

        # Asked for something already behind the window: start over.  Ascending
        # access means this is rare, and correctness matters more than the cost.
        if index < self._base:
            self._rewind()

        while self._next_index <= index:
            try:
                packet = next(self._demux)
            except StopIteration:
                break
            # A flush packet (empty, no data) marks the end; it is not one of
            # the stream's packets and must not be counted as one.
            if packet.dts is None and packet.pts is None and not bytes(packet):
                continue
            self._cache.append(packet)
            self._next_index += 1
            if len(self._cache) > self.WINDOW:
                # Drop from the front; ascending access will not want it again.
                drop = len(self._cache) - self.WINDOW
                del self._cache[:drop]
                self._base += drop

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(self._count)
            if step != 1:
                return [self[i] for i in range(start, stop, step)]
            if stop <= start:
                return []
            # Read up to the last packet wanted, then take the run from the
            # window.  A span longer than the window is read in pieces.
            if stop - start > self.WINDOW:
                return [self[i] for i in range(start, stop)]
            self._read_until(stop - 1)
            lo = start - self._base
            hi = stop - self._base
            if lo < 0:
                # The window moved past the start of the run; fetch one by one.
                return [self[i] for i in range(start, stop)]
            return self._cache[lo:max(lo, hi)]

        if key < 0:
            key += self._count
        if not (0 <= key < self._count):
            raise IndexError(key)
        self._read_until(key)
        offset = key - self._base
        if 0 <= offset < len(self._cache):
            return self._cache[offset]
        raise IndexError(key)

    def __iter__(self):
        for i in range(self._count):
            yield self[i]

    def __bool__(self):
        return self._count > 0
