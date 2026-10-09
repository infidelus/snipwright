"""
Export dialogs: a live progress dialog and a completion summary, modelled on
VideoReDo's.

ExportProgressDialog shows a smooth percentage bar, the current phase
("Fast Frame Copy" while stream-copying, "Encoding Frames" at cut boundaries),
a scene counter, and an estimated time remaining.  It exposes Pause is omitted
(smartcut has no pause) - only Abort, which cancels the worker.

ExportCompleteDialog shows a VideoReDo-style stats table.
"""

from PySide6.QtCore import QCoreApplication, QT_TRANSLATE_NOOP, Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from utils.eta import EtaTracker, RECODE_PHASES, format_seconds as _fmt_secs
from utils.note_text import translate_note


# Marked for translation here and translated where shown (self.tr in
# ExportProgressDialog) - left as plain strings, the progress window stayed
# in English in the German interface while everything around it was German.
_WORKING = QT_TRANSLATE_NOOP("ExportProgressDialog", "Working…")
_PHASE_LABELS = {
    "copy": QT_TRANSLATE_NOOP("ExportProgressDialog", "Fast Frame Copy"),
    "encode": QT_TRANSLATE_NOOP("ExportProgressDialog", "Encoding Frames"),
    "crop": QT_TRANSLATE_NOOP("ExportProgressDialog", "Cropping (re-encoding)…"),
    "verify": QT_TRANSLATE_NOOP("ExportProgressDialog", "Verifying output"),
    "finalise_mkv": QT_TRANSLATE_NOOP("ExportProgressDialog", "Finalising MKV…"),
    "recode_audio": QT_TRANSLATE_NOOP("ExportProgressDialog", "Recoding…"),
    # Not "Recoding": the repair re-encodes a handful of frames and
    # copies every other one byte for byte, so calling it a recode
    # misdescribes both what it does and how long it will take.
    "repair_audio": QT_TRANSLATE_NOOP("ExportProgressDialog", "Repairing audio…"),
    # Both streams copied: nothing is being re-encoded, so saying
    # "Recoding" would be a plain untruth about what is happening to
    # the file.
    "repackage_mp4": QT_TRANSLATE_NOOP("ExportProgressDialog", "Repackaging to MP4…"),
    "recode_full": QT_TRANSLATE_NOOP("ExportProgressDialog", "Major recode required…"),
    "rebuild_audio": QT_TRANSLATE_NOOP("ExportProgressDialog", "Rebuilding audio…"),
    "graft_audio": QT_TRANSLATE_NOOP("ExportProgressDialog", "Copying audio…"),
    "done": QT_TRANSLATE_NOOP("ExportProgressDialog", "Finishing"),
}


def _fmt_size(num_bytes):
    mb = num_bytes / (1024 * 1024)
    if mb < 1024:
        return f"{mb:.0f} MB"
    return f"{mb / 1024:.2f} GB"


def _fmt_duration(secs):
    secs = int(round(secs))
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_bitrate(bps):
    if not bps:
        return "—"
    mbps = bps / 1_000_000
    if mbps >= 1:
        return f"{mbps:.2f} Mbps"
    return f"{bps / 1000:.0f} kbps"


