#!/usr/bin/env bash
#
# One-step setup for Snipwright on Linux: Debian/Ubuntu/Mint, Fedora, Arch
# and openSUSE, and the distributions built on them.
#
#   ./install-linux.sh
#
# It will, in order:
#   1. install the system packages Snipwright needs (Python, venv support,
#      ffmpeg, mkvmerge, and the Qt runtime libraries) with the
#      distribution's own package manager, asking for sudo only if something
#      is actually missing, and check the ffmpeg build can handle broadcast
#      video;
#   2. create a self-contained virtual environment in the project root
#      (.venv) and install the Python dependencies into it;
#   3. add "Snipwright" and "Snipwright Watcher" to your applications menu,
#      pointing at the environment's Python (via install-desktop-entries.sh);
#   4. check the installed dependencies actually import, and print the exact
#      error if they don't.
#
# Re-running it is safe: existing system packages are left alone and the venv
# is reused.  Re-run it (or just install-desktop-entries.sh) after moving the
# project to a new folder, so the menu entries pick up the new absolute paths.
#
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/.." && pwd)"                    # the src/ directory
ROOT="$(cd "$SRC/.." && pwd)"                    # the project root (holds src/)
REQ="$ROOT/requirements.txt"
VENV="$ROOT/.venv"

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }    # bold heading
info() { printf '  %s\n' "$*"; }

# --- 1. system packages ---------------------------------------------------
say "1/4  System packages"

# Which family of distribution this is, from /etc/os-release: ID names the
# distribution itself, ID_LIKE what it is built on (Mint says "ubuntu debian",
# EndeavourOS "arch", Rocky "rhel centos fedora").  Each family has its own
# package manager and its own names for the same things.
FAMILY=""
if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    OS_IDS="$(. /etc/os-release; echo "${ID:-} ${ID_LIKE:-}")"
    for id in $OS_IDS; do
        case "$id" in
            debian|ubuntu)              FAMILY=debian ;;
            fedora|rhel|centos)         FAMILY=fedora ;;
            arch)                       FAMILY=arch ;;
            opensuse*|suse|sles)        FAMILY=suse ;;
        esac
        [ -n "$FAMILY" ] && break
    done
fi
# Fall back on the package manager itself, for a distribution whose
# os-release says nothing useful.
if [ -z "$FAMILY" ]; then
    if   command -v apt-get >/dev/null 2>&1; then FAMILY=debian
    elif command -v dnf     >/dev/null 2>&1; then FAMILY=fedora
    elif command -v pacman  >/dev/null 2>&1; then FAMILY=arch
    elif command -v zypper  >/dev/null 2>&1; then FAMILY=suse
    fi
fi

SUDO=""
[ "$(id -u)" -ne 0 ] && SUDO="sudo"

