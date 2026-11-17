#!/usr/bin/env python3
"""Colour and scale metrics used when rationalising tokens (standard library only).

Importable as a module, or run directly:
  python -I colormetrics.py lab COLOR [COLOR ...] [--family-rules <rules.json>]
                                   # L*, a*, b*, C*, h, suggested family and step
  python -I colormetrics.py de COLOR_A COLOR_B          # CIEDE2000 colour difference
  python -I colormetrics.py contrast FG BG [--base #ffffff]   # WCAG 2.x contrast ratio
  python -I colormetrics.py selftest                    # check ΔE2000 against Sharma 2005 data

Colour formats: #rgb, #rrggbb, #rrggbbaa, rgb()/rgba() (comma syntax). A translucent
foreground is composited over the background, a translucent background over the base.

Family rules (JSON, same shape as DEFAULT_FAMILY_RULES):
  neutral_chroma_max  C* below this is "neutral"
  named_hue_ranges    [[name, start_deg, end_deg), ...]; end may exceed 360 to wrap past 0
  fallback_bin_deg    other hues fall into bins of this width, named hue-<start>
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- parsing

_RGB_RE = re.compile(r"^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$", re.I)


def parse_color(s: str):
    """Return (r, g, b, a): r/g/b in 0-255, a in 0-1; None when the value cannot be parsed."""
    s = s.strip().lower()
    if s.startswith("#"):
        h = s[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255)
        return None
    m = _RGB_RE.match(s)
    if m:
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    return None


def is_opaque(s: str) -> bool:
    c = parse_color(s)
    return c is not None and c[3] >= 1.0


def to_hex(c) -> str:
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c[:3])


def composite(fg, bg):
    """Composite fg over an opaque bg."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


# ---------------------------------------------------------------- WCAG

def _lin(v: float) -> float:
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(c) -> float:
    r, g, b = (_lin(x) for x in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str, base: str = "#ffffff") -> float:
    b0 = parse_color(base)
    bgc = parse_color(bg)
    if bgc[3] < 1:
        bgc = composite(bgc, b0)
    fgc = parse_color(fg)
    if fgc[3] < 1:
        fgc = composite(fgc, bgc)
    l1, l2 = luminance(fgc), luminance(bgc)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- CIELAB (D65)

def to_lab(c):
    r, g, b = (_lin(x) for x in c[:3])
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.0
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lch(lab):
    L, a, b = lab
    C = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360
    return L, C, h


