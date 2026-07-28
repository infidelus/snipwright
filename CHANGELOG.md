# Changelog

All notable changes to Snipwright are documented here. Releases before
2.0.0 were published under the project's former name, VRD Next.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-07-28

### Fixed

- **The Windows icon was pixellated.** Two faults, one on top of the other: the
  `.ico` files at first contained only a 16x16 frame, and once the other sizes
  were added they were all PNG-compressed. Windows only reads PNG frames
  reliably at 256x256 — below that Explorer wants a BMP frame, and falls back to
  scaling whatever it can decode. Both icons now carry ten frames from 16x16 to
  256x256, stored as BMP below 256 and PNG at 256, which is what Windows
  expects.

  The Windows installer was also setting the shortcut's `IconLocation` without
  an index. Windows wants `"path,index"` there, and without it does not reliably
  choose the right frame from a multi-size icon — commonly settling on the
  smallest and scaling it up. The `.vprj` registration had always set an index;
  the shortcut had been missed. The installer now also nudges the shell to drop
  its icon cache, since Windows will otherwise keep showing an icon it drew
  before the file was replaced.

### Changed

- **VRD Next is now Snipwright.** One of VideoReDo's original developers asked
  that "VRD" not appear in the name: he still owns the VideoReDo domains, and a
  similarly-named project risks people assuming the two are connected and
  sending him support requests for software he has nothing to do with. That's a
  fair thing to ask and it costs nothing to honour, so the application, the
  repository and the settings folder have all been renamed. He was happy for
  VideoReDo to keep being mentioned in the documentation, which it is — the
  guide still has its "Coming from VideoReDo" section, and the project is still
  built for people who relied on that software.

  Nothing about how it works has changed, and it still reads and writes
  VideoReDo's `.vprj` project files exactly as before.

- **Settings now live in `~/.config/snipwright/`.** On first run, an existing
  `vrd-next` folder is *copied* across — settings, output profiles, the batch
  queue and its staged projects,
  and the watcher's ignore list with its last-seen dates. Copied rather than
  moved, so the old folder is left exactly as it was and going back to an
  earlier version costs nothing. It runs at most once, and never overwrites
  settings that are already there. Log files are skipped. You're told when it
  happens rather than having your configuration moved about silently. The same
  applies on Windows, where the folder lives under your user profile.

  A start-on-login entry written under the old name is removed when the Watcher
  next checks or changes that setting, so an upgrade can't leave two watchers
  starting with the desktop.

## [1.10.0] - 2026-07-27

### Added

- **Send a running export to the Batch Manager.** A long re-encode used to hold
  the editor hostage until it finished. The export window now has a **Send to
  Batch** button that hands the job over and gives you the editor back.

  Nothing restarts and no encoding time is lost: the export carries on from
  exactly where it had reached, still writing to the destination you chose under
  the name you gave it. All that changes is that it reports its progress as a row
  in the Batch Manager, shown as *Exporting… 47%*. The batch runner steps over it,
  so pressing **Start** processes the other queued jobs and leaves that one to
  finish on its own. Changed your mind? Select the row and press **Remove** — that
  offers to stop the export and discard the part-finished file. Quitting VRD Next
  while one is still running warns you first, and if the application is closed or
  crashes the job returns to the queue as an ordinary entry, still bound to the
  destination you originally picked.

- **Keyframe spacing is now a profile setting.** VRD Next hard-coded a keyframe
  every second in every re-encode, which is broadcast practice — it suits a
  stream you might need to join at any moment, and is wasteful for a file you are
  going to watch. Keyframes are several times the size of the frames between them
  and they reset the encoder's prediction chain, so an HEVC export was larger than
  it needed to be for the same quality. **Keyframes every** in the profile editor
  now controls this, with **Automatic** using five seconds for HEVC and keeping
  one second for the H.264 crop path. (VideoReDo called this Max GOP length.)

  This changes the output of existing HEVC profiles: they'll produce smaller files
  at the same CRF. On a measured hour-long 1080p recording the same export dropped
  from 1.42 GiB to 1.29 GiB — about 9% — with everything else identical. Quality
  is unchanged, since only the keyframe spacing differs, and anyone who wants the
  old behaviour back can set it to one second explicitly.