def _esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class ExportProgressDialog(QDialog):

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setWindowTitle(self.tr("Exporting"))
        self.setModal(True)
        self.setMinimumWidth(420)

        self._eta = EtaTracker()
        self._phase = ""
        self._aborted = False

        layout = QVBoxLayout(self)

        self._title_label = QLabel(title)
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        layout.addWidget(self._bar)

        self._eta_label = QLabel(self.tr("Estimated time remaining: —"))
        layout.addWidget(self._eta_label)

        row = QHBoxLayout()
        self._phase_label = QLabel(self.tr("Preparing…"))
        self._scene_label = QLabel("")
        row.addWidget(self._phase_label)
        row.addStretch(1)
        row.addWidget(self._scene_label)
        layout.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self._batch_btn = QPushButton(self.tr("Send to Batch"))
        self._batch_btn.setFocusPolicy(Qt.NoFocus)
        self._batch_btn.setToolTip(
            self.tr("Hand this export to the Batch Manager and carry on working. "
            "It keeps running from where it is - nothing restarts, and the "
            "file still goes where you asked.")
        )
        self._batch_btn.clicked.connect(self._on_send_to_batch)
        self._batch_btn.hide()          # shown only when a handler is set
        btn_row.addWidget(self._batch_btn)
        self._abort_btn = QPushButton(self.tr("Abort"))
        self._abort_btn.setFocusPolicy(Qt.NoFocus)
        self._abort_btn.clicked.connect(self._on_abort)
        btn_row.addWidget(self._abort_btn)
        layout.addLayout(btn_row)

        self._abort_callback = None
        self._batch_callback = None

    def current_percent(self):
        """The percentage last reported, or 0 during an indeterminate phase."""
        if self._bar.maximum() == 0:
            return 0
        return max(0, self._bar.value())

    def current_phase(self):
        """The phase last reported, for seeding the Batch Manager's row."""
        return self._phase

    def eta_tracker(self):
        """The live estimate for this export.

        Handed to the Batch Manager along with the worker when an export is
        sent to the background.  Transferring the tracker rather than starting a
        new one matters: a fresh tracker would time the remaining work from the
        moment of handover while reading a percentage that started much
        earlier, and conclude that a job at 40% was nearly finished.
        """
        return self._eta

    def set_abort_callback(self, cb):
        self._abort_callback = cb

    def set_batch_callback(self, cb):
        """Offer 'Send to Batch'.  The callback hands the running export over
        to the Batch Manager; this dialog just closes afterwards."""
        self._batch_callback = cb
        self._batch_btn.setVisible(cb is not None)

    def _on_send_to_batch(self):
        if self._batch_callback is None:
            return
        self._batch_btn.setEnabled(False)
        if self._batch_callback():
            self.close()
        else:
            self._batch_btn.setEnabled(True)

    def _on_abort(self):
        self._aborted = True
        self._abort_btn.setEnabled(False)
        self._abort_btn.setText(self.tr("Aborting…"))
        if self._abort_callback is not None:
            self._abort_callback()

    def update_progress(self, info):
        percent = info.get("percent", 0)
        phase = info.get("phase", "copy")

        # A join reports its own line of text, time estimate included: it runs
        # in stages (each scene, then a whole-file pass) and restarts the bar
        # for each, which this dialog's estimator - timing one bar from start
        # to finish - would misread.  So show the Joiner's own text instead.
        if phase == "join":
            self._phase = phase
            if self._bar.maximum() == 0:
                self._bar.setRange(0, 100)
            self._bar.setValue(max(0, int(percent)))
            # The Joiner translates its own label before sending it.
            self._phase_label.setText(info.get("label") or self.tr("Joining…"))
            self._scene_label.setText("")
            self._eta_label.setText("")
            return
        scene = info.get("scene", 1)
        total_scenes = info.get("total_scenes", 1)

        remaining = self._eta.update(info)
        self._phase = phase

        # A negative percent means "busy, but with no measurable progress" - the
        # mkvmerge mux and audio verify/rebuild, which can take 20-30s with
        # nothing to count.  Show a pulsing indeterminate bar and a clear phase
        # label so it never looks frozen at 99%.
        if percent < 0:
            self._bar.setRange(0, 0)
            self._phase_label.setText(self.tr(_PHASE_LABELS.get(phase, _WORKING)))
            self._scene_label.setText("")
            self._eta_label.setText(self.tr("Estimated time remaining: …"))
            return

        if self._bar.maximum() == 0:
            self._bar.setRange(0, 100)
        self._bar.setValue(percent)

        self._phase_label.setText(self.tr(_PHASE_LABELS.get(phase, _WORKING)))

        recoding = phase in RECODE_PHASES
        if recoding or phase in ("verify", "done"):
            self._scene_label.setText("")
        else:
            self._scene_label.setText(
                self.tr("Scene %(scene)d of %(total)d")
                % {"scene": scene, "total": total_scenes})

        # Estimated time remaining.
        if remaining is not None:
            self._eta_label.setText(
                self.tr("Estimated time remaining: %s")
                % _fmt_secs(remaining)
            )
        elif percent >= 100:
            self._eta_label.setText(self.tr("Estimated time remaining: done"))
        else:
            self._eta_label.setText(self.tr("Estimated time remaining: …"))


