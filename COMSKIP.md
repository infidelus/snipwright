# Building Comskip

Comskip is not part of Snipwright — it is a separate project by Erik Kaashoek,
used for automatic commercial detection. Snipwright cuts video perfectly well
without it, but two things need it: **Tools → Detect Commercials** in the editor,
and the Watcher finding adverts on its own.

Prebuilt Windows binaries exist and are usually the easiest route. This page is
for when you want to build it yourself, and exists because the upstream
instructions leave out a few things that will stop you.

**These notes describe what actually worked, on Linux Mint and on Windows 10.**
They are not a guarantee, and Comskip is not our software — if it fails in a way
this page doesn't cover, the Comskip issue tracker is the right place.

---

## Linux (Debian, Ubuntu, Mint)

Straightforward:

```bash
sudo apt install build-essential autoconf automake libtool pkg-config git \
  libavformat-dev libavcodec-dev libavutil-dev libswscale-dev \
  libargtable2-dev libsdl2-dev

git clone https://github.com/erikkaashoek/Comskip
cd Comskip
./autogen.sh
./configure
make
sudo make install
```

`make install` puts `comskip` in `/usr/local/bin`, which is on the default
`PATH` on most distributions — Snipwright will find it without being told where
it is. Stop after `make` if you would rather not install system-wide: the binary
is then just `comskip` in the build directory, and you can point Snipwright at
it under **Settings → External tools**.

If `configure` cannot find ffmpeg, your distribution's ffmpeg development
packages are either missing or too old — Comskip needs 2.4 or newer, which any
current release comfortably exceeds.

---

## Windows

The upstream README suggests building ffmpeg, argtable2 and SDL2 from source.
That is hours of work and where most people give up. MSYS2 has all three as
prebuilt packages, which skips the hardest part entirely.

MSYS2 uses `pacman`, borrowed from Arch Linux — that is expected, and the
binaries it installs are ordinary Windows ones. MinGW-w64 is a Windows compiler
toolchain, not an emulator: the `comskip.exe` you end up with runs on any
Windows machine without MSYS2 installed.

### 1. Install MSYS2

From [msys2.org](https://www.msys2.org/). Then open the **UCRT64** shell — not
the plain "MSYS" one. Each MSYS2 environment has its own package prefix and they
do not mix, so stay in the same shell throughout.

```bash
pacman -Syu
```

Close and reopen when it asks, then run it once more.

### 2. Install the toolchain and libraries

```bash
pacman -S --needed \
  mingw-w64-ucrt-x86_64-toolchain \
  mingw-w64-ucrt-x86_64-ffmpeg \
  mingw-w64-ucrt-x86_64-argtable \
  mingw-w64-ucrt-x86_64-SDL2 \
  base-devel git autoconf automake libtool pkgconf
```

Two things worth knowing:

- **`base-devel` does not include a C compiler.** The compiler is in the
  `toolchain` package above, and leaving it out gives you
  `no acceptable C compiler found in $PATH` from `configure`.
- **The package is `argtable`, not `argtable2`.** It is version 2.13, so it *is*
  argtable2 — only the package name differs. Asking for `argtable2` gives
  `target not found`.

Check everything is visible:

```bash
gcc --version
pkg-config --modversion libavcodec argtable2 sdl2
```

### 3. Build

```bash
git clone https://github.com/erikkaashoek/Comskip
cd Comskip
./autogen.sh
./configure
make
```

### 4. Patch for ffmpeg 7 and later

`make` will stop with:

```
mpeg2dec.c:1311: error: 'AVCodecContext' has no member named 'ticks_per_frame'
```

`ticks_per_frame` was deprecated in ffmpeg 6 and **removed in ffmpeg 7**, which
MSYS2 now ships. Comskip 0.83 predates that. It was always 2 for the
field-based codecs (H.264, MPEG-1/2) and 1 for everything else, so the value can
be reconstructed — but note that Comskip explicitly set it to 1 in
`stream_component_open` regardless, so a fixed 1 reproduces what the original
did.

From the Comskip directory:

```bash
cp mpeg2dec.c mpeg2dec.c.orig

python3 - <<'PATCH'
src = open("mpeg2dec.c", encoding="utf-8", errors="surrogateescape").read()

helper = '''
/* ffmpeg 7 removed AVCodecContext.ticks_per_frame. */
static int cs_ticks_per_frame = 1;
'''

marker = "#define ISSAME(T1,T2)"
assert marker in src, "anchor not found - the file has changed"
src = src.replace(marker, helper + "\n" + marker, 1)
src = src.replace("is->dec_ctx->ticks_per_frame = 1;", "cs_ticks_per_frame = 1;")
n = src.count("is->dec_ctx->ticks_per_frame")
src = src.replace("is->dec_ctx->ticks_per_frame", "cs_ticks_per_frame")
open("mpeg2dec.c", "w", encoding="utf-8", errors="surrogateescape").write(src)
print("replaced %d reads plus the assignment" % n)
PATCH

make
```

### 5. Collect the DLLs

The binary needs ffmpeg's libraries beside it, or it will not start outside the
MSYS2 shell — usually with no error message at all.

```bash
mkdir -p dist
cp comskip.exe dist/
ldd comskip.exe | grep ucrt64 | awk '{print $3}' | xargs -I{} cp {} dist/
```

Everything in `dist` is what you copy to the machine that will run it. Point
Snipwright at that `comskip.exe` under **Settings → External tools**.

---

## Known limitations

**Network paths.** Comskip does not reliably read UNC paths
(`\\server\share\...`) and fails with an error 6. Mapping the share to a drive
letter does not always help either. If your recordings live on a NAS, the
dependable answer is to work from a local copy. This is Comskip's own behaviour
and not something Snipwright can work around.

**Frame timing after the ffmpeg 7 patch** above has had light testing only. If
detected commercial boundaries look consistently wrong in a way they did not
with a prebuilt binary, that patch is the first thing to suspect.
