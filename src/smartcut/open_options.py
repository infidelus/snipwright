"""How every source container is opened - one set of options, used everywhere.

Opened with FFmpeg's default probe, a broadcast recording's receiver-mix
audio-description track can come out with no sample rate and no channel
count: an AAC-LATM AD track on BBC Three HD (2026-10-04) does, because the
programme's opening minutes give the probe nothing to go on.  The cutter
then cannot time the frames that LATM packs without timestamps - five in
every six - and drops them, so the export kept a sixth of the narration and
lost the track entirely part-way through.  The same file opened with the
exporter's DEEP_PROBE (120M / 200M) reads that track correctly as 48 kHz
stereo.  A MEDIUM probe is worse than either: at 30M / 60M the track comes
out as type "unknown", not audio at all - which is how the usability check
of the time lost it before the cutter ever saw it.

So every place the cutter opens a source uses these, and they must stay the
same everywhere: a deeper probe can NUMBER the streams differently (on that
file the main audio is stream 1 by default and stream 2 when probed deep),
and the cutter hands stream objects from one opened container to another.
Matches exporter.DEEP_PROBE; change both together.
"""

SOURCE_OPEN_OPTIONS = {"analyzeduration": "120000000", "probesize": "200000000"}

# PyAV 18 decodes metadata tags strictly as UTF-8 unless told otherwise, so a
# recording with one badly-encoded tag would not open at all - hence
# metadata_errors="ignore" on every open.  PyAV 19 removed the argument
# (passing it is a TypeError) because it now always reads metadata safely,
# byte for byte.  So pass it only to the version that has it.
import av as _av

LEGACY_OPEN_ARGS = (
    {"metadata_errors": "ignore"}
    if int(_av.__version__.split(".")[0]) < 19 else {})
