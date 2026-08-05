"""Output profiles: the named bundles of export settings the Save Video dialog
and the Profile Options manager share, plus their persistence in the config.

A profile currently carries:
  * name, container          - drive the export today
  * output_dir               - per-profile default destination (Save dialog)
  * audio, audio_bitrate     - lossless copy, or re-encode to AAC on export
  * aspect                   - display aspect, stamped losslessly on export
  * favourite, enabled, order - manager/list behaviour

All video is smart-cut (copied), so the codec column always reads
"Match Source" and the output mode always "Smart".
"""

from PySide6.QtCore import QT_TRANSLATE_NOOP

from config.loader import save_config

# Display labels.  These stay English here (they're data, and the profile file
# stores the keys); they are translated where they're shown, under the shared
# "ProfileEditor" context, so the dropdowns and the table agree.
_CONTAINER_LABELS = {
    "match": QT_TRANSLATE_NOOP("ProfileEditor", "Match Source"),
    "mkv": QT_TRANSLATE_NOOP("ProfileEditor", "Matroska MKV"),
    "mp4": "MP4",
}

AUDIO_MODES = ("copy", "aac")          # smart copy (lossless) | re-encode AAC

# Encoder speed presets for the re-encode paths (HEVC output, or cropping).
# These are x264/x265 preset names; slower means better quality per byte.
# "veryfast" is deliberately absent - it measures the same as "faster" for both
# speed and quality, so it would only add a pointless choice.
ENCODER_PRESETS = ("slow", "medium", "faster", "superfast", "ultrafast")
DEFAULT_PRESET = "faster"               # what Snipwright has always used

# Constant Rate Factor: lower is better quality and a bigger file.  The scales
# differ between the two encoders, so CRF_AUTO resolves per codec.
CRF_AUTO = -1                           # -1 == pick a sensible value for the codec
CRF_MIN, CRF_MAX = 0, 51
DEFAULT_CRF = {"hevc": 24, "copy": 20}  # "copy" here means an H.264 crop re-encode

# How far apart keyframes (I-frames) are placed in a re-encode, in seconds.
# I-frames are several times the size of the frames between them and they reset
# the prediction chain the encoder relies on, so placing them further apart makes
# a meaningfully smaller file at the same quality.  Placing them closer together
# makes seeking finer and re-cutting the result cheaper.
#
# Broadcast uses about a second (fast channel changes); encoders default to ten
# for file playback.  Five is the middle ground: most of the size saving, still
# responsive to seek, and comfortably inside streaming conventions if a server
# ever repackages the file.  The H.264 crop path keeps the one second Snipwright
# has always used, since a cropped broadcast recording is the kind of file
# somebody is most likely to cut again.
# 0 rather than -1 (which is what CRF_AUTO uses): a CRF of 0 is meaningful
# (lossless), whereas a keyframe every zero seconds is not, so 0 is free to mean
# "automatic" and the spin box has no dead value between it and one second.
GOP_AUTO = 0                            # 0 == pick a sensible value for the codec
GOP_MIN, GOP_MAX = 1, 15                # seconds
DEFAULT_GOP_SECONDS = {"hevc": 5, "copy": 1}

ASPECT_MODES = ("source", "4:3", "16:9")
CROP_MODES = ("none", "auto", "fixed")  # off | auto-detect bars | fixed pixels
AAC_AUTO = 0                            # 0 == let the bitrate follow the source
# Spread wider than the old 128-384: a 5.1 Blu-ray track folded to stereo
# wants headroom at the top, and speech-only material is fine well below
# 128.  Matches the range VideoReDo offers.
AAC_BITRATES = (64, 96, 128, 160, 192, 224, 256, 288, 320, 384, 448)

# Audio delay, in milliseconds, applied to every audio track on export.
# Broadcast recordings occasionally arrive with the sound a little ahead of or
# behind the picture - a fault in the transmission or the tuner, not something
# cutting can fix - and without this the only remedy is another tool entirely.
# Positive delays the audio (use when sound arrives early), negative advances it.
AUDIO_SYNC_NONE = 0
AUDIO_SYNC_MIN, AUDIO_SYNC_MAX = -5000, 5000     # +/- five seconds is ample

