#!/usr/bin/env python3
"""tokens.json -> tokens.css + tokens.dtcg.json (standard library only, deterministic output).

Usage:
  python -I build_tokens.py --tokens <tokens.json> --css <tokens.css> --dtcg <tokens.dtcg.json> [--check]

--check: do not write; compare the existing outputs with the regenerated result
(exit 0 when identical, 1 otherwise).

tokens.json layout (list form):
- each family is {"tokens": [{name, value, tier, origin, usage, ...}]}; typography lives in
  `type`: type.families (font stacks), type.scales (font-size / line-height / font-weight /
  letter-spacing) and type.groups[].styles[] (type styles, optional breakpoints[{min, <field>}]).
- aliases are written {name}; composite values (shadows) may embed {name}. All tokens share
  one namespace.
- `themes` reserves the theme list; today every value has a single theme.
- every family is optional: a brand without shadows, durations or easing simply omits it.
- colours may be #rgb, #rgba, #rrggbb, #rrggbbaa, rgb() or rgba().
- `css.prefix` is the CSS custom-property prefix (required).

tokens.css output:
- colours and shadows go in `:root, [data-theme="<first theme>"]`; other families in :root.
- CSS variables are --<prefix>-<name>; font stacks --<prefix>-font-family-<key>;
  type styles --<prefix>-<style>-<font-family|font-size|line-height|font-weight|letter-spacing>.
- type-style breakpoint overrides are emitted as @media (min-width: <bp>) { :root { ... } }.
- every type style also gets a class .<prefix>-<style> (style names start with type-).

tokens.dtcg.json output: DTCG 2025.10 ($value, $type, aliases {group.token}). Values that no
DTCG type can express (%, em, vh, keywords) carry no $type and are listed in the root $extensions.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAMILIES = ["color", "space", "radius", "shadow", "size", "duration", "easing", "breakpoint"]
SCALES = ["font-family", "font-size", "line-height", "font-weight", "letter-spacing"]
TYPE_FIELDS = [("family", "font-family"), ("fontSize", "font-size"), ("lineHeight", "line-height"),
               ("fontWeight", "font-weight"), ("letterSpacing", "letter-spacing")]
DTCG_GROUP = {"color": "color", "space": "space", "radius": "radius", "shadow": "shadow", "size": "size",
              "duration": "duration", "easing": "easing", "breakpoint": "breakpoint",
              "font-family": "fontFamily", "font-size": "fontSize", "line-height": "lineHeight",
              "font-weight": "fontWeight", "letter-spacing": "letterSpacing", "type": "typography"}
EASING_BEZIER = {"ease": [0.25, 0.1, 0.25, 1], "ease-in-out": [0.42, 0, 0.58, 1], "ease-out": [0, 0, 0.58, 1],
                 "ease-in": [0.42, 0, 1, 1], "linear": [0, 0, 1, 1]}
REF = re.compile(r"\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}")


# ---------------------------------------------------------------- index

def index(tok: dict) -> dict:
    """name -> {value, tier, origin, family, entry}; font stacks are named font-family-<key>."""
    out = {}

    def add(name, value, family, entry):
        if name in out:
            raise ValueError("duplicate token name: %s" % name)
        out[name] = {"value": value, "tier": entry.get("tier"), "origin": entry.get("origin"),
                     "family": family, "entry": entry}

    for fam in FAMILIES:
        for t in (tok.get(fam) or {}).get("tokens", []):
            add(t["name"], t["value"], fam, t)
    ty = tok.get("type") or {}
    for k, v in (ty.get("families") or {}).items():
        add("font-family-" + k, v["value"], "font-family", v)
    for sc in SCALES:
        for t in ((ty.get("scales") or {}).get(sc) or {}).get("tokens", []):
            add(t["name"], t["value"], sc, t)
    for g in ty.get("groups", []):
        for s in g["styles"]:
            add(s["name"], None, "type", s)
    return out


def fam_tokens(tok: dict, fam: str) -> list:
    """Token list of a top-level family; [] when the family is absent."""
    return (tok.get(fam) or {}).get("tokens", [])


def type_part(tok: dict, key: str, empty):
    """type.<key> (families / scales), or `empty` when absent."""
    return (tok.get("type") or {}).get(key) or empty


def scale_tokens(tok: dict, sc: str) -> list:
    """Token list of a type scale; [] when the scale is absent."""
    return (type_part(tok, "scales", {}).get(sc) or {}).get("tokens", [])


def styles(tok: dict):
    for g in (tok.get("type") or {}).get("groups", []):
        for s in g["styles"]:
            yield s


def prefix_of(tok: dict) -> str:
    """CSS custom-property prefix from tokens.json `css.prefix` (required)."""
    p = (tok.get("css") or {}).get("prefix")
    if not p:
        raise SystemExit("tokens.json has no css.prefix")
    return p


def bp_px(tok: dict, name: str) -> str:
    for t in (tok.get("breakpoint") or {}).get("tokens", []):
        if t["name"] == name:
            return str(t["value"])
    raise KeyError("unknown breakpoint: %s" % name)


def css_value(prefix: str, v) -> str:
    if isinstance(v, (int, float)):
        return str(v)
    if not isinstance(v, str):
        raise ValueError("unsupported value: %r" % (v,))
    m = REF.fullmatch(v)
    if m:
        return "var(--%s-%s)" % (prefix, m.group(1))
    return REF.sub(lambda mm: "var(--%s-%s)" % (prefix, mm.group(1)), v)


# ---------------------------------------------------------------- CSS

def render_css(tok: dict) -> str:
    p = prefix_of(tok)
    themes = tok.get("themes") or [{"id": "default"}]
    first = themes[0]["id"]
    out = ["/* Generated by build_tokens.py from tokens.json. Do not edit by hand. */", ""]

    def block(fam, tokens, comment=None):
        out.append("  /* %s%s */" % (fam, (": " + comment) if comment else ""))
        for t in tokens:
            out.append("  --%s-%s: %s;" % (p, t["name"], css_value(p, t["value"])))

    out.append(':root, [data-theme="%s"] {' % first)
    block("color", fam_tokens(tok, "color"))
    block("shadow", fam_tokens(tok, "shadow"))
    out.append("}")
    out.append("")
    out.append(":root {")
    out.append("  /* font-family */")
    for k, v in type_part(tok, "families", {}).items():
        out.append("  --%s-font-family-%s: %s;" % (p, k, v["value"]))
    for sc in SCALES:
        block(sc, scale_tokens(tok, sc))
    for fam in ["space", "radius", "size", "duration", "easing"]:
        block(fam, fam_tokens(tok, fam))
    block("breakpoint", fam_tokens(tok, "breakpoint"), "reference values; @media cannot use var(), write the min-width literal")
    out.append("  /* type styles */")
    for s in styles(tok):
        for key, prop in TYPE_FIELDS:
            out.append("  --%s-%s-%s: %s;" % (p, s["name"], prop, css_value(p, s[key])))
    out.append("}")

    by_bp = {}
    for s in styles(tok):
        for b in s.get("breakpoints") or []:
            for key, prop in TYPE_FIELDS:
                if key in b:
                    by_bp.setdefault(b["min"], []).append((s["name"], prop, b[key]))
    order = [t["name"] for t in fam_tokens(tok, "breakpoint")]
    for bp in sorted(by_bp, key=order.index):
        out.append("")
        out.append("@media (min-width: %s) {" % bp_px(tok, bp))
        out.append("  :root {")
        for name, prop, val in by_bp[bp]:
            out.append("    --%s-%s-%s: %s;" % (p, name, prop, css_value(p, val)))
        out.append("  }")
        out.append("}")

    out.append("")
    out.append("/* type classes */")
    for s in styles(tok):
        out.append(".%s-%s {" % (p, s["name"]))
        for _key, prop in TYPE_FIELDS:
            out.append("  %s: var(--%s-%s-%s);" % (prop, p, s["name"], prop))
        out.append("}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- DTCG

NUM_UNIT = re.compile(r"^(-?\d+(?:\.\d+)?)(px|rem|ms|s)?$")


def _num(x: str):
    f = float(x)
    return int(f) if f.is_integer() else f


def _color_obj(s: str):
    """DTCG colour object for #rgb, #rgba, #rrggbb, #rrggbbaa, rgb() or rgba(); None otherwise."""
    s = s.strip()
    if s.startswith("#"):
        h = s[1:]
        if not re.fullmatch(r"[0-9A-Fa-f]{3,4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8}", h):
            return None
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = round(int(h[6:8], 16) / 255, 4) if len(h) == 8 else 1
        return {"colorSpace": "srgb", "components": [round(r / 255, 4), round(g / 255, 4), round(b / 255, 4)],
                "alpha": _num(str(a)), "hex": "#" + h[:6].lower()}
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", s)
    if m:
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        return {"colorSpace": "srgb", "components": [round(r / 255, 4), round(g / 255, 4), round(b / 255, 4)],
                "alpha": _num(str(a)), "hex": "#%02x%02x%02x" % (int(r), int(g), int(b))}
    return None


