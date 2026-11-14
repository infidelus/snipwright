"""Media utilities and enums for Smart Media Cutter.

This module contains all media-related enums, codec compatibility helpers,
and low-level media knowledge. All media format details should be centralized here.
"""

from enum import Enum


class VideoExportMode(Enum):
    """Video export modes."""
    SMARTCUT = 1    # Recode only around cutpoints (fast and accurate)
    KEYFRAMES = 2   # Cut on keyframes (inaccurate timing, lossless, very fast)
    RECODE = 3      # Recode the whole video (slow)


class VideoExportQuality(Enum):
    """Video quality presets."""
    LOW = 1                    # "Low"
    NORMAL = 2                 # "Normal"
    HIGH = 3                   # "High"
    INDISTINGUISHABLE = 4      # "Almost indistinguishable (Large file size)"
    NEAR_LOSSLESS = 5          # "Near lossless (Huge file size)"
    LOSSLESS = 6               # "Lossless (Extremely large file size)"


def get_crf_for_quality(quality: VideoExportQuality) -> int:
    """Get CRF value for the selected quality preset.

    Args:
        quality: Video quality enum value

    Returns:
        CRF value (lower = higher quality)
    """
    crf_map = {
        VideoExportQuality.LOW: 23,
        VideoExportQuality.NORMAL: 18,
        VideoExportQuality.HIGH: 14,
        VideoExportQuality.INDISTINGUISHABLE: 8,
        VideoExportQuality.NEAR_LOSSLESS: 3,
        VideoExportQuality.LOSSLESS: 0
    }
    return crf_map.get(quality, 18)


# --- Validation helpers centralizing media rules ---