# What to do with surround audio.  "keep" leaves the channel layout alone;
# "stereo" folds it down.  A 5.1 broadcast mix played through two speakers often
# has dialogue that is nearly inaudible, because the centre channel carrying it
# is simply absent - a downmix puts it back into both speakers.
DOWNMIX_MODES = ("keep", "stereo")

# Loudness processing.  Broadcast recordings vary a good deal in level between
# channels and between programmes, and some drama is mixed so quietly that it
# is hard to hear without reaching for the remote.
#
#   "none"     - leave the audio alone (and keep copying it losslessly)
#   "normalise"- EBU R128 loudness normalisation to a target, the broadcast
#                standard; evens out the whole programme without pumping
#   "dynamic"  - dynamic range compression, which lifts quiet dialogue at the
#                cost of the loud moments being less loud
#   "gain"     - a plain level change, up or down, applied uniformly
LEVEL_MODES = ("none", "normalise", "dynamic", "gain")

# Target loudness for "normalise", in LUFS.  -23 is the EBU R128 broadcast
# standard; -16 suits headphones and quiet rooms better.
LEVEL_TARGET_MIN, LEVEL_TARGET_MAX = -40.0, -5.0
LEVEL_TARGET_DEFAULT = -23.0

# Gain in dB for "gain" mode.
LEVEL_GAIN_MIN, LEVEL_GAIN_MAX = -30.0, 30.0


