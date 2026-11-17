#!/usr/bin/env python3
"""Check a residue ledger row by row (standard library only).

Usage:
  python -I residue_ledger_check.py <ledger.md> [--package <package-dir>]
         [--section "<heading>"] [--categories "<a>,<b>,..."] [--delete-disposition "<text>"]
         [--ignore-prefix <rel-prefix>]...
  python -I residue_ledger_check.py --selftest

The ledger is a Markdown file whose detail section (a "## " heading, --section, default
"## Ledger") holds a table with six columns: number, location, content, category,
disposition (the template's "action"), location after disposition.
- every row needs a category, a disposition and a location after disposition (not empty, not
  a dash);
- the category must be one of --categories (default: the category IDs of the residue-ledger
  template: brand-value, mechanism-bound-value, motion, mechanism);
- with --package, back-quoted package paths in the "after" column (with a / or an extension)
  must exist, except paths under an --ignore-prefix; when the disposition equals
  --delete-disposition (default delete-file), back-quoted .css / .py paths in the location
  column must be gone.
Exit 1 when a problem is found or the table is empty.
"""
import argparse
import re
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_SECTION = "## Ledger"
DEFAULT_CATEGORIES = ["brand-value", "mechanism-bound-value", "motion", "mechanism"]
DEFAULT_DELETE = "delete-file"


def rows(text, section):
    m = re.search(r"^" + re.escape(section.strip()) + r"[ \t]*$", text, re.M)
    if not m:
        return
    sec = text[m.end():].split("\n## ", 1)[0]
    for ln in sec.splitlines():
        if ln.startswith("| ") and not ln.startswith("| #") and not ln.startswith("| ---"):
            yield [c.strip() for c in ln.strip().strip("|").split("|")]


def check(text, pkg=None, section=DEFAULT_SECTION, cats=DEFAULT_CATEGORIES, delete=DEFAULT_DELETE, ignore=()):
    probs, n = [], 0
    for cells in rows(text, section):
        n += 1
        if len(cells) != 6:
            probs.append("column count %d: %s" % (len(cells), cells[:2]))
            continue
        no, loc, what, cat, disp, after = cells
        if cat not in cats:
            probs.append("#%s category %s" % (no, cat))
        for k, v in (("disposition", disp), ("location after disposition", after)):
            if not v or v in ("\u2014", "-"):
                probs.append("#%s missing %s" % (no, k))
        if pkg:
            for p in re.findall(r"`([\w./*-]+\.(?:md|css|json|py|html))`", after):
                if "*" not in p and "<" not in p and not (pkg / p).exists() and not p.startswith(tuple(ignore)):
                    probs.append("#%s location after disposition does not exist: %s" % (no, p))
            if disp == delete:
                for p in re.findall(r"`([\w./-]+\.(?:css|py))`", loc):
                    if (pkg / p).exists():
                        probs.append("#%s should be deleted: %s" % (no, p))
    return n, probs


def selftest():
    ledger = "\n".join([
        "# Residue ledger", "", "## Categories", "", "| ID | Category |", "| --- | --- |",
        "| `motion` | Motion duration |", "", "## Ledger", "",
        "| # | Location | Content | Category | Action | Location after action |",
        "| --- | --- | --- | --- | --- | --- |",
        "| 1 | `components/a.md` | value | brand-value | keep | `components/a.md` |",
        "| 2 | `components/old.css` | file | mechanism | delete-file | `DESIGN.md` |",
        "| 3 | `x.md` | value | other | keep | - |",
        "", "## Version log feed", ""])
    with tempfile.TemporaryDirectory() as d:
        pkg = Path(d)
        (pkg / "components").mkdir()
        (pkg / "components" / "a.md").write_text("a", encoding="utf-8")
        (pkg / "components" / "old.css").write_text("a", encoding="utf-8")
        n, probs = check(ledger, pkg)
    want = ["#2 location after disposition does not exist: DESIGN.md", "#2 should be deleted: components/old.css",
            "#3 category other", "#3 missing location after disposition"]
    ok = n == 3 and probs == want
    if not ok:
        print("FAIL\n  got:  %r %r\n  want: 3 %r" % (n, probs, want))
    print("residue_ledger_check selftest: %s" % ("1/1 passed" if ok else "0/1 passed"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ledger", nargs="?", help="ledger Markdown file")
    ap.add_argument("--package", help="package root the paths are relative to")
    ap.add_argument("--section", default=DEFAULT_SECTION, help="heading line of the detail section")
    ap.add_argument("--categories", help="comma-separated allowed categories")
    ap.add_argument("--delete-disposition", default=DEFAULT_DELETE, help="disposition text meaning 'file deleted'")
    ap.add_argument("--ignore-prefix", action="append", default=[], help="relative path prefix not required to exist (repeatable)")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.ledger:
        ap.error("ledger file is required")
    cats = [x.strip() for x in a.categories.split(",")] if a.categories else DEFAULT_CATEGORIES
    n, probs = check(Path(a.ledger).read_text(encoding="utf-8"), Path(a.package) if a.package else None,
                     a.section, cats, a.delete_disposition, a.ignore_prefix)
    for p in probs:
        print("FAIL", p)
    print("%d rows, %d problems" % (n, len(probs)))
    return 1 if probs or n == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
