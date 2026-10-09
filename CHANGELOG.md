# Changelog

All notable changes to Snipwright are documented here. Releases before
2.0.0 were published under the project's former name, VRD Next.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [2.11.0] - 2026-10-09

### Changed

- **PyAV 19 is supported.** Snipwright now works with PyAV 18.1 and 19, so a
  new installation takes PyAV 19.0.1 (which brings FFmpeg 9.0.2 for decoding)
  and an existing one can stay on 18.1. PyAV is held below 20 until that has
  been tried, and 19.0.0, which never was, is left out. Exports are
  byte-for-byte the same on both versions, re-encoded cut points included,
  and advert detection gives identical results across the whole test corpus.

- **PySide6 6.11.2, tqdm 4.70.1, bitarray 3.11.0 and numpy 2.5.3.** Routine
  updates of supporting libraries, PySide6 being the toolkit the interface is
  built with; they change nothing you will see. Exports are
  byte-for-byte the same, and advert detection gives identical results.

- **Holding a skip shortcut keeps skipping.** Shift, Ctrl and Ctrl+Shift with
  the left or right arrow now repeat while held, about ten skips a second,
  instead of moving once and then only now and again.

### Fixed

- **A join saved with Match Source as .mkv is a real Matroska file, with
  chapters.** Joining scenes from .mkv recordings - Blu-ray rips, say - with
  the Match Source profile wrote an MPEG-TS file under an .mkv name. It
  played, but it was mislabelled and had no chapter at each join, because
  the chapters are written by the Matroska step that never ran. Match Source
  now follows the file's extension, as it already did for a single export.

- **Joining scenes from a Blu-ray rip keeps the subtitles.** When the
  scenes shared one format, so the join could copy them rather than
  re-encode, a disc's subtitles were lost and the summary said only
  "Subtitles: None". They are now converted to broadcast (DVB) subtitles
  from the recording itself, as a re-encoded join already did - same words,
  colours, positions and timings - and the summary says so. Any kind a joined
  video cannot carry at all is named in the summary instead of disappearing,
  and a join saved as .mp4, which has no room for broadcast or disc
  subtitles, now says it left them out.

- **A re-encoded join keeps its subtitles when an audio-description track
  starts late.** Joining recordings whose audio description is sent only
  while the narrator speaks - such as an SD and an HD scene with a quiet
  opening - could leave the joined video without any subtitles, with a note
  saying they could not be carried through. The audio description track
  starts too late in the joined file for a quick look to identify it, and
  writing the subtitles failed on it. The file is now read the way every
  recording is, and the subtitles and the audio description both arrive.

- **Export and join progress, and the notes under a finished export, are
  in German in the German interface.** The progress window's steps - Fast
  Frame Copy, Encoding Frames, Finalising MKV and the rest - the Joiner's
  progress lines and time estimate, and the notes under the export summary
  (a track not carried over, an output a little longer than the edit,
  subtitles converted in a join) along with any error at the top were always
  in English, as were the "Indexing…" bar when a recording opens and the
  renamers' "e.g." example. They now follow the interface language. The log
  keeps them in English, so a problem report reads the same whoever sends it.

- **A join no longer logs a misleading subtitle warning.** Joining a scene
  from a Blu-ray rip logged "MATCH cannot carry this recording's
  hdmv_pgs_subtitle" for that scene, which read as the subtitles having been
  lost even when the join went on to convert them. The message now says what
  happens to them.

- **An MP4 export now says when it leaves the subtitles out.** MP4 has no
  place for a broadcast's DVB subtitles or teletext, so they are not in an
  .mp4 file - but the export summary said only "Subtitles: None", with
  nothing to show a track had been dropped. It now notes how many subtitle
  tracks were not carried over and suggests exporting to .mkv, which keeps
  them, and the log says the same.

- **Opening a file with chapters says how many marks it added.** Since
  2.4.0, a recording's chapters become marks on the timeline when it is
  opened, and the status bar was meant to report how many. The message was
  wiped as the first frame appeared, so it was never seen. It now stays for
  its few seconds.

- **Tvheadend recordings named .bin can be saved.** Tvheadend sometimes
  names a recording .bin rather than .ts. Snipwright opened them but every
  save failed, because the output kept the .bin name and FFmpeg cannot write
  a file with that extension. Such recordings are now saved as .ts, and .bin
  files can be dropped onto the window and appear in the Open dialog.

- **Audio description stays in step on channels that send it only during
  narration.** Some channels, such as 5USA, transmit their audio description
  only while the narrator speaks, with long gaps in between. A .ts export
  closed those gaps up, so the narration drifted ahead of the picture and
  then fell silent for most of the programme; an MP4 export did the same.
  The narration now stays where it belongs in .ts, MKV and MP4 alike.