class OutputProfile:
    """One named output profile."""

    def __init__(self, name, container, *, audio="copy", audio_bitrate=AAC_AUTO,
                 aspect="source", crop_mode="none", crop=(0, 0, 0, 0),
                 video="copy", preset=DEFAULT_PRESET, crf=CRF_AUTO,
                 gop_seconds=GOP_AUTO,
                 audio_sync_ms=AUDIO_SYNC_NONE, downmix="keep",
                 level_mode="none", level_value=LEVEL_TARGET_DEFAULT,
                 output_dir="", favourite=False, enabled=True, builtin=False):
        self.name = name
        self.container = container          # "match" | "mkv" | "mp4"
        self.audio = audio                  # "copy" | "aac"
        self.audio_bitrate = audio_bitrate  # kbps, or AAC_AUTO (0) for automatic
        self.aspect = aspect                # "source" | "4:3" | "16:9"
        # Video handling.  "copy" is the lossless default (the video is copied,
        # re-encoding only where a container demands it); "hevc" deliberately
        # re-encodes to HEVC/H.265 for a smaller file (lossy and slower).
        self.video = video if video in ("copy", "hevc") else "copy"
        # Encoder speed and quality, used only when something is actually
        # re-encoded (HEVC output, or a crop).  The defaults reproduce what
        # Snipwright did before these were configurable.
        self.preset = preset if preset in ENCODER_PRESETS else DEFAULT_PRESET
        self.crf = self._clean_crf(crf)
        # Keyframe spacing for the re-encode, in seconds.  GOP_AUTO resolves
        # per codec at export time.
        self.gop_seconds = self._clean_gop(gop_seconds)
        # Cropping re-encodes the video.  "none" leaves the lossless path alone;
        # "auto" detects the black bars per file at export time; "fixed" uses the
        # pixel amounts in ``crop`` = (top, bottom, left, right).
        self.crop_mode = crop_mode if crop_mode in CROP_MODES else "none"
        self.crop = tuple(int(x) for x in crop)[:4] if crop else (0, 0, 0, 0)
        if len(self.crop) != 4:
            self.crop = (0, 0, 0, 0)
        # Audio delay in milliseconds, and whether to fold surround to stereo.
        # Both apply however the audio is handled - a delay is a timestamp
        # change, so it works even on a straight copy; a downmix necessarily
        # re-encodes the audio, and says so in the editor.
        self.audio_sync_ms = self._clean_sync(audio_sync_ms)
        self.downmix = downmix if downmix in DOWNMIX_MODES else "keep"
        # Loudness processing.  `level_value` means different things per mode -
        # a LUFS target for "normalise", a dB change for "gain" - so it is
        # clamped against whichever range applies.
        self.level_mode = level_mode if level_mode in LEVEL_MODES else "none"
        self.level_value = self._clean_level(self.level_mode, level_value)
        self.output_dir = output_dir        # per-profile default destination
        self.favourite = favourite
        self.enabled = enabled
        self.builtin = builtin

    @staticmethod
    def _clean_level(mode, value):
        """Clamp the level figure to whatever the mode means by it."""
        try:
            v = float(value)
        except (TypeError, ValueError):
            return LEVEL_TARGET_DEFAULT if mode == "normalise" else 0.0
        if mode == "normalise":
            return max(LEVEL_TARGET_MIN, min(LEVEL_TARGET_MAX, v))
        if mode == "gain":
            return max(LEVEL_GAIN_MIN, min(LEVEL_GAIN_MAX, v))
        return v

    @staticmethod
    def _clean_sync(value):
        """Clamp the audio delay, treating anything unparseable as no delay."""
        try:
            ms = int(value)
        except (TypeError, ValueError):
            return AUDIO_SYNC_NONE
        return max(AUDIO_SYNC_MIN, min(AUDIO_SYNC_MAX, ms))

    # -- display helpers for the list columns ------------------------------
    @property
    def codec_label(self):
        if self.video == "hevc":
            return QT_TRANSLATE_NOOP("ProfileEditor", "HEVC (re-encode)")
        return QT_TRANSLATE_NOOP("ProfileEditor", "Match Source")               # otherwise the video is copied

    @property
    def container_label(self):
        return _CONTAINER_LABELS.get(self.container, self.container)

    @property
    def output_mode_label(self):
        return QT_TRANSLATE_NOOP("ProfileEditor", "Smart")

    def audio_label(self):
        if self.audio == "aac":
            if self.audio_bitrate:
                return "Re-encode AAC %d kbps" % self.audio_bitrate
            return "Re-encode AAC (automatic)"
        return "Smart copy (lossless)"

    def aspect_label(self):
        return {"source": "Source", "4:3": "4:3", "16:9": "16:9"}.get(
            self.aspect, self.aspect
        )

    def crop_label(self):
        """Short description of the crop setting, for the profile list/summary."""
        if self.crop_mode == "auto":
            return "Auto-detect bars (re-encode)"
        if self.crop_mode == "fixed":
            t, b, l, r = self.crop
            parts = []
            if t:
                parts.append("T%d" % t)
            if b:
                parts.append("B%d" % b)
            if l:
                parts.append("L%d" % l)
            if r:
                parts.append("R%d" % r)
            return ("Crop " + " ".join(parts) + " (re-encode)") if parts else "None"
        return "None"

    def extension(self, source_ext):
        """The output file extension.  ``match`` keeps the source's own
        extension (e.g. .ts for Freeview recordings)."""
        if self.container == "mkv":
            return ".mkv"
        if self.container == "mp4":
            return ".mp4"
        return source_ext or ".ts"

    # -- persistence -------------------------------------------------------
    @staticmethod
    def _clean_crf(value):
        """Keep CRF within the encoder's range, or CRF_AUTO for 'pick for me'."""
        try:
            value = int(value)
        except (TypeError, ValueError):
            return CRF_AUTO
        if value == CRF_AUTO:
            return CRF_AUTO
        return max(CRF_MIN, min(CRF_MAX, value))

    @staticmethod
    def _clean_gop(value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return GOP_AUTO
        if value == GOP_AUTO:
            return GOP_AUTO
        return max(GOP_MIN, min(GOP_MAX, value))

    def effective_gop_seconds(self):
        """Keyframe spacing actually handed to the encoder, in seconds."""
        if self.gop_seconds != GOP_AUTO:
            return self.gop_seconds
        return DEFAULT_GOP_SECONDS["hevc" if self.video == "hevc" else "copy"]

    def effective_crf(self):
        """The CRF actually handed to the encoder.

        CRF_AUTO resolves per codec, because the x264 and x265 scales differ -
        HEVC needs a slightly higher number for the same visible quality.
        """
        if self.crf != CRF_AUTO:
            return self.crf
        return DEFAULT_CRF["hevc" if self.video == "hevc" else "copy"]

    def to_dict(self):
        return {
            "name": self.name,
            "container": self.container,
            "audio": self.audio,
            "audio_bitrate": self.audio_bitrate,
            "aspect": self.aspect,
            "crop_mode": self.crop_mode,
            "crop": list(self.crop),
            "video": self.video,
            "preset": self.preset,
            "crf": self.crf,
            "gop_seconds": self.gop_seconds,
            "audio_sync_ms": self.audio_sync_ms,
            "downmix": self.downmix,
            "level_mode": self.level_mode,
            "level_value": self.level_value,
            "output_dir": self.output_dir,
            "favourite": self.favourite,
            "enabled": self.enabled,
            "builtin": self.builtin,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get("name", "Profile"),
            d.get("container", "match"),
            audio=d.get("audio", "copy"),
            audio_bitrate=int(d.get("audio_bitrate", AAC_AUTO)),
            aspect=d.get("aspect", "source"),
            crop_mode=d.get("crop_mode", "none"),
            crop=d.get("crop", (0, 0, 0, 0)),
            video=d.get("video", "copy"),
            # Older profile files predate these; the defaults reproduce
            # exactly what those profiles used to do.
            preset=d.get("preset", DEFAULT_PRESET),
            crf=d.get("crf", CRF_AUTO),
            # Profiles written before this existed get the automatic value,
            # which for HEVC is a longer gap than the one second Snipwright used
            # to hard-code - so they produce smaller files at the same quality.
            gop_seconds=d.get("gop_seconds", GOP_AUTO),
            # Absent from older profiles, and the defaults are "do nothing",
            # so an existing profile behaves exactly as it always has.
            audio_sync_ms=d.get("audio_sync_ms", AUDIO_SYNC_NONE),
            downmix=d.get("downmix", "keep"),
            level_mode=d.get("level_mode", "none"),
            level_value=d.get("level_value", LEVEL_TARGET_DEFAULT),
            output_dir=d.get("output_dir", ""),
            favourite=bool(d.get("favourite", False)),
            enabled=bool(d.get("enabled", True)),
            builtin=bool(d.get("builtin", False)),
        )

    def copy(self):
        return OutputProfile.from_dict(self.to_dict())


def default_profiles():
    """The built-in profiles seeded on first use."""
    return [
        OutputProfile(QT_TRANSLATE_NOOP("ProfileEditor", "Match Source"),
                      "match", favourite=True, builtin=True),
        OutputProfile(QT_TRANSLATE_NOOP("ProfileEditor", "Matroska MKV"),
                      "mkv", favourite=True, builtin=True),
        OutputProfile("MP4", "mp4", favourite=False, builtin=True),
    ]


def load_profiles(config):
    """Return the saved profiles, seeding the built-ins on first use."""
    raw = config.get("profiles")
    if not raw:
        return default_profiles()
    out = []
    for d in raw:
        try:
            out.append(OutputProfile.from_dict(d))
        except Exception:
            continue
    return out or default_profiles()


def save_profiles(config, profiles):
    """Persist the profile list to the config."""
    config["profiles"] = [p.to_dict() for p in profiles]
    try:
        save_config(config)
    except Exception:
        # Persisting profiles should never crash the dialog.
        pass


def profile_names(config):
    """Names of the saved profiles, in list order (for a picker)."""
    return [p.name for p in load_profiles(config)]


def default_profile_name(config):
    """A sensible default profile name for a new job: a favourite if there is
    one, else the first profile, else the built-in Match Source."""
    profiles = load_profiles(config)
    for p in profiles:
        if p.favourite and p.enabled:
            return p.name
    return profiles[0].name if profiles else "Match Source"


def resolve_profile(config, name):
    """The saved profile with this ``name``.

    If it's gone (renamed or deleted since a job was queued) fall back to a
    favourite, then the first profile, then a plain Match-Source profile - so a
    queued job can always still run rather than being orphaned by a profile
    edit.
    """
    profiles = load_profiles(config)
    for p in profiles:
        if p.name == name:
            return p
    for p in profiles:
        if p.favourite and p.enabled:
            return p
    return profiles[0] if profiles else OutputProfile("Match Source", "match")