- **Ignore-list housekeeping.** The Watcher's ignore list can now tidy itself up.
  Each entry records when a new recording last matched it, and under
  **Housekeeping** in the ignore list editor you can have entries dropped once
  nothing has matched for a chosen number of months (twelve by default, which
  suits series that return annually). It's off by default. **Review and prune
  now** lists every title with the date it was last seen, oldest first, with the
  stale ones ticked ready to remove so you can untick anything worth keeping.

  "Last seen" is the date of the matching *recording*, not of the scan that
  noticed it, so old episodes left sitting in a folder don't keep an entry looking
  permanently fresh. Pruning an entry marks any recordings still in the watched
  folders that matched it as already done, so tidying the list never sends a
  back-catalogue through Comskip; genuinely new recordings are picked up as
  normal.

- **Mouse-wheel scrubbing.** Over the picture, the thumbnail strip or the
  navigation bar, a notch of the wheel moves one frame; hold `Ctrl` and each notch
  moves by the short skip distance instead. Scrolling up moves forward through the
  recording, scrolling down moves back. Trackpads and high-resolution wheels are
  accumulated to whole notches, so they scrub steadily rather than flying off down
  the timeline. The wheel keeps its existing job wherever it had one — scrolling
  the scene list, adjusting the volume.

- **Estimated time remaining in the Batch Manager.** The progress bar now reads
  something like `Encoding — 76% — 4m 12s left`. The clock starts at the first
  measurable progress rather than when the job starts, since indexing happens
  before anything can be counted, and a re-encode is timed separately from the
  much faster stream copy that preceded it. Nothing is shown while a phase has no
  measurable progress, rather than freezing a stale figure that ticks down to a
  lie. Closing and reopening the Batch Manager mid-batch doesn't restart the
  clock.

- **A "Coming from VideoReDo" section in the user guide**, mapping the old names
  onto the new ones — Intelligent Recode, Force Recode, Max GOP length, Quality
  Factor Adjustment and the rest. Several features were already there under
  different names, which isn't obvious to anyone searching for the vocabulary they
  know. It's also honest about what has no equivalent.

- **The German user guide is complete again.** Four subsections had never been
  translated — both editing-mode walkthroughs, the navigation-bar colour key and
  the whole Joiner section — and two headings were still in English, so a German
  reader had no documentation of Cut Mode at all. Both guides now carry the same
  28 sections in the same order. The German guide also named buttons that don't
  exist in the German interface (looking for "In-Punkt setzen" when the button
  reads "Anfang markieren", among others); every UI term it mentions is now taken
  from the actual translations. The interface itself has been fully translated
  throughout.

### Fixed

- **Quick Stream Fix could hang forever.** ffmpeg's warnings were read from a pipe
  that was only drained *after* the process finished. A pipe holds about 64 KiB;
  once full, ffmpeg blocked writing the next warning, which stopped it writing
  progress, which left VRD Next waiting for a line that could never arrive.
  Remuxing an MPEG program stream produced 3.7 MB of warnings — sixty times the
  buffer — on a thirty-second clip, and damaged broadcast recordings are just as
  capable of it, which is unfortunate for the tool that exists to repair them.
  Warnings now go to a temporary file that can't block. The same pattern was
  present in the exporter, the joiner's re-encode and the crop runner, and has
  been fixed in all of them.

- **A failed re-encode no longer passes for a finished export.** When a profile
  asks for HEVC, the recording is cut first and the re-encode runs afterwards as a
  finishing pass. If that pass failed, the exporter kept the cut file — which is
  in the *source* codec — logged a warning, and then reported "Export complete".
  The result was a file with exactly the name the finished article was going to
  have, in the wrong format, presented as a success. It now says so in the export
  summary, and in a batch the job is held for review with its output removed
  rather than marked Done.

- **Cancelling during the finishing re-encode now removes the output.** A killed
  encoder exits non-zero and looked identical to a failure, so cancelling an HEVC
  export part-way left the source-codec cut behind under the final name — and the
  log claimed the partial output had been cleaned up when nothing had been
  deleted.

