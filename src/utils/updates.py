"""Checking whether a newer Snipwright has been released.

Deliberately limited in scope: this asks GitHub what the latest release is and
compares it with the running version.  It does not download anything, and it
never touches the installation - Snipwright runs from a folder the user
extracted, and replacing files underneath a running Python process is a good way
to break somebody's editor mid-cut.  On Windows the files would be locked
anyway.  So the most this does is tell you there is something newer and offer to
open the releases page.

The check is off unless the user turns it on, and the interval is theirs to
choose.  Some people reasonably object to software contacting anything without
being asked, and "we only check once a day" is not an answer to that.
"""

import json
import logging
import re
import time
import urllib.error
import urllib.request

log = logging.getLogger("snipwright")

RELEASES_API = "https://api.github.com/repos/infidelus/snipwright/releases/latest"
RELEASES_PAGE = "https://github.com/infidelus/snipwright/releases"

# How often to look, in days.  "off" is the default and means never.
INTERVALS = {"off": 0, "daily": 1, "weekly": 7, "monthly": 30}
DEFAULT_INTERVAL = "off"

_TIMEOUT = 6            # seconds; a slow network must never hold up the UI


def parse_version(text):
    """'v2.1.0' or '2.1.0' -> (2, 1, 0).  Returns None if it isn't a version.

    Anything after the numbers - '2.1.0-beta', '2.1.0 (hotfix)' - is ignored for
    comparison purposes, so a pre-release tag doesn't read as newer than the
    release it precedes.
    """
    if not text:
        return None
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", str(text))
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))


def is_newer(latest, current):
    """True if `latest` is a higher version than `current`."""
    a, b = parse_version(latest), parse_version(current)
    if a is None or b is None:
        return False
    return a > b


def due(last_checked, interval):
    """Whether a check is due, given the last check time and the interval."""
    days = INTERVALS.get(interval, 0)
    if days <= 0:
        return False
    if not last_checked:
        return True
    try:
        elapsed = time.time() - float(last_checked)
    except (TypeError, ValueError):
        return True
    return elapsed >= days * 86400


def fetch_latest(url=RELEASES_API, timeout=_TIMEOUT):
    """Ask GitHub for the latest release.

    Returns (tag, page_url) or (None, None).  Every failure is a None - a
    version check is a convenience, and there is nothing useful to say to
    somebody whose network happens to be down.
    """
    try:
        # Request() itself raises on a malformed URL, so it belongs inside the
        # try - not just the fetch.
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                # GitHub asks for a User-Agent and returns 403 without one.
                "User-Agent": "Snipwright-update-check",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, ValueError, OSError, TimeoutError) as exc:
        log.debug("Update check failed: %s", exc)
        return None, None

    if not isinstance(data, dict):
        return None, None
    tag = data.get("tag_name") or data.get("name")
    page = data.get("html_url") or RELEASES_PAGE
    return (tag, page) if tag else (None, None)
