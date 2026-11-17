#!/usr/bin/env python3
"""Asset inventory scan (standard library only).

Lists image / font / document files under the given asset directories, reads format and
pixel size, hashes each file to find duplicates, and finds where each file is referenced
(markup, stylesheets, scripts). Also extracts every CSS url(...) and data: URI with
path:line, and reports colours used inside SVG files (fill / stroke / stop-color).

Usage:
  python -I asset_scan.py --root <web-root> --out <assets.json>
         --assets <rel-dir> [<rel-dir> ...]
         --refs <rel-dir> [<rel-dir> ...]
         [--css <rel-dir-or-file> ...] [--ref-ext .<ext> ...] [--exclude <dir-name> ...]
  python -I asset_scan.py --selftest

Reference files default to .vue .html .htm .css .js .json; add server template or
source extensions with --ref-ext. Small PNGs (<= 40000 px, 8-bit, non-interlaced) also get
their top opaque colours, to tell whether a raster icon is single-colour and which colour.

Classification (brand / UI icon / hero / campaign) is a human judgement and is not done here.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import zlib
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp",
             ".ttf", ".otf", ".woff", ".woff2", ".eot", ".pdf", ".mp4"}
REF_EXT = {".vue", ".html", ".htm", ".css", ".js", ".json"}
DEFAULT_EXCLUDE = {"node_modules", "dist", "build", ".git"}

RE_URL = re.compile(r'url\(\s*([\'"]?)(.*?)\1\s*\)', re.I)
RE_SVG_COLOR = re.compile(r'(?:fill|stroke|stop-color)\s*[:=]\s*["\']?\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|[a-zA-Z]+)', re.I)


def png_size(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR":
        return struct.unpack(">II", b[16:24])
    return None


def png_colors(b, max_pixels=250000, top=3):
    """Top opaque colours of a small 8-bit non-interlaced PNG (types 2, 3, 6).

    Returns None when the PNG variant is not supported. Pixels with alpha
    below 128 are ignored; near colours are bucketed (8 levels per channel) to
    merge anti-aliasing noise, and each bucket reports its most frequent exact
    colour.
    """
    if png_size(b) is None:
        return None
    pos, idat, plte, trns = 8, b"", None, None
    w = h = depth = ctype = interlace = None
    while pos < len(b):
        ln = struct.unpack(">I", b[pos:pos + 4])[0]
        typ = b[pos + 4:pos + 8]
        data = b[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", data)
        elif typ == b"PLTE":
            plte = data
        elif typ == b"tRNS":
            trns = data
        elif typ == b"IDAT":
            idat += data
        elif typ == b"IEND":
            break
        pos += 12 + ln
    if depth != 8 or interlace or ctype not in (2, 3, 6) or w * h > max_pixels:
        return None
    bpp = {2: 3, 3: 1, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride = w * bpp
    prev = bytearray(stride)
    counts = defaultdict(int)
    exact = defaultdict(lambda: defaultdict(int))
    i = 0
    for _ in range(h):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            up = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + up) & 255
            elif f == 3:
                line[x] = (line[x] + ((a + up) >> 1)) & 255
            elif f == 4:
                p = a + up - c
                pa, pb, pc = abs(p - a), abs(p - up), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (up if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        prev = line
        for x in range(w):
            if ctype == 6:
                r, g, bl, al = line[x * 4:x * 4 + 4]
            elif ctype == 2:
                r, g, bl = line[x * 3:x * 3 + 3]
                al = 255
            else:
                k = line[x]
                r, g, bl = plte[k * 3:k * 3 + 3]
                al = trns[k] if trns and k < len(trns) else 255
            if al < 128:
                continue
            key = (r // 8, g // 8, bl // 8)
            counts[key] += 1
            exact[key]["#%02x%02x%02x" % (r, g, bl)] += 1
    total = sum(counts.values()) or 1
    out = []
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1])[:top]:
        modal = max(exact[k].items(), key=lambda kv: kv[1])[0]
        out.append({"color": modal, "share": round(v / total, 3)})
    return out


def gif_size(b):
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", b[6:10])
    return None


def jpg_size(b):
    if b[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(b) - 9:
        if b[i] != 0xFF:
            i += 1
            continue
        marker = b[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return (w, h)
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg = struct.unpack(">H", b[i + 2:i + 4])[0]
        i += 2 + seg
    return None


def ico_size(b):
    if b[:4] == b"\x00\x00\x01\x00":
        n = struct.unpack("<H", b[4:6])[0]
        sizes = []
        for k in range(n):
            w, h = b[6 + 16 * k], b[7 + 16 * k]
            sizes.append(f"{w or 256}x{h or 256}")
        return sizes
    return None


def webp_size(b):
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        if b[12:16] == b"VP8X":
            w = int.from_bytes(b[24:27], "little") + 1
            h = int.from_bytes(b[27:30], "little") + 1
            return (w, h)
        if b[12:16] == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return (w & 0x3FFF, h & 0x3FFF)
    return None


def svg_info(text):
    w = re.search(r'<svg[^>]*\swidth\s*=\s*["\']([^"\']+)', text)
    h = re.search(r'<svg[^>]*\sheight\s*=\s*["\']([^"\']+)', text)
    vb = re.search(r'viewBox\s*=\s*["\']([^"\']+)', text)
    colors = sorted({c.lower() for c in RE_SVG_COLOR.findall(text)} - {"none"})
    return {"width": w.group(1) if w else None, "height": h.group(1) if h else None,
            "viewBox": vb.group(1) if vb else None, "colors": colors,
            "glyphs": len(re.findall(r'<glyph\b', text))}


def measure(path, ext):
    with open(path, "rb") as f:
        b = f.read()
    info = {"bytes": len(b), "md5": hashlib.md5(b).hexdigest()}
    size = None
    if ext == ".png":
        size = png_size(b)
        if size and size[0] * size[1] <= 40000:
            try:
                info["png_colors"] = png_colors(b)
            except (ValueError, IndexError, TypeError, struct.error):
                info["png_colors"] = None
    elif ext == ".gif":
        size = gif_size(b)
    elif ext in (".jpg", ".jpeg"):
        size = jpg_size(b)
    elif ext == ".webp":
        size = webp_size(b)
    elif ext == ".ico":
        info["ico_sizes"] = ico_size(b)
    elif ext == ".svg":
        info["svg"] = svg_info(b.decode("utf-8", errors="replace"))
    if size:
        info["width"], info["height"] = size
    # header sniff to catch extension / content mismatch
    sniff = None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        sniff = "png"
    elif b[:3] == b"GIF":
        sniff = "gif"
    elif b[:2] == b"\xff\xd8":
        sniff = "jpg"
    elif b[:4] == b"%PDF":
        sniff = "pdf"
    info["sniff"] = sniff
    return info


def walk(root, rels, exts, exclude):
    for rel in rels:
        base = os.path.join(root, rel)
        if os.path.isfile(base):
            yield base
            continue
        for dp, dns, fns in os.walk(base):
            dns[:] = sorted(d for d in dns if d not in exclude)
            for fn in sorted(fns):
                if os.path.splitext(fn)[1].lower() in exts:
                    yield os.path.join(dp, fn)




def ref_pattern(name):
    """File name matched on path boundaries: `logo.png` matches `img/logo.png` and `"logo.png?v=2"`
    but not `mylogo.png` or `logo.png.bak`."""
    return re.compile(r"(?<![\w.-])%s(?!\.?[\w-])" % re.escape(name))


def scan(root, assets_dirs, refs_dirs, css_dirs, exclude, ref_ext):
    ref_texts = []
    for p in walk(root, refs_dirs, ref_ext, exclude):
        rel = os.path.relpath(p, root).replace("\\", "/")
        if rel.endswith((".min.js", ".map")):
            continue
        try:
            ref_texts.append((rel, open(p, encoding="utf-8-sig", errors="replace").read().splitlines()))
        except OSError:
            pass

    assets = []
    by_hash = defaultdict(list)
    for p in walk(root, assets_dirs, ASSET_EXT, exclude):
        rel = os.path.relpath(p, root).replace("\\", "/")
        ext = os.path.splitext(p)[1].lower()
        info = measure(p, ext)
        info["path"] = rel
        info["format"] = ext.lstrip(".")
        name = os.path.basename(rel)
        name_rx = ref_pattern(name)
        refs = []
        for rrel, lines in ref_texts:
            for i, line in enumerate(lines, 1):
                if name in line and name_rx.search(line):
                    refs.append(f"{rrel}:{i}")
        info["refs"] = refs
        assets.append(info)
        by_hash[info["md5"]].append(rel)
    for x in assets:
        x["duplicates"] = [p for p in by_hash[x["md5"]] if p != x["path"]]

    css_urls = []
    for p in walk(root, css_dirs, {".css"}, exclude):
        rel = os.path.relpath(p, root).replace("\\", "/")
        for i, line in enumerate(open(p, encoding="utf-8-sig", errors="replace"), 1):
            for m in RE_URL.finditer(line):
                u = m.group(2)
                entry = {"src": f"{rel}:{i}", "url": u[:120] + ("..." if len(u) > 120 else "")}
                if u.startswith("data:"):
                    entry["data_uri"] = True
                    entry["colors"] = sorted({c.lower() for c in re.findall(r'(?:%23|#)([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', u)})
                    entry["rgba"] = re.findall(r'rgba?\([^)]*\)', u)
                css_urls.append(entry)
    return {"root": root, "assets": assets, "css_urls": css_urls}


def _png(w, h, rgb):
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def selftest():
    with tempfile.TemporaryDirectory() as d:
        for sub in ("img", "css", "views"):
            os.makedirs(os.path.join(d, sub))
        png = _png(3, 2, (0x33, 0x66, 0x99))
        open(os.path.join(d, "img", "x-dot.png"), "wb").write(png)
        open(os.path.join(d, "img", "x-dot-copy.png"), "wb").write(png)
        open(os.path.join(d, "img", "x-mark.svg"), "w", encoding="utf-8").write(
            '<svg width="8" height="8" viewBox="0 0 8 8"><path fill="#336699" stroke="none"/></svg>')
        open(os.path.join(d, "css", "s.css"), "w", encoding="utf-8").write(
            ".x-a{background:url(../img/x-dot.png)}\n.x-b{background:url(\"data:image/svg+xml,%3Csvg fill='%23336699'/%3E\")}\n")
        open(os.path.join(d, "views", "p.html"), "w", encoding="utf-8").write('<img src="img/x-mark.svg">\n<img src="img/ax-mark.svg">\n')
        res = scan(d, ["img"], ["views", "css"], ["css"], DEFAULT_EXCLUDE, REF_EXT)
    by = {a["path"]: a for a in res["assets"]}
    checks = [
        ("png size", (by["img/x-dot.png"]["width"], by["img/x-dot.png"]["height"]), (3, 2)),
        ("png colours", by["img/x-dot.png"]["png_colors"], [{"color": "#336699", "share": 1.0}]),
        ("duplicates", by["img/x-dot.png"]["duplicates"], ["img/x-dot-copy.png"]),
        ("svg colours", by["img/x-mark.svg"]["svg"]["colors"], ["#336699"]),
        ("refs", (by["img/x-mark.svg"]["refs"], by["img/x-dot.png"]["refs"]), (["views/p.html:1"], ["css/s.css:1"])),
        ("sorted asset order", [a["path"] for a in res["assets"]], ["img/x-dot-copy.png", "img/x-dot.png", "img/x-mark.svg"]),
        ("data uri colours", [u.get("colors") for u in res["css_urls"]], [None, ["336699"]]),
    ]
    fails = [c for c in checks if c[1] != c[2]]
    for name, got, want in fails:
        print("FAIL %s\n  got:  %r\n  want: %r" % (name, got, want))
    print("asset_scan selftest: %d/%d passed" % (len(checks) - len(fails), len(checks)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="web root; reported paths are relative to it")
    ap.add_argument("--out", help="output JSON path")
    ap.add_argument("--assets", nargs="+", help="asset directories, relative to --root")
    ap.add_argument("--refs", nargs="+", help="directories searched for references, relative to --root")
    ap.add_argument("--css", nargs="*", default=[], help="stylesheet directories or files for url() extraction")
    ap.add_argument("--ref-ext", nargs="*", default=[], help="extra reference file extensions")
    ap.add_argument("--exclude", nargs="*", default=sorted(DEFAULT_EXCLUDE),
                    help="directory names to skip (replaces the default node_modules dist build .git; add the project's build-output folders)")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    missing = [n for n in ("root", "out", "assets", "refs") if not getattr(a, n)]
    if missing:
        ap.error("missing: " + ", ".join("--" + m for m in missing))
    ref_ext = REF_EXT | {e.lower() if e.startswith(".") else "." + e.lower() for e in a.ref_ext}
    res = scan(os.path.abspath(a.root), a.assets, a.refs, a.css, set(a.exclude), ref_ext)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"assets={len(res['assets'])} css_urls={len(res['css_urls'])} "
          f"unreferenced={sum(1 for x in res['assets'] if not x['refs'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
