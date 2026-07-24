#!/usr/bin/env python3
"""Assemble a flat Thought Palette draft.json into an import-ready Library[] JSON.

Usage: python assemble.py <draft.json> [output.json]
Default output: import.json alongside the draft.

See SCHEMA.md for the draft format. This is the reference implementation;
assemble.mjs and assemble.ps1 must produce identical output.
"""
import json
import re
import sys
from pathlib import Path

# Windows consoles may default to a legacy codepage; keep CJK readable in the report
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

PROTECTED = ("未分類", "通用")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def main(argv):
    if len(argv) < 2:
        print("Usage: python assemble.py <draft.json> [output.json]", file=sys.stderr)
        return 2
    draft_path = Path(argv[1])
    out_path = Path(argv[2]) if len(argv) > 2 else draft_path.with_name("import.json")

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    errors, warnings = [], []

    library = draft.get("library") or "Analysis"
    elements = draft.get("elements") or []
    palettes = draft.get("palettes") or []

    # --- validate + index elements ---
    ele_by_id = {}
    for i, e in enumerate(elements):
        eid = e.get("id")
        if not eid:
            errors.append(f"elements[{i}] missing id")
            continue
        if eid in ele_by_id:
            errors.append(f"duplicate element id '{eid}'")
        if not SLUG_RE.match(str(eid)):
            warnings.append(f"element id '{eid}' is not a latin slug [a-z0-9-]")
        if not e.get("text"):
            warnings.append(f"element '{eid}' has empty text")
        if not e.get("storage_cat"):
            warnings.append(f"element '{eid}' has no storage_cat; filed under 未分類")
        ele_by_id[eid] = e

    referenced = set()

    # --- storage cats: protected first, then neutral source/subsystem cats in first-seen order ---
    order = list(PROTECTED)
    buckets = {name: [] for name in PROTECTED}
    for e in elements:
        if not e.get("id"):
            continue
        cat = e.get("storage_cat") or "未分類"
        if cat not in buckets:
            buckets[cat] = []
            order.append(cat)
        buckets[cat].append({"ele_id": e["id"], "text": e.get("text", "")})
    storage_element = [
        {"cat_id": f"scat-{i + 1}", "cat_name": name, "cat_ele": buckets[name]}
        for i, name in enumerate(order)
    ]

    # --- palettes ---
    paletas = []
    for pi, p in enumerate(palettes):
        pname = p.get("name") or f"Palette {pi + 1}"
        u_cat = {"cat_id": f"pcat-{pi + 1}-u", "cat_name": "未分類",
                 "cat_base": 0, "cat_factor": 1, "cat_ele": []}
        g_cat = {"cat_id": f"pcat-{pi + 1}-g", "cat_name": "通用",
                 "cat_base": 0, "cat_factor": 1, "cat_color": "#FFFFFF", "cat_ele": []}
        protected_targets = {"未分類": u_cat, "通用": g_cat}
        out_cats = [u_cat, g_cat]
        seen_in_palette = set()

        for ci, c in enumerate(p.get("cats") or []):
            cname = c.get("name") or f"cat {ci + 1}"
            base = c.get("base", 0)
            factor = c.get("factor", 1)
            if not isinstance(base, (int, float)):
                errors.append(f"palette '{pname}' cat '{cname}' base is not numeric")
                base = 0
            if not isinstance(factor, (int, float)):
                errors.append(f"palette '{pname}' cat '{cname}' factor is not numeric")
                factor = 1
            if isinstance(base, (int, float)) and base < 0:
                warnings.append(f"palette '{pname}' cat '{cname}' has negative base ({base})")

            refs = []
            for pl in (c.get("elements") or []):
                ele = pl.get("ele")
                if ele not in ele_by_id:
                    errors.append(f"palette '{pname}' cat '{cname}' references unknown element '{ele}'")
                    continue
                if ele in seen_in_palette:
                    errors.append(f"palette '{pname}' references element '{ele}' more than once")
                    continue
                seen_in_palette.add(ele)
                referenced.add(ele)
                val = pl.get("val", 0)
                if not isinstance(val, (int, float)):
                    errors.append(f"palette '{pname}' cat '{cname}' element '{ele}' val is not numeric")
                    val = 0
                elif val < -5 or val > 5:
                    warnings.append(f"palette '{pname}' cat '{cname}' element '{ele}' val {val} outside -5..+5")
                refs.append({"ele_id": ele, "val": val, "index": len(refs)})

            color = c.get("color")
            if color is not None and not HEX_RE.match(str(color)):
                errors.append(f"palette '{pname}' cat '{cname}' color '{color}' is not #RRGGBB")
                color = None

            if cname in protected_targets:
                target = protected_targets[cname]
                target["cat_base"] = base
                target["cat_factor"] = factor
                if cname == "未分類" and color:
                    target["cat_color"] = color  # 通用 stays white
                for r in refs:
                    r["index"] = len(target["cat_ele"])
                    target["cat_ele"].append(r)
                continue

            cat = {"cat_id": f"pcat-{pi + 1}-{ci + 1}", "cat_name": cname,
                   "cat_base": base, "cat_factor": factor, "cat_ele": refs}
            if color:
                cat["cat_color"] = color
            out_cats.append(cat)

        if not g_cat["cat_ele"]:
            warnings.append(
                f"palette '{pname}' has an empty 通用 cat; consider cross-cutting elements "
                f"(documentation health, conventions, DX)")

        named = [c for c in out_cats if c["cat_name"] not in PROTECTED]
        if len(named) > 21:
            errors.append(f"palette '{pname}' has {len(named)} named cats (max 21)")
        elif len(named) > 11:
            warnings.append(f"palette '{pname}' has {len(named)} named cats (>11 may fatigue the user)")

        metadata = dict(p.get("metadata") or {})
        if p.get("kind"):
            metadata["kind"] = p["kind"]
        # preserve semantic group hints for future color mixing
        groups = {c.get("name"): c.get("group") for c in (p.get("cats") or []) if c.get("group")}
        if groups:
            metadata.setdefault("cat_groups", groups)

        paletas.append({"pal_id": f"pal-{pi + 1}", "pal_name": pname,
                        "metadata": metadata, "cats": out_cats})

    for eid in ele_by_id:
        if eid not in referenced:
            warnings.append(f"element '{eid}' is not referenced by any palette")

    lib = {"storage_id": "lib-1", "storage_name": library,
           "storage_element": storage_element, "paletas": paletas}
    output = [lib]

    report(errors, warnings, output)
    if errors:
        print(f"\nNOT written: resolve {len(errors)} error(s) first.", file=sys.stderr)
        return 1

    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")
    return 0


def report(errors, warnings, output):
    lib = output[0]
    print("=== Thought Palette assembly ===")
    print(f"library: {lib['storage_name']}")
    print(f"storage cats: {len(lib['storage_element'])}, "
          f"elements: {sum(len(c['cat_ele']) for c in lib['storage_element'])}")
    for p in lib["paletas"]:
        named = [c for c in p["cats"] if c["cat_name"] not in PROTECTED]
        print(f"palette '{p['pal_name']}' ({p['metadata'].get('kind', '-')}): "
              f"{len(named)} named cats, {sum(len(c['cat_ele']) for c in p['cats'])} refs")
    if warnings:
        print(f"\n{len(warnings)} WARNING(s):")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print(f"\n{len(errors)} ERROR(s):")
        for e in errors:
            print(f"  x {e}")
    if not errors and not warnings:
        print("no issues.")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
