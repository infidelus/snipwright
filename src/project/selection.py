class SelectionManager:

    def __init__(self):

        #
        # Temporary markers
        #

        self.pending_in = None
        self.pending_out = None

        #
        # Saved keep ranges
        #

        self.ranges = []
        self.undo_stack = []
        self.redo_stack = []

        # When the user marks IN inside an existing range, that range's index
        # is recorded here so the next commit REPLACES it (adjusts its
        # boundaries) rather than merging into it.  None means "new range".
        self.editing_index = None

    def range_index_at(self, frame):
        """Return the index of the range containing `frame`, or None."""
        for i, (start, end) in enumerate(self.ranges):
            if start <= frame <= end:
                return i
        return None

    def clear_pending(self):

        self.pending_in = None
        self.pending_out = None
        self.editing_index = None

    def clear_all(self):

        self.clear_pending()

        self.ranges.clear()

    def push_undo_state(self):

        self.undo_stack.append(
            list(
                self.ranges
            )
        )

        #
        # New edits invalidate redo
        #

        self.redo_stack.clear()

    def set_in(
            self,
            frame,
    ):

        self.pending_in = frame

    def set_out(
            self,
            frame,
    ):

        self.pending_out = frame

    def commit_range(self):

        if (
            self.pending_in is None
            or
            self.pending_out is None
        ):
            return False

        start = min(
            self.pending_in,
            self.pending_out
        )

        end = max(
            self.pending_in,
            self.pending_out
        )

        self.push_undo_state()

        new_start = start
        new_end = end

        #
        # Decide EDIT vs ADD by whether the new IN..OUT span overlaps any
        # existing scene.  This is more robust than keying off where the IN
        # landed: when adjusting a scene the new IN often sits just before or
        # after the old boundary (so it isn't strictly "inside" the old span),
        # but the intent is still to replace that scene.
        #
        # EDIT (span overlaps existing scenes): the new IN..OUT replaces them
        # exactly - any overlapping scene material, inside or partially inside
        # the span, is discarded.  This matches VideoReDo, where marking IN in
        # one scene and OUT in the next collapses to a single IN..OUT scene.
        #
        # ADD (span overlaps nothing): insert as a new scene, merging only
        # with directly adjacent scenes.
        #
        overlaps = any(
            not (existing_end < new_start or existing_start > new_end)
            for existing_start, existing_end in self.ranges
        )

        if overlaps:
            kept = [
                (existing_start, existing_end)
                for existing_start, existing_end in self.ranges
                if existing_end < new_start or existing_start > new_end
            ]
            kept.append((new_start, new_end))
            kept.sort()
            self.ranges = kept
            self.clear_pending()
            return True

        #
        # ADDING a new range: merge with any directly adjacent ranges.
        #
        merged = []

        for existing_start, existing_end in self.ranges:

            #
            # No overlap
            #

            if (
                    existing_end < new_start - 1
                    or
                    existing_start > new_end + 1
            ):
                merged.append(
                    (
                        existing_start,
                        existing_end,
                    )
                )

                continue

            #
            # Merge overlap
            #

            new_start = min(
                new_start,
                existing_start,
            )

            new_end = max(
                new_end,
                existing_end,
            )

        #
        # Add merged result
        #

        merged.append(
            (
                new_start,
                new_end,
            )
        )

        merged.sort()

        self.ranges = merged

        #
        # Reset temporary markers
        #

        self.clear_pending()

        return True

    @staticmethod
    def _subtract_from(ranges, start, end):
        """`ranges` with start..end removed.  Pure - no undo, no state."""
        result = []

        for r_start, r_end in ranges:
            if r_end < start or r_start > end:
                result.append((r_start, r_end))
                continue

            if r_start < start:
                result.append((r_start, start - 1))

            if r_end > end:
                result.append((end + 1, r_end))

        result.sort()

        return result

    def adjust_cut(self, old_start, old_end, new_start, new_end):
        """Replace the existing cut `old_start`..`old_end` with a new span.

        Cut Mode's equivalent of re-marking a scene in Scene Mode: it lets a
        cut be nudged or resized rather than only ever grown.  Restoring the
        old cut and applying the new one happen together, as a single undo
        step.
        """
        if None in (old_start, old_end, new_start, new_end):
            return False

        if new_start > new_end:
            new_start, new_end = new_end, new_start

        self.push_undo_state()

        restored = self._union_into(self.ranges, old_start, old_end)
        self.ranges = self._subtract_from(restored, new_start, new_end)

        self.clear_pending()

        return True

    def subtract_range(self, start, end):
        """Remove the frames `start`..`end` (inclusive) from the kept ranges.

        This is Cut Mode's core operation - VideoReDo's "Cut Selection".  A cut
        landing inside a kept range splits it in two; one that covers a range
        entirely removes it; one that overlaps an edge trims it.  The whole
        thing is a single undo step no matter how many ranges it touches.

        Returns True if anything actually changed.
        """
        if start is None or end is None:
            return False

        if start > end:
            start, end = end, start

        result = []
        changed = False

        for r_start, r_end in self.ranges:
            if r_end < start or r_start > end:
                # No overlap - keep the range untouched.
                result.append((r_start, r_end))
                continue

            changed = True

            if r_start < start:
                # Something survives before the cut.
                result.append((r_start, start - 1))

            if r_end > end:
                # ...and/or after it.  Both means the cut split the range.
                result.append((end + 1, r_end))

        if not changed:
            return False

        self.push_undo_state()

        result.sort()
        self.ranges = result

        self.clear_pending()

        return True

    @staticmethod
    def _union_into(ranges, start, end):
        """`ranges` with start..end merged in.  Pure - no undo, no state."""
        merged = []
        new_start, new_end = start, end

        for r_start, r_end in ranges:
            if r_end < new_start - 1 or r_start > new_end + 1:
                # Disjoint and not merely touching - keep as is.
                merged.append((r_start, r_end))
            else:
                # Overlaps or abuts: absorb it.
                new_start = min(new_start, r_start)
                new_end = max(new_end, r_end)

        merged.append((new_start, new_end))
        merged.sort()

        return merged

    def union_range(self, start, end):
        """Add `start`..`end` back into the kept ranges, merging with anything
        it touches.

        Cut Mode's "Remove Selected Cuts": deleting a cut from the list means
        putting that part of the programme back.  A single undo step.
        """
        if start is None or end is None:
            return False

        if start > end:
            start, end = end, start

        self.push_undo_state()

        self.ranges = self._union_into(self.ranges, start, end)

        self.clear_pending()

        return True

    def union_ranges(self, spans):
        """Restore several cuts at once as a single undo step.

        Returns how many were applied.
        """
        spans = [
            s for s in spans
            if s and s[0] is not None and s[1] is not None
        ]

        if not spans:
            return 0

        self.push_undo_state()

        result = list(self.ranges)

        for start, end in spans:
            if start > end:
                start, end = end, start
            result = self._union_into(result, start, end)

        self.ranges = result

        self.clear_pending()

        return len(spans)

    def intersect_range(self, start, end):
        """Keep only what falls between `start` and `end` - VideoReDo's "Trim
        Unselected".  Everything outside the marked span is cut, which is how
        you top-and-tail a recording in one action.  A single undo step.

        Returns True if anything actually changed.
        """
        if start is None or end is None:
            return False

        if start > end:
            start, end = end, start

        result = []
        changed = False

        for r_start, r_end in self.ranges:
            new_start = max(r_start, start)
            new_end = min(r_end, end)

            if new_start > new_end:
                # Entirely outside the marked span - dropped.
                changed = True
                continue

            if (new_start, new_end) != (r_start, r_end):
                changed = True

            result.append((new_start, new_end))

        if not changed:
            return False

        self.push_undo_state()

        result.sort()
        self.ranges = result

        self.clear_pending()

        return True

    def select_all(self, last_frame):
        """Keep the whole programme - the starting state for Cut Mode, and a
        handy "start again from everything" action in either mode."""
        if last_frame is None or last_frame < 0:
            return False

        if self.ranges == [(0, last_frame)]:
            return False

        self.push_undo_state()

        self.ranges = [(0, last_frame)]

        self.clear_pending()

        return True

    def cut_ranges(self, last_frame):
        """The complement of the kept ranges - i.e. what has been cut.

        Cut Mode's list shows these rather than the kept scenes, so this is
        what feeds that view.  Derived on demand: the kept ranges remain the
        single source of truth, so nothing can drift out of step.
        """
        if last_frame is None or last_frame < 0:
            return []

        cuts = []
        cursor = 0

        for r_start, r_end in sorted(self.ranges):
            if r_start > cursor:
                cuts.append((cursor, r_start - 1))
            cursor = max(cursor, r_end + 1)

        if cursor <= last_frame:
            cuts.append((cursor, last_frame))

        return cuts

    def remove_range(
            self,
            index,
    ):

        if (
                index < 0
                or
                index >= len(
            self.ranges
        )
        ):
            return False

        self.push_undo_state()

        del self.ranges[index]

        return True

    def remove_ranges(self, indices):
        """Remove several ranges at once as a single undo step.

        Returns the number actually removed.  Indices are de-duplicated and
        deleted high-to-low so earlier deletions don't shift later ones.
        """
        valid = sorted(
            {i for i in indices if 0 <= i < len(self.ranges)},
            reverse=True,
        )

        if not valid:
            return 0

        self.push_undo_state()

        for i in valid:
            del self.ranges[i]

        return len(valid)

    def undo(self):

        if not self.undo_stack:
            return False

        self.redo_stack.append(
            list(
                self.ranges
            )
        )

        self.ranges = (
            self.undo_stack.pop()
        )

        return True

    def redo(self):

        if not self.redo_stack:
            return False

        self.undo_stack.append(
            list(
                self.ranges
            )
        )

        self.ranges = (
            self.redo_stack.pop()
        )

        return True