"""The remembered-logos manager: what Chalkline has learned, per channel.

Chalkline files each learned logo under the channel key it read from the
recording, and the two PVRs give different kinds of key for the same channel:
Tvheadend keeps the SDT so a service *name* survives, Jellyfin keeps the PAT
so a service *id* survives, and neither recording ever carries both - see
channel_key() in chalkline.py.  Nothing in Snipwright can resolve one to the
other, which is why the pairing is typed in here by hand rather than worked
out.  It is the only route there is.

A row is one channel.  Most rows are a learned logo; a channel with no logo
but a learned break ident (Film4, item 1y) gets a row from the card store
instead, so it can be named and paired like any other.  The Channel and
Service ID columns are both lookup keys for that same channel, so filling in
the empty half of a row makes what was learned work for recordings from the
other PVR too.  Typing a key that already has a row of its own merges the
two.

The Learn column switches learning off per channel (item 1x): what was
learned is still used to detect breaks, but correcting a project on that
channel no longer spends minutes decoding it to learn again.

The mask itself is drawn rather than described.  A learned logo looks like a
logo; a mask learned from a poor edit looks like scattered noise or a
fragment of a caption, and no number conveys that as quickly as the shape
does.

All user-facing text uses British English.
"""

import logging
import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from repair.chalkline import (
    CARD_H,
    CARD_MATCH,
    CARD_W,
    GH,
    GW,
    LOGO_STORE,
    MASK_HISTORY_MAX,
    RECHECK_EVERY,
    SETTLE_AFTER,
    active_index,
    is_settled,
    settle_state,
    card_distances,
    card_only_channels,
    card_store_path,
    channel_cards,
    load_cards,
    load_store,
    mask_history,
    same_mask,
    save_cards,
    save_store,
    store_display_name,
    store_service_id,
    write_history,
)

# The thumbnail is drawn as blocks at the mask's own scale, one block per
# analysis pixel.  A logo is 30-70 pixels on a 160x90 analysis frame, so
# there is no detail to smooth and nothing to interpolate - each stored
# pixel is drawn, or it isn't.
_THUMB_W, _THUMB_H = 96, 54
# Breathing room inside the cell, so a mask never touches the row edges.
_PAD = 8
# How far a mask may be magnified.  Without a limit, every mask was scaled to
# fill the thumbnail, so a five-pixel sliver and a seventy-pixel logo were
# drawn the same size - and a mask only one row tall came out as a bold line
# across the whole cell, which flatters it enormously.  Capping the zoom
# keeps the column comparable: a big logo looks big, a scrap looks like a
# scrap.
_MAX_ZOOM = 6
# A one-pixel gap between neighbouring mask pixels.  Drawn solid, adjacent
# pixels merge into a blob and the mask's internal structure disappears;
# drawn with a two-pixel gap it dissolves into scattered dots.  One is the
# balance - the shape still reads, and the pixel grid it is made of stays
# visible, which is honest about how coarse a 160x90 mask really is.
_GUTTER = 1
_SID_PREFIX = "sid:"

log = logging.getLogger("snipwright")


def _mask_thumbnail(entry):
    """Draw a learned mask as a small monochrome picture, to scale.

    The stored pixels are fractions of the recording's active picture, so
    multiplying them by the analysis grid gives the mask's size in grid
    pixels - the same arithmetic mask_to_pixels() does when the mask is
    actually used, which is the reason to copy it rather than invent a
    second scale.  Every row is then drawn at one magnification, so a big
    logo looks big and a scrap looks like a scrap.

    The entry's own `box` is deliberately not used here: it is the mask's
    bounding box as a fraction of the picture, not the picture itself, and
    scaling the pixels by it collapses every mask to a single dot.
    """
    pixels = entry.get("pixels") or []
    if not pixels:
        return None

    # Into grid pixels, so a mask's drawn size means something.
    try:
        xs = [float(p[0]) * (GW - 1) for p in pixels]
        ys = [float(p[1]) * (GH - 1) for p in pixels]
    except (TypeError, ValueError, IndexError):
        return None
    if not xs:
        return None

    left, top = min(xs), min(ys)
    bw = max(1, int(round(max(xs) - left)) + 1)
    bh = max(1, int(round(max(ys) - top)) + 1)

    zoom = min(
        (_THUMB_W - _PAD) / bw,
        (_THUMB_H - _PAD) / bh,
        float(_MAX_ZOOM),
    )
    cell = max(1, int(round(max(zoom, 1.0))))
    block = max(1, cell - _GUTTER)

    pix = QPixmap(_THUMB_W, _THUMB_H)
    pix.fill(QColor(27, 27, 31))
    painter = QPainter(pix)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(230, 230, 235))
    origin_x = (_THUMB_W - bw * cell) // 2
    origin_y = (_THUMB_H - bh * cell) // 2
    # Drawn as blocks rather than scaled from an image: a scaled image has no
    # way to leave the gap between pixels, and nearest-neighbour magnification
    # is what produced the solid blobs this replaces.
    for x, y in zip(xs, ys):
        px = int(round(x - left))
        py = int(round(y - top))
        if 0 <= px < bw and 0 <= py < bh:
            painter.drawRect(
                origin_x + px * cell, origin_y + py * cell, block, block
            )
    painter.end()
    return pix


