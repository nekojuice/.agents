#!/usr/bin/env python3
"""tokens.json -> Tailwind v4 theme (`@theme inline`; standard library only, deterministic output).

Usage:
  python -I build_tailwind.py --tokens <tokens.json> --out <tailwind/theme.css> [--check]

--check compares only and does not write; exit 1 when the file differs.

Mapping rules:
- every namespace the theme uses is first reset to `initial`, so the framework's default
  colour names, type sizes, radii, shadows and so on cannot be used.
- values always point at var(--<prefix>-*); breakpoints are the exception and are written as
  literals (media queries cannot use var()).
- semantic colours -> --color-<name without color->; primitive and component colours stay
  out of @theme (use `bg-(--<prefix>-...)`).
- spacing -> --spacing: var(--<prefix>-<spacing token>); allowed steps = space token px / 4.
- type styles type-<role>-<size> -> --text-<role>-<size> with --line-height / --font-weight /
  --letter-spacing companions; font stacks pair through font-*.
- font stacks font-family-<key> -> --font-<key>; weights, line heights, letter spacing,
  radii, shadows, easing and layout widths follow the table in the package manual.

Breakpoints: every breakpoint-<step> token becomes the variant <step> (breakpoint-md -> md:).
A brand whose breakpoint tokens are named otherwise maps them in tokens.json
`tailwind.breakpoints`. The script exits 1 when breakpoint tokens exist but none can be mapped,
so responsive variants never disappear silently; a brand without a breakpoint family (a
fixed-size medium) gets an empty breakpoint section. Every family is optional.

Layout widths: size tokens whose names start with a container prefix become --container-*
(max-w-*). The default prefix is size-layout-, the skeleton's layout-width family. The script
exits 1 when a prefix given in tailwind.container_prefixes matches no size token.

Naming that differs between brands is read from tokens.json `tailwind` (all keys optional):
  breakpoints        {"<breakpoint token>": "<variant>"}  default: derived from breakpoint-<step>
  shadow_names       {"<shadow token>": "<theme name>"}  default {"focus-ring": "focus"}
  text_shadow        {"<shadow token>": "<theme name>"}  tokens emitted as --text-shadow-*; default {}
  container_prefixes [size token prefixes for max-w-*]   default ["size-layout-"]
  spacing_token      space token behind --spacing        default "space-4"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RESET = ["--color-*", "--font-*", "--text-*", "--font-weight-*", "--leading-*", "--tracking-*", "--radius-*",
         "--shadow-*", "--ease-*", "--breakpoint-*", "--container-*", "--text-shadow-*"]
BP_HEAD = "breakpoint-"
DEFAULTS = {
    "shadow_names": {"focus-ring": "focus"},
    "text_shadow": {},
    "container_prefixes": ["size-layout-"],
    "spacing_token": "space-4",
}


def fam_tokens(tok: dict, fam: str) -> list:
    """Token list of a top-level family; [] when the family is absent."""
    return (tok.get(fam) or {}).get("tokens", [])


def breakpoint_map(tok: dict) -> dict:
    """{breakpoint token: variant}: tokens.json `tailwind.breakpoints` when given, otherwise
    breakpoint-<step> -> <step>. Exits when breakpoint tokens exist and none can be mapped;
    {} when the brand has no breakpoint tokens."""
    names = [t["name"] for t in fam_tokens(tok, "breakpoint")]
    given = (tok.get("tailwind") or {}).get("breakpoints")
    if given:
        unknown = [n for n in given if n not in names]
        if unknown:
            raise SystemExit("tailwind.breakpoints names unknown breakpoint tokens: %s" % ", ".join(unknown))
        return dict(given)
    derived = {n: n[len(BP_HEAD):] for n in names if n.startswith(BP_HEAD) and len(n) > len(BP_HEAD)}
    if names and not derived:
        raise SystemExit("no usable breakpoint: name breakpoint tokens %s<step> or map them in tokens.json "
                         "tailwind.breakpoints" % BP_HEAD)
    return derived


def config(tok: dict) -> dict:
    """Tailwind naming config: DEFAULTS overlaid with tokens.json `tailwind`; breakpoints resolved."""
    cfg = dict(DEFAULTS, **(tok.get("tailwind") or {}))
    cfg["breakpoints"] = breakpoint_map(tok)
    given = (tok.get("tailwind") or {}).get("container_prefixes")
    if given:
        sizes = [t["name"] for t in fam_tokens(tok, "size")]
        unmatched = [p for p in given if not any(n.startswith(p) for n in sizes)]
        if unmatched:
            raise SystemExit("tailwind.container_prefixes match no size token: %s" % ", ".join(unmatched))
    return cfg


def prefix_of(tok: dict) -> str:
    p = (tok.get("css") or {}).get("prefix")
    if not p:
        raise SystemExit("tokens.json has no css.prefix")
    return p


def strip(name: str, head: str) -> str:
    return name[len(head):] if name.startswith(head) else name


def theme_entries(tok: dict):
    """Return [(section comment, [(theme variable, value)])] in a fixed order."""
    p = prefix_of(tok)
    cfg = config(tok)
    BP_NAMES, SHADOW_NAMES, TEXT_SHADOW = cfg["breakpoints"], cfg["shadow_names"], cfg["text_shadow"]

    def v(name):
        return "var(--%s-%s)" % (p, name)

    out = []
    bps = [(("--breakpoint-" + BP_NAMES[t["name"]]), t["value"]) for t in fam_tokens(tok, "breakpoint") if t["name"] in BP_NAMES]
    out.append(("breakpoint: literals (media queries cannot use var()), kept in sync with tokens.json", bps))
    out.append(("spacing: utility number x %s; allowed steps are listed in the package manual" % cfg["spacing_token"],
                [("--spacing", v(cfg["spacing_token"]))]))
    out.append(("color: semantic colours", [("--color-" + strip(t["name"], "color-"), v(t["name"]))
                                    for t in fam_tokens(tok, "color") if t.get("tier") == "semantic"]))
    ty = tok.get("type") or {}
    out.append(("font-family", [("--font-" + k, v("font-family-" + k)) for k in (ty.get("families") or {})]))
    texts = []
    for g in ty.get("groups") or []:
        for s in g["styles"]:
            n = s["name"]
            key = "--text-" + strip(n, "type-")
            texts += [(key, v(n + "-font-size")), (key + "--line-height", v(n + "-line-height")),
                      (key + "--font-weight", v(n + "-font-weight")), (key + "--letter-spacing", v(n + "-letter-spacing"))]
    out.append(("text: type styles (pair a font stack through font-*)", texts))
    sc = ty.get("scales") or {}

    def scale(name):
        return (sc.get(name) or {}).get("tokens", [])
    out.append(("font-weight", [("--font-weight-" + strip(t["name"], "font-weight-"), v(t["name"]))
                                for t in scale("font-weight") if t.get("tier") != "component"]))
    out.append(("leading", [("--leading-" + strip(t["name"], "line-height-"), v(t["name"]))
                            for t in scale("line-height") if t.get("tier") != "component"]))
    out.append(("tracking", [("--tracking-" + strip(t["name"], "letter-spacing-"), v(t["name"]))
                             for t in scale("letter-spacing") if t.get("tier") != "component"]))
    out.append(("radius", [("--radius-" + strip(t["name"], "radius-"), v(t["name"]))
                           for t in fam_tokens(tok, "radius") if t.get("tier") != "component"]))
    sh, tsh = [], []
    for t in fam_tokens(tok, "shadow"):
        if t.get("tier") == "component":
            continue
        if t["name"] in TEXT_SHADOW:
            tsh.append(("--text-shadow-" + TEXT_SHADOW[t["name"]], v(t["name"])))
        else:
            sh.append(("--shadow-" + SHADOW_NAMES.get(t["name"], t["name"]), v(t["name"])))
    out.append(("shadow", sh))
    out.append(("text-shadow", tsh))
    out.append(("ease", [("--ease-" + strip(t["name"], "easing-"), v(t["name"])) for t in fam_tokens(tok, "easing")]))
    out.append(("container: layout widths (max-w-*)", [("--container-" + strip(t["name"], "size-"), v(t["name"]))
                                                       for t in fam_tokens(tok, "size")
                                                       if t["name"].startswith(tuple(cfg["container_prefixes"]))]))
    return out


def render(tok: dict) -> str:
    lines = ["/* Generated by build_tailwind.py from tokens.json. Do not edit by hand.",
             "   Tailwind v4 theme: values point at tokens.css variables; load tokens.css first (see the tailwind entry file). */",
             "",
             "@theme inline {"]
    for r in RESET:
        lines.append("  %s: initial;" % r)
    for title, items in theme_entries(tok):
        lines.append("")
        lines.append("  /* %s */" % title)
        for k, val in items:
            lines.append("  %s: %s;" % (k, val))
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokens", required=True, help="tokens.json")
    ap.add_argument("--out", required=True, help="theme CSS to write or check")
    ap.add_argument("--check", action="store_true", help="compare only; exit 1 when the file differs")
    a = ap.parse_args(argv)
    css = render(json.loads(Path(a.tokens).read_text(encoding="utf-8")))
    out = Path(a.out)
    if a.check:
        same = out.exists() and out.read_text(encoding="utf-8") == css
        print("%s %s" % (out.name, "matches tokens.json" if same else "differs from regenerated output; rerun build_tailwind.py"))
        return 0 if same else 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(css.encode("utf-8"))
    print("wrote %s (%d lines)" % (out.name, css.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
