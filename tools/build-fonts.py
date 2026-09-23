#!/usr/bin/env -S uv run --quiet --with fonttools --with brotli python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools>=4.50", "brotli"]
# ///
"""Regenerate the inlined ``@font-face`` block inside ``typora-vitepress.css``.

The theme ships two SIL OFL 1.1 fonts so that Typora renders identically on
machines where neither is installed.  Both are embedded as base64 WOFF2 data
URIs -- Typora is Electron/Chromium, so a data URI is treated exactly like a
remote font file and the theme stays a single self-contained CSS file.

Fonts
-----
Ioskeley Mono (Latin)   official ``IoskeleyMono-Web`` WOFF2 build, 4 faces.
Sarasa Mono J  (CJK)    subset of the official release TTF, 2 faces.

Sarasa Gothic is a ~26 MB-per-face CJK font (the glyphs are the payload), so
the full face cannot be embedded -- 4 faces would be ~37 MB of WOFF2 and
~50 MB of base64.  The script therefore subsets it to the characters a
Chinese/Japanese note is actually written in (see ``CJK_EXTRA_RANGES``) and
lets anything rarer fall through to the next font in the CSS stack.

Usage
-----
    uv run tools/build-fonts.py            # regenerate typora-vitepress.css
    uv run tools/build-fonts.py --check    # fail if the block is stale

Downloads are cached in ``tools/.cache/`` (git-ignored).
"""

from __future__ import annotations

import argparse
import base64
import io
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

# --- paths -----------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CSS_FILE = ROOT / "typora-vitepress.css"
CACHE = Path(__file__).resolve().parent / ".cache"

BEGIN_MARK = "/* ===== BEGIN INLINED FONTS"
END_MARK = "/* ===== END INLINED FONTS ===== */"

# --- sources ---------------------------------------------------------------

IOSKELEY_URL = (
    "https://github.com/ahatem/IoskeleyMono/releases/download/v2.1.0/"
    "IoskeleyMono-Web.zip"
)
SARASA_URL = (
    "https://github.com/be5invis/Sarasa-Gothic/releases/download/v1.0.41/"
    "SarasaMonoJ-TTF-1.0.41.7z"
)

# (internal family, css family, weight, style, member-in-download)
IOSKELEY_FACES = [
    ("IoskeleyMono-Regular.woff2", 400, "normal"),
    ("IoskeleyMono-Bold.woff2", 700, "normal"),
    ("IoskeleyMono-Italic.woff2", 400, "italic"),
    ("IoskeleyMono-BoldItalic.woff2", 700, "italic"),
]
SARASA_FACES = [
    ("SarasaMonoJ-Regular.ttf", 400),
    ("SarasaMonoJ-Bold.ttf", 700),
]

# --- CJK coverage ----------------------------------------------------------

# Everything encodable in GB2312: the 6763 simplified hanzi of the two
# national standard levels plus its own kana / Greek / Cyrillic / box-drawing.
# That is the "common Chinese" line; traditional-only and rare kanji are not
# covered and fall back to the system CJK font.
CJK_EXTRA_RANGES = [
    (0x2000, 0x206F),  # general punctuation
    (0x2070, 0x209F),  # super/subscripts
    (0x20A0, 0x20CF),  # currency
    (0x2100, 0x214F),  # letterlike symbols
    (0x2190, 0x21FF),  # arrows
    (0x2200, 0x22FF),  # mathematical operators
    (0x2300, 0x23FF),  # misc technical (incl. control pictures)
    (0x2460, 0x24FF),  # enclosed alphanumerics
    (0x2500, 0x257F),  # box drawing
    (0x2580, 0x259F),  # block elements
    (0x25A0, 0x25FF),  # geometric shapes
    (0x2600, 0x26FF),  # misc symbols
    (0x2700, 0x27BF),  # dingbats
    (0x2900, 0x2AFF),  # supplemental arrows / math
    (0x2B00, 0x2BFF),  # misc symbols and arrows
    (0x3000, 0x303F),  # CJK symbols and punctuation
    (0x3040, 0x309F),  # hiragana
    (0x30A0, 0x30FF),  # katakana
    (0x31F0, 0x31FF),  # katakana phonetic extensions
    (0xFE10, 0xFE1F),  # vertical forms
    (0xFE30, 0xFE4F),  # CJK compatibility forms
    (0xFF00, 0xFFEF),  # halfwidth and fullwidth forms
]


def log(msg: str) -> None:
    print(f"  {msg}", flush=True)


# --- download helpers ------------------------------------------------------


