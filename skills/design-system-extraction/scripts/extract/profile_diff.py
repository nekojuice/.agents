#!/usr/bin/env python3
"""Compare the "last same-selector declaration wins" result of two stack profiles.

Purpose: while resolving values per component, find where a variant profile (for example one
that loads an extra stylesheet group) and a baseline profile end with a different winning
declaration for the same selector, the same media condition and the same property.

Only identical selector text + identical media are compared: !important first, then global
order (later wins). Specificity contests between different selectors are not handled here and
still need a human reading.

Standard library only; css_index.py must sit next to this file.

Usage:
  python -I profile_diff.py --index <css-index.json> --a <profileA> --b <profileB>
         [--class <name>]... [--selector <fragment>]... [--page-a <view>] [--page-b <view>] [--json]
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_indexer():
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("css_index", here / "css_index.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def order_map_for(ix, doc, pid, page=None):
    profs = doc.get("profiles") or {}
    prof = next((p for p in profs.get("profiles", []) if p["id"] == pid), None)
    if prof is None:
        sys.exit("profile not found: %s" % pid)
    om, off = {}, 0
    for sid, cnt, lab in ix.page_segments(doc, prof, page):
        om.setdefault(sid, off)
        off += cnt
    return om


def winners(doc, om, pats, src_by_id):
    table = {}
    for r in doc["rules"]:
        if r["kind"] != "style" or r["source"] not in om:
            continue
        g = om[r["source"]] + r["order"]
        for s in r["selectors"]:
            if not any(p.search(s["text"]) for p in pats):
                continue
            for d in r["decls"]:
                key = (s["text"], r.get("media") or "", d["property"])
                cand = (bool(d.get("important")), g, d["value"],
                        "%s:%s" % (src_by_id[r["source"]]["path"], d["line"]))
                cur = table.get(key)
                if cur is None or (cand[0], cand[1]) > (cur[0], cur[1]):
                    table[key] = cand
    return table


def diff(doc, ix, a, b, classes=(), selectors=(), page_a=None, page_b=None):
    src_by_id = {s["id"]: s for s in doc["sources"]}
    pats = [re.compile(r"\." + re.escape(c) + r"(?![\w-])") for c in classes]
    pats += [re.compile(re.escape(s), re.I) for s in selectors]
    ta = winners(doc, order_map_for(ix, doc, a, page_a), pats, src_by_id)
    tb = winners(doc, order_map_for(ix, doc, b, page_b), pats, src_by_id)
    rows = []
    for key in sorted(set(ta) | set(tb)):
        x, y = ta.get(key), tb.get(key)
        vx = (x[2], x[0]) if x else None
        vy = (y[2], y[0]) if y else None
        if vx == vy:
            continue
        rows.append({"selector": key[0], "media": key[1] or None, "property": key[2],
                     "a": None if not x else {"value": x[2], "important": x[0], "at": x[3]},
                     "b": None if not y else {"value": y[2], "important": y[0], "at": y[3]}})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", required=True, help="index JSON written by css_index.py (with profiles)")
    ap.add_argument("--a", required=True, help="profile id A")
    ap.add_argument("--b", required=True, help="profile id B")
    ap.add_argument("--page-a", help="view whose page-level styles join profile A")
    ap.add_argument("--page-b", help="view whose page-level styles join profile B")
    ap.add_argument("--class", dest="cls", action="append", default=[], help="class name (repeatable)")
    ap.add_argument("--selector", action="append", default=[], help="selector fragment (repeatable)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not args.cls and not args.selector:
        ap.error("need --class or --selector")
    ix = load_indexer()
    doc = ix.load_index(Path(args.index))
    rows = diff(doc, ix, args.a, args.b, args.cls, args.selector, args.page_a, args.page_b)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    print("-- %d difference(s) %s vs %s" % (len(rows), args.a, args.b))
    for r in rows:
        fa = "-" if not r["a"] else "%s%s @%s" % (r["a"]["value"], " !imp" if r["a"]["important"] else "", r["a"]["at"])
        fb = "-" if not r["b"] else "%s%s @%s" % (r["b"]["value"], " !imp" if r["b"]["important"] else "", r["b"]["at"])
        print("%s%s | %s\n   A: %s\n   B: %s" % (r["selector"], " [%s]" % r["media"] if r["media"] else "",
                                              r["property"], fa, fb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