# Per family: the package providing each command, the packages holding the
# Qt runtime libraries the PySide6 wheels need (libxcb-cursor in particular -
# without it Qt 6.5+ dies silently when launched from the menu), whether a
# package is installed, and how to install some.
case "$FAMILY" in
    debian)
        declare -A NEED=([python3]=python3 [ffmpeg]=ffmpeg [mkvmerge]=mkvtoolnix)
        QT_LIBS=(libxcb-cursor0 libegl1 libxkbcommon-x11-0)
        VENV_PKG=python3-venv
        have_pkg()  { dpkg -s "$1" >/dev/null 2>&1; }
        known_pkg() { apt-cache show "$1" >/dev/null 2>&1; }
        install_pkgs() {
            # A failed update (say, one stale third-party repository)
            # shouldn't abort the install - the packages we need are in the
            # main archives.
            $SUDO apt-get update || info "apt-get update reported problems; carrying on."
            $SUDO apt-get install -y "$@"
        }
        ;;
    fedora)
        # Fedora's own "ffmpeg-free" cannot decode H.264 or HEVC, which is
        # most of what Snipwright opens; the full ffmpeg is in RPM Fusion and
        # is only installed from there - see the check below.
        declare -A NEED=([python3]=python3 [ffmpeg]=ffmpeg [mkvmerge]=mkvtoolnix)
        QT_LIBS=(xcb-util-cursor mesa-libEGL libxkbcommon-x11)
        VENV_PKG=""                     # venv is part of Fedora's python3
        have_pkg()  { rpm -q "$1" >/dev/null 2>&1; }
        known_pkg() { dnf -q list --available "$1" >/dev/null 2>&1 || have_pkg "$1"; }
        install_pkgs() { $SUDO dnf install -y "$@"; }
        ;;
    arch)
        declare -A NEED=([python3]=python [ffmpeg]=ffmpeg [mkvmerge]=mkvtoolnix-cli)
        QT_LIBS=(xcb-util-cursor libglvnd libxkbcommon-x11)
        VENV_PKG=""                     # venv is part of Arch's python
        have_pkg()  { pacman -Qi "$1" >/dev/null 2>&1; }
        known_pkg() { pacman -Si "$1" >/dev/null 2>&1 || have_pkg "$1"; }
        install_pkgs() { $SUDO pacman -S --needed --noconfirm "$@"; }
        ;;
    suse)
        # As on Fedora, openSUSE's own ffmpeg lacks H.264/HEVC; the full one
        # comes from the Packman repository - see the check below.
        declare -A NEED=([python3]=python3 [ffmpeg]=ffmpeg [mkvmerge]=mkvtoolnix)
        # libgthread is a package of its own on openSUSE (everywhere else it
        # comes with glib), and Qt's core library cannot load without it:
        # "ImportError: libgthread-2.0.so.0" on Tumbleweed (2026-10-24).
        QT_LIBS=(libxcb-cursor0 Mesa-libEGL1 libxkbcommon-x11-0 libgthread-2_0-0)
        VENV_PKG=""                     # venv is part of openSUSE's python3
        have_pkg()  { rpm -q "$1" >/dev/null 2>&1; }
        known_pkg() { zypper --non-interactive -q info "$1" 2>/dev/null | grep -q "^Name"; }
        install_pkgs() { $SUDO zypper --non-interactive install "$@"; }
        ;;
esac

if [ -z "$FAMILY" ]; then
    info "This distribution was not recognised (Debian/Ubuntu/Mint, Fedora,"
    info "Arch and openSUSE are).  Install these yourself, then re-run to"
    info "finish the setup: Python 3.12-3.14 with venv support, ffmpeg (a"
    info "build that decodes H.264, HEVC and MPEG-2), mkvtoolnix, and the Qt"
    info "xcb-cursor, EGL and xkbcommon-x11 libraries."
else
    info "Distribution family: $FAMILY"
    missing=()
    for cmd in "${!NEED[@]}"; do
        command -v "$cmd" >/dev/null 2>&1 || missing+=("${NEED[$cmd]}")
    done
    # venv support isn't a command; probe the module on the system Python.
    if [ -n "$VENV_PKG" ] && ! python3 -c "import venv, ensurepip" >/dev/null 2>&1; then
        missing+=("$VENV_PKG")
    fi
    for pkg in "${QT_LIBS[@]}"; do
        if ! have_pkg "$pkg" && known_pkg "$pkg"; then
            missing+=("$pkg")
        fi
    done

    if [ "${#missing[@]}" -eq 0 ]; then
        info "All present (python3, venv, ffmpeg, mkvmerge, Qt libraries)."
    else
        # De-duplicate.
        mapfile -t missing < <(printf '%s\n' "${missing[@]}" | sort -u)
        info "Installing: ${missing[*]}"
        install_pkgs "${missing[@]}"
    fi
fi