def download(url: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / url.rsplit("/", 1)[-1]
    if dest.exists():
        log(f"cached  {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest
    log(f"fetch   {dest.name}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as resp, tmp.open("wb") as out:
        shutil.copyfileobj(resp, out, length=1 << 20)
    tmp.rename(dest)
    log(f"saved   {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def fetch_ioskeley() -> list[tuple[str, int, str, bytes]]:
    archive = download(IOSKELEY_URL)
    faces = []
    with zipfile.ZipFile(archive) as zf:
        for member, weight, style in IOSKELEY_FACES:
            name = next(n for n in zf.namelist() if n.endswith("/" + member))
            faces.append((member, weight, style, zf.read(name)))
    return faces


def cjk_codepoints() -> list[int]:
    chars: set[str] = set()
    for hi in range(0xA1, 0xFF):
        for lo in range(0xA1, 0xFF):
            try:
                chars.add(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    for start, end in CJK_EXTRA_RANGES:
        chars.update(chr(cp) for cp in range(start, end + 1))
    return sorted({ord(c) for c in chars})


def extract_7z(archive: Path, members: list[str]) -> dict[str, Path]:
    outdir = CACHE / (archive.stem + ".extracted")
    missing = [m for m in members if not (outdir / m).exists()]
    if missing:
        sevenzip = shutil.which("7zz") or shutil.which("7z") or shutil.which("7za")
        if not sevenzip:
            sys.exit("7z is required to unpack Sarasa Gothic (brew install sevenzip)")
        log(f"unpack  {archive.name} -> {', '.join(missing)}")
        outdir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sevenzip, "x", "-y", f"-o{outdir}", str(archive), *missing],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    return {m: outdir / m for m in members}


def fetch_sarasa() -> list[tuple[str, int, bytes]]:
    archive = download(SARASA_URL)
    paths = extract_7z(archive, [name for name, _ in SARASA_FACES])
    codepoints = cjk_codepoints()
    log(f"subset  Sarasa Mono J -> {len(codepoints)} codepoints")

    options = subset.Options()
    options.layout_features = ["*"]  # keep ccmp / vert / palt / ... in CJK runs
    options.drop_tables += ["DSIG"]
    options.recalc_timestamp = False

    faces = []
    for name, weight in SARASA_FACES:
        font = TTFont(paths[name])
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=codepoints)
        subsetter.subset(font)
        # ``Options.recalc_timestamp`` only applies to the ``pyftsubset`` CLI;
        # a direct ``save()`` looks at this attribute instead.  Without it
        # ``head.modified`` becomes "now", which changes the head checksum and
        # cascades into a completely different (and unstable) Brotli stream.
        font.recalcTimestamp = False
        font.flavor = "woff2"
        buf = io.BytesIO()
        font.save(buf)
        faces.append((name, weight, buf.getvalue()))
        log(f"        {name}: {len(buf.getvalue()) / 1e6:.2f} MB WOFF2")
    return faces


# --- CSS emission ----------------------------------------------------------


def font_face(css_family: str, weight: int, style: str, data: bytes) -> str:
    b64 = base64.b64encode(data).decode("ascii")
    return (
        "@font-face {\n"
        f"  font-family: '{css_family}';\n"
        f"  font-style: {style};\n"
        f"  font-weight: {weight};\n"
        f"  font-display: swap;\n"
        f"  src: url(data:font/woff2;base64,{b64}) format('woff2');\n"
        "}"
    )


def build_block() -> str:
    print("Ioskeley Mono  (SIL OFL 1.1, (c) 2025 Ahmed Hatem)")
    ioskeley = fetch_ioskeley()
    print("Sarasa Mono J  (SIL OFL 1.1, (c) 2015-2025 Renzhi Li)")
    sarasa = fetch_sarasa()

    faces = [
        font_face("Ioskeley Mono", weight, style, data)
        for _, weight, style, data in ioskeley
    ]
    faces += [
        # Only the upright faces are embedded: italic CJK is rare, and
        # Chromium synthesises an oblique from the regular face anyway.
        font_face("Sarasa Mono J", weight, "normal", data)
        for _, weight, data in sarasa
    ]

    total = sum(len(d) for *_, d in ioskeley) + sum(len(d) for _, _, d in sarasa)
    header = (
        f"{BEGIN_MARK} =========================================================\n"
        " * Generated by tools/build-fonts.py -- do not edit by hand.\n"
        " *\n"
        " * Ioskeley Mono  (Latin)   SIL OFL 1.1, (c) 2025 Ahmed Hatem\n"
        " * Sarasa Mono J  (CJK)     SIL OFL 1.1, (c) 2015-2025 Renzhi Li\n"
        " *                          subset: GB2312 + kana + CJK punctuation +\n"
        " *                          fullwidth forms + common code symbols.\n"
        " *                          Rare / traditional-only hanzi fall back to\n"
        " *                          the next font in the stack.\n"
        " *\n"
        " * Full licence texts: licenses/\n"
        f" * Embedded payload: {total / 1e6:.2f} MB WOFF2 "
        f"(~{total * 4 / 3 / 1e6:.2f} MB base64)\n"
        " * ======================================================================== */"
    )
    return header + "\n\n" + "\n\n".join(faces) + "\n\n" + END_MARK + "\n"


def splice(css: str, block: str) -> str:
    start = css.find(BEGIN_MARK)
    if start != -1:
        end = css.index(END_MARK, start) + len(END_MARK)
        return css[:start] + block.rstrip("\n") + css[end:]
    # First run: insert right after the leading banner comment.  ``rstrip``
    # here keeps this branch byte-identical to the replace branch above, so a
    # later regeneration is a no-op.
    banner_end = css.index("*/") + 2
    return css[:banner_end] + "\n\n" + block.rstrip("\n") + css[banner_end:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if typora-vitepress.css is out of date",
    )
    args = parser.parse_args()

    original = CSS_FILE.read_text()
    updated = splice(original, build_block())

    if args.check:
        if original != updated:
            sys.exit("typora-vitepress.css is stale -- run: uv run tools/build-fonts.py")
        print("typora-vitepress.css is up to date")
        return

    CSS_FILE.write_text(updated)
    log(f"wrote   {CSS_FILE.name} ({len(updated) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
