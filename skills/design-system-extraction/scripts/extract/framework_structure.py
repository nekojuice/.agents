#!/usr/bin/env python3
"""Structural check of a vendored CSS framework file when no pristine copy is available.

Usage:
  python -I framework_structure.py --css <vendored.css> [--reference <other-version.css>]
         [--probe "<selector>"]... [--out <report.json>]
  python -I framework_structure.py --selftest

Reports (JSON to stdout or --out):
  - header comment, byte size, line count, CRLF line count, BOM, trailing sourceMappingURL
  - custom properties declared in :root
  - non-ASCII characters (line numbers + snippet), e.g. non-ASCII comments left by local edits
  - comments other than the leading license block
  - class tokens present in --css but absent from --reference (residual list for manual review)
  - declarations of each --probe selector (exact selector-text match) with line numbers
Standard library only. Does not decide whether the file was modified; it gives evidence.
"""
import argparse
import json
import os
import re
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
CLASS_RE = re.compile(r"\.(-?[_a-zA-Z][_a-zA-Z0-9-]*)")


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def strip_comments(text):
    return COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def iter_rules(text):
    """Yield (selector_text, body, start_pos) for innermost rules (handles @media nesting)."""
    clean = strip_comments(text)
    stack = []
    last = 0
    for i, ch in enumerate(clean):
        if ch == "{":
            stack.append((last, i))
            last = i + 1
        elif ch == "}":
            if stack:
                s, b = stack.pop()
                sel = clean[s:b].strip()
                body = clean[b + 1:i]
                if "{" not in body and not sel.startswith("@"):
                    yield sel, body, s + (len(clean[s:b]) - len(clean[s:b].lstrip()))
            last = i + 1
        elif ch == ";" and not stack:
            last = i + 1


def class_tokens(text):
    toks = set()
    for sel, _body, _pos in iter_rules(text):
        for m in CLASS_RE.finditer(re.sub(r"\[[^\]]*\]|url\([^)]*\)", "", sel)):
            toks.add(m.group(1))
    return toks


def report(css_path, reference=None, probes=()):
    raw = open(css_path, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    rep = {
        "file": css_path,
        "bytes": len(raw),
        "lines": text.count("\n") + (0 if text.endswith("\n") else 1),
        "crlf_lines": raw.count(b"\r\n"),
        "has_bom": raw.startswith(b"\xef\xbb\xbf"),
    }
    comments = [(m.start(), m.group(0)) for m in COMMENT_RE.finditer(text)]
    rep["header_comment"] = comments[0][1][:400] if comments else None
    rep["other_comments"] = [{"line": line_of(text, p), "text": c[:160]} for p, c in comments[1:]]
    sm = re.search(r"sourceMappingURL=([^\s*]+)", text)
    rep["source_mapping_url"] = sm.group(1) if sm else None

    nonascii = []
    for n, ln in enumerate(text.splitlines(), 1):
        if any(ord(c) > 127 for c in ln) and n > 1:
            nonascii.append({"line": n, "snippet": ln.strip()[:120]})
    rep["non_ascii_lines"] = nonascii[:200]
    rep["non_ascii_line_count"] = len(nonascii)

    root_vars = []
    for sel, body, pos in iter_rules(text):
        if sel == ":root":
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body):
                root_vars.append({"name": m.group(1), "value": m.group(2).strip()})
    rep["root_custom_properties"] = root_vars

    rules = list(iter_rules(text))
    rep["rule_count"] = len(rules)
    mine = class_tokens(text)
    rep["class_token_count"] = len(mine)
    if reference:
        ref_text = open(reference, "rb").read().decode("utf-8", errors="replace")
        rep["reference"] = reference
        rep["class_tokens_not_in_reference"] = sorted(mine - class_tokens(ref_text))

    out = {}
    for p in probes:
        hits = []
        for sel, body, pos in rules:
            sels = [s.strip() for s in sel.split(",")]
            if p in sels:
                decls = [d.strip() for d in body.split(";") if d.strip()]
                hits.append({"line": line_of(text, pos), "selector": sel[:120], "decls": decls})
        out[p] = hits
    rep["probes"] = out
    return rep


def selftest():
    css = ("/*! sample framework v0 */\n:root{--x-gap:4px;}\n.x-btn{color:#336699}\n"
           "@media (min-width:600px){.x-btn,.x-wide{padding:2px}}\n/* r\u00e9vision local note */\n.x-local{margin:0}\n")
    ref = "/*! sample framework v0 */\n.x-btn{color:#336699}\n.x-wide{padding:2px}\n"
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.css"), os.path.join(d, "b.css")
        open(a, "w", encoding="utf-8", newline="\n").write(css)
        open(b, "w", encoding="utf-8", newline="\n").write(ref)
        rep = report(a, b, [".x-btn"])
    checks = [
        ("root vars", rep["root_custom_properties"], [{"name": "--x-gap", "value": "4px"}]),
        ("not in reference", rep["class_tokens_not_in_reference"], ["x-local"]),
        ("probe hits", [h["line"] for h in rep["probes"][".x-btn"]], [3, 4]),
        ("non-ascii", rep["non_ascii_line_count"], 1),
        ("other comments", len(rep["other_comments"]), 1),
    ]
    fails = [c for c in checks if c[1] != c[2]]
    for name, got, want in fails:
        print("FAIL %s\n  got:  %r\n  want: %r" % (name, got, want))
    print("framework_structure selftest: %d/%d passed" % (len(checks) - len(fails), len(checks)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--css", help="vendored framework stylesheet")
    ap.add_argument("--reference", help="another version of the framework to diff class tokens against")
    ap.add_argument("--probe", action="append", default=[], help="exact selector text to list (repeatable)")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.css:
        ap.error("--css is required")
    out = json.dumps(report(a.css, a.reference, a.probe), ensure_ascii=False, indent=2)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