# The ffmpeg program has to read what Snipwright opens and write what it
# saves: decode H.264, HEVC and MPEG-2, encode H.264, HEVC and AAC.  Fedora
# and openSUSE ship builds without the first two, which would install and
# then fail on most recordings - so check the build rather than the package.
if command -v ffmpeg >/dev/null 2>&1; then
    lacking=()
    decoders="$(ffmpeg -hide_banner -decoders 2>/dev/null || true)"
    encoders="$(ffmpeg -hide_banner -encoders 2>/dev/null || true)"
    for c in h264 hevc mpeg2video; do
        grep -qE "^ [A-Z.]{6} $c( |$)" <<<"$decoders" || lacking+=("$c decoding")
    done
    for c in libx264 libx265 aac; do
        grep -qE "^ [A-Z.]{6} $c( |$)" <<<"$encoders" || lacking+=("$c encoding")
    done
    if [ "${#lacking[@]}" -gt 0 ]; then
        info ""
        info "WARNING: this ffmpeg cannot do: $(IFS=,; echo "${lacking[*]}" | sed 's/,/, /g')."
        case "$FAMILY" in
            fedora)
                info "Fedora's own ffmpeg leaves these out.  Enable RPM Fusion"
                info "(https://rpmfusion.org/Configuration), then run:"
                info "  sudo dnf swap ffmpeg-free ffmpeg --allowerasing"
                ;;
            suse)
                info "openSUSE's own ffmpeg leaves these out.  Add the Packman"
                info "repository (https://en.opensuse.org/Additional_package_repositories#Packman),"
                info "then run:  sudo zypper dup --from packman --allow-vendor-change"
                ;;
            *)
                info "Install a full ffmpeg build from your distribution."
                ;;
        esac
        info "Snipwright will start without it, but most recordings will not"
        info "open or save correctly until it is replaced."
    fi
fi

# --- 2. virtual environment + Python dependencies -------------------------
say "2/4  Virtual environment"

# Snipwright needs Python 3.12, 3.13 or 3.14 - the range the locked versions
# in requirements.txt are built for.  Linux Mint 22's system Python is 3.12.
# Prefer an explicit python3.12 (then 3.13, 3.14) if present, so the venv is
# built on a suitable one even where the default python3 is something else;
# fall back to python3 otherwise, and check it below.
BUILD_PY="$(command -v python3.12 || command -v python3.13 || command -v python3.14 \
            || command -v python3 || true)"
if [ -z "$BUILD_PY" ]; then
    info "No python3 found on PATH - install Python 3.12 and re-run."
    exit 1
fi
PY_VER="$("$BUILD_PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"

if [ ! -x "$VENV/bin/python" ]; then
    info "Creating $VENV on Python $PY_VER…"
    "$BUILD_PY" -m venv "$VENV"
else
    have="$("$VENV/bin/python" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    info "Reusing existing $VENV (Python $have)."
    if [ "$have" != "$PY_VER" ]; then
        info "(To rebuild it on Python $PY_VER instead: rm -rf \"$VENV\" and re-run.)"
    fi
fi

PY="$VENV/bin/python"

# Check the environment's Python is one the locked versions support.  Without
# this, an older system (Linux Mint 21 has Python 3.10) fails part-way through
# with a pip error about "no matching distribution", which says nothing useful.
VENV_VER="$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
case "$VENV_VER" in
    3.12|3.13|3.14) ;;
    *)
        info "Snipwright needs Python 3.12, 3.13 or 3.14, but this environment"
        info "uses Python $VENV_VER."
        case "$PY_VER" in
            3.12|3.13|3.14)
                # The system has a suitable Python; the environment is just old.
                info "It was made earlier on another Python.  Remove it and re-run,"
                info "and it will be rebuilt on Python $PY_VER:"
                ;;
            *)
                info "Install a supported Python first (Linux Mint 22 and later"
                info "include 3.12), then remove the environment and re-run:"
                ;;
        esac
        info "    rm -rf \"$VENV\""
        exit 1
        ;;
esac

info "Installing the Python dependencies into the environment…"
"$PY" -m pip install --upgrade pip

# The known package set, used if requirements.txt is missing.  Held to the
# versions Snipwright is tested with, exactly as in requirements.txt (which
# explains each range) - keep the two in step.  PyAV 19.0.0 broke every
# export on a fresh install the day after it was published, because nothing
# stopped pip taking it.
KNOWN_DEPS=("PySide6>=6.11.2,<6.12" "av>=18.1.0,!=19.0.0,<20" "numpy>=2.5.3,<2.6"
            "bitstring==4.4.0" "bitarray>=3.11.0,!=3.12.0,!=3.12.1,<4" "tibs==0.5.7" "tqdm>=4.70.1,<5")

