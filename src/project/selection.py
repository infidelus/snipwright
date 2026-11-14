class SelectionManager:

    def __init__(self):

        #
        # Temporary markers
        #

        self.pending_in = None
        self.pending_out = None

        # Which markers the user has placed since the last scene or cut was
        # committed.  finish_edit() deliberately leaves the markers in place
        # so a boundary can be nudged and re-added; this records which of them
        # are FRESH, which is what tells a nudge apart from a half-marked new
        # scene.  See the inverted-span guard in commit_range().
        self._marked_since_commit = set()

        #
        # Saved keep ranges
        #

        self.ranges = []
        self.undo_stack = []
        self.redo_stack = []

    def clear_pending(self):

        self.pending_in = None
        self.pending_out = None

    def finish_edit(self):
        """Finish a scene or cut without discarding the IN/OUT markers.

        VideoReDo leaves the markers where they are after a scene is added, and
        replaces each only when it is next placed.  That matters when you spot
        a boundary is a frame out immediately after adding: nudge the marker,
        add again, and commit_range's overlap handling adjusts the scene you
        just made rather than adding a second one.  Clearing both markers meant
        re-marking from scratch for the sake of one frame.

        `_marked_since_commit` is cleared, so commit_range() can tell a
        marker the user has just placed from one left over from this scene.
        See the inverted-span guard there.
        """
        self._marked_since_commit = set()

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
        self._marked_since_commit.add("in")

    def set_out(
            self,
            frame,
    ):

        self.pending_out = frame
        self._marked_since_commit.add("out")

    def commit_range(self):

        if (
            self.pending_in is None
            or
            self.pending_out is None
        ):
            return False

        # Refuse a span that runs BACKWARDS from a leftover marker.
        #
        # The markers survive a commit on purpose (see finish_edit), so after
        # adding a scene the OUT still sits at that scene's end.  Mark IN for
        # the next scene, forget the OUT, press Add - and IN is now AFTER OUT.
        # min/max quietly turned that into the span between the two, which
        # then overlapped the neighbouring scenes and REPLACED them: a user
        # reported losing two scenes this way, having marked one point.
        #
        # Only when a single fresh marker is involved.  Marking OUT and then
        # IN deliberately is still fine - both are fresh, so the user means
        # that span and min/max is doing what they asked.  And the nudge case
        # the markers exist for is untouched, because nudging IN back a frame
        # keeps it BEFORE the OUT.
        if (
            self.pending_in > self.pending_out
            and len(self._marked_since_commit) < 2
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

        # Undo is recorded only if the commit changes something: adding a
        # scene exactly as it already is pushed an empty undo step and threw
        # the redo history away (code scan, 2026-11-13).
        before = list(self.ranges)

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
            self._record_undo_if_changed(before)
            self.finish_edit()
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
        self._record_undo_if_changed(before)

        #
        # The markers stay where they are - see finish_edit.
        #

        self.finish_edit()

        return True

    def _record_undo_if_changed(self, before):
        if self.ranges != before:
            self.undo_stack.append(before)
            self.redo_stack.clear()

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

    def replace_cuts(self, olds, new_start, new_end):
        """Replace every cut in `olds` with the single span new_start..new_end.

        Cut Mode's equivalent of re-marking a scene in Scene Mode: it lets a
        cut be nudged or resized rather than only ever grown.  Restoring the
        old cuts and applying the new one happen together, as a single undo
        step.

        Takes a LIST because a marked span can overlap more than one cut -
        mark across two advert breaks and the material between them is being
        claimed as well, so all of them are restored first and the new span
        applied once.  Replacing only the first would leave the second sitting
        inside what the user just marked.
        """
        if new_start is None or new_end is None:
            return False

        if new_start > new_end:
            new_start, new_end = new_end, new_start

        self.push_undo_state()

        restored = self.ranges
        for old_start, old_end in olds:
            restored = self._union_into(restored, old_start, old_end)
        self.ranges = self._subtract_from(restored, new_start, new_end)

        # Keep the markers, as subtract_range and commit_range do.  This is the
        # path taken when a new mark starts inside an existing cut - which is
        # precisely the correcting-a-boundary case the markers are kept for, so
        # clearing them here defeated the whole point in Cut Mode.
        self.finish_edit()

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

        # Same as Scene Mode: keep the markers so a cut that is a frame out can
        # be corrected by nudging one and cutting again.
        self.finish_edit()

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

        # Trim Unselected is a single marked edit like a scene or a cut, so it
        # keeps its markers for the same reason: a boundary that is a frame out
        # can be corrected by nudging one marker and trimming again.
        self.finish_edit()

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
