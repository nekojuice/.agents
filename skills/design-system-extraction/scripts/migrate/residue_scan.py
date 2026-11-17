#!/usr/bin/env python3
"""Inventory legacy-framework mechanism residue in a design-system package (read-only,
standard library only): block-element-modifier classes, forced-state classes and mechanism
keys of the component map.

Usage:
  python -I residue_scan.py --package <package-dir> [--prefix <css-prefix>]
         [--framework-words <regex>] [--json <out.json>]
  python -I residue_scan.py --selftest

Output: per text file, the hit counts of prefixed block / part (`__`) / modifier (`--`) names,
forced-state classes (`is-hover` ...) and framework words; then the mechanism keys found in
components/component-tokens.json (`bem`, `states`, forced-state class lists, variant / size /
semantic-state classes, compound rules). The prefix defaults to tokens.json `css.prefix`;
`<prefix>-preview-*`, `<prefix>-type-*` and `<prefix>-brand` are not counted as blocks.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TEXT = {".md", ".json", ".css", ".html", ".py", ".yaml"}


def scan(pkg: Path, pfx: str, fw_words=None):
    p = re.escape(pfx)
    part = re.compile(r"\b%s-(?!preview-)[a-z0-9-]+__[a-z0-9-]+" % p)
    mod = re.compile(r"\b%s-(?!preview-)[a-z0-9]+(?:-[a-z0-9]+)*--[a-z0-9-]+" % p)
    block = re.compile(r"(?<![\w-])\.?%s-(?!preview|type-|brand\b)[a-z0-9]+(?:-[a-z0-9]+)*(?![\w-])" % p)
    forced = re.compile(r"(?<![\w-])\.?is-(hover|active|focus|disabled|invalid)\b")
    fw = re.compile(fw_words) if fw_words else None
    rows = []
    for f in sorted(pkg.rglob("*")):
        if not f.is_file() or f.suffix not in TEXT or "__pycache__" in f.parts:
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        r = {"file": f.relative_to(pkg).as_posix(),
             "part": len(part.findall(t)), "modifier": len(mod.findall(t)),
             "forced": len(forced.findall(t)), "framework_words": len(fw.findall(t)) if fw else 0}
        r["block"] = len(block.findall(t))
        if any(r[k] for k in ("part", "modifier", "forced", "framework_words", "block")):
            rows.append(r)
    cm = pkg / "components" / "component-tokens.json"
    fields = {}
    if cm.exists():
        m = json.loads(cm.read_text(encoding="utf-8"))
        fields["forced_state_classes"] = m.get("forced_state_classes")
        fields["state_selectors.class"] = sorted({v.get("class") for v in (m.get("state_selectors") or {}).values() if v.get("class")})
        fields["preview_rules.outer_frame_class"] = (m.get("preview_rules") or {}).get("outer_frame_class")
        units = list((m.get("layout") or {}).items()) + list((m.get("components") or {}).items()) + [(x["id"], x) for x in m.get("patterns") or []]
        fields["units_with_bem"] = sum(1 for _k, u in units if "bem" in u)
        fields["units_with_states"] = sum(1 for _k, u in units if u.get("states"))
        fields["variant_class"] = sum(1 for _k, u in units for v in (u.get("variants") or {}).values() if "class" in v)
        fields["size_class"] = sum(1 for _k, u in units for v in (u.get("sizes") or {}).values() if "class" in v)
        fields["semantic_states.class"] = sum(1 for _k, u in units for v in (u.get("semantic_states") or {}).values() if "class" in v)
        fields["compound"] = sum(len(u.get("compound") or []) for _k, u in units)
    return rows, fields


def selftest():
    with tempfile.TemporaryDirectory() as d:
        pkg = Path(d)
        (pkg / "components").mkdir()
        (pkg / "tokens.json").write_text(json.dumps({"css": {"prefix": "x"}}), encoding="utf-8")
        (pkg / "components" / "a.md").write_text(
            '<div class="x-card x-card--wide"><span class="x-card__title is-active">t</span></div>\n'
            '<p class="x-preview-cell x-type-body-md">p</p>\n', encoding="utf-8")
        (pkg / "components" / "component-tokens.json").write_text(json.dumps({
            "components": {"card": {"bem": {"block": "x-card"}, "variants": {"card--wide": {"class": "x-card--wide"}}}}}),
            encoding="utf-8")
        rows, fields = scan(pkg, "x")
    by = {r["file"]: r for r in rows}
    md = by.get("components/a.md", {})
    checks = [
        ("part/modifier/forced", (md.get("part"), md.get("modifier"), md.get("forced")), (1, 1, 1)),
        ("blocks skip preview/type", md.get("block"), 1),
        ("map fields", (fields.get("units_with_bem"), fields.get("variant_class")), (1, 1)),
    ]
    fails = [c for c in checks if c[1] != c[2]]
    for name, got, want in fails:
        print("FAIL %s\n  got:  %r\n  want: %r" % (name, got, want))
    print("residue_scan selftest: %d/%d passed" % (len(checks) - len(fails), len(checks)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--package", help="package root to scan")
    ap.add_argument("--prefix", help="CSS prefix; default: tokens.json css.prefix")
    ap.add_argument("--framework-words", help="regex of legacy framework words (plug-in attribute prefixes, widget names); not counted when absent")
    ap.add_argument("--json", help="also write the result as JSON")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.package:
        ap.error("--package is required")
    pkg = Path(a.package)
    pfx = a.prefix or (json.loads((pkg / "tokens.json").read_text(encoding="utf-8")).get("css") or {}).get("prefix")
    if not pfx:
        ap.error("no --prefix given and tokens.json has no css.prefix")
    rows, fields = scan(pkg, pfx, a.framework_words)
    for r in rows:
        print("%-45s block=%-4d part=%-4d mod=%-4d forced=%-4d fw=%-3d" % (
            r["file"], r["block"], r["part"], r["modifier"], r["forced"], r["framework_words"]))
    print(json.dumps(fields, ensure_ascii=False, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"files": rows, "map_fields": fields}, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