def _card_thumbnail(entry):
    """Draw a channel's most recent break ident, from its fingerprint.

    The fingerprint is the ident shrunk to CARD_W x CARD_H greyscale, which
    is what Chalkline matches against - so this is exactly what it looks
    for, blocky as it is.  Shown in the column where a logo row shows its
    mask, so a card-only row is recognisable at a glance too.
    """
    cards = entry.get("cards") or []
    if not cards:
        return None
    try:
        fp = [int(v) for v in _flatten(cards[-1].get("fingerprint") or [])]
    except (TypeError, ValueError):
        return None
    if len(fp) != CARD_W * CARD_H:
        return None
    cell = max(1, min((_THUMB_W - _PAD) // CARD_W, (_THUMB_H - _PAD) // CARD_H))
    pix = QPixmap(_THUMB_W, _THUMB_H)
    pix.fill(QColor(27, 27, 31))
    painter = QPainter(pix)
    painter.setPen(Qt.NoPen)
    origin_x = (_THUMB_W - CARD_W * cell) // 2
    origin_y = (_THUMB_H - CARD_H * cell) // 2
    for i, v in enumerate(fp):
        v = max(0, min(255, v))
        painter.setBrush(QColor(v, v, v))
        painter.drawRect(origin_x + (i % CARD_W) * cell,
                         origin_y + (i // CARD_W) * cell, cell, cell)
    painter.end()
    return pix


def _flatten(values):
    """A fingerprint stored as rows or as one flat list, as one flat list."""
    out = []
    for v in values:
        if isinstance(v, (list, tuple)):
            out.extend(_flatten(v))
        else:
            out.append(v)
    return out


def _union_cards(*lists):
    """Cards from several lists, oldest first, without repeating one.

    Two cards are the same ident when their fingerprints match as closely as
    Chalkline needs them to - the test add_card() uses to avoid filing an
    ident twice.
    """
    out = []
    for cards in lists:
        for card in cards or []:
            fp = card.get("fingerprint")
            if fp is None:
                continue
            if any(card_distances([_flatten(fp)], _flatten(c["fingerprint"]))[0]
                   < CARD_MATCH for c in out):
                continue
            out.append(card)
    return out


class LogoStoreDialog(QDialog):
    """Show and edit the logos Chalkline has learned."""

    COL_MASK, COL_NAME, COL_SID, COL_LOGO, COL_CONTRAST, COL_IDENTS, \
        COL_LEARN = range(7)

    def __init__(self, parent=None, store_path=LOGO_STORE):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Remembered logos"))
        self.setMinimumSize(780, 420)
        self._store_path = store_path
        self._filling = False
        # An edit in flight, and the edit waiting for the event loop to
        # settle before it is applied.  See _on_item_changed.
        self._editing = False
        self._pending_edit = None
        # Keys the user has forgotten in this session.  Without these, an
        # additive reload would fetch a forgotten channel straight back off
        # the disk it has not yet been removed from.
        self._removed_keys = set()
        self._removed_card_keys = set()
        self._store = load_store(store_path)
        # Break idents (item 1u) live in their own file beside the logos.
        # Every card entry is held here, not just the card-only ones, so Save
        # can write the file back whole - see _save_cards().
        self._card_path = card_store_path(store_path)
        self._cards = load_cards(self._card_path)
        # What each table row shows: ("logo", entry) for the logo store's
        # entries, in their order and first, then ("card", entry) for
        # channels known only by a break ident.  Rebuilt by _fill_table().
        self._rows = []

        layout = QVBoxLayout(self)

        intro = QLabel(self.tr(
            "Chalkline learns each channel's logo, and any ident it shows at "
            "the edges of its breaks, when you correct a detection and save "
            "the project. A recorder that keeps the channel name gives a name "
            "here; one that keeps the service number gives a number. They are "
            "the same channel, but Snipwright cannot tell - fill in the "
            "missing half of a row and what was learned will be used for "
            "recordings from both. Untick Learn for a channel that already "
            "detects well: what it has learned is still used, but correcting "
            "it no longer spends minutes learning again."
        ))
        intro.setWordWrap(True)
        intro.setStyleSheet("color: gray;")
        layout.addWidget(intro)

        body = QHBoxLayout()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            self.tr("Logo"), self.tr("Channel"), self.tr("Service ID"),
            self.tr("Mask"), self.tr("Contrast"), self.tr("Idents"),
            self.tr("Learn"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        for c in (self.COL_MASK, self.COL_SID, self.COL_LOGO,
                  self.COL_CONTRAST, self.COL_IDENTS, self.COL_LEARN):
            header.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.table.itemChanged.connect(self._on_item_changed)
        body.addWidget(self.table, 1)

        side = QVBoxLayout()
        self._forget_btn = QPushButton(self.tr("Forget"))
        self._forget_btn.clicked.connect(self._forget)
        side.addWidget(self._forget_btn)
        side.addStretch(1)
        body.addLayout(side)
        layout.addLayout(body)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet("color: gray;")
        layout.addWidget(self._status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).clicked.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._fill_table()

    # -- the store can change under us -------------------------------------

    def event(self, ev):
        """Re-read the store when the window is activated.

        Learning runs on a background thread while the editor is in use, so a
        logo can be learned while this dialog sits open.  Without this, the
        table would show a stale picture and Save would write it back,
        deleting whatever had been learned in the meantime.
        """
        from PySide6.QtCore import QEvent
        if ev.type() == QEvent.WindowActivate:
            self._reload_if_changed()
        return super().event(ev)

    def _reload_if_changed(self):
        """Take in anything learned since this opened, without losing edits.

        Additive only.  The first version of this replaced the whole store
        whenever the file differed from what was loaded - which is true of
        every unsaved edit in this dialog, so joining two rows was
        immediately undone by the window regaining focus, and the status line
        blamed a background learn that had never happened.

        Learning can only ever *add* a channel, so a row on disk that this
        dialog knows nothing about is new and worth taking.  Everything else
        on disk is either already here, possibly edited, or was deliberately
        forgotten - and in both cases what is on screen is the newer truth.
        """
        if self._editing or self._pending_edit is not None:
            # An edit is part-way through and is holding entries out of the
            # current store.  Swapping the store now would orphan them, and
            # the edit would silently do nothing.
            return
        try:
            on_disk = load_store(self._store_path)
        except Exception:
            return

        channels = self._channels()
        known = {k for e in channels for k in e.get("keys", [])}
        known |= self._removed_keys

        added = [
            dict(e) for e in on_disk.get("channels", [])
            if e.get("keys") and not (set(e["keys"]) & known)
        ]
        try:
            cards_on_disk = load_cards(self._card_path)
        except Exception:
            cards_on_disk = {"channels": []}
        card_known = {k for e in self._cards.get("channels", [])
                      for k in e.get("keys", [])} | self._removed_card_keys
        card_added = [
            dict(e) for e in cards_on_disk.get("channels", [])
            if e.get("keys") and not (set(e["keys"]) & card_known)
        ]
        if card_added:
            self._cards.setdefault("channels", []).extend(card_added)
            if not added:
                self._fill_table()
        if not added:
            return

        channels.extend(added)
        self._fill_table()
        names = ", ".join(
            store_display_name(e) or store_service_id(e) for e in added
        )
        self._status.setText(self.tr(
            "Chalkline learned a logo while this window was open, and it has "
            "been added to the list: %s"
        ) % names)

    # -- table --------------------------------------------------------------

    def _channels(self):
        return self._store.setdefault("channels", [])

    def _card_rows(self):
        """Card-store entries with no logo row to belong to."""
        return card_only_channels(self._cards, self._store)

    def _fill_table(self):
        self._filling = True
        channels = self._channels()
        self._rows = ([("logo", e) for e in channels]
                      + [("card", e) for e in self._card_rows()])
        self.table.setRowCount(len(self._rows))
        self.table.verticalHeader().setDefaultSectionSize(_THUMB_H + 6)
        for i, entry in enumerate(channels):
            thumb = QTableWidgetItem()
            thumb.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            pix = _mask_thumbnail(entry)
            if pix is not None:
                thumb.setData(Qt.DecorationRole, pix)
            self.table.setItem(i, self.COL_MASK, thumb)

            name = QTableWidgetItem(store_display_name(entry))
            self.table.setItem(i, self.COL_NAME, name)

            sid = QTableWidgetItem(store_service_id(entry))
            self.table.setItem(i, self.COL_SID, sid)

            kind = entry.get("kind") or ""
            history = mask_history(entry)
            text = (self.tr("%(count)dpx %(kind)s")
                    % {"count": int(entry.get("count", 0)), "kind": kind})
            if len(history) > 1:
                text = (self.tr("%(logo)s, best of %(held)d")
                        % {"logo": text, "held": len(history)})
            logo = QTableWidgetItem(text)
            logo.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            # What each logo this channel holds has done on the projects the
            # user corrected - the evidence the choice above rests on.
            lines = []
            for item in history:
                record = item["record"].get("on", {})
                line = self.tr(
                    "%(count)dpx: %(seen)d project(s), "
                    "%(false)d invented break(s)"
                ) % {
                    "count": int(item["mask"].get("count", 0)),
                    "seen": len(record),
                    "false": sum(r.get("false", 0) for r in record.values()),
                }
                if same_mask(item["mask"], entry):
                    line += self.tr(" - in use")
                lines.append(line)
            logo.setToolTip("\n".join(lines))
            self.table.setItem(i, self.COL_LOGO, logo)

            contrast = QTableWidgetItem("%.2f" % float(entry.get("contrast", 0)))
            contrast.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            contrast.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, self.COL_CONTRAST, contrast)

            # On every cell of the row, not just the one that happens to name
            # the mask.  The user went looking for this on the logo picture -
            # the column actually HEADED "Logo" - and found nothing there.
            for col in range(self.table.columnCount()):
                cell = self.table.item(i, col)
                if cell is not None:
                    cell.setToolTip("\n".join(lines))

            first = (entry.get("keys") or [""])[0]
            self._set_idents(i, len(channel_cards(self._cards, self._store,
                                                  first)), lines)
            self._set_learn(i, entry, lines)
        for i, (_kind, entry) in enumerate(self._rows[len(channels):],
                                           start=len(channels)):
            self._fill_card_row(i, entry)
        self._filling = False
        if not self._rows:
            self._status.setText(self.tr(
                "Nothing learned yet. Correct a detection and save the "
                "project, and the channel's logo will appear here."
            ))

    def _set_idents(self, row, count, tip_lines):
        """How many break idents the row's channel has learned."""
        item = QTableWidgetItem(str(count) if count else "")
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        item.setTextAlignment(Qt.AlignCenter)
        if tip_lines:
            item.setToolTip("\n".join(tip_lines))
        self.table.setItem(row, self.COL_IDENTS, item)

    def _set_learn(self, row, entry, tip_lines=None):
        """The per-channel learning switch, as a tick box."""
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable
                      | Qt.ItemIsUserCheckable)
        on = entry.get("learn", True) is not False
        item.setCheckState(Qt.Checked if on else Qt.Unchecked)
        tip = self.tr(
            "Learn from the projects you correct on this channel. Untick it "
            "once the channel detects well: what it has learned is still "
            "used, and saving a correction no longer starts a learning pass."
        )
        # Settled channels learn only on every 10th corrected project - see
        # chalkline.SETTLE_AFTER.  Shown here so the quiet is explained.
        streak, since = settle_state(entry)
        if on and is_settled(entry):
            item.setText(self.tr("Settled"))
            tip += "\n\n" + self.tr(
                "Settled: this logo was confirmed by %(n)d corrected projects "
                "in a row, so a full learning pass now runs only on every "
                "%(every)dth one (%(left)d to go). A check that does not "
                "confirm it starts learning on every project again."
            ) % {"n": streak, "every": RECHECK_EVERY,
                 "left": max(1, RECHECK_EVERY - since)}
        elif on:
            # On the way there - the count, so it can be watched building
            # (asked for 2026-10-15: with nothing shown until a channel
            # settled, there was no way to tell the feature was working).
            tip += "\n\n" + self.tr(
                "%(n)d of %(need)d confirmed saves: after %(need)d corrected "
                "projects in a row confirm this logo, the channel is settled "
                "and learns only on every %(every)dth project."
            ) % {"n": streak, "need": SETTLE_AFTER, "every": RECHECK_EVERY}
        item.setToolTip(tip)
        self.table.setItem(row, self.COL_LEARN, item)

    def _fill_card_row(self, row, entry):
        """A channel known only by a break ident - Film4 is the reason."""
        thumb = QTableWidgetItem()
        thumb.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        pix = _card_thumbnail(entry)
        if pix is not None:
            thumb.setData(Qt.DecorationRole, pix)
        self.table.setItem(row, self.COL_MASK, thumb)
        self.table.setItem(row, self.COL_NAME,
                           QTableWidgetItem(store_display_name(entry)))
        self.table.setItem(row, self.COL_SID,
                           QTableWidgetItem(store_service_id(entry)))
        tip = [self.tr(
            "No logo - this channel is recognised by the ident at the edges "
            "of its breaks. The picture is the most recent one learned."
        )]
        for col, text in ((self.COL_LOGO, self.tr("No logo")),
                          (self.COL_CONTRAST, "")):
            item = QTableWidgetItem(text)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, col, item)
        self._set_idents(row, len(entry.get("cards") or []), tip)
        self._set_learn(row, entry)
        for col in (self.COL_MASK, self.COL_NAME, self.COL_SID,
                    self.COL_LOGO, self.COL_CONTRAST):
            cell = self.table.item(row, col)
            if cell is not None:
                cell.setToolTip("\n".join(tip))

    def _on_item_changed(self, item):
        """Note the edit and handle it once the cell editor has closed.

        Nothing is done here directly.  Committing an edit emits this while
        the table is still finishing with its editor widget, and opening a
        modal question from inside that runs a nested event loop - during
        which the dialog is deactivated and reactivated, `_reload_if_changed`
        fires, and `self._store` can be replaced underneath the very entries
        this handler is holding.  The merge then edits an orphaned list and
        the table, refilled from the reloaded store, shows no change at all.

        Deferring to the next turn of the event loop costs nothing and means
        every path below runs with the table settled and the store still the
        one the row indices refer to.
        """
        if self._filling:
            return
        col = item.column()
        if col == self.COL_LEARN:
            self._toggle_learn(item)
            return
        if col not in (self.COL_NAME, self.COL_SID):
            return
        self._pending_edit = (item.row(), col, item.text().strip())
        QTimer.singleShot(0, self._apply_pending_edit)

    def _apply_pending_edit(self):
        pending = self._pending_edit
        self._pending_edit = None
        if pending is None:
            return
        row, col, typed = pending

        # Held across the whole edit, modal question included, so a reload
        # cannot swap the store out from under the entries below.
        self._editing = True
        try:
            self._apply_edit(row, col, typed)
        except Exception:
            # An exception in a Qt slot goes to the terminal and the handler
            # simply stops, which looks exactly like nothing having happened.
            # Put it in the log where it will be found.
            log.exception("Editing the remembered-logo list failed")
            self._fill_table()
        finally:
            self._editing = False

    def _toggle_learn(self, item):
        """Switch learning on or off for one channel (item 1x).

        Stored on the row's own entry - the logo entry, or the card entry for
        a card-only channel - as `learn: false`; on is stored as nothing at
        all, so the file stays exactly as it was for every channel left on.
        """
        row = item.row()
        if not (0 <= row < len(self._rows)):
            return
        _kind, entry = self._rows[row]
        on = item.checkState() == Qt.Checked
        if on:
            entry.pop("learn", None)
            # Switched back on: start counting confirmations afresh, so a
            # channel the user wanted watched is not left settled.
            entry.pop("settle", None)
        else:
            entry["learn"] = False
        label = (store_display_name(entry) or store_service_id(entry)
                 or self.tr("this channel"))
        if on:
            self._status.setText(self.tr(
                "%s will learn from the projects you correct again."
            ) % label)
        else:
            self._status.setText(self.tr(
                "%s will no longer learn from your corrections. What it has "
                "learned is still used to find its breaks."
            ) % label)

    def _apply_edit(self, row, col, typed):
        channels = self._channels()
        if len(channels) <= row < len(self._rows):
            self._apply_card_edit(self._rows[row][1], col, typed)
            return
        if not (0 <= row < len(channels)):
            return

        entry = channels[row]
        old = (store_display_name(entry) if col == self.COL_NAME
               else store_service_id(entry))

        if col == self.COL_SID and typed and not typed.startswith(_SID_PREFIX):
            # Accept a bare number: the Tvheadend UI shows service ids without
            # the prefix, so requiring it would mean retyping what was copied.
            typed = _SID_PREFIX + typed

        if typed == old:
            return

        if not typed:
            # Clearing a key is allowed, but never the last one - an entry
            # with no keys can never be found again and would sit in the file
            # unreachable.
            keys = [k for k in entry.get("keys", []) if k != old]
            if not keys:
                self._warn(self.tr(
                    "A logo needs at least one of Channel or Service ID. Use "
                    "Forget to remove it entirely."
                ))
                self._fill_table()
                return
            entry["keys"] = keys
            self._fill_table()
            return

        clash = None
        for other in channels:
            if other is not entry and typed in other.get("keys", []):
                clash = other
                break

        if clash is not None:
            if not self._confirm_merge(entry, clash, typed):
                self._fill_table()
                return
            self._merge(entry, clash, typed, old)
            self._fill_table()
            return

        entry["keys"] = [k for k in entry.get("keys", []) if k != old]
        entry["keys"].append(typed)
        self._fill_table()

    # -- merging ------------------------------------------------------------

    def _confirm_merge(self, entry, clash, typed):
        return QMessageBox.question(
            self,
            self.tr("Remembered logos"),
            self.tr(
                "\u201c%s\u201d already has a logo of its own. Joining them "
                "keeps both logos under the one name, and Snipwright uses "
                "whichever does better on the projects you correct."
                "\n\nJoin them?"
            ) % typed,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        ) == QMessageBox.Yes

    def _merge(self, entry, clash, typed, old=None):
        """Join two rows, keeping BOTH masks under one entry.

        This used to keep whichever mask had the higher contrast and throw
        the other away, on the reasoning that contrast is an objective
        measure of a template.  It is not a comparable one: contrast is
        measured on the recording each mask was learned from, and the corpus
        has twice shown the higher-contrast mask to be the worse one - ITV1's
        5px mask (0.812) beat its 10px mask (0.721) in a join and then read
        the SD recording's logo 0% of the time, and in 2.6.19 a fuller
        Channel 4 mask gave one more false positive than the sparser one.

        So nothing is thrown away.  The joined entry holds both masks, and
        the projects the user corrects decide between them - see
        mask_history() and pick_active() in chalkline.py.  The mask in use
        stays the one the typed name was already being detected with, until
        the other beats it on a recording they have both been scored against.
        """
        # The name being typed over goes, exactly as it does on a rename
        # that does not collide: the user is saying this entry is "typed",
        # not what it was called.  Its OTHER keys - a service id - stay, and
        # so do the clash's.  Keeping the old name here was how one entry
        # ended up answering to both "ITV1" and "ITV1 HD", two different
        # pictures, with one mask between them.
        keys = list(dict.fromkeys(
            [k for k in entry.get("keys", []) if k != old]
            + list(clash.get("keys", []))
        ))

        channels = self._channels()
        # Located by identity, not by value.  list.index() and "in" both
        # compare with ==, and two entries can compare equal while being
        # different rows - most easily right after a reload, when the list
        # holds fresh copies of the same dictionaries.  Matching the wrong
        # one silently merges the wrong pair.
        at = next((i for i, e in enumerate(channels) if e is entry), -1)
        clash_at = next((i for i, e in enumerate(channels) if e is clash), -1)
        if at < 0 or clash_at < 0:
            log.warning(
                "Could not join the logo entries: the list changed underneath "
                "the edit (entry %s, clash %s).", keys, clash.get("keys"),
            )
            self._status.setText(self.tr(
                "The entries could not be joined - the list had changed. "
                "Try again."
            ))
            return

        # Both histories, the clash's first: the typed name is already being
        # detected with its mask, so that is the incumbent and it keeps its
        # place until the evidence says otherwise.
        history = mask_history(clash)
        incumbent = active_index(clash, history)
        for item in mask_history(entry):
            if not any(same_mask(item["mask"], h["mask"]) for h in history):
                history.append(item)
        history = history[:MASK_HISTORY_MAX]
        merged = write_history(dict(clash), history, incumbent)
        merged["keys"] = keys
        # Learning stays off if it was off for either: the user stopped it
        # for a reason, and joining two names does not change the channel.
        if entry.get("learn", True) is False:
            merged["learn"] = False
        # The merged entry takes the EDITED row's place and the clash row is
        # the one removed, whichever mask ends up in use.  An earlier version
        # removed whichever entry lost the contrast comparison, which did
        # nothing at all when that was the edited row - it had already been
        # replaced on the line above and was no longer in the list.
        channels[at] = merged
        clash_at = next((i for i, e in enumerate(channels) if e is clash), -1)
        if clash_at >= 0:
            del channels[clash_at]

        self._status.setText(self.tr(
            "Joined into one entry holding %(held)d logo(s), using the "
            "%(use)dpx one for now. Correct a detection on this channel and "
            "save it, and the better logo will be chosen on the evidence."
        ) % {
            "held": len(mask_history(merged)),
            "use": int(merged.get("count", 0)),
        })

    # -- actions ------------------------------------------------------------

    def _apply_card_edit(self, entry, col, typed):
        """Rename, pair or join a channel known only by its break ident.

        The same three outcomes as a logo row: a new name is added, a name
        another card-only row already has joins the two, and a name that
        belongs to a logo row pairs this channel with that logo - after which
        the logo's row shows these idents too, because channel_cards() finds
        cards under any name the logo entry lists.
        """
        old = (store_display_name(entry) if col == self.COL_NAME
               else store_service_id(entry))
        if col == self.COL_SID and typed and not typed.startswith(_SID_PREFIX):
            typed = _SID_PREFIX + typed
        if typed == old:
            return
        if not typed:
            keys = [k for k in entry.get("keys", []) if k != old]
            if not keys:
                self._warn(self.tr(
                    "A channel needs at least one of Channel or Service ID. "
                    "Use Forget to remove it entirely."
                ))
                self._fill_table()
                return
            entry["keys"] = keys
            self._fill_table()
            return

        keys = [k for k in entry.get("keys", []) if k != old] + [typed]
        logo = next((e for e in self._channels()
                     if typed in e.get("keys", [])), None)
        if logo is not None:
            if QMessageBox.question(
                self,
                self.tr("Remembered logos"),
                self.tr(
                    "\u201c%s\u201d has a remembered logo. Joining them makes "
                    "this channel's idents part of that channel, so both are "
                    "used together.\n\nJoin them?"
                ) % typed,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            ) != QMessageBox.Yes:
                self._fill_table()
                return
            entry["keys"] = list(dict.fromkeys(keys))
            logo["keys"] = list(dict.fromkeys(
                list(logo.get("keys", [])) + entry["keys"]))
            if entry.get("learn", True) is False:
                logo["learn"] = False
            self._fill_table()
            self._status.setText(self.tr(
                "Joined: %s now uses this channel's idents with its logo."
            ) % (store_display_name(logo) or store_service_id(logo)))
            return

        other = next((e for e in self._cards.get("channels", [])
                      if e is not entry and typed in e.get("keys", [])), None)
        if other is not None:
            if QMessageBox.question(
                self,
                self.tr("Remembered logos"),
                self.tr(
                    "\u201c%s\u201d already has idents of its own. Joining "
                    "them keeps all of them under the one channel."
                    "\n\nJoin them?"
                ) % typed,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            ) != QMessageBox.Yes:
                self._fill_table()
                return
            entry["keys"] = list(dict.fromkeys(keys + list(other.get("keys", []))))
            entry["cards"] = _union_cards(other.get("cards"), entry.get("cards"))
            if other.get("learn", True) is False:
                entry["learn"] = False
            self._cards["channels"] = [e for e in self._cards["channels"]
                                       if e is not other]
            self._fill_table()
            self._status.setText(self.tr(
                "Joined into one channel holding %d ident(s)."
            ) % len(entry["cards"]))
            return

        entry["keys"] = list(dict.fromkeys(keys))
        self._fill_table()

    def _warn(self, text):
        QMessageBox.information(self, self.tr("Remembered logos"), text)

    def _forget(self):
        row = self.table.currentRow()
        channels = self._channels()
        if len(channels) <= row < len(self._rows):
            self._forget_card(self._rows[row][1])
            return
        if not (0 <= row < len(channels)):
            return
        entry = channels[row]
        label = (store_display_name(entry) or store_service_id(entry)
                 or self.tr("this channel"))
        if QMessageBox.question(
            self,
            self.tr("Forget logo"),
            self.tr(
                "Forget the logo remembered for \u201c%s\u201d?\n\nChalkline "
                "will learn it again the next time you correct a detection "
                "for that channel and save the project."
            ) % label,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        del channels[row]
        self._removed_keys |= set(entry.get("keys", []))
        self._fill_table()
        self._status.setText(self.tr("Forgotten: %s") % label)

    def _forget_card(self, entry):
        """Forget a card-only channel's idents."""
        label = (store_display_name(entry) or store_service_id(entry)
                 or self.tr("this channel"))
        if QMessageBox.question(
            self,
            self.tr("Forget idents"),
            self.tr(
                "Forget the idents remembered for \u201c%s\u201d?\n\n"
                "Chalkline will learn them again the next time you correct a "
                "detection for that channel and save the project."
            ) % label,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        self._cards["channels"] = [e for e in self._cards.get("channels", [])
                                   if e is not entry]
        self._removed_card_keys |= set(entry.get("keys", []))
        self._fill_table()
        self._status.setText(self.tr("Forgotten: %s") % label)

    def _save_cards(self):
        """Write the card store back, merged against what is on disk now.

        The same reasoning as the logo store in _save(), one step further:
        an ident learned while this window was open is kept even for a
        channel shown here, because the names and the Learn switch come from
        this window but the idents themselves come from disk.
        """
        try:
            on_disk = load_cards(self._card_path)
        except Exception:
            on_disk = {"channels": []}
        mine = self._cards.get("channels", [])
        my_keys = {k for e in mine for k in e.get("keys", [])}
        my_keys |= self._removed_card_keys
        kept = [e for e in on_disk.get("channels", [])
                if not (set(e.get("keys", [])) & my_keys)]
        written = []
        for entry in mine:
            keys = set(entry.get("keys", []))
            fresh = [e.get("cards") for e in on_disk.get("channels", [])
                     if set(e.get("keys", [])) & keys]
            out = dict(entry)
            out["cards"] = _union_cards(entry.get("cards"), *fresh)
            written.append(out)
        if not (kept or written) and not os.path.exists(self._card_path):
            return      # nothing learned and nothing to write
        save_cards({"version": on_disk.get("version", 1),
                    "channels": kept + written}, self._card_path)

    def _save(self):
        """Write the table back, merged against whatever is on disk now.

        Not a straight overwrite: a background learn may have added a channel
        since this dialog opened, and writing the loaded snapshot back would
        delete it.  Only the entries this dialog actually touched are
        applied.
        """
        try:
            on_disk = load_store(self._store_path)
        except Exception:
            on_disk = {"channels": []}

        mine = self._channels()
        my_keys = {k for e in mine for k in e.get("keys", [])}
        # Forgotten keys count as "mine" too.  They are absent from the table
        # by definition, so without this the row would be read back off disk
        # as an untouched entry and written straight out again - Forget would
        # appear to work and then quietly undo itself on Save.
        my_keys |= self._removed_keys

        kept = [
            e for e in on_disk.get("channels", [])
            if not (set(e.get("keys", [])) & my_keys)
        ]
        merged = {"channels": kept + [dict(e) for e in mine]}

        try:
            save_store(merged, self._store_path)
            self._save_cards()
        except OSError as exc:
            QMessageBox.warning(
                self,
                self.tr("Remembered logos"),
                self.tr("The logo list could not be saved:\n\n%s") % exc,
            )
            return
        self.accept()