# Install the dependencies.  Prefer requirements.txt, fall back to the known
# set.  We do NOT hide pip's output or let a failure pass silently - a partial
# install (an interrupted download of the large PySide6 wheels, say) is exactly
# what leaves a venv that looks present but can't import PySide6.
install_deps() {
    if [ -f "$REQ" ]; then
        "$PY" -m pip install -r "$REQ"
    else
        info "requirements.txt not found at $REQ - installing the known set instead."
        "$PY" -m pip install "${KNOWN_DEPS[@]}"
    fi
}
install_deps

# Verify the dependencies actually import.  A reused venv from a previously
# interrupted install can have some packages but not others, and pip won't
# reinstall what it thinks is already there - so if the import check fails,
# force a clean reinstall before giving up.
if ! "$PY" -c 'import PySide6, av, numpy, bitstring, tqdm' >/dev/null 2>&1; then
    info "Some dependencies are missing or incomplete - reinstalling them cleanly…"
    if [ -f "$REQ" ]; then
        "$PY" -m pip install --force-reinstall --no-cache-dir -r "$REQ"
    else
        "$PY" -m pip install --force-reinstall --no-cache-dir "${KNOWN_DEPS[@]}"
    fi
fi

# --- 3. menu entries ------------------------------------------------------
say "3/4  Application menu entries"
bash "$HERE/install-desktop-entries.sh" "$PY"

# --- 4. verification --------------------------------------------------------
say "4/4  Checking the installation"
# The Qt modules themselves, not just the PySide6 package: importing the
# package loads none of Qt's libraries, so an openSUSE install passed this
# check and then could not start, from the menu or a terminal, because Qt
# needed a system library that was not there (2026-10-24).
if err="$("$PY" -c 'import PySide6, av, numpy, bitstring, tqdm
from PySide6 import QtCore, QtGui, QtWidgets' 2>&1)"; then
    info "All Python dependencies import cleanly."
else
    info "A dependency didn't install correctly:"
    printf '%s\n' "$err" | sed 's/^/    /'
    info "Try re-running this script; if it still fails, please report the"
    info "text above at https://github.com/infidelus/snipwright/issues"
    exit 1
fi

# The system libraries Qt's own libraries and its X11 plugin link against.
# PySide6 brings Qt but not these, and which ones a distribution installs by
# default varies; one missing makes Snipwright fail to start with nothing
# on screen when launched from the menu.  ldd names each one that is absent.
qt_files="$(find "$VENV" \( -path '*/PySide6/Qt/lib/libQt6Core.so*' \
    -o -path '*/PySide6/Qt/lib/libQt6Gui.so*' \
    -o -path '*/PySide6/Qt/lib/libQt6Widgets.so*' \
    -o -path '*/PySide6/Qt/lib/libQt6Multimedia.so*' \
    -o -path '*/PySide6/Qt/plugins/platforms/libqxcb.so' \) 2>/dev/null)"
if [ -n "$qt_files" ] && command -v ldd >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    lost="$(ldd $qt_files 2>/dev/null | awk '/not found/ {print $1}' | sort -u)"
    if [ -n "$lost" ]; then
        info ""
        info "WARNING: Qt needs these system libraries, which are not installed:"
        printf '%s\n' "$lost" | sed 's/^/    /'
        case "$FAMILY" in
            debian) info "Find the package for each with:  apt-file search <name>" ;;
            fedora) info "Install each with:  sudo dnf install '<name>()(64bit)'" ;;
            arch)   info "Find the package for each with:  pacman -F <name>" ;;
            suse)   info "Install each with:  sudo zypper install '<name>()(64bit)'" ;;
        esac
        info "Snipwright will not start until they are."
    fi
fi

say "Done."
info "Launch Snipwright from your applications menu, or run it directly with:"
info "  $PY $SRC/main.py"
info "The Watcher is \"Snipwright Watcher\" in the menu, or:"
info "  $PY $SRC/watcher.py"
info "If the menu entry ever fails to launch, run the command above in a"
info "terminal - the error it prints says what's wrong."