def delta_e2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0) -> float:
    """CIEDE2000 (Sharma, Wu, Dalal 2005)."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cbar ** 7 / (Cbar ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0
    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    else:
        dhp = h2p - h1p
        if dhp > 180:
            dhp -= 360
        elif dhp < -180:
            dhp += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp = (L1 + L2) / 2
    Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    else:
        if abs(h1p - h2p) <= 180:
            hbp = (h1p + h2p) / 2
        elif h1p + h2p < 360:
            hbp = (h1p + h2p + 360) / 2
        else:
            hbp = (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dtheta = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc = 1 + 0.045 * Cbp
    Sh = 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dtheta)) * Rc
    return math.sqrt((dLp / (kL * Sl)) ** 2 + (dCp / (kC * Sc)) ** 2 + (dHp / (kH * Sh)) ** 2
                     + Rt * (dCp / (kC * Sc)) * (dHp / (kH * Sh)))


def de(c1: str, c2: str) -> float:
    return delta_e2000(to_lab(parse_color(c1)), to_lab(parse_color(c2)))




# ---------------------------------------------------------------- family / step

DEFAULT_FAMILY_RULES = {
    "neutral_chroma_max": 8.0,      # C* < 8 -> neutral
    "named_hue_ranges": [],         # [name, start, end); end may exceed 360 to wrap past 0
    "fallback_bin_deg": 30.0,       # other hues: 30-degree bins named hue-<start>
}


def family_of(hexv: str, rules=None) -> str:
    rules = rules or DEFAULT_FAMILY_RULES
    L, C, h = lch(to_lab(parse_color(hexv)))
    if C < rules["neutral_chroma_max"]:
        return "neutral"
    for name, a, b in rules.get("named_hue_ranges") or []:
        hh = h if h >= a else h + 360
        if a <= hh < b:
            return name
    w = rules["fallback_bin_deg"]
    start = int(h // w * w)
    return "hue-%d" % start


def step_of(hexv: str, lo: int = 25, hi: int = 950) -> int:
    L = to_lab(parse_color(hexv))[0]
    s = round((100 - L) / 5) * 50
    return max(lo, min(hi, s)) if s != 0 else lo


# ---------------------------------------------------------------- selftest

_SHARMA = [  # (L1,a1,b1, L2,a2,b2, dE00) - excerpt of Sharma 2005 Table 1
    (50.0000, 2.6772, -79.7751, 50.0000, 0.0000, -82.7485, 2.0425),
    (50.0000, 3.1571, -77.2803, 50.0000, 0.0000, -82.7485, 2.8615),
    (50.0000, 2.8361, -74.0200, 50.0000, 0.0000, -82.7485, 3.4412),
    (50.0000, -1.3802, -84.2814, 50.0000, 0.0000, -82.7485, 1.0000),
    (50.0000, 0.0000, 0.0000, 50.0000, -1.0000, 2.0000, 2.3669),
    (50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0009, 7.1792),
    (50.0000, 2.5000, 0.0000, 50.0000, 0.0000, -2.5000, 4.3065),
    (50.0000, 2.5000, 0.0000, 73.0000, 25.0000, -18.0000, 27.1492),
    (50.0000, 2.5000, 0.0000, 56.0000, -27.0000, -3.0000, 31.9030),
    (60.2574, -34.0099, 36.2677, 60.4626, -34.1751, 39.4387, 1.2644),
    (63.0109, -31.0961, -5.8663, 62.8187, -29.7946, -4.0864, 1.2630),
    (35.0831, -44.1164, 3.7933, 35.0232, -40.0716, 1.5901, 1.8645),
    (22.7233, 20.0904, -46.6940, 23.0331, 14.9730, -42.5619, 2.0373),
    (90.8027, -2.0831, 1.4410, 91.1528, -1.6435, 0.0447, 1.4441),
    (2.0776, 0.0795, -1.1350, 0.9033, -0.0636, -0.5514, 0.9082),
]


def selftest() -> bool:
    ok = True
    for row in _SHARMA:
        got = delta_e2000(row[0:3], row[3:6])
        if abs(got - row[6]) > 1e-4:
            ok = False
            print("FAIL", row, round(got, 4))
    rules = {"neutral_chroma_max": 8.0, "named_hue_ranges": [["x-warm", 20.0, 60.0]], "fallback_bin_deg": 30.0}
    fam = (family_of("#808080"), family_of("#cc3333", rules), family_of("#336699"))
    if fam != ("neutral", "x-warm", "hue-240"):
        ok = False
        print("FAIL family_of", fam)
    print("colormetrics selftest:", "PASS" if ok else "FAIL", f"({len(_SHARMA)} ΔE2000 pairs + family rules)")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lab", help="print L* a* b* C* h, family and step")
    p.add_argument("colors", nargs="+")
    p.add_argument("--family-rules", help="JSON file with family rules (default: neutral + 30-degree bins)")
    p = sub.add_parser("de", help="print the CIEDE2000 difference of two colours")
    p.add_argument("a")
    p.add_argument("b")
    p = sub.add_parser("contrast", help="print the WCAG 2.x contrast ratio")
    p.add_argument("fg")
    p.add_argument("bg")
    p.add_argument("--base", default="#ffffff", help="opaque backdrop for a translucent background")
    sub.add_parser("selftest", help="check the ΔE2000 implementation against reference data")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return 0 if selftest() else 1
    if a.cmd == "lab":
        rules = None
        if a.family_rules:
            with open(a.family_rules, encoding="utf-8-sig") as fh:
                rules = dict(DEFAULT_FAMILY_RULES, **json.load(fh))
        for c in a.colors:
            L, A, B = to_lab(parse_color(c))
            _, C, h = lch((L, A, B))
            print(f"{c}\tL*={L:.2f}\ta*={A:.2f}\tb*={B:.2f}\tC*={C:.2f}\th={h:.1f}\t{family_of(c, rules)}-{step_of(c)}")
        return 0
    if a.cmd == "de":
        print(f"{de(a.a, a.b):.3f}")
        return 0
    print(f"{contrast(a.fg, a.bg, a.base):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
