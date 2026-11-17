#!/usr/bin/env python3
"""Find declarations of a first-loaded stylesheet that a later one does not override.

Purpose: when two copies of the same style set load one after the other (A first, B later),
only A's declarations that differ from or are missing in B still affect the page. Only
identical selector text and media conditions are compared; contests between different
selectors still need a human reading.

Usage:
  python -I sheet_residue.py --index <css-index.json> --first <A relative path>
         --second <B relative path> [--grep <selector substring>]... [--json]
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if "rule_files" in doc:
        doc["rules"] = []
        for name in doc["rule_files"]:
            doc["rules"].extend(json.loads((Path(path).parent / name).read_text(encoding="utf-8"))["rules"])
    return doc


def table(doc, sid):
    out = {}
    for r in doc["rules"]:
        if r["source"] != sid or r["kind"] != "style":
            continue
        for s in r["selectors"]:
            key = (s["text"], r.get("media") or "")
            d = out.setdefault(key, {})
            for decl in r["decls"]:
                d[decl["property"]] = (decl["value"], decl["important"], r["line"], decl["line"])
    return out


def residue(doc, first, second, grep=None):
    sid = {s["path"]: s["id"] for s in doc["sources"]}
    for p in (first, second):
        if p not in sid:
            sys.exit("source not found: %s" % p)
    A, B = table(doc, sid[first]), table(doc, sid[second])
    res = []
    for key, props in A.items():
        if grep and not any(g.lower() in key[0].lower() for g in grep):
            continue
        other = B.get(key, {})
        for prop, (val, imp, rline, dline) in props.items():
            o = other.get(prop)
            if o is None:
                res.append({"selector": key[0], "media": key[1], "property": prop, "first": val,
                            "first_important": imp, "first_line": dline, "second": None})
            elif (o[0].replace(" ", "").lower(), o[1]) != (val.replace(" ", "").lower(), imp) and not o[1] and imp:
                res.append({"selector": key[0], "media": key[1], "property": prop, "first": val,
                            "first_important": imp, "first_line": dline, "second": o[0], "second_line": o[3],
                            "note": "first is !important; second does not override"})
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", required=True, help="index JSON written by css_index.py")
    ap.add_argument("--first", required=True, help="relative path of the stylesheet loaded first")
    ap.add_argument("--second", required=True, help="relative path of the stylesheet loaded later")
    ap.add_argument("--grep", action="append", help="only selectors containing this substring (repeatable)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = residue(load(a.index), a.first, a.second, a.grep)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    for r in res:
        print("%s:%d  %s%s  { %s: %s%s }%s" % (a.first, r["first_line"], r["selector"],
                                                (" @" + r["media"]) if r["media"] else "", r["property"], r["first"],
                                                " !important" if r["first_important"] else "",
                                                ("  vs second L%d %s" % (r["second_line"], r["second"])) if r.get("second") else ""))
    print("-- %d residual declaration(s)" % len(res), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