- **Audio description is no longer dropped when the same recording is
  exported a second time.** On such a recording the second export - to any
  format - left the audio description track out ("1 audio track could not
  be written"), while the first had kept it.
- **No "Failed to disconnect" warning in the terminal at start-up.**

## [2.10.0] - 2026-10-04

### Added

- **Uninstallers for Linux and Windows**, beside the installers in
  `src/packaging`. They remove what the installer set up - menu entries or
  shortcuts, Snipwright's file types for `.vprj` and `.swproj`, the Watcher's
  start-on-login entry and the Python environment - plus Snipwright's cache and
  temporary files, and on Windows the Defender exclusion if one was added. They
  ask before deleting Quick Stream Fix working copies and your settings, so
  learned channel logos can be kept for a reinstall, and they never touch
  recordings, exported videos, projects or logs. If another copy of Snipwright
  is installed, its menu entries and file types are left alone.
- **Learning can be switched off per channel.** The Remembered logos window
  has a new Learn column. Untick it for a channel that already detects well:
  everything it has learned is still used to find its breaks, but saving a
  corrected project on it no longer starts a learning pass, which could take
  several minutes on a long recording.
- **Channels without a logo now appear in Remembered logos.** A channel
  recognised only by the ident at the edges of its breaks, such as Film4,
  gets its own row with a picture of that ident, and its name and service ID
  can be filled in and joined like any other row - so idents learned from
  one recorder's recordings are used for the other's too. A new Idents column
  shows how many idents each channel has learned.
- **The About box lists what Snipwright is running on.** Your system, Python,
  each library with its version - including the FFmpeg built into PyAV, which
  does the decoding - and the FFmpeg and MKVToolNix programs. A library that
  differs from the version Snipwright was tested with is marked, so if other
  software has updated one you can see it at a glance. "Copy details" puts
  the whole list on the clipboard, ready to paste into a bug report.
- **Advert detection finds where a programme starts and ends more closely.**
  Many channels show the same frame - a sponsor card, a continuity board -
  just before or after every programme. Chalkline now learns these from the
  projects you correct, alongside each channel's logo and idents, and uses
  them to pull the start and end of the programme in to the right place.
  Across the test recordings, programme edges within two seconds of the
  hand-placed cut rose from 25 of 67 to 30, none got worse, and scanning is
  no slower. It only refines edges Chalkline has already found, and it only
  learns from recordings whose padding you've trimmed, so recordings without
  padding are left as they were. Unticking Learn for a channel stops this
  learning too.
- **Re-encoded joins keep their subtitles.** Joining scenes that don't match -
  an SD and an HD recording, say - re-encodes them, and until now their
  broadcast subtitles were dropped. They are now carried into the joined
  video, each on the right picture. Where a scene's subtitles were drawn for
  a different picture size from the joined video, they are redrawn to fit,
  words and colours unchanged, so they show in every player - including a
  web browser through Jellyfin, which otherwise lost them. A Blu-ray's
  subtitles are converted to the same broadcast kind, so a join of
  recordings and disc rips keeps them all in one subtitle track. Anything
  that still can't be carried, such as teletext, is named in the summary at
  the end.

### Fixed

- **Audio description is no longer lost from some HD recordings.** On
  channels such as BBC Three HD, the audio description track can give no
  clue to its format during the first minutes of a recording, and the export
  left it out ("1 audio track could not be carried over"). Where such a
  track did survive, the last step - restoring the channel name and track
  labels on a .ts - could fail. Recordings are now read deeply enough to see
  these tracks properly from the start, so they are kept whole, narration
  and all. In testing, recordings that were already fine exported exactly
  as before, byte for byte.
- **The Linux installer is executable again.** In 2.9.1, `install-linux.sh`
  lost its executable permission, so running it directly gave "Permission
  denied". Anyone following the documented `chmod +x` step was unaffected,
  but the permission should never have been lost.

### Changed

- **Learning names the channel, not its service number.** A recording from a
  recorder that keeps only the service number - Jellyfin, for one - made the
  status bar and the log say, for example, "sid:17664" where they meant
  Channel 4 HD. Once that number is paired with the channel's name in
  Remembered logos, every learning message now uses the name.

## [2.9.1] - 2026-10-01

### Fixed

- **A fresh install could not export anything.** Snipwright's installers
  asked for the newest version of each Python library it uses, and on 29
  September 2026 a new major version of PyAV - the library that reads and
  writes the video - was published. It no longer accepts an option
  Snipwright uses when opening every recording, so anyone who installed
  Snipwright from that day on got a copy that failed on every export. Every
  library is now locked to the exact version Snipwright has been tested
  with, so a new release of something it depends on can no longer break it
  overnight; newer versions are adopted once they have been tried. If you
  installed or reinstalled Snipwright since 29 September, run the installer
  again: it puts the right versions back, and your settings are untouched.

### Changed

- **Snipwright now needs Python 3.12, 3.13 or 3.14.** These are the versions
  the locked libraries are built for, and in practice what a working
  install has needed for some time; the documentation said 3.10. Linux
  Mint 22 and later include 3.12, and the Windows installer fetches 3.14 if
  it doesn't find a suitable Python. Both installers now say plainly when
  the Python available isn't one of these, instead of stopping on an
  unhelpful error part-way through.

## [2.9.0] - 2026-09-30

### Added

- **Chalkline learns a channel's break ident, and uses it.** Some channels
  show the same short full-screen card at the very start and end of every
  advert break - Film4's red ident is the first seen. When you save a
  corrected project, Chalkline now learns that card as well as the logo,
  if it appears at most break edges and never in the programme. From then
  on it puts each break's start and end on the exact frame - Film4's edges
  had been 5 to 8 seconds out, cutting a few seconds of film at every break
  - and on a channel where nothing else marks the breaks, such as a
  full-screen Film4 film, it finds the breaks themselves. ITV1, ITV4, Rewind
  TV and Sky Mix have cards too and gain more exact edges. The lead-in and
  the end of a recording aren't marked by the card, so a full-screen film's
  may still need trimming by hand.

- **Snipwright has its own project format, `.swproj`.** A VideoReDo project
  records each cut as two times and nothing else, so Snipwright has always
  had to guess which recording a project belongs to and map the times back
  to frames, hoping they land on the same ones. A Snipwright project records
  the recording itself - so it can tell when it is opened against a
  different copy, and find a recording moved together with its project -
  and places every cut on the exact frame you chose, even on a broadcast
  whose clock jumps. It also notes whether the cuts came from you or from the
  advert detector. It is a readable text file.

  **Nothing changes for you unless you choose it.** A new installation saves
  Snipwright projects; an existing one carries on saving `.vprj` until you
  switch in Settings > Files & folders > Project format. Both open in
  Snipwright either way, and Save Project As offers both, along with an EDL.
  VideoReDo cannot open a `.swproj`, so if you move projects between the two,
  stay on `.vprj`.

  The Watcher writes whichever format you choose, and the batch queue and
  Batch Manager take either. Projects the queue makes for itself are always
  Snipwright's own, so a queued export cuts on exactly the frames the editor
  showed.

- **The Joiner can send its list to the batch queue.** Joining recordings
  that don't match has to re-encode the whole thing, which can take a long
  time - exactly when you would rather it ran in the background. Joiner >
  Queue Joiner List to Batch, or Queue to batch in the Joiner list window,
  queues the join instead of running it now. It asks the same questions
  Create Video does, keeps your answer with the job, and uses the Batch
  Manager's profile and output folder like any other job. The result is the
  same file Create Video would have made.

  A join you have already started can be handed over as well: its progress
  window now has Send to Batch, as an export's does, and the join carries on
  in the Batch Manager from where it was rather than starting again.

- **The export summary says which subtitles the file kept.** The window at
  the end of an export or a join now has a Subtitles line, read from the
  finished file itself - "DVB subtitles (eng)", say, or "None" - and the
  summary written to the log says the same, batch exports included. Subtitles can
  go missing for good reasons (a format that can't hold them, a join that has
  to be re-encoded), and when they do the summary already says why; now it
  also says plainly what you have. The same window was partly untranslated -
  only its title was in German - and is now translated in full.

- **Faster first start on Windows, if you choose it.** Windows Defender
  checks every file Snipwright loads the first time it starts after a reboot,
  which roughly doubled that first start - about 9 seconds rather than 5.5 in
  testing. The Windows installer now offers, at the end, to exclude
  Snipwright's own Python folder from those checks. It explains the trade-off
  - Defender stops scanning that folder - and does nothing unless you say
  yes. Later starts are quick either way. Snipwright's log now also records
  how long each start took.

- **Programme information now lists the subtitles.** Tools > Show video
  programme information showed the video and every audio track but said
  nothing about subtitles, so there was no way to tell from inside Snipwright
  whether a recording had any. Each subtitle track now gets its own section
  with its type, language, PID and - for broadcast subtitles - the page
  number, as VideoReDo showed. It tells you the track is there; a
  broadcaster can still leave it empty for part of a recording.

### Fixed

- **Save Project As could ignore the format you chose.** The suggested name
  already ends in a project extension, and the format you picked was only
  used when the name had none - so choosing EDL saved a file called
  `name.vprj.edl`. The format you choose now decides, and the extension in
  the name follows it, changing as you switch format where your desktop's
  save dialog allows.

- **Ticking or unticking Favourites Only in Save Video lost your choice of
  profile.** The list jumped back to its first entry, Match Source, whatever
  you had picked. It now keeps the profile you chose. If ticking the box hides
  it, the first favourite with the same container is picked instead, so an
  MKV choice stays MKV; and a one-off edit to the profile is kept too.

- **A join that had to be re-encoded dropped subtitles without saying so.**
  Joining recordings that don't match - standard and high definition, say -
  re-encodes the picture and sound, and broadcast subtitles can't come
  through that process, so the joined video had none. The completion summary
  and the log now say so. A join of scenes that all match isn't re-encoded,
  and keeps its subtitles as before.

- **A channel could keep switching between logos that were as good as each
  other.** Where a channel holds several learned logos that all see the
  programme equally well, the one in use could change with every recording
  on differences of a fraction of a percent - each time reporting that it
  had "found a better logo". A logo now has to be clearly better on the
  recordings both have been measured against before it takes over.

- **Subtitles came on by themselves in every exported .mkv.** A broadcast
  recording carries no "default track" information, so the tool that builds
  the .mkv marked every track as a default - subtitles included - and in a
  .mkv that tells your player to show them. Every recording exported to .mkv
  therefore opened with subtitles on, and they had to be switched off each
  time. Subtitles are now kept but left off, for you to turn on when you
  want them.

  **Files you have already exported can be put right without re-exporting**,
  with a small separate tool in the `tools` folder: `fix-subtitle-defaults`
  (run the `.bat` on Windows, the `.sh` on Linux). Choose a folder and it
  works through every subfolder, shows you what it would change, and changes
  nothing until you press Apply. It only switches off subtitles in the same
  language as the audio - a foreign-language film's subtitles are left alone -
  and never touches a track marked forced. Only the one setting in each file
  changes, so it is quick even over a network. It is not part of Snipwright
  itself and can be ignored once it has done its job.

## [2.8.0] - 2026-09-20

### Changed

- **Snipwright can change its mind about a channel's logo.** It used to learn
  a channel's logo once and keep it for good: a logo learned from an awkward
  recording was stuck, and there was no way to tell a good one from a bad one.
  It now keeps up to four logos for a channel and, whenever you save a project
  you have corrected, scores the ones it already has against your own cuts -
  the logo should be out of sight through the adverts and on screen through
  the programme. Two logos are only ever compared on recordings they have
  both been scored against, so a logo is never punished for having been tried
  on a harder recording than its rival. Whichever wins there is the one used
  from then on, and a logo learned from the recording you just saved has to
  prove itself on a later one before it can take over. This only runs if
  "Learn channel logos from my edits" is ticked in Settings > Advert
  detection, and a channel whose logo is
  already settled is left alone when you save cuts exactly as proposed. The
  log records what each logo scored.

- **Trimming the end of a recording no longer leaves the continuity on it.**
  A recorded programme ends, an advert break follows, and then comes
  continuity or the start of the next programme - with the channel's logo
  back on screen. Snipwright cut the advert break and stopped there, leaving
  seven to ten minutes on the end of what you trimmed. Where the picture's
  shape or aspect changes as the programme ends and stays changed to the end
  of the recording, that trim now carries on to the end. The cut still starts
  where it always did, so nothing is taken off the programme, and channels
  whose picture does not change are unaffected.

- **"Show tooltips on the transport controls" turned off every tooltip in
  Snipwright.** It reads as though it covers the play and step buttons, and
  that is what it was for, but it silently suppressed every hint in the
  program - including the ones that carry information nothing else shows,
  such as what each remembered logo has scored, or the full path behind an
  abbreviated menu entry. It now does what it says and leaves the rest alone.

- **What a channel's logos have scored was hidden where nobody would look.**
  The tip listing each remembered logo, the projects it has been measured
  against and the breaks it would have invented only appeared over the Mask
  column, not over the logo picture or the channel name - so resting the
  pointer where you would expect showed nothing at all. It now appears
  anywhere on the channel's row, and the user guide says so.

- **Joining two remembered logos no longer throws one away.** Renaming a
  remembered logo onto a name that already has one used to keep whichever
  had the higher contrast and discard the other. Contrast is measured on the
  recording each logo came from, so the two figures were never comparable,
  and the discarded logo was sometimes the better one. The joined channel now
  keeps both and carries on with the one it was already using, until your
  corrected projects show the other to be better. The list also shows how many
  logos a channel holds, and hovering over it says what each has scored.

- **Advert detection ignores a learned logo that does not match the
  recording.** A channel's logo can change, or a recording can be framed
  differently from the one the logo was learned from, and a learned logo that
  no longer matches sees nothing at all. Snipwright used it anyway, which cost
  nothing obvious but quietly switched off the checks that stop it inventing
  breaks. It now checks first, and a logo that matches too little of the
  recording is left out of that recording - detection carries on exactly as
  it would for a channel it has not learned. The log says when this happens.

- **The user guide now says what to expect at the end of a recording, and how
  channel logos are chosen.** It said nothing about the trim at the end of a
  recording, which is reliable on channels whose picture changes shape as the
  programme finishes and stops at the advert break on those that do not - so
  it is worth a look before exporting. Its account of logo learning was also
  out of date: a channel keeps several logos now and picks between them on
  the projects you correct, rather than keeping the first one it learned for
  good.

- **The user guide understated how far cut marks can drift between Snipwright
  and VideoReDo.** It said "a frame or two"; a dozen or so in both directions
  is closer to what actually happens, so it now says "a handful of frames".
  The advice either side of it was already right - check a mark in whichever
  editor you are using before saving, because it will cut where it now sits.

- **Snipwright now runs as a single instance.** Opening a project from your
  file manager brings the Snipwright you already have to the front and loads it
  there, instead of starting a second copy. If the project you are working on
  has unsaved changes you get the usual save prompt first, with Cancel to leave
  things as they are. Two copies shared the batch queue, the settings and the
  logo store, and two batches running at once would work through the same queue
  with neither knowing about the other - so this closes a whole class of
  problem rather than being a tidiness measure.

### Fixed

- **Subtitles from a disc rip were lost on export, without a word.** A cut
  bound for .mkv or .mp4 is written to a transport stream first, and a
  transport stream can only carry broadcast subtitles - so the PGS or SubRip
  subtitles in a rip disappeared on the way. An .mkv export now takes those
  recordings through a Matroska working file instead and keeps them; a
  broadcast recording is unaffected and follows exactly the path it did
  before. Where the format genuinely cannot hold them - .ts and .mp4 - the
  export now says so in its summary rather than dropping them in silence.

- **Subtitles could be missing from an exported recording.** Where the export
  had to rebuild the audio - which happens on a profile that re-encodes audio
  to AAC, and on a few repair routes - the rebuilt file was assembled from
  the video and audio alone, and any subtitles the recording carried were
  dropped without a word. They are now carried through every route. (An .mp4
  export still cannot keep broadcast subtitles: the format has no place to
  put them.)

- **A recording whose timestamps jump exported as hours long.** Some
  broadcasts carry a clock that leaps forward partway through the programme,
  by hours, with nothing actually missing - a 45-minute Channel 4 HD
  recording can claim to run for over seven. Snipwright showed and cut these
  correctly, but an export spanning the leap came out reported as hours long:
  in MKV every subtitle after the leap was placed hours late, and in TS the
  audio was needlessly rebuilt. The leap is now closed as the cut is made, so
  video, audio and subtitles all run on without a gap, the file reports its
  real length, chapter marks land where they should, and the export log shows
  scene times as they play rather than hours out. It also says where the leap
  was. Recordings whose timestamps run normally export exactly as before.

- **The export summary showed a wall of text where a footnote belonged.** When
  an export had something to explain - scenes re-encoded to join them, say -
  the box printed the whole explanation, and printed it as Python's own
  rendering of the underlying data, brackets and quotes included. It now shows
  the short version and says to check the log, which carries the full
  explanation as it always did.

- **Joining scenes that did not match dropped all but the first audio track.**
  When scenes share a format they are joined without re-encoding, and that
  path was fixed earlier; scenes that do not match have to be re-encoded, and
  that path still carried a single audio track however many went in. An audio
  description or second language was lost. It now carries every track the
  scenes have in common, each kept at its own channel layout and bitrate, so a
  5.1 main track and a stereo audio description stay as they were rather than
  both being forced to the same shape. If the scenes have different numbers of
  audio tracks, the ones they share are kept and the export notes say so.

- **The TV Renamer missed the second half of a double episode.** A recording
  named `S01E01 S01E02` - the two episodes separated by a space, each with its
  own season number - was read as episode one alone, so the file was renamed
  and filed as a single episode. `S01E01E02` and `1x01-02` were already
  understood; the spaced form, and `S01E01 & S01E02` and `S01E01, S01E02`,
  now are too. A title that merely looks like a second episode is still
  ignored, so `S03E21 - E2 - The Title` remains one episode.

- **The TV Renamer named a double episode after its first half.** Selecting
  both parts gave the right numbering but kept the part marker from the first
  title, so a file covering two episodes came out as `Stargate SG-1 -
  S01E01-02 - Children of the Gods (1)` - the numbering saying two episodes
  and the title saying part one. The marker is now dropped when a file holds
  more than one episode, so that becomes `Stargate SG-1 - S01E01-02 -
  Children of the Gods`. Two episodes that are not
  parts of the same story keep both titles, joined, rather than one being
  quietly lost. A title that simply ends in something marker-shaped - Apollo
  13, Catch-22, Episode 50 - is left alone.

- **Snipwright could refuse to learn a channel's logo from a perfectly good
  recording.** It expected your recorder to be padding the start or end of
  each recording - a few minutes either side of the scheduled time - and
  treated a recording without that padding as one that had already been cut,
  refusing to learn from it and saying so in the log. Most recorders do not
  pad by default, so anyone who had not turned it on could never teach
  Snipwright a logo at all, and the reason given pointed at the wrong thing.
  The padding was never used for the learning itself - a padded and an
  unpadded edit of the same recording teach it from exactly the same
  boundaries - so the requirement has gone. The checks that matter are
  unchanged: every cut has to be a plausible length for an advert break, and
  they cannot remove more than half the recording.

- **Adjusting both ends of a cut at once only moved one of them.** Moving the
  start of an existing cut earlier and its end earlier, then pressing Cut
  Selection once, moved the start and left the end where it was. Pressing Cut
  Selection again without touching anything then moved the end, which made it
  look as though the first press had been ignored. Snipwright was deciding
  what to do from where the IN marker landed rather than from what the marked
  span covered, and the path it chose could only ever remove more material,
  never give any back. A marked span that overlaps an existing cut now simply
  becomes that cut, both ends together - the same rule Scene Mode has always
  used. Marking across two cuts joins them into the one span you marked.

- **Advert detection invents fewer breaks.** When Snipwright has learned a
  channel's logo, it now trusts that over its general search for something
  parked in a corner. Where the two disagree - the corner search says the logo
  has gone, the learned one says it is still there - the learned one wins, and
  no break is proposed. Measured across thirty recordings this removed two
  false breaks and cost nothing: no real advert break was lost and no other
  recording changed. It also fixed a break that started 46 seconds early on
  one recording, cutting into the programme.

  The learned logo is now held to the same standard itself. A logo that is
  really there, but hard to make out against a busy background, can be lost
  for a moment every few seconds - and a minute of that used to be read as
  the logo being gone, and proposed as a break. Where the learned logo's own
  reading says it was there for most of that time, no break is proposed. Cuts
  close to the start or end of a recording are left alone by both checks, so
  the padding either side of the programme - where the channel's logo is
  often still on screen - is still trimmed. Measured across the same thirty
  recordings, this removed three more false breaks, again without losing a
  real one or changing anything else.

- **Cutting without marking OUT could remove part of the programme.** This is
  the Cut Mode version of the scene fault fixed just before it, and it was the
  more damaging of the two. The markers stay where they are after a cut so you
  can nudge a boundary and cut again, which leaves the OUT sitting on the cut
  you just made. Mark IN for the next advert break, forget the OUT, press Cut,
  and the range ran backwards - Snipwright turned it into the gap between the
  two marks and removed everything in between, which is programme rather than
  adverts. A range that runs backwards from a leftover marker is now refused,
  with a note in the status bar. Marking OUT before IN deliberately still
  works, and so does nudging a boundary.

- **Adding a scene without marking OUT could destroy the scenes either side of
  it.** The IN and OUT markers stay where they are after you add a scene, so
  you can nudge a boundary that is a frame out and add again. But that leaves
  the OUT sitting on the scene you just finished: mark IN for the next scene,
  forget the OUT, press Add, and the range ran backwards from the old OUT to
  the new IN. Snipwright quietly turned that into a scene covering the gap
  between them, which overlapped the neighbouring scenes and replaced both -
  two scenes lost from one mislaid click. A range that runs backwards from a
  leftover marker is now refused, with a note in the status bar saying the OUT
  is still on the previous scene. Marking OUT before IN deliberately still
  works, and so does nudging a boundary.

- **Running two copies of Snipwright could lose queued batch jobs, and could
  delete a project one of them still needed.** The batch queue is read once
  when Snipwright starts and written back whole whenever it changes, so two
  copies each held their own idea of it and whichever saved last quietly erased
  the other's additions. Nothing was ever corrupted - the jobs simply went,
  with no error. Worse, removing a job deleted the working copy of its project,
  and that decision was made from one copy's view of the queue: a job removed
  in one window could have its project deleted while the other window still
  had that job and later tried to run it, failing with "The project file has no
  source recording recorded".

  The queue is now re-read and merged at the moment it is saved, so jobs added
  in one window survive a save in the other and a job you delete stays deleted.
  Working copies are kept if ANY window's queue still refers to them. And the
  queue is refreshed from disk when the Batch Manager is opened and again when
  a batch is started, so a window is not working from a list it read hours ago.
  Settings have the same shape and are not fixed here; a later release will
  make opening a project use the window you already have rather than starting
  another.

## [2.7.0] - 2026-09-10

### Changed

- **The log now says why a channel's logo could not be learned.** It used to
  record only that nothing was learned, which named the outcome and none of the
  evidence - so a report of "no logo saved" could not be answered without
  asking the user to run the whole thing again. It now writes what it measured
  for each kind of logo it looked for: the strongest contrast it found, the
  contrast it needed, and which test refused the result. It also records how
  long the pass took against the length of the recording, which makes an
  unexpectedly quick pass visible rather than something to be guessed at.

- **You can now see when Chalkline is learning a channel's logo.** Saving a
  project starts a background pass that reads the whole recording and takes a
  few minutes, but the message saying so disappeared after fifteen seconds -
  so for nearly all of that time nothing on screen said work was in progress.
  It was easy to conclude it had finished, and closing Snipwright cancels the
  pass. The status bar now keeps a message until the work is genuinely done,
  and says how many recordings are waiting behind it. Closing still cancels
  without asking, but now records in the log what was discarded.

- **Cut boundaries are easier to see in the thumbnail strip.** A frame inside a
  kept scene was marked by a one-pixel border, which is a losing proposition
  against arbitrary picture content - it was reported as hard to see twice,
  once against a dark scene and once on a bright one where the picture and the
  border were a similar colour. Each such frame now carries a band along its
  top edge, so the boundary is where the band stops between two adjacent
  thumbnails. The band is drawn over the top of the picture rather than above
  it, so it costs no height.

  With the band doing that job, the yellow border around those frames has gone
  - it was saying the same thing twice, and it muddied the blue marker on the
  frame you are actually on by squeezing it between two yellows. That marker
  has moved back out to the edge of the thumbnail where it used to sit. Scene
  markers keep their own border, which is a different thing and still the only
  thing saying it.

- **The thumbnail strip is now dark in light mode too.** It was the one editor
  bar without a background of its own, so in light mode the gaps around the
  thumbnails came out the same near-white as the rest of the window. The
  thumbnails themselves were identical in both themes, but a yellow cut marker
  has far less to separate it against a bright surround than a dark one - so
  the cut marks were noticeably harder to see in light mode for no reason
  anyone chose. The timeline and scene bars were already dark in both.

### Fixed

- **The Joiner silently dropped every audio track but the first, and the
  subtitles.** A join is supposed to be lossless, but the finished video kept
  only one audio track however many the scenes had - so an audio description
  track, or a second language, was thrown away without a word, and the
  subtitles with it. Each scene was rendered correctly with all of its audio;
  the loss happened when the scenes were joined together. Found on a recording
  whose audio description track carried real audio and simply vanished.
  Snipwright now also checks the finished join against the scenes it was built
  from and says so in the log if anything went missing, which is how this
  should have been caught long ago. Note that joining scenes that do NOT share
  a format still produces a single audio track, because those have to be
  re-encoded through a path that can only carry one; that is a separate
  limitation and is not fixed here.

- **A channel's logo could not be learned from a visually busy programme.**
  Snipwright works out where a logo sits by finding pixels that are edgier
  during the programme than during the adverts. That test assumed a logo was
  the only thing that could raise a pixel, so a programme filled with detail -
  stone walls, rubble, foliage - measured as edgier than its own smooth advert
  graphics across the whole picture, and the resulting shape covered almost
  the entire frame instead of a corner. Snipwright rejected it as too large
  and learned nothing, even though the logo was plainly visible. Each pixel is
  now measured against the rest of the frame rather than against zero, so a
  whole-picture difference cancels out and only what genuinely stands out is
  kept. On the Channel 4 recording this was found with, the logo is now
  learned where before nothing was.

- **Automatic advert detection did not work on Windows at all.** Snipwright
  asks ffmpeg to write scene changes to a temporary file, and the path to that
  file is given inside an ffmpeg filter description - where a colon separates
  options and a backslash escapes the next character. Every Windows temporary
  path begins `C:\`, so ffmpeg read the instruction as nonsense and refused to
  start. No frames were ever analysed, and the result was reported as "no logo
  clear enough to remember", which pointed at the recording rather than at the
  fault. Snipwright now hands ffmpeg a plain filename with no drive letter or
  folder separators in it, so there is nothing left to misread. Linux and
  macOS were never affected; on Windows this is the difference between advert
  detection working and not working at all.

- **Advert detection could report the wrong reason for finding nothing.** When
  the analysis could not run - the case above being the obvious example - the
  log still said no logo was clear enough, which is a statement about the
  picture and sent two separate investigations after the wrong thing. It now
  reports what actually stopped it.

- **Advert artwork in a corner could split one break into several.** On
  channels that change picture shape for the adverts, an advert's own logo
  sitting in the same corner as the channel's could be mistaken for it, and
  each such moment cut one break into two. On the Talking Pictures recordings
  this was measured on, a single break contained seven of them - and one
  recording went from finding half its breaks with four false ones to finding
  both with a single false one. A remembered logo seen while the picture has
  changed shape is no longer allowed to hold a break open.

- **Saving a second project while a logo was being learned threw the second
  one away.** Learning reads the whole recording, so only one runs at a time -
  but instead of waiting its turn, anything saved while one was in progress was
  silently discarded. If you worked through several recordings in a sitting,
  only the first taught Chalkline anything, and nothing told you the rest had
  been dropped. Saves are now queued and worked through in order, up to eight
  deep. Re-saving the same project still will not queue it twice.

- **Advert detection could mistake an advert's own artwork for the channel
  logo.** Snipwright works out where a channel puts its logo by looking for
  something that stays in one corner, and it assumes that something is present
  during the programme and absent during the breaks. Things like advert logos
  and QR codes are the exact opposite - an advert parks its own artwork in a
  corner and leaves it there, so it is present through the advert and absent
  through the programme, and gets read as a channel logo that had been missing
  for the entire show. Corners are now judged on how much of the recording
  they are actually present for, and one that only appears for a minority of
  it can no longer outrank a real logo. On the 5STAR recording this was
  measured with, Snipwright now trims the ten-minute shopping segment that
  follows the programme to within half a second, where before it removed the
  programme instead. No other recording in the 30-recording test set changed.

- **Advert detection could remove almost the whole programme.** On a recording
  where the detector misread which corner held the channel logo, it proposed a
  single "break" running from the start of the recording to two thirds of the
  way through, and reported it. The length ceiling that exists to catch
  exactly this did not apply, because a break touching the very start or end
  of a recording is allowed to be longer - the PVR's own padding often is. That
  allowance is still there, but a break at the start or end can no longer take
  more than half the recording. Measured on a 43-minute 5STAR recording that
  lost all 25 minutes of programme and kept only the padding; the same run
  showed no change to any other recording, including the nine legitimate
  10-13 minute padding trims the allowance was added for.

- **The Joiner did not record its finished video in the log.** It wrote a full
  completion summary for every scene it rendered on the way to the join, and
  then nothing at all for the file it actually produced - so the one set of
  figures worth keeping was the one missing. The finished join now writes the
  same summary a normal export does. The per-scene entries have been reduced to
  a single line each: they are intermediate pieces, not finished exports, and
  giving each one the full block made a five-scene join read as six separate
  videos in the log.

- **The progress bar stalled at half way when writing an MKV.** The audio check
  that runs at the end of an MKV export reserved the upper half of the bar for
  a second comparison pass that only happens when the first pass finds a
  problem - which is the minority of exports. On a clean file the bar therefore
  filled to 50% and then jumped straight to the end. The check now uses the
  whole bar, and the second pass, when it is needed, is shown as a pass of its
  own with its own label. Affects the Joiner and ordinary MKV exports alike.

- **Checking for updates could crash the editor a few seconds after launch.**
  The check runs on a worker thread that deletes itself when it finishes, and
  the next check could arrive still holding a reference to it - asking a
  destroyed object whether it was still running, which raised an internal
  error rather than answering. Most likely to be seen by anyone who used
  *Check for updates* from the menu within the first few seconds of starting,
  because that made the scheduled check the second one.

- **The Watcher screenshot in the user guide was out of date.** It still showed
  the settings window without the *Keep missing recordings for (hours)*
  option added in 2.6.0.

## [2.6.0] - 2026-09-05

### Changed

- **The joiner's progress bar was misleading throughout.** It passed the
  exporter's progress straight through, and the exporter counts each of its
  stages from zero, so an eight-scene join ran to 11%, back to 0, and up to 11%
  again, eight times over. Worse, converting the joined file to MP4 - a full
  re-encode, and the longest part of the run - was squeezed into the last few
  percent, so the bar sat near the top for minutes with nothing appearing to
  happen.

  A join is really several jobs: cutting each scene, joining them, then writing
  the result in the requested format. Each of those now gets the whole bar in
  turn, the way a normal export does - the bar fills, the label changes, and it
  fills again. Within a stage it only ever moves forwards, and the status line
  shows a time estimate once enough of that stage is done to give an honest
  one.

- **Cancel did nothing while a join was converting to MP4.** The dialog
  vanished and immediately came back, the conversion carried on to the end, and
  a second click landed on the video underneath and started it playing. Cancel
  now stops the conversion, and the dialog stays up and says it is cancelling
  rather than blinking out of the way.

- **Save Video remembers whether you want only your favourites.** The tick box
  reset to on every time it opened. It now keeps whatever you chose, in the
  joiner and in a normal export alike.

  It also appeared to remember a choice nobody had made: preselecting a profile
  that is not a favourite has to drop the filter so you can see it, and that
  was indistinguishable from unticking the box yourself. Only your own change
  is remembered now.

- **The joiner's progress window was too narrow, and grew part-way through.**
  It sized itself to whatever text it was showing, so it opened small and
  jumped wider a few seconds in, when the time estimate appeared. It now opens
  at the same width as the export window and stays there.

- **Save Video preselected the wrong profile.** When it was asked to open on
  a particular container it picked the *last* profile using that container
  rather than the first, so anyone with several MKV profiles was handed
  whichever happened to be at the bottom of the list. From the joiner this was
  every time, and it stuck: the container was saved and matched again next
  time, landing on the same wrong profile.

  The joiner no longer carries anything over between sessions. It opens on
  Match Source and behaves exactly as Save Video does from the editor.

- **The joiner logged an "Export complete" for every scene.** It renders each
  scene before joining them, and each of those wrote a full completion summary,
  so a five-scene join looked like six finished exports. The intermediate
  renders now say which scene they were.

- **The joiner now shows the same completion summary as an export.** It
  finished with a one-line "Joined video created" box while a plain export got
  the full figures - the wrong way round, since a join is the operation most
  likely to have quietly re-encoded and reshaped several recordings into one.
  It now reports length, size, scenes, frame counts, tracks and bitrate, all
  measured from the finished file, and says plainly when the scenes had to be
  re-encoded to be joined.

- **Re-encoded audio now keeps the recording's own bitrate and channels.**
  Wherever Snipwright has to re-encode audio it used to impose a flat 192 kbps,
  whatever the recording was: fine for a stereo broadcast, wasteful or lossy
  for anything else. It now follows what the source actually has, and says
  nothing to the encoder at all when that cannot be read, rather than
  substituting a figure. An output profile that specifies a bitrate still wins.

  The joiner was worse than that. When it has to re-encode rather than copy -
  joining recordings that do not match, or anything with a fade or a title card
  - it flattened every scene to stereo before joining, so joining two halves of
  a 5.1 recording gave a stereo result. It now joins at the widest layout
  present, so surround survives and a stereo title card no longer drags the
  programme down to match it.

- **A surround recording is no longer downmixed to stereo to fix a few
  frames.** When a recording's audio changes channel configuration too widely
  to patch, the whole track has to be re-encoded to a single configuration -
  and that was hardcoded to stereo. A Channel 4 HD film is 5.1 for its entire
  length apart from the continuity announcements at the advert breaks, so the
  surround mix was thrown away for the sake of a few seconds of bumper. The
  re-encode now keeps whichever configuration the recording mostly uses, at a
  bitrate measured from the recording rather than a fixed figure. A genuinely
  stereo recording still comes out stereo; nothing is ever upmixed.

- **The MKV audio check could pass a file with faults in it.** It sampled six
  thirty-second windows rather than checking the whole recording, and the
  problem it exists to catch is a scattering of bad frames - 83 out of 415,696
  on the recording it was written for, sitting at scene starts. Three minutes
  of a three-hour film will nearly always miss them, so a repackaged MKV could
  carry brief glitches and still be reported as verified. It now checks the
  whole recording. On a three-hour file that costs about twenty seconds, on an
  export that already takes minutes.

  It also now counts the audio frames in the finished file against the cut it
  was built from, which the re-encode fallback already did. A track that has
  lost most of its frames decodes perfectly - that is precisely why a decode
  check alone could not catch it.

- **Audio description tracks went unverified.** Every audio check looked only
  at the first track, so a recording's second track - typically the audio
  description - could lose its content without anything noticing. That is the
  wrong way round: an AD track is silent for long stretches by design, which
  makes it the likeliest to fail quietly. Every track is now checked, both for
  decoding and for frame count. A track the export deliberately leaves out,
  because it carried nothing in the kept scenes, is still not treated as lost
  audio.

- **MP4 exports were not checked at all.** Writing an MP4 repackages the audio
  as surely as writing an MKV does - the configuration moves out of the frame
  headers and into the container - but only MKV was verified. MP4 now has its
  audio counted against the cut it was built from, and says so in the export
  summary if it comes up short.

- **Verifying an MKV's audio now shows progress.** The check samples six
  windows across the file and, when it needs to compare against the cut it was
  built from, does it twice. That ran under the mux's busy indicator, so a
  dozen decodes on a long recording looked like the mux had stalled. It now
  reports its own progress and says *Verifying output* while it does.

- **The audio repair now shows real progress.** Repairing a recording whose
  audio changes channel configuration used to sit on a busy indicator with no
  indication of how far along it was or how much longer it would take. It now
  reports a percentage and an estimated time, counted across every track that
  needs work. It is also named *Repairing audio* rather than *Recoding*, which
  it never was.

### Fixed

- **An export that copied both streams into MP4 said it was recoding.** The
  label was chosen from the video codec alone, before anything had looked at
  the audio, so a recording that was copied through untouched was announced the
  same way as one being re-encoded and downmixed to stereo. There was no way to
  tell the two apart from the dialog. It now says what is actually happening,
  including *Repackaging to MP4* when nothing is being re-encoded at all.

- **A failed audio adjustment crashed the export instead of reporting itself.**
  Asking for an audio delay, a surround downmix or loudness processing that
  ffmpeg then could not apply raised an internal error, rather than finishing
  the export and saying plainly that the cut was fine but the adjustment had
  not been applied.

- **Numbers were clipped in the watcher's settings.** The window opened at a
  fixed size smaller than its own contents needed, so everything that could be
  squeezed was: the spin boxes under *Scanning* lost several pixels of height
  and their values were cut off along the bottom. It now opens at the size the
  contents ask for, whatever the language, and cannot be dragged smaller than
  that.

  The list of watched folders was reserving room for far more entries than
  anyone has, which was most of the reason the window was so tall to begin
  with. It now shows four folders and scrolls beyond that, and the window is
  around a hundred pixels shorter as a result. (Both reported in testing.)

- **The watcher detected everything again when a network share came back.**
  It keeps a list of the recordings it has already looked at, and dropped any
  entry whose file it could not see. A recording that has gone and a recording
  on a share that is rebooting look exactly alike to that check, so a server
  going down for maintenance - or a share being renamed - emptied the whole
  list at once, and every recording on it was detected again from scratch when
  the share returned. A week's recordings is a long evening's work for nothing.

  A folder the watcher cannot read is now left strictly alone: nothing under it
  is forgotten, however long it stays away, and the log names the folder it
  could not reach. Anything else that disappears is held for a period set in
  the watcher's settings - a day by default - and only forgotten once it has
  stayed missing that long. That second guard covers the harder case of a
  share that is mounted but not readable, where the folder itself looks
  perfectly healthy and every recording under it does not. (Reported in
  testing.)

- **Channel 4 HD recordings failed to export with "index out of range".** UK
  broadcast AAC is LATM-framed, and the reader that unpacks it indexed past
  the end of a damaged frame instead of reporting it as unreadable. The
  exporter is built to skip a frame it cannot parse; this particular failure
  went straight past that and stopped the export. Frames that cannot be read
  are now skipped as intended.

  The same reader was also mis-measuring the configuration header, walking off
  the end of frames that were perfectly good. (Reported in testing.)

- **5.1 audio was lost from MKV exports.** The output track was created
  without a channel layout, so it was built as stereo whatever the recording
  actually contained, and a 5.1 recording came out with a silent or unusable
  track. MP4 escaped it because of how that container is written, which is why
  this looked like an MKV-only fault. A recording that is 5.1 from beginning
  to end, with no change anywhere in it, was enough to trigger it.

- **Audio description tracks were dropped from cuts that began in a break.**
  An AD track carries nothing during continuity announcements and advert
  breaks, so a cut starting in one of those gaps has its first AD packet half
  a minute in. The checks that inspect a cut gave up long before reaching it,
  read the track as having no channels and no sample rate, and either failed
  the mux outright or quietly left the track out. Every one of those checks now
  looks far enough into the file to find the audio, which is what the check on
  the *source* recording already did.

- **Cuts spanning an advert break could produce a video with no sound.**
  Broadcast AAC changes its channel configuration at the breaks - Channel 4 HD
  runs continuity in stereo and the programme in 5.1, thirteen times in a
  three-hour recording. MPEG-TS carries that configuration with every frame, so
  a `.ts` export plays correctly, but MKV and MP4 hold one configuration for
  the whole track: copying such a cut gave a track with the right length and no
  audio.

  Snipwright now replaces only the minority frames - 83 out of 415,649 on the
  recording this was found with - and passes everything else through
  untouched. The 5.1 mix is kept, the repair takes seconds rather than the ten
  minutes a full re-encode of a feature film costs, and every timestamp in the
  original is carried across unchanged, so a recording with broadcast dropouts
  in it stays in sync. A cut that spans no configuration change is left
  completely alone.

- **A good MKV export was thrown away and re-encoded over two damaged
  frames.** The check that confirms the audio survived the repackage failed on
  any decoder complaint at all. Broadcast recordings carry a few frames no
  decoder can read - 53 out of 500,483 on the recording this was found with -
  and those are in the source, the intermediate and the finished file alike.
  Two of them were enough to condemn a perfectly good export: it was rebuilt,
  saw the same two frames, and re-encoded the whole track. An hour of work and
  a real loss of quality, to fix nothing.

  The check now compares against the intermediate the file was built from, so
  it answers the question that matters - did the repackage damage the audio? -
  rather than whether the recording is flawless. It also samples across the
  file instead of only the first minute, and counts the frames it found, since
  a nearly empty track decodes perfectly and used to pass.

  The last-resort re-encode was also reading the already-broken file rather
  than the intermediate, which is how it once produced two minutes of audio
  for a two-and-a-half-hour film.

- **An exported recording no longer said which channel it came from.** Writing
  a `.ts` let ffmpeg put its own defaults in, so every export claimed to be
  "Service01" whatever channel it was recorded off - and, less visibly, had its
  service ID renumbered to 1. Recorders differ in which of those they preserve:
  some write a channel name but renumber the service, others keep the original
  service number but write no name. Snipwright can use either, so an export
  that lost both could no longer be tied to the channel it came from at all.
  Both are now carried through.

- **A repaired recording no longer said which channel it came from.** Quick
  Stream Fix rebuilds the file, and the rebuild wrote a default service name
  in place of the broadcaster's, so every repaired recording claimed to be from
  the same channel. Advert detection keys what it learns on that name, so it
  was filing every channel's logo under one entry. The channel name, provider
  and service ID are now carried through the repair.

- **Removing a batch job left its project file behind.** *Queue to Batch*
  writes a staging project into the configuration folder for each job, and
  nothing ever removed one, so the folder grew for as long as the feature was
  used. A staged project is now deleted when its job leaves the queue, and any
  left behind by a crash are cleared at the next start. Projects you added to
  the Batch Manager yourself are never touched - only the copies Snipwright
  staged for itself.

- **Quick Stream Fix could fail when the recording was already open.** Where
  the working copy's name was already taken - because the same recording was
  loaded, or a background export was still reading it - the code that picks an
  alternative name raised an internal error instead. It also would have put
  that copy in the system temporary folder rather than the Quick Stream Fix
  folder set in Settings, where the automatic cleanup would never have found it
  to delete.

## [2.5.0] - 2026-08-29

### Added

- **Chalkline, a built-in advert detector.** Detecting commercials needed
  Comskip, a separate program to find, install and point Snipwright at, with
  an `.ini` to configure. Chalkline is part of Snipwright and needs none of
  that.

  It reads three things from the recording — the channel logo, the shape of
  the picture, and the aspect ratio the broadcaster declares — and where they
  disagree it prefers to report nothing rather than guess. That matters more
  than it sounds: a missed break costs you a manual pass through the
  timeline, while an invented one silently removes part of the programme, and
  that is not recoverable once the video has been saved.

  Which detector runs is chosen in *Settings → Advert detection*, and the
  choice applies to both *Detect Commercials* in the editor and the Watcher's
  unattended scans. Comskip's program path, its `.ini` and the per-channel
  `.ini` selection have moved onto that page from *External tools*, so
  everything to do with finding adverts is in one place.

  Chalkline learns each channel's logo from the edits you make. When you
  correct a detection and save the project, it remembers what that channel's
  logo looks like and finds the breaks more accurately on the next recording
  from the same channel. It only ever learns from a project you have edited
  yourself — never from its own unattended results, which would teach it from
  its own mistakes. This can be turned off on the same settings page.

- **EDL cut lists can be imported and exported.** Snipwright could read the
  EDL that Comskip produces during Detect Commercials, but there was no way to
  load one of your own. Choosing an `.edl` through *Import Project* gave
  "This project file could not be read: syntax error: line 1, column 0",
  because the file was being handed to the project reader, which expects XML.
  Dragging one onto the window did nothing at all, and opening one from a file
  manager pointed at a *File → Import → EDL* menu entry that has never
  existed.

  An EDL holds cut times and nothing else — no reference to the recording it
  describes — so it cannot open a video the way a project can. *Import
  Project* now accepts EDLs and applies them to the video already open; if
  none is, it offers to find the recording the cut list belongs to, the same
  prompt a project gets when its source has moved. Dragging an EDL onto the
  window and opening one from a file manager both do the same thing.

  Cut lists can be written out too, as a second format in *Save Project As*
  rather than a menu entry of its own. An EDL saved this way does not become
  the current project, so Ctrl+P still saves a full `.vprj` and cannot quietly
  replace your work with a copy that has no marks in it.

  Because an EDL names no video, nothing normally stops one being applied to
  the wrong recording — and the result looks plausible rather than broken.
  Two shapes are now stopped for: a cut list that runs past the end of the
  video, which nothing legitimate does, and one that covers less than half of
  it, which usually means the times came from a shorter recording. Neither is
  certain, so both ask rather than refuse. Where nothing looks wrong the
  status bar reports how far the cut list reaches and how long the video is,
  because no check can be sure and the numbers are worth seeing.

- **The Quick Stream Fix working folder can now be chosen.** Settings →
  Maintenance gains a folder box above the existing retention setting; leave
  it blank and the system temporary folder is used exactly as before. A
  working copy is a full remux of the recording, so it is roughly the size of
  the original, and on Windows the system temporary folder sits on the system
  drive — usually the smallest one on the machine. Deleting old copies, which
  Snipwright has done since 2.1.0, does not help at all when a *single* repair
  needs more room than that drive has: those are two different problems and
  only one of them had a fix. Raised by PaulWebster, who filled a Windows
  system drive part-way through a repair. If the folder set here goes missing
  or cannot be written to — a disconnected share, a renamed drive — the system
  folder is used instead rather than the repair failing.

- **Export without audio.** Output profiles gain a third audio setting, "No
  audio (silent)", alongside the lossless copy and the AAC re-encode. Useful
  for a recording with background noise you would rather lose entirely than
  keep. The audio tracks are never offered to the cutter rather than being
  stripped afterwards, so nothing is decoded, re-encoded or muxed on their
  account, and the export is correspondingly quicker. The bitrate, surround
  and loudness settings grey out when it is chosen, since there is no longer
  a track for them to act on.

### Changed

- **Projects Snipwright writes now carry Snipwright's name.** The version
  element inside a `.vprj` was still `<VideoReDoVersion>`, even though its
  contents have said "Snipwright" for some time. It is now
  `<SnipwrightVersion>`, and both are read, so every existing project still
  opens. The root element is deliberately unchanged: VideoReDo matches on
  that, and renaming it would stop VideoReDo opening Snipwright's projects
  altogether, whereas a child element it does not recognise is simply
  ignored. Nothing else about the file has changed.

- **File dialogues no longer name another editor.** *Save Project As* and the
  project pickers described the format as a “VideoReDo Project”. Snipwright
  writes the same `.vprj` format and always will, but the dialogue is naming
  Snipwright's own output, so it now reads “Snipwright Project”. The
  acknowledgement in the About box is unchanged.

### Fixed

- **The current frame no longer hides which scene it belongs to.** In the
  thumbnail strip, the frame under the playhead was drawn with a blue border
  *instead of* the yellow one marking a frame as part of a kept scene — so the
  one frame whose membership matters most, the one you have just stepped onto,
  was the only frame not showing it. Stepping towards a cut, the yellow was
  visible the whole way and then vanished at exactly the frame you were
  checking. The cursor is now drawn as a ring *inside* the frame's own border
  rather than replacing it, so both read at once. Reported by PaulWebster,
  who could not tell when he had reached the edge of a cut while reviewing
  cut points after a repair. Nothing in the layout changed.

- **An empty audio-description track is no longer reported as a fault.**
  A recording whose description track carries nothing during the programme —
  because the description belongs to whatever aired next — could finish its
  export with an error saying the track "could not be written", that "the
  audio is present in the recording", and asking for a bug report. None of
  that was true, and the check that would have said so had already run: the
  export knew the track held no audio in the scenes kept, and then ignored
  that in favour of reporting the muxing step that had failed *because* the
  track was empty. Where the dropped track carries nothing within the scenes
  you kept, it is now described as what it is — nothing lost. A track that
  genuinely holds audio and could not be written is still reported as a
  fault, which is the case that wording was written for.

- **Settings pages no longer spread their controls out to fill the window.**
  The pages were meant to pack their contents at the top, but the alignment
  they used has no effect on a page's own layout, so each page stretched its
  rows to fill whatever height the dialog had. It went unnoticed while the
  pages were of similar length — the dialog is as tall as its tallest page,
  so only a shorter page shows the gap.

- **Project files written by Comskip appear in the file dialog again.** The
  filter matched `.vprj` and `.VPRJ`, but Comskip writes `.VPrj`, which is
  neither — so the files the dialog is most often pointed at were the ones it
  could not show. All three spellings are now matched.

- **Every Settings page showed an English heading.** Each page's title is
  marked for translation and looked up when the navigation list is built, but
  the heading at the top of the page itself was given the raw untranslated
  string. So a German user saw *Advert detection* above a page of German
  controls, on all six pages. The string was in the translation file and
  counted as translated the whole time — it was simply never looked up, which
  is why no count of untranslated strings could have found it.

- **Settings field labels are translatable.** The labels and placeholder text
  on the file and folder rows — Comskip's program and `.ini`, the three
  Files & folders paths, the log folder, and the mkvmerge, ffmpeg and ffprobe
  paths — were never wrapped for translation, leaving English labels beside
  German descriptions. Fourteen strings, now translated. They were invisible
  to the untranslated-string scan because it reads a call's first argument and
  these are the second and third.

- **The German interface addressed the reader inconsistently.** Eight strings
  used the informal *du* while the other nine hundred-odd used the formal
  *Sie* — the update checker, the favourite-folders hint and the batch requeue
  tooltip among them. All now use *Sie*. (The user guide is written throughout
  in *du*; that is unchanged.)

- **Two age settings on the Maintenance page showed English units.** The
  cached-data and renamer-match age spinboxes read "30 days" and "never" in
  German, directly below a third reading "7 Tage" — the newer working-copy
  setting wrapped its suffix for translation and the two older ones never had.
  Both strings were already translated, so nothing but the lookup was missing.

### Documentation

- **The guide no longer presents Comskip as the only detector.** Sections 1
  and 3, the keyboard shortcut table and the VideoReDo comparison all still
  described ad detection as a Comskip feature, and the introduction called
  Comskip "optional but recommended". Chalkline is now the default answer in
  all four places, with Comskip presented as the alternative to reach for when
  Chalkline is not giving good results on a particular channel.

- **Added a Batch Manager screenshot**, showing a queue part-way through with
  a job handed over from the editor mid-export.


- **The user guide covers everything added since 2.4.0**, in both languages:
  choosing a detector, how Chalkline works and why it reports nothing rather
  than guessing, learning channel logos from your edits and the conditions
  that apply, the Remembered logos dialog and the channel-name-versus-service-ID
  pairing it exists for, the silent audio option, the configurable working-copy
  folder, and the Watcher following the editor's detector choice. The settings
  reference listed five pages under names that no longer matched the dialog.

- **Three sections of the German guide were hollow** and had been since
  15 August: the keyboard shortcuts section had lost the paragraph about skip
  distances and the `jump_back_30` naming, *Saving video* had lost an entire
  note covering multi-track audio, audio-description flags and DVB subtitles,
  and *Getting started* had dropped drag-and-drop opening and multi-file
  selection. A fourth, the note on moving projects to and from VideoReDo, had
  quietly lost its warning that a drifted mark cuts where it now sits. Found
  by comparing the two guides section by section rather than by totals.

## [2.4.0] - 2026-08-13

### Added

- **Chapters in a file become marks on the timeline when it is opened.** Files
  that have been through an encoder often carry chapters — upscaling and HEVC
  workflows produce MKVs with them, and Snipwright's own export writes its
  marks out as chapters — but opening one showed an empty timeline. The marks
  had to be found in another player, their timestamps noted, and each one
  re-entered by hand.

  Chapter starts are now mapped to the nearest frame and added as marks, with a
  brief note in the status bar saying how many were loaded. A chapter at the
  very start is skipped: encoders write one to mean "the beginning" and a mark
  on the first frame is no use for navigation. Marks that come with a project
  are never overwritten, and a file with no chapters — anything straight off a
  tuner — opens exactly as before.

### Fixed

- **HDR colour is now kept across every cut.** The frames re-encoded at each cut
  point were written with their colour unspecified while the rest of the file
  declared BT.2020 and PQ — on one 10-bit HDR10 test cut, 199 frames tagged and
  78 tagged nothing, which on an HDR display shows as a flash at every join.
  Those frames now carry the source's colour description.
- **Spliced HEVC streams now carry one coherent picture numbering.** Supplying
  that colour was, on its own, enough to break the join: a lost frame and
  `Duplicate POC in a sequence` from the decoder. That was not a colour fault
  but a splicing fault the missing colour had been hiding.

  Segments copied from the source keep the source's own picture order counts,
  so segments taken from different points in a recording can bring the same POC
  with them — measured on the project's 10-bit test file as two pictures both
  claiming 44, twenty-five pictures apart. It went unnoticed because the
  boundary encoder wrote a different SPS from the source's, so a decoder
  re-initialised at every switch between copied and re-encoded material and
  cleared the earlier picture out of the DPB before the colliding one arrived.
  Setting the colour makes x265 reproduce the source's SPS exactly, the two
  parameter sets stop differing, nothing re-initialises, and the collision
  surfaces. ffmpeg-based players tolerated the old output; a decoder that does
  not re-initialise the same way need not have.

  Each run of output pictures is now given one constant POC offset, chosen to
  clear whatever could still be in the decoder's DPB. Constant, because the
  reference picture sets in the slice headers are deltas, so shifting a whole
  run leaves every reference pointing where it did. An IDR always begins a run
  of its own at offset zero: it flushes the DPB, so it cannot collide with
  anything before it, and it carries no `slice_pic_order_cnt_lsb` to rewrite in
  any case.

  On the 10-bit test file this takes 38 latent collisions to none with the
  decoded picture byte-for-byte identical to 2.3.0's. Sources whose keyframes
  are IDR rather than CRA — many commercial encodes — were never affected and
  come out unchanged. H.264 numbers pictures by a different scheme and is not
  touched.

  If the renumbering meets something it cannot account for — long-term
  reference pictures, separate colour planes, a parameter set it cannot parse,
  a packet that is not Annex B — it turns off for the rest of that export,
  writes the stream exactly as 2.3.0 did, and logs the reason.

- **The log no longer says the audio will be re-encoded for MP4 when it is
  copied.** A broadcast AAC recording exported to MP4 logged "re-encoded for
  .mp4" and then, moments later, "copying the audio as-is (aac)" — a flat
  contradiction that made a correct, fast export look as though it had skipped
  work. Nothing was wrong: the LATM graft has already produced raw AAC, which
  MP4 can carry untouched, so there is nothing to re-encode. Only formats MP4
  cannot carry, such as mp2, are re-encoded, and that is still logged when it
  happens.

- **A track lost to an export failure is no longer described as a silent one.**
  When the export could not write an audio track and completed without it, the
  summary said the track "carries no audio at all" and that "nothing was
  lost". Both were untrue, and the reassurance is what kept a real fault from
  being noticed. A track lost this way is now reported as an error at the top
  of the summary, saying plainly that the audio is present in the recording
  and asking for the log.

- **Audio description tracks survived the first export but were dropped from
  the next one.** With the track kept (below), exporting a recording to `.ts`
  worked, and exporting the same recording to `.mkv` or `.mp4` immediately
  afterwards lost it again — reported, wrongly, as a silent track that cost
  nothing.

  Walking a file is what teaches ffmpeg the parameters of a stream whose
  header does not declare them. The first export walks the file and caches the
  result; the next one loads that cache and skips the walk, so the track's
  channel count and sample rate were never established, and the muxer rejected
  the output stream copied from it. Those parameters are now determined when
  the cache is used, and the output stream is built from them.

- **Audio description tracks are no longer dropped from broadcast recordings.**
  A BBC One recording with a working AD track exported without it, reported as
  "carries no audio in this recording". It carried plenty — 141,570 packets,
  and audible description throughout.

  Whether a track was usable was decided from the channel count and sample rate
  in the container header. Zeroes there mean the parameters could not be worked
  out, which is not the same as the track being empty, and some broadcast AD
  streams simply do not declare them. Probing harder does not help: this one
  still read as "0 channels, 0 Hz" with a 100 MB probe while decoding its very
  first packets without difficulty. When the header says nothing, Snipwright now
  asks the decoder instead, and keeps the track if it produces audio.

  Worth knowing if you have checked such a track by ear and thought it empty: UK
  audio description is often a receiver-mix track carrying only the narration,
  silent between descriptions. Skipping through one will land in silence most of
  the time even when it is working perfectly.

- **The user guide no longer says cutting a Blu-ray uses several gigabytes of
  RAM.** That stopped being true in 2.2.0, when audio stopped being held in
  memory all at once. Large, high-bitrate sources still take longer to analyse
  for cut points, which the guide continues to say.

- **The log no longer claims MKV audio was converted to AAC when it was not.**
  Repackaging an MKV with mkvmerge was logged as "repackaged to native AAC"
  whatever the audio actually was, so a Dolby Digital Plus soundtrack appeared
  to have been converted when both the input and the output were E-AC-3 and
  nothing had changed. The message no longer names a codec.

- **Commercial detection now says which pass it is on.** The progress bar would
  climb to around half way, drop back to zero and start again, which looked as
  though detection had crashed and restarted.

  It had not, and the bar was right: Comskip rescans a recording from the
  beginning when it cannot settle on a logo, and the percentage genuinely
  returns to zero each time. One Sky Mix recording took three passes, processing
  234,316 frames for a 109,470-frame programme. The dialog now reads "pass 2",
  "pass 3" and so on, so a reset is recognisable as normal work rather than a
  fault. The dialog is also sized up front for the longest message it can show,
  since it previously grew partway through detection and cut the text off.

- **Cut points on interlaced recordings are no longer coded as progressive.**
  The frames re-encoded at each cut are meant to be coded as fields when the
  source is interlaced, or players skip deinterlacing and show combing on
  motion until the copied stream resumes. Two separate faults meant that
  usually did not happen.

  First, whether a recording counted as interlaced was decided by decoding a
  single frame — the first one. Broadcast material is routinely mixed, and
  film-sourced programmes tend to open on progressive frames. One Channel 4 HD
  recording was therefore treated as progressive throughout even though 326 of
  the 686 frames later re-encoded were field-coded. The check now samples a run
  of frames, and also consults the field-pair evidence already gathered while
  indexing.

  Second, the interlace decision was made once per export, but each re-encoded
  run opens its own encoder and the setting has to be applied before that
  encoder starts. Only the first run was ever configured; every later one came
  out progressive whatever it contained. It is now decided per run.

  A run is coded as fields only when the frame that opens it is itself
  interlaced. Field order comes from that frame, and a progressive one carries
  none — enabling interlaced coding off a progressive opening frame produced a
  stream marked bottom-field-first on a recording whose fields are top-field
  first, which judders on playback and is worse than the combing being fixed.
  A run that opens progressive is therefore left as it was.

- **The frame index cache is invalidated after the indexing fixes above.** Its
  version was not bumped when the field-pair collapse changed, so an index built
  by an earlier version stayed valid and kept being loaded — putting the halved
  frame count and the old interlaced flag back out of reach. Nothing needs
  clearing by hand; entries from earlier versions are now ignored.


- **The GOP fix below now reaches files that had already been opened.** Smartcut
  caches its index of GOP boundaries, and an entry written before that fix holds
  the shifted values — so loading one put the cut straight back into the fault,
  and a fixed build behaved exactly like the broken one on every recording
  already indexed. The cache format version has been bumped, so those entries
  are ignored.

- **Clearing the cache in Settings now clears both caches.** Snipwright keeps
  two: its own frame index, and smartcut's index of GOP boundaries. Only the
  first was being cleared, so a file that had already been opened kept behaving
  as it did before no matter how many times the cache was cleared.

- **Recordings that begin part-way through a GOP can now be exported without
  Quick Stream Fix.** Exporting one produced a file with a video stream and no
  video packets in it, reported as "Export produced no readable video" — so
  Quick Stream Fix became a routine step before cutting anything off the tuner.

  Each keyframe closes the GOP before it. A recording that starts mid-GOP,
  which is normal off a tuner and true of any byte-copied excerpt of one, has
  video packets before its first keyframe, and those belong to no GOP. They
  were being recorded as the end of one anyway, which shifted the whole array
  by one: every GOP then ran from its start to a timestamp 1800 ticks earlier,
  so no packet could fall inside one and nothing was copied. Running Quick
  Stream Fix appeared to cure it because the repaired copy starts on a
  keyframe.

  On a recording that already starts on a keyframe nothing changes, and an
  export of one is byte-for-byte what the previous build produced.

- **Progress and logging named the wrong scene on broadcast recordings.** An
  export of a five-scene project reported "scene 5" for all 2046 of its cut
  segments, and the progress dialog counted every scene as the last one. The
  cut itself was correct throughout — only the labelling was wrong.

  Scene boundaries were worked out as an offset from the start of the stream,
  then compared against cut segments timed on the source's own clock. A
  broadcast recording begins wherever the transmission clock happened to be —
  one started at 51,305s — which put every segment past the last scene. Both
  are now on the same timeline. Files starting at or near zero were never
  affected, which is why this only showed on recordings straight off the tuner.

- **A recording could be indexed at half its real length.** A 2h38m film opened
  as 01:19:20, with the timeline scale, the Info panel and every reported timing
  halved to match. Scene markers still landed in the right places, because the
  timestamps themselves were correct — only half the frames were in the index —
  which made it easy to miss until an export went wrong.

  Field-coded broadcast recordings carry some frames as two field-pictures, and
  the index merges those back into one frame. It used to do that by placing
  every packet on a grid, `round((pts - first_pts) / ticks_per_frame)`, keeping
  one packet per slot. A field pair is two half-frame gaps and returns the
  stream to the grid, so pairs normally cancel — but an odd number of them
  anywhere in the file leaves everything after it sitting exactly half-way
  between slots, and rounding then puts consecutive frames in the same slot.
  Half the recording was discarded.

  Frames are now paired locally: a packet is merged into the previous frame when
  it sits less than a field period after it. Nothing depends on where the
  timestamps happen to fall, so the same recording indexes the same way whatever
  its field pairs do.

  The recording this was found on had 2027 half-frame gaps — an odd number.
  The same file after Quick Stream Fix had 2004, and indexed correctly. Whether
  that count came out odd or even was the only difference between a good index
  and a ruined one, which is why running Quick Stream Fix appeared to be the
  cure.

- **Exporting the same project twice now produces the same file.** It did not:
  two exports of one project, with a restart between, came out with their
  re-encoded segments different, while every copied segment was byte-identical.
  The picture was never wrong and nothing was lost — the difference was small
  enough to need a frame-by-frame comparison to see at all — but it meant an
  export could not be checked against a previous one, so there was no way to
  tell whether a change to the cutting code had altered the output or not.

  The cause was the decoder that feeds the boundary re-encoder. It was opened
  with frame threading across every core, and frame-threaded H.264 decoding of
  a field-coded broadcast recording does not return the same pixels every time
  when the machine is busy. On a Channel 4 HD recording exported five times
  with the application playing in the background, 10 of the 686 frames handed
  to the encoder decoded differently — every one of them a field-coded picture,
  and no progressive frame ever varied. One such frame changes every packet to
  the end of its re-encoded run, because the encoder's references change with
  it, which is why a single frame moved 125 of them.

  That decoder now runs on one thread. Only the GOPs at cut points are decoded
  at all — 833 frames for a five-minute recording with six re-encoded segments —
  so the cost is a few seconds on an export, not a proportional slowdown.
  Playback and indexing are untouched and still use every core.

  This is not a new fault: it pre-dates 2.3.0 and affected every version with
  the boundary re-encoder in its current form.

### Changed

- **Every export is now checked for length, including HD broadcast
  recordings.** The check compared the output's packet count against the number
  of frames the edit kept. On a field-coded source those two count different
  things, so the check was skipped altogether — which is most UK HD. For those
  files the only verification was "is the output completely empty", and the
  frame count in the completion dialog was the number of frames requested
  rather than the number produced. A partial export would have looked exactly
  like a good one.

  The finished file's duration is now compared against the length the edit asked
  for, which means the same thing for every codec and container and costs one
  ffprobe of the container header. Anything more than a second out is flagged
  in the completion dialog and written to the log, which now records the length
  written against the length expected for every export.

- **Clearer wording when an export produces no video.** The message said the
  source "may need repairing" and pointed at Quick Stream Fix, which was
  misleading — the recording was usually fine and Snipwright was mishandling
  it, as the GOP fix above describes. Now that cause is gone, the message says
  plainly that the file has not been saved, that the recording itself is likely
  damaged, and what Quick Stream Fix will do about it.

## [2.3.0] - 2026-08-08

### Added

- **Cutting a 10-bit HEVC recording could fail outright.** Depending on where
  the scenes fell, the export died with `Invalid argument ... returned 22` from
  the muxer, and moving the same scenes a little made it succeed again.

  Matroska gives the opening packets of a file no decode timestamp at all —
  there is nothing to report until enough pictures have been read to absorb the
  reorder delay. Cutting at a CRA GOP whose leading pictures reference frames
  before it means seeking back to prime the decoder, and when that reached the
  head of the file, those timestamp-less packets were mistaken for packets of
  the GOP being cut. The picture that opens the file was then taken for the CRA,
  so no leading picture was recognised as one and none was re-encoded, and two
  packets from the start of the recording were remuxed into a segment ten
  seconds in — where rebasing their timestamps put them before the start of the
  file and the muxer refused them.

  A packet with no decode timestamp is now only ever treated as belonging to the
  first GOP of the file, and the CRA is identified by being the keyframe that
  opens its own GOP rather than by being the first packet to hand. Cuts that
  already worked are byte-for-byte unchanged; the ones that failed now export
  clean, frame-accurate and free of the timestamp warnings that the previous
  stopgap left behind.
- **Cropping an HEVC recording no longer converts it to H.264.** A crop forces
  a re-encode even when the profile says copy the video, and that re-encode
  always used H.264 — so an HEVC source came out H.264: a larger file for the
  same picture, and for a 10-bit source it meant the High 10 profile, which
  fewer players decode than the HEVC it started as. The crop now keeps whatever
  codec the source used, unless the profile explicitly asks for HEVC.
- **The In and Out markers now stay put after adding a scene.** They used to
  disappear the moment you pressed Add Selection, so noticing a boundary was a
  frame out immediately afterwards meant marking both again from scratch. Each
  marker is now replaced only when you next place it: nudge the one that's wrong,
  add again, and the scene you just made is adjusted rather than a second one
  added — the overlap handling that made re-marking work has always done this,
  it simply wasn't reachable. The same applies to Cut Selection and Trim
  Unselected. Operations that aren't a single marked edit — Select All, and the
  bulk range operations — still clear the markers, since there is nothing left
  to correct. (Requested during testing; matches VideoReDo's behaviour.)
- **Re-encoding keeps the source's bit depth.** Every re-encode path asked
  ffmpeg for `yuv420p`, which is 8-bit — right for the broadcast recordings
  Snipwright was built around, and wrong for anything better. A 10-bit source
  cropped, aspect-corrected or converted to MP4 came out 8-bit with no warning:
  banding in skies and gradients, and no way to recover the detail. The output
  now matches the source, and the log says when 10-bit is being kept.

  10-bit H.264 means the High 10 profile, which some hardware players refuse, so
  the log notes that HEVC is the safer choice for 10-bit material. A lossless
  copy was never affected either way — this only concerns the paths that
  genuinely re-encode.
- **COMSKIP.md** — build instructions for Comskip on Linux and Windows that
  actually work. Comskip is a separate project and Snipwright runs fine without
  it, but its own documentation omits enough to stop most people: on Windows the
  MSYS2 package is called `argtable`, not `argtable2`; `base-devel` contains no C
  compiler; and ffmpeg 7 removed `AVCodecContext.ticks_per_frame`, which Comskip
  0.83 still uses, so it needs a patch to compile at all. The known limitation
  with UNC network paths is noted too.

### Changed

- **Switching verbose logging on or off is recorded in the log**, not just
  stated at startup. It is usually turned on mid-session, and the log then had
  no record of when — or whether — that happened. Only a change is logged, so
  opening Settings and clicking OK does not add a line each time.
- **Playback and scene-selection chatter is now verbose-only.** Starting
  playback wrote two lines to the log and each scene selection wrote another,
  none of which mean anything unless that specific thing is being investigated
  — and all of which pushed the lines that do matter further apart. They are
  still available under **Settings → Logs → Verbose logging**. Export
  diagnostics are deliberately untouched: those write a handful of lines per
  export, and are what a problem report gets read from.
- **The audio output device is announced once, not on every play.** The sink is
  rebuilt before playback whenever it has gone into an error state, and each
  rebuild logged "output device ready" afresh. A genuine change of device still
  logs at INFO, since that is worth knowing; an identical rebuild is
  verbose-only.
- **The Info panel's Program row now reads as a duration**, like Selection and
  Output beside it. It showed the last frame's timecode, one frame short of the
  file's length, so an uncut recording put Program a frame behind Output. Cursor
  is still a position, so at the last frame it reads one frame lower — that part
  is correct and matches VideoReDo.
- **Selecting a scene in the list loads it into the In and Out markers**, and
  takes the playhead to its start. Only double-click did this before, which was
  hard to discover. Because the span then overlaps the existing scene,
  correcting one is: select it, nudge the marker that's wrong, add again. Click
  and the Up/Down keys now go through the same path, so all three behave
  identically.
  highlight marks the row you are working on, but it stayed lit after you had
  navigated somewhere else entirely, which was a distraction and said something
  about the current position that was no longer true. The In and Out markers are
  deliberately left alone — those hold the edit in progress, and VideoReDo keeps
  them too.

### Fixed

- **Cancelling a batch job logged it as a crash, with a traceback.** The
  exporter unwinds an abort by raising, and the batch runner could only catch
  it as a generic exception — so pressing stop produced "Batch job crashed"
  followed by a stack trace, which reads like a fault in a log that is
  otherwise the first thing consulted when something goes wrong. A cancelled
  job is now recorded as cancelled, with a plain one-line message. An error
  arriving after a stop is treated as a cancellation too, since killing a
  subprocess can surface either way — the single-file export path already did
  this and the batch runner did not. A genuine crash still logs in full.
- **Chapter marks never reached the exported file**, and after that was fixed,
  still did not reach one exported from the batch. Marks added with the A key
  were held in the project and saved with it, but the export was never told
  about them — `export_ranges` had no way to receive them, so an .mkv came out
  with chapters at the scene joins only, exactly as if no marks had been
  placed. The batch was a second instance of the same gap: it reads the
  project's marks when loading the job and then dropped them on the way to the
  export, so the same project gave chapters from Save Video and only scene
  joins from the queue. Both routes now carry them, positioned from the frame
  index rather than by frame arithmetic, so they stay on the picture they were
  placed on even on field-coded HD. A mark that falls in cut material has
  nowhere to go and is dropped; the log says how many, because a mark
  vanishing silently looks like a fault. A mark landing on a scene join is
  merged with it rather than written as a second chapter a millisecond later.
- **Raising the volume during playback stayed silent until you paused.** Audio
  only decodes while the volume is above zero, and nothing re-checked that when
  the slider moved — so starting playback at zero and then turning it up raised
  the sink's volume with nothing feeding it. Pausing and playing again was the
  only way to recover. Moving the slider now re-evaluates whether audio should
  be running, and picks up from the current position; dropping to zero stops
  the decoder rather than decoding sound nobody can hear. Reported in testing.
- **The audio device was rebuilt before every single play.** The sink was
  treated as broken whenever Qt reported any error at all, including
  `UnderrunError` — which is not a fault: the buffer running dry is what
  happens at the end of every playback, and Qt keeps reporting it until the
  sink is started again. So each play tore down a perfectly good device and
  built another. Underrun now counts as healthy, and the error is compared both
  by equality and by numeric value, because `error()` can return an enum member
  or a plain int depending on the PySide6 build and those never match each
  other. A rebuild still happens for the states that mean something is actually
  wrong, and the log records which one.
- **The log could report an error state that was never true.** The rebuild
  message read the sink's error a second time to print it, so it could report
  `NoError` while having just decided the sink was unusable — impossible, and
  useless for diagnosis. The error is now read once and the same value is used
  for both the decision and the message.
- **Playing a section logged nothing if the volume was down.** The playback
  line lived in the audio path, which only runs when an output device exists
  and the volume is above zero — so on mute, or with no sound device, a whole
  session of playback left no trace even with verbose logging on. It now logs
  from the transport itself, where the play state actually changes, and records
  the stop as well as the start.
- **A log now says whether verbose logging was on.** Without it, a log with no
  playback or scene-selection lines was ambiguous between "verbose was off" and
  "those things did not happen" — which cost a round trip to work out. The
  startup lines now state it outright, and point at the setting when it is off.
- **The German guide was missing content the English one has.** A parity check
  by section found two gaps: the Navigating section had lost the three skip
  distances (short, medium, long), their keyboard shortcuts and the note that
  all three are configurable, and the output profile list was missing the
  Encoder speed and Quality (CRF) entry. Both are restored, and the two guides
  now match section for section on headings, bullets and table rows.
- **The In and Out markers were invisible against a highlighted scene.** They
  were drawn as thin pale lines, which vanished into the yellow of a selected
  row, so after clicking a scene it looked as though no markers had been set at
  all. They are now a dark line inside a light one, which reads against every
  colour the bar draws: the dark red of a cut, the green of a kept scene, the
  yellow highlight and the white playhead.
- **The Info panel's MB figures were guesses, and could be out by 5%.** They
  assumed every frame occupied the same number of bytes, so a range's size was
  simply its share of the file by frame count. Broadcast video is nowhere near
  constant bitrate: on an hour of Top Gear the panel predicted 2172 MB for a cut
  that wrote 2297 MB, because the programme itself runs above the average of a
  recording padded with lower-bitrate continuity either side. VideoReDo reported
  2302 MB for the same cut because it counts real bytes.

  Indexing now records a running total of video packet bytes per frame, which
  costs one demux field it was already reading and about 900 KB of memory on an
  hour-long recording. Cursor, Selection and Output are measured from those
  totals — exact for the video, with audio, subtitles and transport overhead
  spread evenly across the running time, which is fair because those streams are
  near constant rate. The joiner's per-scene sizes use the same measurement.

  Cached indexes gain the byte totals, so `CACHE_VERSION` rises to 4 and every
  file is re-scanned once on first open. An index that predates the change still
  loads and falls back to the old flat estimate rather than failing.
- **A dropped audio-description track was reported in the wrong terms, and the
  explanation was wrong about VideoReDo.** Where a description track was both
  HE-AAC and silent across the kept scenes — which is the usual case, since the
  description often runs either side of a programme and not within it — the note
  said the track "can't be re-encoded in sync from a mid-stream cut", implying
  something had been lost. Nothing had: there was no audio in it to carry. The
  silent-track wording now takes precedence, and the claim that "VideoReDo drops
  them too" is gone, because a Channel 4 HD log shows it carrying such a track
  straight through.
- **The Info panel's Selection row stayed empty while you were selecting.**
  Marking In and Out — the main way of selecting anything — left the row showing
  dashes; it filled in only after a scene had been added and then clicked in the
  list. It now shows the marked span's duration and size as soon as both markers
  are placed, which is what VideoReDo does. A highlighted row still fills the
  row when there are no markers.
- **In Cut Mode, selecting a row in the list acted on the wrong range.** The
  list shows the cuts in Cut Mode, but selecting a row looked the number up in
  the kept ranges instead — so row 1 of the cuts selected kept scene 1. The
  playhead jumped somewhere else entirely, the Info panel reported that other
  range's duration and size, and double-clicking loaded the wrong span into the
  markers. Rows are now read from the list itself, so the two can't disagree.

## [2.2.0] - 2026-08-05

### Added

- **Audio delay in output profiles.** A recording that arrives with the sound
  running ahead of or behind the picture can be corrected on export: set
  **Audio delay** in the profile, positive when the sound is early and negative
  when it lags. This changes only the timing, so the audio is still copied
  losslessly. (Prompted by VideoReDo's "Audio Sync Adjustment", which Snipwright
  had no equivalent of at all.)
- **Trim and Copy Source File is now documented** in both user guides: what it
  is for, what each of the four start/stop options does, and honestly what its
  limits are — it copies bytes rather than rebuilding the file, so the result is
  approximate even when snapped to a keyframe, and it cannot work on MP4.
- **Loudness processing in output profiles.** Broadcast recordings vary a good
  deal in level, and some drama is mixed so quietly it's hard to hear. A profile
  can now **Normalise (EBU R128)** to a target loudness — -23 LUFS is the
  broadcast standard, -16 suits headphones — **Compress dynamic range**, which
  lifts quiet dialogue without the loud moments becoming painful, or apply a
  plain **Change level** in dB.

  Normalisation measures the recording first and then applies the correction, so
  it hits the target exactly; a single pass estimates as it goes and lands a
  couple of LUFS out. Any loudness processing re-encodes the audio, so leaving it
  alone is what keeps the lossless copy.
- **Surround downmix.** **Surround audio → Fold down to stereo** in a profile
  folds a 5.1 mix to two channels. A broadcast surround mix played through two
  speakers often has nearly inaudible dialogue, because the centre channel
  carrying it isn't there. Only tracks with more than two channels are touched —
  a stereo track is copied untouched rather than needlessly re-encoded.

  Both apply before any container conversion, so they hold for `.ts`, `.mkv` and
  `.mp4` alike, and a failure leaves the cut untouched rather than losing it.

### Changed

- **"Match Source" wrote MPEG-TS into files named `.mkv` and `.mp4`.** The
  format was only resolved to a real container when a profile forced MKV or MP4;
  matching the source fell through to the MPEG-TS path while still taking the
  source's extension. The result played, but was mislabelled — MediaInfo reports
  it as MPEG-TS with an invalid extension — and had no chapters, because
  chapters are written during a Matroska mux that never ran. Matching now
  resolves to the destination's actual container. (Spotted in testing, from a
  Blu-ray export that had lost its chapter markers.)
- **Trim and Copy offered only transport streams, and produced broken MP4s.**
  The source filter listed a handful of extensions, which was both too narrow —
  MKV trims perfectly well — and too broad, since MP4 does not. There is now a
  single **All files** entry, and pressing **Start Copy** on an MP4, MOV or M4V
  asks first: those containers keep their index in a header, so a byte-range
  copy leaves it describing data that is no longer there and the result won't
  open. The output filter also defaults to the source's own extension rather
  than always offering `.ts`.
- **The user guide stayed dark in the light theme.** Its stylesheet was written
  for the dark look and hard-coded into the HTML, so anyone using the light
  theme opened Help and got white text on a dark background. The guide is now
  recoloured as it loads. There is still one guide file per language — the light
  palette is a substitution table rather than a second copy to keep in step —
  and only the stylesheet changes, verified by comparing the document body
  before and after.
- **MP4 exports re-encoded audio that didn't need it.** The MP4 path always
  re-encoded to 192 kbps AAC, which was there for broadcast LATM and MP2 that
  MP4 genuinely cannot carry — but it applied to everything, so an MP4 source
  with AAC or E-AC-3 had good audio decoded and re-encoded for no reason. That
  cost time, and could make the output *larger* than the source. Audio MP4 can
  carry is now copied untouched. (Found while testing on Windows.)
- **Folder settings showed forward slashes on Windows.** Qt's file dialogs
  return them on every platform; the settings page now displays paths the way
  the platform writes them.
- **An MKV whose audio wouldn't play is now re-encoded rather than shipped.**
  Some broadcasts - Channel 4 HD films among them - change their AAC channel
  configuration part-way through. Matroska stores one configuration for the
  track, so whichever is written, the frames using the other fail to decode:
  `channel element 1.0 is not allocated`, and a file with no usable sound.
  Snipwright already detected this and fell back from mkvmerge to ffmpeg, but
  that hits the same wall, so it shipped the file anyway with a footnote
  suggesting AAC - after an export that may have taken an hour.

  The result is now checked again after the fallback, and if it still won't
  decode the audio is re-encoded to AAC, which collapses the stream to one
  configuration. Lossless where possible, playable always. Setting Audio to
  Re-encode AAC in the profile still skips the attempt entirely.
- **The source file's index is now cached between exports.** Working out where
  a file can be cut means walking every packet in it, and that was repeated in
  full every time the same unchanged file was exported — over three minutes for
  a 21 GB Blu-ray on a network share. The result is now written beside the
  frame-index cache and reused, so a second export of the same file starts
  almost immediately.

  The cache holds only the computed index; the file itself is re-opened each
  time. It is keyed on path, size and modification time, so an edited or
  replaced file gets a fresh index rather than a stale one, and it ages out
  under the same **Delete cached data older than** setting as everything else.
  Verified attribute by attribute, and by comparing the cut plans a cached and
  a freshly-walked index produce.
- **Exports no longer scan the source file twice before cutting starts.**
  Working out the cut plan requires walking the whole file to map its GOPs and
  packet timestamps, and that was being done once to work out the segments and
  again immediately afterwards to describe them. On a 21 GB Blu-ray held on a
  network share the second pass alone took three minutes and twenty-three
  seconds, with nothing happening on screen. The second scan is gone; the plan
  it produces is identical, verified segment boundary by segment boundary.

  (This is a separate index from the one Snipwright caches on disk. That cache
  works correctly — it was smartcut's own, which is built fresh each time.)
- **Cutting no longer holds the whole file's audio in memory.** Every audio
  packet was collected up front — the original smartcut code carried a note
  saying as much — which is unnoticeable for a Freeview recording and punishing
  for anything larger. A Blu-ray with six DTS tracks meant about 3.5 GB of
  compressed audio plus a Python object for each of some two and a half million
  packets, most of the 15 GB working set observed while cutting one.

  Packets are now read from the file as the cut needs them, keeping a bounded
  window rather than the lot. Measured on a 700 MB recording, one audio track
  went from 254 MB held to effectively nothing. The saving scales with the file,
  so it matters most on exactly the material that was worst affected.

### Fixed

- **Loudness normalisation changed the audio's sample rate.** ffmpeg's
  `loudnorm` works internally at 192 kHz and leaves its output there, so an
  8 kHz recording came out at 96 kHz — twelve times the data for no gain
  whatsoever, since upsampling cannot add detail that was never there. The audio
  is now resampled back to whatever the source used.
- **Audio delay, downmix and loudness failed on anything that wasn't MPEG-TS.**
  The adjustment pass always wrote MPEG-TS, which was fine while it only ran on
  the intermediate that MKV and MP4 exports go through — but a "match source"
  export writes straight to the final file, so an AVI had MPEG-TS written into
  it under an `.avi` name, and PCM audio in MPEG-TS fails outright. It now keeps
  whatever container the file is already in.
- **A failed audio adjustment was reported as an unqualified success.** The cut
  is deliberately kept when an adjustment fails — losing a good export over a
  sync tweak would be worse — but the summary said "Export complete" with no
  mention that the loudness or delay you asked for hadn't been applied. It now
  says so plainly.
- **A downmixed surround track was encoded at ffmpeg's default bitrate.** The
  AAC bitrate control was enabled only when Audio was set to AAC, so a profile
  that copied audio while downmixing left the field greyed out — no bitrate
  reached ffmpeg, and it fell back to its own default of about 128 kbps. A 5.1
  DTS-HD track from a Blu-ray came out as thin stereo. The control is now
  enabled whenever the audio will be encoded, downmix included, and its tooltip
  says what a sensible figure looks like.
- **Saving a video crashed if the profile set an audio delay or downmix.**
  `ExportWorker` never received the two new settings, so the export raised a
  TypeError before it began. The static keyword-argument check that exists to
  catch exactly this only understood function calls, not constructors, so a bad
  keyword on a class went unnoticed; it now covers constructors too, and ignores
  names defined more than once in the tree rather than checking one class
  against another's signature.
- **A crash parsing HEVC streams with an explicit aspect ratio.** The H.265
  parser referenced `EXTENDED_SAR` without ever defining it, so any stream
  setting `aspect_ratio_idc` to 255 — the value meaning "the aspect ratio is
  given explicitly rather than by table index" — would have raised a NameError
  rather than parsing. This is in the vendored smartcut code, which came from a
  project that is no longer maintained, so it is ours to fix.

## [2.1.0] - 2026-08-01

### Added

- **Optional check for new versions.** Under **Settings → Maintenance**, set
  **Check for new versions** to Daily, Weekly or Monthly and Snipwright will say
  when a newer release exists and offer to open the releases page. There's also
  **Help → Check for Updates** for a one-off look.

  It is **off by default** and stays off unless you turn it on — nothing contacts
  anything otherwise. Nothing is downloaded or installed either: Snipwright runs
  from a folder you extracted, and replacing files underneath a running editor is
  a good way to break someone's work mid-cut. Only GitHub's public releases list
  is read, and the check runs on a background thread so a slow network can't hold
  up the editor.
- **Favourite folders.** If you keep different series on different drives, add
  those folders under **Settings → Files & folders**; the Save Video dialog and
  the Batch Manager then have a **Folders** button that sends the output straight
  to one of them, keeping the file name. A folder that isn't currently available
  is shown greyed out rather than hidden, so a missing drive is visible instead
  of puzzling. Choosing a favourite applies to that export only — your usual
  destination is what the dialog offers next time.

  The Batch Manager has a **Folder** column instead, so each job in the queue can
  go somewhere different: two episodes of one series to one drive, something else
  to another. Names are still derived and de-duplicated as usual, so two jobs
  landing in the same folder don't overwrite each other.
  (Requested by Paul-Webster, who was reproducing it with one output profile per
  series — which works, but conflates how a file is encoded with where it goes.)
- **Send to End in the Batch Manager.** When a job fails or is held for review
  the batch moves on, and until now a fixed job had to wait for the whole queue
  to drain before it could be retried — the running job couldn't be crossed.
  Selecting a job and pressing **Send to End** moves it to the back of the
  queue, where the runner reaches it on the same pass. The running job, an
  adopted export and anything already finished stay put.

  **Move Up** and **Move Down** now refuse any swap involving a completed job.
  The runner walks the queue by index and never revisits a position it has
  passed, so a queued job lifted above the block of finished jobs would sit
  where the cursor has already been and never run at all. Completed jobs stay
  at the top; Send to End is how a job gets back into the current pass.

### Changed

- **Ignore-list entries now match from the start of the file name.** Matching
  was substring-anywhere, so an entry of "Gone" quietly ignored *Star Trek
  S01E03 Where No Man Has Gone Before*. Recording file names begin with the
  programme title, which is what people are typing, so entries are now compared
  against the start of the name. Keyword-anywhere matching is still available
  under **Matching** in the ignore list editor, and an individual entry written
  with a leading `*` is always matched anywhere regardless of the setting.

  If your list contains entries meant to match mid-name, either switch the mode
  or prefix those entries with `*`. The full explanation is in the user guide;
  the editor keeps a short **Match** dropdown beside the list rather than
  spending its height on prose.

### Fixed

- **Quick Stream Fix working copies are now cleaned up.** Repairing a recording
  writes a working copy of it — a whole video file, frequently several
  gigabytes — into the system temporary folder, and nothing ever removed it.
  Linux clears `/tmp` at reboot so this went unnoticed; Windows never clears its
  temporary folder, so a few sessions of repairing recordings could quietly
  consume tens of gigabytes.

  Working copies are now deleted once they reach a set age — a week by default,
  adjustable under **Settings → Maintenance**, where the space they occupy is
  shown along with buttons to open the folder or delete them now. They are kept
  rather than deleted at exit so you can close Snipwright and come back to a
  recording without repairing it again.

  Nothing in use is ever deleted: not the recording open in the editor, not one a
  background export is reading, and not one referenced by a job waiting in the
  batch queue. That last case is the important one — after a repair, a queued
  job's project file points at the working copy rather than the original,
  because the cut points belong to the repaired file's timeline, and the queue
  survives restarts.
- **Check for Updates froze the application on Windows.** The result handler was
  connected to the worker thread's signal through a lambda. A lambda has no
  QObject receiver, so Qt cannot work out which thread should run it and calls it
  directly on the emitting thread — meaning the message box was being built off
  the GUI thread. Linux tolerated that; Windows deadlocked, leaving an empty
  dialog and a frozen main window. It now connects to a bound method, which gives
  Qt the receiver it needs. A second check can no longer start while one is
  already running, either.
- **Windows no longer flashes a console window for every helper process.**
  Snipwright shells out to ffmpeg, ffprobe, mkvmerge and Comskip constantly —
  over forty call sites, several inside a loop over scenes — and on Windows each
  one popped a console window that took focus, making it impossible to work in
  another application while an export ran. Every subprocess now starts hidden.
  No effect on Linux or macOS, where the problem doesn't arise. (Reported by
  WhatsAName42.)
- The README now states plainly that Python is required to *run* Snipwright and
  not only to install it, and answers the "why not a compiled .exe" question
  directly. Both had come up more than once.
- The export log now records the destination folder and whether it exists and is
  writable. An export that stalls before it starts is usually a destination
  problem, and the log previously gave no way to tell.
- **Exporting to MP4 could produce a zero-byte file.** A recording carrying an
  audio-description track that was silent through the kept scenes left an audio
  stream with no packets and no timebase in the intermediate file. Handed to the
  MP4 encode, ffmpeg held video back waiting for audio that never arrived — the
  log fills with "Too many packets buffered for output stream 0:0" — the filter
  graph failed on a 1/0 timebase, and nothing was written at all. Such tracks are
  now left out of the MP4 encode, as they already were for `.ts` output. (Found
  in testing, on the same Star Trek recording as the audio-track issues above.)
- **A dropped audio track is no longer reported as a loss when nothing was
  lost.** Broadcast audio description is often transmitted for a few seconds of
  one programme and silent across the rest of a long capture. Cut scenes that
  avoid those moments and the track has nothing to contribute, so it doesn't
  appear in the output — but the export summary reported it as "1 audio track
  missing", which reads like damage. Snipwright now checks whether a dropped
  track carried any audio *within the scenes kept*, and if it didn't, says so as
  a footnote rather than a warning. A track that really did carry audio still
  warns exactly as before.
- **A `.ts` export could keep an empty audio track and fail its final metadata
  step.** Broadcasters register an audio-description PID that is only
  transmitted during some programmes — one Star Trek recording carried 26
  seconds of description in 73 minutes, all of it outside the episode. Cut a
  section where it was silent and the track survived into the output with no
  sample rate and no channel count, which ffmpeg refuses to remux at all
  ("Error opening output files: Invalid argument"). The finalise step then
  failed, leaving the file without its audio dispositions and with a dead track
  a viewer could select and hear nothing from. Such tracks are now dropped
  before the remux, using the same test Quick Stream Fix has always applied on
  the way in.
- The export log now identifies each audio track by its source stream, language
  and whether it is the audio description, and names any track it drops — rather
  than reporting only how many were dropped.
- The Watcher's log said only that a recording was on the ignore list, not which
  entry caught it — unhelpful with a long list. It now names the entry.
- **The German user guide was being maintained in the wrong place.** Two copies
  existed — `assets/help/user-guide_de.html`, which is where the application
  looks, and a stray `translations/user-guide_de.html`. Recent work had gone into
  the stray, so readers of the German guide were seeing a version three sections
  and 1,100 words short: no "Coming from VideoReDo", no ignore-list section, and
  no note about handing a long export to the Batch Manager. The complete guide is
  now in the place the application reads, the duplicate is gone, and the
  translations README says explicitly where a translated guide belongs.
- The German user guide's keyboard shortcut table was missing Cut Selection,
  Trim Unselected and Select All, and named the three skip distances as fixed
  durations (10s/30s/120s) when they have been configurable for some time.

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
