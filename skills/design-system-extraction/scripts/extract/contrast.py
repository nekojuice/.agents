#!/usr/bin/env python3
"""WCAG 2.x relative luminance and contrast ratio (standard library only).

Usage:
  single:  python -I contrast.py FG BG [--base #ffffff] [--json]
  batch:   python -I contrast.py --batch <pairs.json> [--out <result.json>]

Colour formats: #rgb, #rgba, #rrggbb, #rrggbbaa, rgb()/rgba() (comma or space syntax,
percentages, `/ alpha`), hsl()/hsla(), CSS named colours, transparent.
Translucent colours are composited in order: BG over --base (default white, must be opaque),
then FG over the composited BG.

Batch input: a JSON array, or {"pairs": [...]}; each item {"id"?, "fg", "bg", "base"?, "note"?}.
Thresholds (compared on the unrounded ratio): AA normal 4.5, AA large 3, AAA normal 7,
AAA large 4.5, non-text UI 3.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NAMED = {
    "black": "000000", "silver": "c0c0c0", "gray": "808080", "grey": "808080", "white": "ffffff",
    "maroon": "800000", "red": "ff0000", "purple": "800080", "fuchsia": "ff00ff", "magenta": "ff00ff",
    "green": "008000", "lime": "00ff00", "olive": "808000", "yellow": "ffff00", "navy": "000080",
    "blue": "0000ff", "teal": "008080", "aqua": "00ffff", "cyan": "00ffff", "orange": "ffa500",
    "aliceblue": "f0f8ff", "antiquewhite": "faebd7", "aquamarine": "7fffd4", "azure": "f0ffff",
    "beige": "f5f5dc", "bisque": "ffe4c4", "blanchedalmond": "ffebcd", "blueviolet": "8a2be2",
    "brown": "a52a2a", "burlywood": "deb887", "cadetblue": "5f9ea0", "chartreuse": "7fff00",
    "chocolate": "d2691e", "coral": "ff7f50", "cornflowerblue": "6495ed", "cornsilk": "fff8dc",
    "crimson": "dc143c", "darkblue": "00008b", "darkcyan": "008b8b", "darkgoldenrod": "b8860b",
    "darkgray": "a9a9a9", "darkgrey": "a9a9a9", "darkgreen": "006400", "darkkhaki": "bdb76b",
    "darkmagenta": "8b008b", "darkolivegreen": "556b2f", "darkorange": "ff8c00", "darkorchid": "9932cc",
    "darkred": "8b0000", "darksalmon": "e9967a", "darkseagreen": "8fbc8f", "darkslateblue": "483d8b",
    "darkslategray": "2f4f4f", "darkslategrey": "2f4f4f", "darkturquoise": "00ced1",
    "darkviolet": "9400d3", "deeppink": "ff1493", "deepskyblue": "00bfff", "dimgray": "696969",
    "dimgrey": "696969", "dodgerblue": "1e90ff", "firebrick": "b22222", "floralwhite": "fffaf0",
    "forestgreen": "228b22", "gainsboro": "dcdcdc", "ghostwhite": "f8f8ff", "gold": "ffd700",
    "goldenrod": "daa520", "greenyellow": "adff2f", "honeydew": "f0fff0", "hotpink": "ff69b4",
    "indianred": "cd5c5c", "indigo": "4b0082", "ivory": "fffff0", "khaki": "f0e68c",
    "lavender": "e6e6fa", "lavenderblush": "fff0f5", "lawngreen": "7cfc00", "lemonchiffon": "fffacd",
    "lightblue": "add8e6", "lightcoral": "f08080", "lightcyan": "e0ffff",
    "lightgoldenrodyellow": "fafad2", "lightgray": "d3d3d3", "lightgrey": "d3d3d3",
    "lightgreen": "90ee90", "lightpink": "ffb6c1", "lightsalmon": "ffa07a", "lightseagreen": "20b2aa",
    "lightskyblue": "87cefa", "lightslategray": "778899", "lightslategrey": "778899",
    "lightsteelblue": "b0c4de", "lightyellow": "ffffe0", "limegreen": "32cd32", "linen": "faf0e6",
    "mediumaquamarine": "66cdaa", "mediumblue": "0000cd", "mediumorchid": "ba55d3",
    "mediumpurple": "9370db", "mediumseagreen": "3cb371", "mediumslateblue": "7b68ee",
    "mediumspringgreen": "00fa9a", "mediumturquoise": "48d1cc", "mediumvioletred": "c71585",
    "midnightblue": "191970", "mintcream": "f5fffa", "mistyrose": "ffe4e1", "moccasin": "ffe4b5",
    "navajowhite": "ffdead", "oldlace": "fdf5e6", "olivedrab": "6b8e23", "orangered": "ff4500",
    "orchid": "da70d6", "palegoldenrod": "eee8aa", "palegreen": "98fb98", "paleturquoise": "afeeee",
    "palevioletred": "db7093", "papayawhip": "ffefd5", "peachpuff": "ffdab9", "peru": "cd853f",
    "pink": "ffc0cb", "plum": "dda0dd", "powderblue": "b0e0e6", "rebeccapurple": "663399",
    "rosybrown": "bc8f8f", "royalblue": "4169e1", "saddlebrown": "8b4513", "salmon": "fa8072",
    "sandybrown": "f4a460", "seagreen": "2e8b57", "seashell": "fff5ee", "sienna": "a0522d",
    "skyblue": "87ceeb", "slateblue": "6a5acd", "slategray": "708090", "slategrey": "708090",
    "snow": "fffafa", "springgreen": "00ff7f", "steelblue": "4682b4", "tan": "d2b48c",
    "thistle": "d8bfd8", "tomato": "ff6347", "turquoise": "40e0d0", "violet": "ee82ee",
    "wheat": "f5deb3", "whitesmoke": "f5f5f5", "yellowgreen": "9acd32",
}

THRESHOLDS = {"AA_normal": 4.5, "AA_large": 3.0, "AAA_normal": 7.0, "AAA_large": 4.5, "UI_non_text": 3.0}


def _num(tok: str, scale: float) -> float:
    tok = tok.strip()
    if tok.endswith("%"):
        return float(tok[:-1]) / 100.0 * scale
    return float(tok)


def parse_color(s: str):
    """Return (r, g, b, a): r/g/b floats in 0-255, a in 0-1."""
    s = s.strip().lower()
    if s == "transparent":
        return (0.0, 0.0, 0.0, 0.0)
    if s in NAMED:
        s = "#" + NAMED[s]
    if s.startswith("#"):
        h = s[1:]
        if not re.fullmatch(r"[0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8}", h):
            raise ValueError("invalid hex color: %s" % s)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
        return (float(r), float(g), float(b), a)
    m = re.fullmatch(r"(rgba?|hsla?)\((.*)\)", s)
    if not m:
        raise ValueError("unsupported color: %s" % s)
    fn, body = m.group(1), m.group(2).strip()
    alpha = 1.0
    if "/" in body:
        body, a_tok = body.split("/", 1)
        alpha = _num(a_tok, 1.0)
    parts = [p for p in re.split(r"[\s,]+", body.strip()) if p]
    if len(parts) == 4:
        alpha = _num(parts[3], 1.0)
        parts = parts[:3]
    if len(parts) != 3:
        raise ValueError("invalid %s(): %s" % (fn, s))
    if fn.startswith("rgb"):
        r, g, b = (_num(p, 255.0) for p in parts)
    else:
        hue = float(re.sub(r"deg$", "", parts[0])) % 360 / 360.0
        sat = _num(parts[1], 1.0) if parts[1].endswith("%") else float(parts[1]) / 100.0
        lig = _num(parts[2], 1.0) if parts[2].endswith("%") else float(parts[2]) / 100.0
        r, g, b = (x * 255.0 for x in colorsys.hls_to_rgb(hue, lig, sat))
    clamp = lambda v, hi: max(0.0, min(hi, v))
    return (clamp(r, 255.0), clamp(g, 255.0), clamp(b, 255.0), clamp(alpha, 1.0))


def composite(top, bottom):
    """Composite top over an opaque bottom (source-over)."""
    a = top[3]
    return tuple(top[i] * a + bottom[i] * (1 - a) for i in range(3)) + (1.0,)


def _channel(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb) -> float:
    return 0.2126 * _channel(rgb[0]) + 0.7152 * _channel(rgb[1]) + 0.0722 * _channel(rgb[2])


def to_hex(rgb) -> str:
    return "#" + "".join("%02x" % int(round(v)) for v in rgb[:3])


def contrast(fg: str, bg: str, base: str = "#ffffff"):
    base_c = parse_color(base)
    if base_c[3] < 1:
        raise ValueError("base must be opaque: %s" % base)
    bg_c = parse_color(bg)
    bg_eff = composite(bg_c, base_c) if bg_c[3] < 1 else bg_c
    fg_c = parse_color(fg)
    fg_eff = composite(fg_c, bg_eff) if fg_c[3] < 1 else fg_c
    l1 = relative_luminance(fg_eff)
    l2 = relative_luminance(bg_eff)
    hi, lo = max(l1, l2), min(l1, l2)
    ratio = (hi + 0.05) / (lo + 0.05)
    return {
        "fg": fg, "bg": bg, "base": base if (bg_c[3] < 1) else None,
        "fg_effective": to_hex(fg_eff), "bg_effective": to_hex(bg_eff),
        "fg_luminance": round(l1, 5), "bg_luminance": round(l2, 5),
        "composited": fg_c[3] < 1 or bg_c[3] < 1,
        "ratio": round(ratio, 2), "ratio_raw": ratio,
        "pass": {k: ratio >= v for k, v in THRESHOLDS.items()},
    }


def _fmt(res):
    p = res["pass"]
    mark = lambda k: "pass" if p[k] else "fail"
    line = "%s on %s -> %.2f:1  AA %s / AA-large %s / AAA %s / AAA-large %s / UI %s" % (
        res["fg"], res["bg"], res["ratio"], mark("AA_normal"), mark("AA_large"),
        mark("AAA_normal"), mark("AAA_large"), mark("UI_non_text"))
    if res["composited"]:
        line += "  (effective %s on %s)" % (res["fg_effective"], res["bg_effective"])
    return line


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fg", nargs="?")
    ap.add_argument("bg", nargs="?")
    ap.add_argument("--base", default="#ffffff", help="opaque backdrop for a translucent BG (default #ffffff)")
    ap.add_argument("--batch", help="batch JSON file")
    ap.add_argument("--out", help="write batch results to this JSON file (default: stdout)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.batch:
        doc = json.loads(Path(args.batch).read_text(encoding="utf-8-sig"))
        pairs = doc.get("pairs", []) if isinstance(doc, dict) else doc
        results = []
        for k, item in enumerate(pairs, 1):
            try:
                res = contrast(item["fg"], item["bg"], item.get("base") or args.base)
            except (KeyError, ValueError) as e:
                res = {"fg": item.get("fg"), "bg": item.get("bg"), "error": str(e)}
            res = {"id": item.get("id", k), **({"note": item["note"]} if "note" in item else {}), **res}
            results.append(res)
        out = {"thresholds": THRESHOLDS, "results": results}
        text = json.dumps(out, ensure_ascii=False, indent=1)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
            for r in results:
                print("%s: %s" % (r["id"], r.get("error") or _fmt(r)))
        else:
            print(text)
        return
    if not (args.fg and args.bg):
        ap.error("need FG and BG, or --batch")
    res = contrast(args.fg, args.bg, args.base)
    print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else _fmt(res))


if __name__ == "__main__":
    main()