- **"Add from Watch Folder" no longer queues a recording twice.** It compared
  project file paths only, so a recording already queued via Queue to Batch —
  which arrives as a timestamped staging file — was added again from the watcher's
  own copy of the same project. It now compares the recording each project points
  at, skips anything already queued, and reports how many it skipped.

- **`.mpg`, `.mpeg` and `.vob` files can now be selected in Open Video.** They
  always opened perfectly well once loaded — the extensions were simply missing
  from the dialog's filter, so the files weren't shown unless you switched to All
  files. The save dialog and drag-and-drop had always accepted them.

- **The Watcher's ignore list editor could be opened several times over.** The
  tray's context menu is a popup owned by the tray rather than an application
  window, so the dialog's modality didn't stop the menu item being chosen again
  while it was already open, and each click stacked up another copy — whichever
  was saved last quietly won. Choosing it again now brings the open editor to the
  front.

- The Batch Manager's progress bar dropped back to zero during phases with nothing
  to count (the audio graft, the mux, the finalise pass), which looked as though
  the job had restarted. It now pulses as an indeterminate bar, the way the export
  dialog already did.

- The Batch Manager showed the same output filename for two jobs cut from the same
  recording. The runner has always added a ' (2)' so nothing was ever overwritten,
  but the preview didn't show it and implied a clash.

- Four German dialogue messages showed a literal `\n` instead of a line break.

### Changed

- The user guide now documents the Watcher's ignore list, which it had never
  covered, in both English and German.

## [1.9.0] - 2026-07-24

The big feature is **Cut Mode** - VideoReDo's default way of working, where you
start with the whole programme and cut the unwanted parts out - alongside a
batch of fixes prompted by the project's first users. Subtitle tracks are now
kept, more awkward broadcast recordings repair and export cleanly, and several
smaller rough edges are smoothed.

### Added

- **Cut Mode**, selectable under Settings -> General (and now the default, as in
  VideoReDo). Cut Mode starts with the whole recording selected and you cut
  sections out; Scene Mode (the previous behaviour) starts empty and you mark
  what to keep. Both share the same cut list and produce identical output - the
  buttons, scene list and navigation bar relabel to match the mode, and you can
  re-mark over an existing cut to adjust it. Switching modes updates the
  interface at once; the starting state applies to the next video opened.
- **DVB subtitle passthrough.** Subtitle tracks are carried through and cut to
  match the video when saving to `.ts` or `.mkv` (MP4 can't carry DVB
  subtitles).
- **Configurable skip distances.** The three navigation jumps (short/medium/
  long, 10/30/120 seconds by default) can be set under Settings -> General, with
  a reset button; the buttons' hover hints follow whatever you choose.
- **Duplicate prompts.** Queueing a recording that's already in the batch queue,
  or adding an identical selection to the joiner, now asks first rather than
  silently adding it again.

### Changed

- The "Show tooltips" and editing-mode settings apply immediately instead of
  needing a restart.
- The user guide covers both modes, the navigation-bar colour key, subtitle
  handling, and clearer advice on correcting cut marks moved between editors.

### Fixed

- **Audio-description tracks are no longer dropped.** A genuine but sparsely-
  transmitted AD track (seen on a Film4 recording) was mis-read as empty by a
  too-short probe and discarded; both the repair and export steps now probe
  thoroughly enough to recognise and keep it.
- **Quick Stream Fix succeeds on more recordings.** The same short-probe issue
  made QSF fail outright ("sample rate not set") on some multi-track broadcasts;
  it now repairs them and keeps every real track.
- The navigation bar highlights the correct section in Cut Mode (the selected
  cut, not a mismatched scene).
- The export warning no longer implies the main audio is missing when only a
  secondary track (such as audio description) was affected.

## [1.8.0] - 2026-07-17

A robustness, cross-platform and housekeeping release: hardened installers on
both Linux and Windows, working start-on-login and file associations on
Windows, safer configuration storage, and a batch of Batch Manager and audio
fixes.