def _dim(s):
    if isinstance(s, (int, float)):
        return None
    m = NUM_UNIT.fullmatch(str(s).strip())
    if not m:
        return None
    unit = m.group(2) or "px"
    if str(s).strip() in ("0",):
        unit = "px"
    if unit not in ("px", "rem"):
        return None
    return {"value": _num(m.group(1)), "unit": unit}


def _dur(s):
    m = NUM_UNIT.fullmatch(str(s).strip())
    if not m or m.group(2) not in ("ms", "s"):
        return None
    return {"value": _num(m.group(1)), "unit": m.group(2)}


def render_dtcg(tok: dict) -> str:
    idx = index(tok)
    unrepresentable = []

    def alias(name):
        return "{%s.%s}" % (DTCG_GROUP[idx[name]["family"]], name)

    def conv(name, fam, value):
        """Return ($type, $value) or (None, original value)."""
        if isinstance(value, str):
            m = REF.fullmatch(value)
            if m:
                tgt = m.group(1)
                ttype = conv(tgt, idx[tgt]["family"], idx[tgt]["value"])[0] if idx[tgt]["value"] is not None else None
                return ttype, alias(tgt)
        if fam == "color":
            c = _color_obj(value)
            return ("color", c) if c else (None, value)
        if fam in ("space", "radius", "size", "breakpoint", "font-size", "letter-spacing"):
            d = _dim(value)
            return ("dimension", d) if d else (None, value)
        if fam == "line-height":
            if isinstance(value, (int, float)):
                return "number", value
            d = _dim(value)
            return ("dimension", d) if d else (None, value)
        if fam == "font-weight":
            return "fontWeight", value
        if fam == "font-family":
            parts = [x.strip().strip('"').strip("'") for x in value.split(",")]
            return "fontFamily", parts
        if fam == "duration":
            d = _dur(value)
            return ("duration", d) if d else (None, value)
        if fam == "easing":
            b = EASING_BEZIER.get(value)
            return ("cubicBezier", b) if b else (None, value)
        if fam == "shadow":
            sh = _shadow(value)
            return ("shadow", sh) if sh is not None else (None, value)
        return None, value

    def _shadow(v):
        layers = []
        for layer in _split_top(v, ","):
            parts = layer.split()
            inset = False
            if parts and parts[0] == "inset":
                inset = True
                parts = parts[1:]
            color = None
            lens = []
            for x in parts:
                m = REF.fullmatch(x)
                if m:
                    color = alias(m.group(1))
                elif _dim(x):
                    lens.append(_dim(x))
                else:
                    c = _color_obj(x)
                    if not c:
                        return None
                    color = c
            if color is None or len(lens) < 2:
                return None
            while len(lens) < 4:
                lens.append({"value": 0, "unit": "px"})
            layers.append({"color": color, "offsetX": lens[0], "offsetY": lens[1], "blur": lens[2],
                           "spread": lens[3], "inset": inset})
        return layers[0] if len(layers) == 1 else layers

    root = {}
    groups = {}

    def put(fam, name, entry):
        gname = DTCG_GROUP[fam]
        ttype, val = conv(name, fam, entry["value"])
        node = {"$value": val}
        if ttype:
            node["$type"] = ttype
        else:
            unrepresentable.append("%s.%s" % (gname, name))
        desc = entry.get("usage")
        if desc:
            node["$description"] = desc
        node["$extensions"] = {"tier": entry.get("tier"), "origin": entry.get("origin")}
        groups.setdefault(gname, {})[name] = node

    for fam in FAMILIES:
        for t in fam_tokens(tok, fam):
            put(fam, t["name"], t)
    for k, v in type_part(tok, "families", {}).items():
        put("font-family", "font-family-" + k, v)
    for sc in SCALES:
        for t in scale_tokens(tok, sc):
            put(sc, t["name"], t)
    for s in styles(tok):
        val = {}
        for key, dkey in [("family", "fontFamily"), ("fontSize", "fontSize"), ("fontWeight", "fontWeight"),
                          ("letterSpacing", "letterSpacing"), ("lineHeight", "lineHeight")]:
            v = s[key]
            m = REF.fullmatch(v) if isinstance(v, str) else None
            if m:
                val[dkey] = alias(m.group(1))
            elif key == "letterSpacing" and v == "normal":
                val[dkey] = {"value": 0, "unit": "px"}
            else:
                val[dkey] = v
        node = {"$type": "typography", "$value": val}
        if s.get("usage"):
            node["$description"] = s["usage"]
        ext = {"tier": s.get("tier"), "origin": s.get("origin")}
        if s.get("breakpoints"):
            ext["breakpoints"] = [{"min": "{breakpoint.%s}" % b["min"],
                                   **{k: (alias(REF.fullmatch(x).group(1)) if isinstance(x, str) and REF.fullmatch(x) else x)
                                      for k, x in b.items() if k != "min"}} for b in s["breakpoints"]]
        node["$extensions"] = ext
        groups.setdefault("typography", {})[s["name"]] = node
    for g in ["color", "fontFamily", "fontSize", "lineHeight", "fontWeight", "letterSpacing", "typography",
              "space", "radius", "shadow", "size", "duration", "easing", "breakpoint"]:
        if g in groups:
            root[g] = groups[g]
    root["$extensions"] = {"generator": "build_tokens.py",
                           "unrepresentable": sorted(unrepresentable),
                           "note": "unrepresentable: values in %, em, vh or keywords have no DTCG 2025.10 type, so they carry no $type."}
    return json.dumps(root, ensure_ascii=False, indent=2) + "\n"


def _split_top(s: str, sep: str):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "({":
            depth += 1
        elif ch in ")}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


# ---------------------------------------------------------------- main

def build(tok: dict):
    return render_css(tok), render_dtcg(tok)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokens", required=True, help="tokens.json (single source)")
    ap.add_argument("--css", required=True, help="tokens.css to write or check")
    ap.add_argument("--dtcg", required=True, help="tokens.dtcg.json to write or check")
    ap.add_argument("--check", action="store_true", help="compare only; exit 1 when outputs differ")
    a = ap.parse_args(argv)
    tok = json.loads(Path(a.tokens).read_text(encoding="utf-8"))
    css, dtcg = build(tok)
    rc = 0
    for path, text in [(Path(a.css), css), (Path(a.dtcg), dtcg)]:
        data = text.encode("utf-8")
        if a.check:
            same = path.exists() and path.read_bytes() == data
            print("%s %s" % (path.name, "up to date" if same else "differs from regenerated output"))
            rc |= 0 if same else 1
        else:
            path.write_bytes(data)
            print("wrote %s (%d bytes)" % (path.name, len(data)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