def _subtitle_summary(stats):
    """The subtitle tracks the finished file carries, as one line -
    "DVB subtitles (eng)", several joined with commas - or "None".

    Read from the OUTPUT, not the source, so it reports what was kept.  The
    exporter and the joiner probe the finished file once and store the result
    in stats["subtitle_tracks"], which the log's summary prints too - so the
    window and the log cannot disagree.  Only the track names are translated
    here.  Returns "" when the file could not be read, so the row is left out
    rather than claiming "None".
    """
    from export.exporter import describe_subtitle_tracks, probe_subtitle_tracks
    from utils.program_info import _SUBTITLE_TYPES

    if "subtitle_tracks" in stats:
        tracks = stats["subtitle_tracks"]
    else:
        tracks = probe_subtitle_tracks(stats.get("out_path", ""))
    if tracks is None:
        return ""
    if not tracks:
        return QCoreApplication.translate("ExportCompleteDialog", "None")

    def name_of(codec):
        kind = _SUBTITLE_TYPES.get(codec)
        return (QCoreApplication.translate("ProgramInfo", kind) if kind
                else (codec or "?").upper())

    return describe_subtitle_tracks(tracks, name_of)


class ExportCompleteDialog(QDialog):

    def __init__(self, stats, parent=None):
        super().__init__(parent)

        self.setWindowTitle(self.tr("Output Processing Complete"))
        self.setModal(True)
        self.setMinimumWidth(340)

        self._out_path = stats.get("out_path", "")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        out_path = self._out_path
        filename = out_path.rsplit("/", 1)[-1] if out_path else ""

        # The labels are marked for translation here and translated as the
        # table is built.  They used to be plain strings, so this one dialog
        # stayed English in the German build - only its title was translated.
        rows = [
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Video length:"),
             _fmt_duration(stats.get("duration_secs", 0))),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Video size:"),
             _fmt_size(stats.get("out_size", 0))),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Output scenes:"),
             str(stats.get("scenes", 0))),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Video output frames:"),
             f"{stats.get('video_frames', 0):,}"),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Audio output frames:"),
             f"{stats.get('audio_frames', 0):,}"),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Audio tracks:"),
             str(stats.get("audio_tracks", 0))),
        ]
        subtitles = _subtitle_summary(stats)
        if subtitles:
            rows.append((QT_TRANSLATE_NOOP("ExportCompleteDialog",
                                           "Subtitles:"), subtitles))
        rows += [
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Processing time:"),
             _fmt_secs(stats.get("processing_secs", 0))),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Processed frames/sec:"),
             f"{stats.get('fps', 0):.0f}"),
            (QT_TRANSLATE_NOOP("ExportCompleteDialog", "Video bitrate:"),
             _fmt_bitrate(stats.get("video_bitrate", 0))),
        ]

        # Build alternating-row HTML table (VideoReDo-style).
        row_html = []
        for i, (label, value) in enumerate(rows):
            bg = "#2f3136" if i % 2 == 0 else "#26282c"
            row_html.append(
                f'<tr style="background:{bg};">'
                f'<td style="padding:8px 18px; color:#9aa0a6; '
                f'white-space:nowrap;">{_esc(self.tr(label))}</td>'
                f'<td style="padding:8px 18px; color:#e8eaed; '
                f'font-weight:600;" align="right">{_esc(value)}</td>'
                f'</tr>'
            )

        errors = stats.get("errors", [])
        notes = stats.get("notes", [])

        # Footnotes continue the figures' alternating-row pattern so they sit
        # flush with the rows above (VRD-style asterisks); detail is in the log.
        #
        # A note is a (headline, explanation) pair.  This used to hand the
        # whole pair to _esc(), so the dialog showed Python's own rendering of
        # a tuple - brackets, quotes, comma and all - followed by a paragraph
        # of explanation that made the box taller than the figures it was
        # annotating.  Only the headline belongs here; the explanation is
        # already written to the log next to it, which is where the other
        # long-form detail lives.
        for j, note in enumerate(notes):
            if isinstance(note, (tuple, list)):
                text = note[0] if note else ""
            else:
                text = note
            if not text:
                continue
            # Written in English for the log; shown in the user's language.
            text = translate_note(text, QCoreApplication.translate)
            bg = "#2f3136" if (len(rows) + j) % 2 == 0 else "#26282c"
            row_html.append(
                f'<tr style="background:{bg};">'
                f'<td colspan="2" style="padding:8px 18px; color:#9aa0a6;">'
                f'* {_esc(text)}</td></tr>'
            )
        if notes:
            # The tr() call is pulled OUT of the f-string deliberately.
            # pyside6-lupdate does not look inside an f-string's expressions,
            # so a tr() written there is invisible to it: the string never
            # reaches the .ts files and can never be translated, with nothing
            # to show anything is wrong.  It was written that way first and
            # caught only because the new-string count did not move.
            see_log = self.tr("See the log for the full explanation.")
            bg = "#2f3136" if (len(rows) + len(notes)) % 2 == 0 else "#26282c"
            row_html.append(
                f'<tr style="background:{bg};">'
                f'<td colspan="2" style="padding:8px 18px; color:#9aa0a6; '
                f'font-size:11px;">'
                f'{_esc(see_log)}'
                f'</td></tr>'
            )

        # Top status line: blank on a clean export; genuine problems shown in a
        # warning colour so they're noticed.  Full detail is in the log.
        status_row = ""
        if errors:
            status_row = (
                '<tr style="background:#3a3d42;">'
                '<td style="padding:0 18px 18px 18px; color:#e0915f; '
                'font-size:12px;">'
                + "<br>".join(
                    _esc(translate_note(e, QCoreApplication.translate))
                    for e in errors)
                + '</td></tr>'
            )
        header_pad_bottom = "8px" if errors else "18px"

        # The header uses the same single-column table + 18px cell padding as
        # the rows below, so the filename and status line up with the labels.
        html = f"""
        <table cellspacing="0" cellpadding="0" width="100%">
          <tr style="background:#3a3d42;">
            <td style="padding:18px 18px {header_pad_bottom} 18px;
                       font-size:15px; font-weight:700; color:#f1f3f4;
                       line-height:150%;">
              {_esc(filename)}
            </td>
          </tr>
          {status_row}
        </table>
        <table cellspacing="0" cellpadding="0" width="100%"
               style="font-size:12px;">
          {''.join(row_html)}
        </table>
        """

        body = QLabel(html)
        body.setTextFormat(Qt.RichText)
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body.setAlignment(Qt.AlignTop)
        # Constrain the width so long filenames wrap instead of stretching the
        # dialog wide.  This keeps the dialog compact and tall like VideoReDo's.
        body.setMaximumWidth(360)
        layout.addWidget(body)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(14, 12, 14, 12)

        open_btn = QPushButton(self.tr("Open Folder"))
        open_btn.setFocusPolicy(Qt.NoFocus)
        open_btn.clicked.connect(self._open_folder)
        btn_row.addWidget(open_btn)

        btn_row.addStretch(1)

        ok = QPushButton(self.tr("OK"))
        ok.setDefault(True)
        ok.setFocusPolicy(Qt.NoFocus)
        ok.clicked.connect(self.accept)
        btn_row.addWidget(ok)

        layout.addLayout(btn_row)

        self.setMaximumWidth(380)

    def _open_folder(self):
        import os
        from utils.open_path import open_path

        folder = os.path.dirname(self._out_path)
        if folder and os.path.isdir(folder):
            open_path(folder)
