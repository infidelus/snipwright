# Installing Snipwright

Two one-step installers set everything up (dependencies, a virtual environment,
and menu/desktop shortcuts).  Run the one for your platform.

## Linux (Debian / Ubuntu / Mint, Fedora, Arch, openSUSE)

```sh
cd src/packaging
chmod +x install-linux.sh          # first time only
./install-linux.sh
```

It works out which family your distribution belongs to and installs the
system packages Snipwright needs (Python with venv support, ffmpeg, mkvmerge
and the Qt runtime libraries) with its own package manager — apt, dnf, pacman
or zypper — asking for sudo only if something's missing. It then checks the
ffmpeg it found can decode H.264, HEVC and MPEG-2 and encode H.264, HEVC and
AAC: Fedora's and openSUSE's own ffmpeg cannot, and the installer says how to
get the full one (from RPM Fusion or Packman). Next it creates a virtual
environment in the project root (`.venv`) on Python 3.12, 3.13 or 3.14,
installs the Python dependencies into it, adds
**Snipwright** and **Snipwright Watcher** to your applications menu pointing at
that environment, and finally checks the installation imports cleanly —
including that every system library Qt links against is present, naming any
that is not.
Re-running it is safe (the venv is reused), and re-running it (or just
`install-desktop-entries.sh`) after moving the project updates the menu
entries' absolute paths.

The Qt runtime libraries matter on a fresh install: without `libxcb-cursor0`
(required by Qt 6.5+) the application starts and then dies without a window,
which is easy to mistake for a broken install — and on openSUSE Qt also needs
`libgthread-2_0-0`, which is a package of its own there.

Tested on Linux Mint, Fedora, EndeavourOS (Arch) and openSUSE Tumbleweed. Any
distribution built on one of those is recognised as that family. On one that
isn't (Gentoo, Void or Alpine, say), the installer can't fetch the system
packages: install Python, ffmpeg, mkvtoolnix and the Qt/`xcb` runtime
libraries with your own package manager first, and it does the rest.

## Windows 10 / 11

Right-click `install-windows.ps1` and choose **Run with PowerShell**, or:

```powershell
powershell -ExecutionPolicy Bypass -File src\packaging\install-windows.ps1
```

It uses **winget** to install Python, ffmpeg and mkvmerge if they're missing,
creates the `.venv`, installs the Python dependencies, and makes a Start-menu
and Desktop shortcut (using the app icon) that launches without a console
window.  If ffmpeg/mkvmerge were just installed, a sign-out/in may be needed
before Snipwright detects them (see **Settings → External tools**).

At the end it **offers** - only offers; the answer is No unless you say
otherwise - to exclude Snipwright's own Python folder (`.venv`) from Windows
Defender. Defender checks every file Snipwright loads the first time it starts
after a reboot: in testing that first start took about 9 seconds, and about
5.5 with the exclusion. Later starts take about a second either way. The
trade-off is that Defender stops scanning that folder altogether. Only the
installer (through pip) puts files there, so the risk is small, but it is your
choice. It needs administrator permission, so Windows will ask; if your
antivirus is managed by an organisation it may not be allowed, and Snipwright
works the same either way. To undo it, run `Remove-MpPreference -ExclusionPath`
with the folder's path in PowerShell as administrator.

> The Windows installer has had basic testing — it installs the dependencies and
> the application launches and runs. Functionality beyond that hasn't been
> exercised much on Windows yet.

## Menu entries only (Linux)

`install-desktop-entries.sh` is the menu-integration step on its own — handy if
you manage the Python environment yourself.  `install-linux.sh` calls it for
you with the venv's interpreter.

```sh
./install-desktop-entries.sh                       # uses python3 from PATH
./install-desktop-entries.sh ../../.venv/bin/python   # or pin the venv's Python
```

It writes two `.desktop` files into `~/.local/share/applications/` with
absolute paths resolved from this checkout, so re-run it if you move the
project.  It also registers the editor as a handler for `.ts` and `.mkv`.
To remove them again, use the uninstaller below.

## Uninstalling

Each platform has an uninstaller beside its installer, which removes what the
installer set up and what Snipwright creates while it runs.

```sh
bash src/packaging/uninstall-linux.sh
```

On Windows, double-click `src\packaging\uninstall-windows.bat`.

It removes the menu entries or shortcuts, Snipwright's `.vprj` and `.swproj`
file types (on Windows only Snipwright's own entries - VideoReDo's are left
alone), the Watcher's start-on-login entry, Snipwright's cache and temporary
scratch files, and the project's `.venv`. On Windows it also offers to remove
the Defender exclusion, if one was added, and Windows asks for permission.

It **asks** before deleting two things:

- **Quick Stream Fix working copies** - temporary repaired copies of
  recordings, often several gigabytes each, which it lists first.
- **Your settings** - settings, output profiles, learned channel logos and
  break idents, the batch queue and the Watcher's settings, in
  `~/.config/snipwright`. Keep them if you might reinstall: Snipwright picks
  them up again, so it doesn't have to relearn your channels.

Every question comes before anything is removed, and it refuses to start while
Snipwright or its Watcher is running. It never touches recordings, exported
videos, project files or logs - log files kept in the settings folder stay even
if you delete your settings - and it leaves FFmpeg, MKVToolNix and Python
installed, since other software may use them.

If you have more than one copy of Snipwright, the menu entries, file types and
start-on-login entry belong to whichever copy installed them last. The
uninstaller leaves them alone if they point at a different copy, so removing an
old copy can't break the one you use.

It can't delete the folder it runs from, so the last step is yours: delete the
Snipwright folder once it has finished. It tells you which.

## Icons

`src/assets/app_icon.svg` is the master icon; `app_icon.ico` (multi-resolution,
16–256 px) is generated from it for Windows shortcuts, and `app_icon_256.png`
is a handy raster copy.  Autostarting the **Watcher** on login is handled from
the Watcher's own settings.
