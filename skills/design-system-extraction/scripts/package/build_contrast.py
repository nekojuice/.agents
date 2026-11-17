#!/usr/bin/env python3
"""Recompute the ratios in data/contrast.json from tokens.json (standard library only, deterministic).

Usage:
  python -I build_contrast.py --tokens <tokens.json> --contrast <contrast.json> [--check]

contrast.json is both the definition and the result file:
- source_pairs[]: the source's own combinations, recorded as they are (colours are never changed).
  Definition fields id, kind (brand / reference), fg, bg, class, context, exempt, opacity
  (optional element opacity, multiplied into the foreground alpha before compositing).
  The script fills fg_value, bg_value, composited, ratio, threshold, result.
- added_states (optional; a Phase 1 snapshot adds no states): acceptance of states with
  origin "added" (threshold `threshold`). Defines
  surfaces[] (surface, controls, ring) and checks[] (state, fg or fg_by_ring, scope all / controls);
  the script writes rows[] and pass.
- image_pairs[]: combinations whose foreground or background is an image, animation or
  underlying content and cannot be computed from tokens. Fields id, kind, component, fg, bg,
  class, context; when fg / bg is a token name the script fills fg_value / bg_value, else null
  (asset:<path>, image, content are kept as written); ratio is always null.

Algorithm: WCAG 2.x relative luminance (sRGB linearisation threshold 0.04045);
ratio = (L1 + 0.05) / (L2 + 0.05), judged on the unrounded value, written with 2 decimals.
Colours may be #rgb, #rgba, #rrggbb, #rrggbbaa, rgb() or rgba().
Translucent colours are composited over the background; a translucent background over #ffffff.
Thresholds: normal 4.5, large 3 (>= 24px, or >= 18.66px with weight >= 700), ui 3.
Result strings: "pass <th>", "fail <th>", "exempt: <reason>", "image-dependent: not computed".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

THRESHOLDS = {"normal": 4.5, "large": 3.0, "ui": 3.0}
REF = re.compile(r"^\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}$")


def color_index(tok: dict) -> dict:
    return {t["name"]: t["value"] for t in tok["color"]["tokens"]}


def resolve(idx: dict, name: str, seen=None) -> str:
    seen = seen or set()
    if name in seen:
        raise ValueError("alias cycle at %s" % name)
    seen.add(name)
    v = idx[name]
    m = REF.match(v) if isinstance(v, str) else None
    return resolve(idx, m.group(1), seen) if m else v


def parse(s: str):
    """(r, g, b, alpha) from #rgb, #rgba, #rrggbb, #rrggbbaa, rgb() or rgba()."""
    s = s.strip().lower()
    if s.startswith("#"):
        h = s[1:]
        if not re.fullmatch(r"[0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8}", h):
            raise ValueError("unsupported color: %s" % s)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        a = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", s)
    if m:
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    raise ValueError("unsupported color: %s" % s)


def over(top, bottom):
    a = top[3]
    return tuple(top[i] * a + bottom[i] * (1 - a) for i in range(3)) + (1.0,)


def lum(c) -> float:
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(fg: str, bg: str, opacity: float = 1.0):
    white = (255.0, 255.0, 255.0, 1.0)
    b = parse(bg)
    f = parse(fg)
    f = f[:3] + (f[3] * opacity,)
    comp = b[3] < 1 or f[3] < 1
    if b[3] < 1:
        b = over(b, white)
    if f[3] < 1:
        f = over(f, b)
    l1, l2 = sorted([lum(f), lum(b)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05), comp


def compute(tok: dict, doc: dict) -> dict:
    idx = color_index(tok)
    out = dict(doc)
    pairs = []
    for p in doc["source_pairs"]:
        q = {k: p[k] for k in ("id", "kind", "fg", "bg", "opacity", "class", "context") if k in p}
        if p.get("exempt"):
            q["exempt"] = p["exempt"]
        fv, bv = resolve(idx, p["fg"]), resolve(idx, p["bg"])
        r, comp = ratio(fv, bv, p.get("opacity", 1.0))
        th = THRESHOLDS[p["class"]]
        q.update({"fg_value": fv, "bg_value": bv, "composited": comp, "ratio": round(r, 2), "threshold": th})
        if p.get("exempt"):
            q["result"] = "exempt: %s" % p["exempt"]
        else:
            q["result"] = ("pass %s" if r >= th else "fail %s") % th
        pairs.append(q)
    out["source_pairs"] = pairs

    if "image_pairs" in doc:
        imgs = []
        for p in doc["image_pairs"]:
            q = {k: p[k] for k in ("id", "kind", "component", "fg", "bg", "class", "context") if k in p}
            q["fg_value"] = resolve(idx, p["fg"]) if p["fg"] in idx else None
            q["bg_value"] = resolve(idx, p["bg"]) if p["bg"] in idx else None
            q["ratio"] = None
            q["threshold"] = THRESHOLDS[p["class"]]
            q["result"] = "image-dependent: not computed"
            imgs.append(q)
        out["image_pairs"] = imgs

    if "added_states" not in doc:
        return out
    ad = dict(doc["added_states"])
    th = ad["threshold"]
    rows, ok = [], True
    for chk in ad["checks"]:
        for s in ad["surfaces"]:
            if chk["scope"] == "controls" and not s["controls"]:
                continue
            fg = chk["fg_by_ring"][s["ring"]] if "fg_by_ring" in chk else chk["fg"]
            fv, bv = resolve(idx, fg), resolve(idx, s["surface"])
            r, comp = ratio(fv, bv)
            row = {"state": chk["state"], "surface": s["surface"], "fg": fg, "fg_value": fv, "bg_value": bv,
                   "composited": comp, "ratio": round(r, 2), "pass": r >= th}
            if "fg_by_ring" in chk:
                row["ring"] = s["ring"]
            ok &= row["pass"]
            rows.append(row)
    ad["rows"] = rows
    ad["pass"] = ok
    out["added_states"] = ad
    return out


def render(tok: dict, doc: dict) -> str:
    return json.dumps(compute(tok, doc), ensure_ascii=False, indent=2) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokens", required=True, help="tokens.json")
    ap.add_argument("--contrast", required=True, help="contrast.json, rewritten in place")
    ap.add_argument("--check", action="store_true", help="compare only; exit 1 when the file differs")
    a = ap.parse_args(argv)
    tok = json.loads(Path(a.tokens).read_text(encoding="utf-8"))
    path = Path(a.contrast)
    doc = json.loads(path.read_text(encoding="utf-8"))
    data = render(tok, doc).encode("utf-8")
    if a.check:
        same = path.read_bytes() == data
        print("%s %s" % (path.name, "up to date" if same else "differs from recomputed output"))
        return 0 if same else 1
    path.write_bytes(data)
    print("wrote %s (%d bytes)" % (path.name, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