### Added

- **Windows start-on-login.** The Watcher's "start on login" checkbox now works
  on Windows as well as Linux, placing a launcher in the Startup folder (and
  removing it when unticked). No manual `shell:startup` setup needed.
- **`.vprj` file association on Windows** and a distinct project-file icon on
  both platforms, so project files are recognisable at a glance and offer
  VRD Next under "Open with" (without displacing an existing default such as
  VideoReDo or a text editor).
- **Command Prompt installer for Windows** (`install-windows.bat`) that runs the
  setup without needing to change PowerShell's execution policy.
- **Renamer cache age limit.** Settings → Maintenance can purge remembered
  TV/film matches older than a chosen number of days (0 = keep forever), with a
  "delete now" button.

### Changed

- **Configuration is split by purpose.** The renamer match cache and the batch
  queue now live in their own files (`renamer-cache.json`, `queue.json`) instead
  of bloating `settings.json`, each migrated automatically on first run.
- **Output paths use the platform's native separator** — no more mixed
  `C:/Users/...ile.mkv` on Windows.
- **Audio device status is logged at startup**, so a sound problem can be
  diagnosed from the log ("output device ready …" or "no default output
  device found").
- Batch Manager: the progress bar seeds immediately when opened mid-run; queued
  jobs can be reordered during a run; Clear Finished works mid-run; and the
  "stopping after the current file" message survives reopening the window.

### Fixed

- **No audio in the preview player until the app was restarted.** If the audio
  device wasn't ready the moment VRD Next started, the playback sink came up
  dead and stayed silent for the session regardless of the volume control. It's
  now rebuilt automatically when playback starts, so sound recovers without a
  restart.
- **Finished batch jobs could return as queued** (and re-process, producing a
  duplicate) if the app closed at the wrong moment. Terminal status is now
  written to disk synchronously as each job finishes.
- **Configuration writes are atomic**, so an interrupted or concurrent write can
  no longer truncate or corrupt `settings.json` and lose every setting.
- **The Linux and Windows installers no longer fail silently** when
  `requirements.txt` is empty or a dependency download is interrupted — they
  verify the packages actually import and reinstall if not.
- The chosen output profile is remembered across a Quick Stream Fix.

## [1.7.0] - 2026-07-14

### Added

- **Lossless LATM audio passthru.** UK broadcast AAC (LATM/LOAS framing) is now
  unwrapped to plain AAC as the cut is made — byte-for-byte identical audio,
  verified on real BBC recordings including HE-AACv2 audio-description tracks —
  so the post-cut audio graft no longer runs in the common case and stays only
  as a verified fallback. Mid-programme configuration changes are handled
  transparently.
- **Drag and drop.** Drop a video onto the window to open it, several to fill
  the joiner, or a `.vprj` to open its project.
- **"Open with VRD Next" opens the file.** File-manager launches now load the
  passed file (previously the app opened empty), and the desktop registration
  covers `.mp4`, `.mpg`, `.mov`, `.avi` and `.vprj` as well as `.ts`/`.mkv`.

### Changed

- **Packet interleaving moved into the cut**, retiring the separate post-export
  re-interleave pass — exports finish sooner. The `.ts` finalise step now runs
  only when there are audio dispositions to restore.
- **Audio-description labelling mirrors the source faithfully** (language and
  dispositions, including the visual-impaired flag, with no invented track
  names), consolidated into one helper shared by all container writers. This
  also fixes the main track showing as a bare index when only the description
  track was named.
- Batch Manager: the progress bar seeds immediately when opened mid-run; queued
  jobs can be reordered during a run; Clear Finished works mid-run.

### Fixed

- **Interlaced cut boundaries** on 1080i and 576i recordings were re-encoded
  progressive, causing combing on motion for the re-encoded stretch after each
  cut. The boundary encoder now matches the source's interlacing, handling
  mixed MBAFF content frame by frame; progressive sources are unaffected.
- **Quick Stream Fix**: no longer strips secondary audio tracks, fails on data
  or unrecognised streams, displaces audio-description timing, or fails on
  recordings with a declared-but-dead audio PID ("sample rate not set").
- The chosen output profile is remembered across a Quick Stream Fix instead of
  resetting to the last container match.

## [1.6.0] - 2026-07-12

### Added

- **Open several files at once.** Selecting more than one file in
  File → Open Video brings up an Open Multiple Files dialogue (modelled on
  VideoReDo's): reorder by dragging or sort by name, then every file is added
  — whole — to the Joiner list and the Joiner opens.
- **Multi-track lossless audio.** The broadcast-audio graft now covers
  recordings with more than one audio track, so Channel 4 HD-style
  audio-description tracks are kept losslessly and in sync instead of being
  dropped by the re-encode fallback. A safety net verifies every grafted track
  decodes, falling back to the previous behaviour if anything is off.
- **Audio-description labelling in every container.** The "visual impaired"
  marking a .ts carries is now re-stated on export: MKV gets Matroska's
  visual-impaired flag plus a track name, MP4 gets the name in its handler
  atom, so players label the track as the broadcaster intended.

### Fixed

- **Quick Stream Fix no longer strips secondary audio tracks** (it kept only
  one stream per type), no longer fails outright on recordings carrying data
  or unrecognised streams (SCTE-35 splice markers, EPG oddments — these are
  now skipped), and **no longer displaces audio-description timing**: ffmpeg's
  discontinuity correction misread the AD track's legitimate transmission gaps
  during ad breaks and shifted its narration by minutes; QSF now preserves
  every stream's timing exactly.
- **Audio dropouts in Kodi/VLC/Jellyfin after cutting.** Exports could leave a
  long run of video-only packets at a cut seam with the matching audio muxed
  many seconds later; players with small demux buffers played silent video
  until the skew passed. Finished .ts exports now get a fast lossless
  re-interleave pass. (Existing affected files can be repaired by running
  Quick Stream Fix on them.)
- **File dialogs were case-sensitive on Linux**, hiding upper-case names such
  as `VIDEO.MP4` until the filter was switched to All files. Every open/save
  dialog now matches both cases.

## [1.5.1] - 2026-07-11

### Changed

- **Create Video From Joiner List** now uses the same Save Video dialogue as
  everywhere else, with full output profiles, matching VideoReDo. A plain
  lossless-copy profile takes the proven fast path (container change only,
  byte-for-byte video, per-scene MKV chapters preserved); a profile that
  processes the picture or audio (HEVC, crop, aspect, or AAC re-encode) is
  applied to the joined result in a single whole-file pass, so the output is
  identical to what Save Video produces for the same profile.
- The Linux installer's virtual environment is now built on Python 3.12,
  installs the Qt runtime libraries the PySide6 wheels need (notably
  `libxcb-cursor0`, without which the application starts and then dies without
  a window on a fresh install), and finishes with an import check that prints
  the exact error if a dependency didn't install. A failed `apt-get update`
  no longer aborts the install.

### Fixed

- **Crop Preview showed anamorphic recordings squashed.** UK SD broadcasts are
  stored 720x576 but displayed 16:9; the preview showed the stored pixel grid.
  The frame is now resampled to square pixels using the stream's sample aspect
  ratio, so the picture keeps its on-screen shape. Crop values are unaffected.
- **Cancelling a join mid-render now reports a quiet "Cancelled."** instead of
  an error box, and removes the partial output file.

## [1.5.0] - 2026-07-09

### Added

- **Encoder speed and quality settings** in the output profile editor, for the
  paths that actually re-encode (HEVC output, or cropping). **Encoder speed**
  chooses the x264/x265 preset (Slower … Fastest) and **Quality (CRF)** sets the
  constant rate factor, with an **Automatic** option. Both default to the values
  VRD Next used previously - `faster`, and CRF 24 for HEVC or 20 for H.264 - so
  existing profiles produce identical output. They are disabled for lossless
  profiles, where they have no effect.
- Unusually low (<18) or high (>30) CRF values now ask for confirmation,
  explaining the consequence. Out-of-range values and unknown presets fall back
  to safe defaults, so a hand-edited profile file cannot break an export.

### Changed

- The output profile editor sizes itself to its contents rather than a fixed
  height, so no rows are clipped - including in translations, whose longer text
  needs more room.
- The timeline's cut regions use a slightly lighter red, reading more clearly
  against the green kept scenes.

## [1.4.0] - 2026-07-09

### Added

- **A translatable interface.** Every user-facing string — menus, dialogs,
  buttons, tooltips, messages, the tray Watcher and the stream-info panel — is
  now translatable, with a **Language** setting under **Settings → General**.
  A complete **German** translation is included, along with a German user guide.
  Adding a language needs no code: translate `translations/snipwright_en.ts`,
  compile it with `translations/compile.sh`, and it appears in the picker.
  Changing language offers to restart the application.
- Qt's own translations are loaded alongside, so standard buttons (OK, Cancel,
  Save) and the file dialogs follow the chosen language too.
- The user guide is shown in the chosen language when a translated copy
  (`assets/help/user-guide_<code>.html`) exists, falling back to English.
- **Batch Manager: remove waiting jobs while the queue is running.** The job
  being processed is protected; everything still waiting can be removed.
- **Batch Manager: a choice when stopping** — finish the current file and then
  stop, or stop straight away.

### Changed

- Theme changes now apply live across the whole interface — chrome, transport
  readouts, icons and buttons — rather than needing a restart.
- Opening a `.vprj` project with *Quick Stream Fix on open* now repairs the
  source first and indexes once, instead of indexing, repairing and re-indexing.
  It's faster, and the project's scene markers map directly onto the repaired
  file rather than being approximated from a frame-count delta.
- **Clear Finished** in the Batch Manager now removes only jobs that completed.
  Cancelled, failed and held jobs stay, matching the behaviour of failed jobs and
  keeping interrupted work resumable.
- The Watcher follows the editor's theme and language.
- The window title no longer repeats the application name.
- The Windows installer targets Python 3.14 and detects a genuine Python
  installation rather than the Microsoft Store's placeholder `python.exe`.
- The Linux installer checks for `ensurepip` and installs the matching
  `python3.X-venv` package, which newer Ubuntu releases require.

### Fixed

- A crash (stack overflow) when switching theme, caused by a palette-change
  recursion in the transport panel.
- The transport panel's readouts kept the old theme's colours after a live theme
  change, because they read their own (stylesheet-resolved) palette.
- Check and radio indicators were nearly invisible on the Light theme.
- The TV renamer no longer misreads an episode whose title looks like an episode
  number — for example a title of "E2" after `S03E21` — as a two-parter.
- The stream-info panel's audio section headings and its "Copy to clipboard"
  output are translated rather than always English.

## [1.3.0] - 2026-07-05

### Added

- **Light and dark themes.** A **Theme** setting (Follow system, Light or Dark)
  under **Settings → General**, applied live without a restart. The Light theme
  echoes the classic VideoReDo look; the timeline and thumbnail bars stay dark in
  every theme by design.
- **HEVC output.** Output profiles gain a **Video** option — **Copy** (the
  lossless default) or **HEVC (re-encode)** to H.265 for much smaller files. It's
  opt-in per profile, and the lossless cutting path is unchanged when it's set to
  Copy. Interlaced sources are deinterlaced when re-encoding to HEVC.
- **Renamer presets.** Save your own naming patterns as named presets in the TV
  and Film renamers (each keeps its own list), with **Save…** and **Delete**.
- **More input formats.** `.mp4`, `.m2ts`, `.mov` and `.avi` can be opened
  alongside `.ts` and `.mkv`, with an "All files" fall-back.
- **Per-channel Comskip `.ini`.** When a recording's filename contains the
  channel name (for example Tvheadend, via its `$c`), the watcher and manual
  detection can pick a `Comskip_<channel>.ini` from beside the main `.ini` — the
  longest, case-insensitive match winning. Enabled under
  **Settings → External tools**.
- **One-step installers.** `packaging/install-linux.sh` (Debian/Ubuntu/Mint) and
  `packaging/install-windows.ps1` (Windows, via winget) set up the dependencies, a
  virtual environment and menu/desktop shortcuts. A multi-resolution app icon is
  included for the shortcuts.

### Changed

- Theme changes now apply live across the whole interface — chrome, transport
  readouts, icons and buttons — rather than needing a restart.

### Fixed

- A crash (stack overflow) when switching theme, caused by a palette-change
  recursion in the transport panel.
- The TV renamer no longer misreads an episode whose title looks like an episode
  number — for example a title of "E2" after `S03E21` — as a two-parter.

## [1.2.0] - 2026-07-02

### Added

- **In-app user guide.** A full illustrated user guide, reached from
  **Help → User Guide**, walks through the editor, cutting, profiles, the
  renamers, Comskip and the watcher/batch, with annotated screenshots.
- **External tool paths.** A new **Settings → External tools** page for
  ffmpeg, ffprobe, mkvmerge and Comskip. Paths are auto-detected from your `PATH`,
  or you can point at a specific build (for example a newer ffmpeg than your
  distribution ships). You're warned if a required tool is missing, or if a path
  you've set no longer exists.
- **Rename/move logging.** Every operation in the TV and Film renamers is now
  recorded in the application log, so you can see exactly where each finished file
  ended up.
- **Source information in the log.** Opening a file now writes an ffprobe-style
  summary (container, codecs, stream layout and timing) to the log, to help with
  troubleshooting.

### Changed

- The renamers' **"Rename Ticked"** button is now **"Process Ticked"**, since the
  step may move files as well as rename them.
- **Open Recent** now keeps entries whose source has since been moved or deleted,
  showing them greyed-out and marked "(missing)" rather than dropping them.

### Fixed

- **Preview audio on Blu-ray and other disc rips.** Audio now plays reliably on
  MKV rips (DTS, DTS-HD MA, AC3) that previously fell silent when seeking. The
  seek strategy is chosen to suit the source, so broadcast recordings keep their
  tight, in-sync preview while disc rips seek by the video index. Exported cuts
  are made straight from the source and stay perfectly in sync regardless of the
  preview.
- Maximising or resizing the window during playback now updates the picture
  smoothly, instead of leaving it briefly at the old size.

## [1.1.0] - 2026-06-27

### Added

- **TMDB episode picker.** Double-click a matched row in the TV renamer to choose
  the exact season and episode from a dialog that fetches the show's seasons and
  episodes from TMDB. Ctrl-click to select two episodes for a two-parter, use
  "Change show…" if the auto-match was wrong, and Season 0 is presented as
  "Specials".
- **Pixel cropping.** A new per-profile option to remove letterbox or pillarbox
  black bars. Because the bars are baked into the picture, cropping re-encodes the
  video (the only non-lossless step in the tool); the normal lossless cutting path
  is untouched when cropping is off.
  - **Auto-detect** finds the bars per file at export time, or set **Fixed pixels**
    by hand.
  - A **preview window** shows a real frame from the open recording with the crop
    shaded in, a slider to skim for a frame to crop against, live edge adjustment,
    and an Auto-detect button.
  - The re-encode matches the source's own bitrate as a ceiling and uses constant
    quality (CRF), so a cropped file is never larger than the source and is usually
    smaller.
  - The **scan type is preserved** — an interlaced source stays interlaced (with
    its original field order), a progressive source stays progressive.
  - Cropping works in the watcher/batch pipeline as well as manual exports, with a
    proper progress bar and accurate timing for the re-encode stage.

### Changed

- The TV renamer now files Season 0 episodes into a "Specials" folder.
- Versioning tidied up: the old build-number field has been retired in favour of a
  `build_stamp()` derived from the version string.

## [1.0.0]

- Initial public release.

[1.9.0]: https://github.com/infidelus/snipwright/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/infidelus/snipwright/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/infidelus/snipwright/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/infidelus/snipwright/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/infidelus/snipwright/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/infidelus/snipwright/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/infidelus/snipwright/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/infidelus/snipwright/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/infidelus/snipwright/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/infidelus/snipwright/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/infidelus/snipwright/releases/tag/v1.0.0
