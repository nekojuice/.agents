#!/usr/bin/env python3
"""Minimal self-test for css_index.py, contrast.py, profile_diff.py, sheet_residue.py and
batch_query.py (embedded samples, standard library only).

Usage:
  python -I selftest.py [--tmp <scratch-dir>]

Without --tmp the fixture tree is written to a temporary directory and removed afterwards.
Exit 0 when every check passes.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


idx = load("css_index")
con = load("contrast")
pdiff = load("profile_diff")
resid = load("sheet_residue")
bq = load("batch_query")

RESULTS = []


def check(name, got, want):
    RESULTS.append((got == want, name, got, want))


# ---------------------------------------------------------------------------
SPEC_CASES = [
    ("*", [0, 0, 0]),
    ("li", [0, 0, 1]),
    ("ul li", [0, 0, 2]),
    ("ul ol+li", [0, 0, 3]),
    (".a", [0, 1, 0]),
    ("#x .a span", [1, 1, 1]),
    ("a:hover", [0, 1, 1]),
    ("a::before", [0, 0, 2]),
    ("a:before", [0, 0, 2]),
    ("input[type=\"text\"]", [0, 1, 1]),
    (":root", [0, 1, 0]),
    ("a:not(.x #y)", [1, 1, 1]),
    (":is(#a, .b) span", [1, 0, 1]),
    (":where(#a) .b", [0, 1, 0]),
    ("li:nth-child(2n+1)", [0, 1, 1]),
    ("li:nth-child(2n+1 of .x)", [0, 2, 1]),
    (".a :deep(.b)", [0, 2, 0]),
    (".a\\:hover", [0, 1, 0]),
    ("svg|rect", [0, 0, 1]),
    ("input::-webkit-input-placeholder", [0, 0, 2]),
]

SAMPLE_CSS = """@charset "UTF-8";
/* comment with { brace } and ; */
:root{--x-main:#123456;--gap: 8px }
.x-btn,  .x-btn-main:hover { color: var(--x-main); background:url("data:image/svg+xml;charset=utf8,%3Csvg%3E;}") no-repeat }
a[title="x,}y"] { content: "};{" ; margin:0 ! important }
@supports (display:grid) {
  @media screen and (max-width: 767px) {
    .grid > .cell { display:block!important; }
  }
}
@font-face { font-family: "X"; src: url(x.woff2) format("woff2"); }
@-webkit-keyframes spin { from { transform: rotate(0) } 50% { opacity:.5 } to { transform: rotate(360deg) } }
.ie { *zoom: 1; _height: 1px; filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#80000000', endColorstr='#80000000'); }
.min{a:1}.min2{b:2}
"""

SAMPLE_AT_TEMPLATE = """{!
    layout x-main
!}
<div class="x-box x-red" id="main" style="color:#fff; background-color: #000 !important">
<!-- <p style="color:red">old</p> -->
{! <style>.dead{color:red}</style> !}
<span style="width:{= width }px">x</span>
<style>
    .x-box { padding: 4px; }
    {@}media screen and (min-width:770px) {
        .x-box { padding: 8px; }
    }
</style>
<script>var h = '<i style="color:blue"></i>'; el.style = "x";</script>
"""

SAMPLE_VUE = """<template>
  <div class="x-card" :class="{ on: isOn }" :style="{ cursor: busy ? 'wait' : 'pointer' }">
    <p style="margin: 0">t</p>
  </div>
</template>
<script setup>
const busy = false
</script>
<style scoped>
.x-card { color: #333; }
.x-card :deep(.x-inner) { color: #444; }
:global(.x-page) .x-card { color: #555; }
</style>
<style>
.x-card { border: 1px solid #ccc; }
</style>
"""

PAGE = "views/Page.tpl"


def test_specificity():
    for sel, want in SPEC_CASES:
        got, _ = idx.specificity(sel)
        check("specificity %r" % sel, got, want)


def test_css_parse():
    p = idx.CssParser(SAMPLE_CSS).parse()
    rules = p.rules
    root = rules[0]
    check("root selector", root["selectors"][0]["text"], ":root")
    check("custom props", [(d["property"], d["value"]) for d in root["decls"]],
          [("--x-main", "#123456"), ("--gap", "8px")])
    check("root line (after comment)", root["line"], 3)
    btn = rules[1]
    check("comma split", [s["text"] for s in btn["selectors"]], [".x-btn", ".x-btn-main:hover"])
    check("comma split specificity", [s["specificity"] for s in btn["selectors"]], [[0, 1, 0], [0, 2, 0]])
    check("data URI kept intact", btn["decls"][1]["value"],
          "url(\"data:image/svg+xml;charset=utf8,%3Csvg%3E;}\") no-repeat")
    attr = rules[2]
    check("attr selector with comma not split", len(attr["selectors"]), 1)
    check("string with braces", attr["decls"][0]["value"], "\"};{\"")
    check("! important with space", (attr["decls"][1]["value"], attr["decls"][1]["important"]), ("0", True))
    grid = rules[3]
    check("nested conditions", [(c["type"], c["text"]) for c in grid["conditions"]],
          [("supports", "(display:grid)"), ("media", "screen and (max-width: 767px)")])
    check("nested rule line", grid["line"], 8)
    check("!important no space", (grid["decls"][0]["value"], grid["decls"][0]["important"]), ("block", True))
    ff = rules[4]
    check("font-face", (ff["kind"], ff["at_rule"], [d["property"] for d in ff["decls"]]),
          ("at-rule", "font-face", ["font-family", "src"]))
    kf = [r for r in rules if r["kind"] == "keyframe"]
    check("keyframes", [(r["prelude"], r["selectors"][0]["text"]) for r in kf],
          [("spin", "from"), ("spin", "50%"), ("spin", "to")])
    ie = [r for r in rules if r["selectors"] and r["selectors"][0]["text"] == ".ie"][0]
    check("legacy hacks", [d["property"] for d in ie["decls"]], ["*zoom", "_height", "filter"])
    mins = [r for r in rules if r["selectors"] and r["selectors"][0]["text"] in (".min", ".min2")]
    check("same-line columns", [(r["line"], r["col"]) for r in mins], [(14, 1), (14, 10)])
    check("order monotonic", [r["order"] for r in rules], list(range(1, len(rules) + 1)))
    check("statement @charset", [s["at_rule"] for s in p.statements], ["charset"])
    check("no warnings", p.warnings, [])


def quiet(fn, *a):
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return fn(*a)


def query_json(argv):
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(io.StringIO()):
        idx.main(argv)
    return json.loads(buf.getvalue())


def test_markup_and_profiles(tmp: Path):
    root = tmp / "root"
    for d in ("web/css", "views", "web/lib"):
        (root / d).mkdir(parents=True, exist_ok=True)
    (root / "web/css/base.css").write_text(".x-box{padding:0}\n.x-box.x-red{color:red}\n", encoding="utf-8")
    (root / "web/css/site.css").write_text(".x-box{padding:2px}\n", encoding="utf-8")
    (root / "web/lib/skip.css").write_text(".x-box{padding:9px}\n", encoding="utf-8")
    (root / PAGE).write_text(SAMPLE_AT_TEMPLATE, encoding="utf-8")
    (root / "views/Card.vue").write_text(SAMPLE_VUE, encoding="utf-8")
    prof = {"profiles": [{"id": "P1", "files": [
        {"path": "$root/web/css/site.css", "position": "head", "order": 2, "condition": None},
        {"path": "/web/css/base.css", "position": "head", "order": 1, "condition": None},
        {"path": "<page>", "position": "head", "order": 3, "condition": None},
        {"path": "web/css/missing.css", "position": "body-end", "order": 4, "condition": None}]},
        {"id": "P0", "files": [{"path": "web/css/base.css", "position": "head", "order": 1}]}],
        "pages": {PAGE: "P1"}}
    (tmp / "profiles.json").write_text(json.dumps(prof), encoding="utf-8")
    out = tmp / "out/index.json"
    common = ["--root", str(root), "--include", "web", "--include", "views", "--exclude", "web/lib", "--template-ext", ".tpl",
              "--template-comment", r"\{!.*?!\}", "--template-expr", r"\{=", "--template-unescape", "{@}=@"]
    quiet(idx.main, ["index"] + common + ["--tag", "web/css/base.css=third-party-base",
                                          "--profiles", str(tmp / "profiles.json"), "--root-alias", "$root/", "--out", str(out)])
    doc = idx.load_index(out)
    paths = [(s["path"], s["type"], s["tag"]) for s in doc["sources"]]
    check("excluded dir skipped", any("lib/" in p for p, _, _ in paths), False)
    check("tag applied", [t for p, _, t in paths if p.endswith("base.css")], ["third-party-base"])
    tpl_blocks = [s for s in doc["sources"] if s["type"] == "template-style-block"]
    check("template style blocks (incl. commented)", [(s["line"], s["commented_out"]) for s in tpl_blocks],
          [(6, True), (8, False)])
    live = tpl_blocks[1]
    rr = [r for r in doc["rules"] if r["source"] == live["id"]]
    check("escaped media unescaped", [(r["line"], r["media"]) for r in rr],
          [(9, None), (11, "screen and (min-width:770px)")])
    vue_blocks = [s for s in doc["sources"] if s["type"] == "vue-style-block"]
    check("vue scoped flags", [s["scoped"] for s in vue_blocks], [True, False])
    vr = [r for r in doc["rules"] if r["source"] == vue_blocks[0]["id"]]
    check("vue scoped compiled specificity",
          [(r["selectors"][0]["specificity"], r["selectors"][0]["specificity_compiled"]) for r in vr],
          [([0, 1, 0], [0, 2, 0]), ([0, 2, 0], [0, 3, 0]), ([0, 2, 0], [0, 2, 0])])
    ins = [(i["path"].split("/")[-1], i["line"], i["kind"], i["commented_out"], i["in_script"],
            tuple(i.get("dynamic", []))) for i in doc["inline_styles"]]
    check("inline styles", ins, [
        ("Card.vue", 2, "inline-style-binding", False, False, ("vue-binding",)),
        ("Card.vue", 3, "inline-style", False, False, ()),
        ("Page.tpl", 4, "inline-style", False, False, ()),
        ("Page.tpl", 5, "inline-style", True, False, ()),
        ("Page.tpl", 7, "inline-style", False, False, ("template-expression",)),
        ("Page.tpl", 14, "inline-style", False, True, ()),
    ])
    first = doc["inline_styles"][2]
    check("inline element context", (first["element"].get("id"), first["element"].get("class")), ("main", "x-box x-red"))
    check("inline important", [(d["property"], d["important"]) for d in first["decls"]],
          [("color", False), ("background-color", True)])
    prof_out = doc["profiles"]["profiles"][0]
    check("profile file order", [f["path"] for f in prof_out["files"]],
          ["/web/css/base.css", "$root/web/css/site.css", "<page>", "web/css/missing.css"])
    check("profile missing flagged", [f.get("found") for f in prof_out["files"]], [True, True, None, False])
    q = query_json(["query", "--index", str(out), "--class", "x-box", "--page", PAGE, "--property", "padding", "--json"])
    check("query by class in page order", [(r["path"].split("/")[-1], r["global_order"], r["decls"][0]["value"])
                                           for r in q["rules"]],
          [("base.css", 1, "0"), ("site.css", 3, "2px"), ("Page.tpl", 4, "4px"), ("Page.tpl", 5, "8px")])

    rows = pdiff.diff(doc, idx, "P0", "P1", classes=["x-box"])
    check("profile_diff padding winner", [(r["selector"], r["property"], r["a"]["value"], r["b"]["value"]) for r in rows],
          [(".x-box", "padding", "0", "2px")])
    res = resid.residue(resid.load(out), "web/css/base.css", "web/css/site.css")
    check("sheet_residue not overridden", [(r["selector"], r["property"], r["first"]) for r in res],
          [(".x-box.x-red", "color", "red")])
    text = bq.run(idx, doc, ["# comment", "", "--class x-box --profile P0 --property padding",
                             "--class x-box --profile NOPE"])
    check("batch_query blocks", [ln for ln in text.splitlines() if ln.startswith(("===", "!!"))],
          ["=== --class x-box --profile P0 --property padding", "=== --class x-box --profile NOPE",
           "!! profile not found in index: NOPE"])

    prof2 = {"profiles": [{"id": "P2", "files": [
        {"path": "web/css/base.css", "position": "head", "order": 1},
        {"path": "web/css/site.css", "position": "body-end", "order": 2}]}],
        "pages": {PAGE: "P2"},
        "page_extras": {PAGE: [{"path": PAGE, "lines": [8, 13], "position": "head", "kind": "inline-style"}]}}
    (tmp / "profiles2.json").write_text(json.dumps(prof2), encoding="utf-8")
    out2 = tmp / "out/index2.json"
    quiet(idx.main, ["index"] + common + ["--profiles", str(tmp / "profiles2.json"), "--out", str(out2)])
    doc2 = idx.load_index(out2)
    pe = doc2["profiles"]["page_extras"][PAGE][0]
    check("page_extras lines filter picks live block only", (pe["found"], len(pe["sources"])), (True, 1))
    q = query_json(["query", "--index", str(out2), "--class", "x-box", "--page", PAGE, "--property", "padding", "--json"])
    check("page_extras head block before body-end file",
          [(r["path"].split("/")[-1], r["global_order"], r["decls"][0]["value"]) for r in q["rules"]],
          [("base.css", 1, "0"), ("Page.tpl", 3, "4px"), ("Page.tpl", 4, "8px"), ("site.css", 5, "2px")])


def test_contrast():
    r = con.contrast("#000", "#fff")
    check("contrast #000/#fff", r["ratio"], 21.0)
    check("contrast #000/#fff AAA", r["pass"]["AAA_normal"], True)
    r = con.contrast("#fff", "#fff")
    check("contrast same color", r["ratio"], 1.0)
    r = con.contrast("#777777", "#ffffff")
    check("contrast #777/#fff", (r["ratio"], r["pass"]["AA_normal"], r["pass"]["AA_large"]), (4.48, False, True))
    r = con.contrast("#767676", "white")
    check("contrast #767676/white AA", (r["ratio"], r["pass"]["AA_normal"]), (4.54, True))
    r = con.contrast("rgba(0,0,0,0.5)", "#ffffff")
    check("rgba over white", (r["fg_effective"], r["ratio"]), ("#808080", 3.98))
    r = con.contrast("rgb(255 255 255)", "rgba(0, 0, 0, .5)", base="#ffffff")
    check("rgb space syntax on translucent bg", (r["bg_effective"], r["ratio"]), ("#808080", 3.98))
    check("hsl parse", con.to_hex(con.parse_color("hsl(120, 100%, 25%)")), "#008000")
    check("hex8 alpha", round(con.parse_color("#00000080")[3], 3), 0.502)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tmp", help="scratch directory for the fixture tree (default: a temporary directory)")
    a = ap.parse_args(argv)
    test_specificity()
    test_css_parse()
    test_contrast()
    if a.tmp:
        d = Path(a.tmp) / "css-index-selftest"
        d.mkdir(parents=True, exist_ok=True)
        test_markup_and_profiles(d)
    else:
        with tempfile.TemporaryDirectory() as d:
            test_markup_and_profiles(Path(d))
    fails = [r for r in RESULTS if not r[0]]
    for ok, name, got, want in fails:
        print("FAIL %s\n  got:  %r\n  want: %r" % (name, got, want))
    print("%d/%d passed" % (len(RESULTS) - len(fails), len(RESULTS)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
