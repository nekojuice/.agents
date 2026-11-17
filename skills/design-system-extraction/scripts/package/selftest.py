#!/usr/bin/env python3
"""Self-test for the package scripts: builds a minimal neutral package in a temporary folder,
runs build_tokens / build_tailwind / build_contrast / build_preview, checks idempotency with
--check, then runs check_package --stage data and --stage full (standard library only).
Also covers: breakpoints derived from breakpoint-<step> tokens, the failure when breakpoint
tokens exist but none can be mapped, and an empty breakpoint section without a breakpoint
family; size-layout- tokens as max-w containers and a container prefix that matches nothing;
optional families; #rgba / #rrggbbaa colours; the --invocation policy choice; and a
Phase 1 snapshot package (layered schema, origin source, orphan residue primitive) that passes
check_package --stage data with --allow-orphans and gets colour swatches in the preview.

Usage:
  python -I selftest.py [--keep <scratch-dir>]

--keep writes the fixture package under <scratch-dir>/package-selftest and leaves it there.
No real Tailwind CLI is used: a stand-in CLI copies the hand-written preview/tailwind.css
fixture, so the full stage's recompile comparison runs; the full stage without a CLI must fail.
Exit 0 when every check passes.
"""
import argparse
import copy
import os
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
SCRIPTS = ["build_tokens.py", "build_tailwind.py", "build_contrast.py", "build_preview.py", "check_package.py"]


def tk(name, value, tier="primitive", origin="source", usage="sample"):
    return {"name": name, "value": value, "tier": tier, "origin": origin, "usage": usage}


TOKENS = {
    "name": "x-sample", "version": "0.1", "css": {"prefix": "x"}, "themes": [{"id": "default", "name": "Default"}],
    "color": {"tokens": [
        tk("palette-blue-600", "#336699"), tk("palette-neutral-0", "#ffffff"), tk("palette-neutral-900", "#222222"),
        tk("color-action-primary", "{palette-blue-600}", "semantic"),
        tk("color-surface-canvas", "{palette-neutral-0}", "semantic"),
        tk("color-text-default", "{palette-neutral-900}", "semantic"),
        tk("color-focus-ring", "{palette-blue-600}", "semantic", "added")]},
    "type": {
        "families": {"sans": {"value": "system-ui, sans-serif", "tier": "primitive", "origin": "source", "usage": "ui text"}},
        "scales": {"font-family": {"tokens": []}, "font-size": {"tokens": [tk("font-size-16", "16px")]},
                   "line-height": {"tokens": [tk("line-height-normal", 1.5)]},
                   "font-weight": {"tokens": [tk("font-weight-regular", 400)]},
                   "letter-spacing": {"tokens": [tk("letter-spacing-normal", "0px")]}},
        "groups": [{"name": "Body", "note": "body text", "styles": [{
            "name": "type-body-md", "family": "{font-family-sans}", "fontSize": "{font-size-16}",
            "lineHeight": "{line-height-normal}", "fontWeight": "{font-weight-regular}",
            "letterSpacing": "{letter-spacing-normal}", "tier": "semantic", "origin": "source", "usage": "body",
            "breakpoints": [{"min": "breakpoint-md", "fontSize": "{font-size-16}"}]}]}]},
    "space": {"tokens": [tk("space-4", "4px"), tk("space-8", "8px")]},
    "radius": {"tokens": [tk("radius-sm", "4px")]},
    "shadow": {"tokens": [tk("focus-ring", "0 0 0 2px {color-focus-ring}", "semantic", "added")]},
    "size": {"tokens": [tk("size-control-40", "40px")]},
    "duration": {"tokens": [tk("duration-150", "150ms")]},
    "easing": {"tokens": [tk("easing-standard", "ease")]},
    "breakpoint": {"tokens": [tk("breakpoint-sm", "576px"), tk("breakpoint-md", "768px")]},
}

# Phase 1 snapshot: same layered schema, every entry origin source, role values written as
# literals, one coexisting component colour, one unbranded residue colour, and a scale step that
# nothing references yet (an orphan primitive).
TOKENS_P1 = copy.deepcopy(TOKENS)
TOKENS_P1["color"] = {"tokens": [
    tk("color-action-primary", "#336699", "semantic"),
    tk("color-surface-canvas", "#ffffff", "semantic"),
    tk("color-text-default", "#222222", "semantic"),
    dict(tk("color-sample-button-border", "#2a5580", "component", usage="component-specific; primary is `color-action-primary`"),
         component="sample-button"),
    tk("residue-focus-glow", "rgba(51, 102, 153, 0.25)", "semantic", usage="unbranded residue, do not use in new work")]}
TOKENS_P1["shadow"] = {"tokens": []}
TOKENS_P1["space"]["tokens"].append(tk("space-12", "12px"))

CMAP = {
    "keywords": [],
    "state_selectors": {"hover": {"tailwind": ["hover"]}},
    "preview_rules": {"layout_file": "preview/foundations/layout.html", "lang": "en"},
    "literals": [],
    "layout": {},
    "components": {"sample-button": {
        "name": "Button", "group": "actions", "summary": "Primary action", "anchor": "sample-button--primary",
        "spec": "components/sample-button.md",
        "preview": {"file": "preview/components/sample-button.html", "anchors": ["sample-button--primary"]},
        "anatomy": ["root"],
        "parts": {"root": {"default": {"color": {"token": "color-surface-canvas"}, "padding": {"tokens": ["space-8"]}}}},
        "variants": {"sample-button--primary": {"parts": {"root": {
            "default": {"background-color": {"token": "color-action-primary"}},
            "hover": {"box-shadow": {"token": "focus-ring"}}}}}}}},
    "patterns": [],
}

CMAP_P1 = copy.deepcopy(CMAP)
CMAP_P1["components"]["sample-button"]["variants"]["sample-button--primary"]["parts"]["root"] = {
    "default": {"background-color": {"token": "color-action-primary"},
                "border-color": {"token": "color-sample-button-border"}}}

CONTRAST = {
    "note": "Sample.", "method": "WCAG 2.x", "class_rule": "normal / large / ui",
    "source_pairs": [{"id": "pair-1", "kind": "brand", "fg": "color-text-default", "bg": "color-surface-canvas",
                      "class": "normal", "context": "body text"}],
    "added_states": {"threshold": 3.0, "focus_ring": "2px ring",
                     "surfaces": [{"surface": "color-surface-canvas", "controls": True, "ring": "default"}],
                     "checks": [{"state": "focus-visible", "fg": "color-focus-ring", "scope": "all"}]},
}

GAPS = {"note": "Known gaps.", "gaps": [{"id": "gap-1", "title": "Sample gap", "detail": "Neutral detail."}]}

FRAG = """<!doctype html>
<html><head><meta charset="utf-8"><title>fragment</title></head><body>
<!-- x-preview:begin -->
%s
<!-- x-preview:end -->
</body></html>
"""

BUTTON = ('<article class="x-preview-card" id="sample-button--primary"><div class="x-preview-cell__stage">'
          '<button class="bg-action-primary text-surface-canvas p-2 rounded-sm" type="button">Go</button></div></article>')

BASE_CSS = """/* tokens in use: var(--x-breakpoint-sm) var(--x-breakpoint-md) var(--x-space-4) */
body { color: var(--x-color-text-default); background-color: var(--x-color-surface-canvas); }
.x-surface { padding: var(--x-space-8); border-radius: var(--x-radius-sm); min-height: var(--x-size-control-40);
  transition-duration: var(--x-duration-150); transition-timing-function: var(--x-easing-standard); }
"""

TAILWIND_FIXTURE = """/*! fixture */
.bg-action-primary{background-color:var(--color-action-primary)}
.text-surface-canvas{color:var(--color-surface-canvas)}
.p-2{padding:calc(var(--spacing)*2)}
.rounded-sm{border-radius:var(--radius-sm)}
"""

DESIGN = """# Sample design system

Read [components](components/README.md) first.

## Legacy usage

The old markup used `<div class="x-banned">`.

## Tokens

Use `--x-color-action-primary` for primary actions.
"""

FORBID = """[allow]
[substring]
x-secret-word
[class]
x-banned
[regex]
\\bx-legacy-\\d+\\b
"""


def write(p: Path, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False, indent=2) + "\n"
    p.write_bytes(text.encode("utf-8"))


def make_package(pkg: Path, tokens=None, cmap=None, contrast=None):
    write(pkg / "tokens.json", tokens or TOKENS)
    write(pkg / "components" / "component-tokens.json", cmap or CMAP)
    write(pkg / "data" / "contrast.json", contrast or CONTRAST)
    write(pkg / "data" / "gaps.json", GAPS)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><circle cx="4" cy="4" r="4" fill="currentColor"/></svg>\n'
    write(pkg / "assets" / "x-dot.svg", svg)
    data = svg.encode("utf-8")
    write(pkg / "assets" / "README.md", "# Assets\n\n- Sample assets.\n\n| file | format | size | bytes | usage | used by | sha-256 |\n"
          "| --- | --- | --- | --- | --- | --- | --- |\n"
          "| `x-dot.svg` | SVG | 8x8 | %d | dot (inverse) | sample-button | %s |\n\n1 files, %d bytes\n"
          % (len(data), hashlib.sha256(data).hexdigest(), len(data)))
    write(pkg / "base.css", BASE_CSS)
    write(pkg / "tailwind" / "index.css", '@import "tailwindcss" source(none);\n@import "./theme.css";\n')
    write(pkg / "preview" / "foundations" / "layout.html", FRAG % '<p class="x-preview-lead">Layout sample.</p>')
    write(pkg / "preview" / "foundations" / "cover.html", FRAG % '<h1 class="x-preview-h1">Sample</h1>')
    write(pkg / "preview" / "components" / "sample-button.html", FRAG % BUTTON)
    write(pkg / "preview" / "preview.css", ".x-preview-page { font-family: system-ui, sans-serif; }\n")
    write(pkg / "preview" / "tailwind.css", TAILWIND_FIXTURE)
    write(pkg / "components" / "README.md", "# Components\n\n- [Button](sample-button.md)\n")
    write(pkg / "components" / "sample-button.md", "# Button\n\n## Variants\n\n### `sample-button--primary`\n\nPrimary action.\n")
    write(pkg / "DESIGN.md", DESIGN)
    write(pkg / "SKILL.md", "\n".join(["---", "name: x-sample", "description: Sample package.",
                                       "disable-model-invocation: true", "metadata:", '  version: "0.1"', "---", "",
                                       "# Sample", "", "See [DESIGN.md](DESIGN.md).", ""]))
    write(pkg / "agents" / "openai.yaml", "\n".join(["policy:", "  allow_implicit_invocation: false", ""]))
    (pkg / "scripts").mkdir(parents=True, exist_ok=True)
    for s in SCRIPTS:
        shutil.copyfile(HERE / s, pkg / "scripts" / s)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fake_cli(folder: Path, fixture: Path) -> str:
    """A stand-in Tailwind CLI: copies the fixture CSS to its -o argument."""
    folder.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        p = folder / "fake-tailwind.cmd"
        p.write_bytes(('@echo off\r\ncopy /b /y "%s" "%%4" >nul\r\n' % fixture).encode("utf-8"))
    else:
        p = folder / "fake-tailwind"
        p.write_bytes(('#!/bin/sh\ncp "%s" "$4"\n' % fixture).encode("utf-8"))
        p.chmod(0o755)
    return str(p)


def run(args):
    r = subprocess.run([sys.executable, "-I"] + [str(a) for a in args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", help="scratch directory to keep the fixture package in")
    a = ap.parse_args(argv)
    results = []

    def check(name, cond, detail=""):
        results.append((bool(cond), name, detail))

    def body(pkg: Path):
        make_package(pkg)
        s = pkg / "scripts"
        tok = pkg / "tokens.json"
        steps = [
            ("build_tokens", [s / "build_tokens.py", "--tokens", tok, "--css", pkg / "tokens.css", "--dtcg", pkg / "tokens.dtcg.json"]),
            ("build_tailwind", [s / "build_tailwind.py", "--tokens", tok, "--out", pkg / "tailwind" / "theme.css"]),
            ("build_contrast", [s / "build_contrast.py", "--tokens", tok, "--contrast", pkg / "data" / "contrast.json"]),
            ("build_preview", [s / "build_preview.py", "--package", pkg]),
        ]
        for name, args in steps:
            rc, out = run(args)
            check(name + " runs", rc == 0, out.strip()[-300:])
            rc, out = run(args + ["--check"])
            check(name + " --check idempotent", rc == 0, out.strip()[-300:])
        css = (pkg / "tokens.css").read_text(encoding="utf-8")
        check("tokens.css uses the configured prefix", "--x-color-action-primary: var(--x-palette-blue-600);" in css)
        check("type breakpoint override", "@media (min-width: 768px)" in css)
        theme = (pkg / "tailwind" / "theme.css").read_text(encoding="utf-8")
        check("theme breakpoints derived from breakpoint-<step> tokens", "--breakpoint-sm: 576px;" in theme and "--breakpoint-lg" not in theme.replace("--breakpoint-*", ""))
        check("theme focus shadow name", "--shadow-focus: var(--x-focus-ring);" in theme)
        cdoc = json.loads((pkg / "data" / "contrast.json").read_text(encoding="utf-8"))
        check("contrast recomputed", cdoc["source_pairs"][0]["ratio"] == 15.91 and cdoc["added_states"]["pass"] is True,
              str(cdoc["source_pairs"][0].get("ratio")))
        page = (pkg / "preview.html").read_text(encoding="utf-8")
        check("preview card enriched", "token mapping (component-tokens.json" in page and 'id="sample-button--primary"' in page)
        check("preview inverse asset tile", "x-preview-asset__view--inverse" in page)

        forbid = pkg.parent / "forbid.txt"
        write(forbid, FORBID)
        chk = s / "check_package.py"
        rc, out = run([chk, "--stage", "data", "--package", pkg])
        check("check_package --stage data", rc == 0, out.strip()[-600:])
        cli = fake_cli(pkg.parent, pkg / "preview" / "tailwind.css")
        nocli = [chk, "--stage", "full", "--package", pkg, "--forbid-list", forbid, "--section-allow-heading", "Legacy"]
        rc, out = run(nocli)
        check("full stage without a Tailwind CLI fails", rc == 1 and "Tailwind CLI given" in out, out.strip()[-300:])
        full = [chk, "--stage", "full", "--package", pkg, "--forbid-list", forbid, "--expect-version", "0.1",
                "--plan-id-regex", r"\bPLAN-\d+\b", "--must-not-exist", "components/retired.css", "--tailwind-cli", cli]
        rc, out = run(full + ["--section-allow-heading", "Legacy"])
        check("check_package --stage full", rc == 0, "\n".join(ln for ln in out.splitlines() if ln.startswith("[FAIL]"))[-800:])
        rc, out = run(full)
        check("forbid class outside allowed section fails", rc == 1 and "class x-banned" in out)
        write(pkg / "components" / "retired.css", "/* retired */\n")
        rc, out = run(full + ["--section-allow-heading", "Legacy"])
        check("must-not-exist detected", rc == 1 and "must not exist: components/retired.css" in out)
        (pkg / "components" / "retired.css").unlink()

        # invocation policy (S6)
        base = full + ["--section-allow-heading", "Legacy"]
        rc, out = run(base + ["--invocation", "auto"])
        check("--invocation auto rejects an explicit-only package", rc == 1 and "required: auto" in out)
        rc, out = run(base + ["--invocation", "any"])
        check("--invocation any accepts inverse values", rc == 0, out.strip()[-300:])
        sk = (pkg / "SKILL.md").read_text(encoding="utf-8")
        write(pkg / "SKILL.md", sk.replace("disable-model-invocation: true", "disable-model-invocation: false"))
        write(pkg / "agents" / "openai.yaml", "policy:\n  allow_implicit_invocation: true\n")
        rc, out = run(base + ["--invocation", "auto"])
        check("--invocation auto accepts an implicit package", rc == 0, out.strip()[-300:])
        rc, out = run(base)
        check("default --invocation explicit rejects an implicit package", rc == 1)

        # breakpoints (T1, N)
        tw = load_module(s / "build_tailwind.py", "st_build_tailwind")
        odd = copy.deepcopy(TOKENS)
        odd["breakpoint"] = {"tokens": [tk("bp-sm", "576px")]}
        odd["type"]["groups"][0]["styles"][0]["breakpoints"] = []
        write(pkg.parent / "odd.json", odd)
        rc, out = run([s / "build_tailwind.py", "--tokens", pkg.parent / "odd.json", "--out", pkg.parent / "odd.css"])
        check("build_tailwind fails when no breakpoint can be mapped", rc == 1 and "no usable breakpoint" in out, out.strip()[-200:])
        odd["tailwind"] = {"breakpoints": {"bp-sm": "sm"}}
        check("tailwind.breakpoints maps other names", "--breakpoint-sm: 576px;" in tw.render(odd))

        # optional families (T2)
        thin = copy.deepcopy(TOKENS)
        for fam in ("shadow", "duration", "easing"):
            del thin[fam]
        write(pkg.parent / "thin.json", thin)
        rc1, o1 = run([s / "build_tokens.py", "--tokens", pkg.parent / "thin.json", "--css", pkg.parent / "thin.css",
                       "--dtcg", pkg.parent / "thin.dtcg.json"])
        rc2, o2 = run([s / "build_tailwind.py", "--tokens", pkg.parent / "thin.json", "--out", pkg.parent / "thin-theme.css"])
        check("families without shadow, duration and easing build", rc1 == 0 and rc2 == 0, (o1 + o2).strip()[-300:])

        # no breakpoint family (N1)
        nobp = copy.deepcopy(TOKENS)
        del nobp["breakpoint"]
        nobp["type"]["groups"][0]["styles"][0]["breakpoints"] = []
        write(pkg.parent / "nobp.json", nobp)
        rc, out = run([s / "build_tailwind.py", "--tokens", pkg.parent / "nobp.json", "--out", pkg.parent / "nobp.css"])
        nobp_css = (pkg.parent / "nobp.css").read_text(encoding="utf-8") if rc == 0 else ""
        check("no breakpoint family gives an empty breakpoint section", rc == 0 and "--breakpoint-*: initial;" in nobp_css
              and "--breakpoint-sm" not in nobp_css, out.strip()[-200:])

        # layout widths from the skeleton's size-layout- family (N2)
        lay = copy.deepcopy(TOKENS)
        lay["size"]["tokens"].append(tk("size-layout-page", "1200px"))
        check("size-layout- tokens become max-w containers",
              "--container-layout-page: var(--x-size-layout-page);" in tw.render(lay))
        lay["tailwind"] = {"container_prefixes": ["size-wrap-"]}
        write(pkg.parent / "lay.json", lay)
        rc, out = run([s / "build_tailwind.py", "--tokens", pkg.parent / "lay.json", "--out", pkg.parent / "lay.css"])
        check("a container prefix that matches no size token fails", rc == 1 and "match no size token" in out, out.strip()[-200:])

        # 4- and 8-digit hex (T3)
        bt = load_module(s / "build_tokens.py", "st_build_tokens")
        bc = load_module(s / "build_contrast.py", "st_build_contrast")
        c4, c8 = bt._color_obj("#3698"), bt._color_obj("#33669980")
        check("DTCG colour from #rgba and #rrggbbaa", c4["hex"] == "#336699" and c4["alpha"] == 0.5333
              and c8["hex"] == "#336699" and c8["alpha"] == 0.502, "%r %r" % (c4, c8))
        check("contrast parses #rgba and #rrggbbaa", bc.parse("#3698")[:3] == (51, 102, 153)
              and abs(bc.parse("#33669980")[3] - 128 / 255) < 1e-9)

    def body_p1(pkg: Path):
        contrast = {k: v for k, v in CONTRAST.items() if k != "added_states"}
        make_package(pkg, TOKENS_P1, CMAP_P1, contrast)
        s = pkg / "scripts"
        tok = pkg / "tokens.json"
        for args in ([s / "build_tokens.py", "--tokens", tok, "--css", pkg / "tokens.css", "--dtcg", pkg / "tokens.dtcg.json"],
                     [s / "build_tailwind.py", "--tokens", tok, "--out", pkg / "tailwind" / "theme.css"],
                     [s / "build_contrast.py", "--tokens", tok, "--contrast", pkg / "data" / "contrast.json"],
                     [s / "build_preview.py", "--package", pkg]):
            rc, out = run(args)
            check("P1 %s runs" % Path(args[0]).stem, rc == 0, out.strip()[-300:])
        chk = s / "check_package.py"
        rc, out = run([chk, "--stage", "data", "--package", pkg])
        check("P1 without --allow-orphans fails on the unreferenced primitive", rc == 1 and "orphan primitives (H5): space-12" in out, out.strip()[-300:])
        rc, out = run([chk, "--stage", "data", "--package", pkg, "--allow-orphans"])
        check("P1 check_package --stage data --allow-orphans", rc == 0,
              "\n".join(ln for ln in out.splitlines() if ln.startswith("[FAIL]"))[-800:])
        page = (pkg / "preview.html").read_text(encoding="utf-8")
        check("P1 preview has colour swatches", page.count("x-preview-swatch__chip") == 5
              and 'id="colors-semantic"' in page and 'id="colors-component"' in page and "residue-focus-glow" in page)

    if a.keep:
        d = Path(a.keep) / "package-selftest"
        if d.exists():
            shutil.rmtree(d)
        body(d / "pkg")
        body_p1(d / "p1" / "pkg")
    else:
        with tempfile.TemporaryDirectory() as d:
            body(Path(d) / "pkg")
            body_p1(Path(d) / "p1" / "pkg")
    fails = [r for r in results if not r[0]]
    for ok, name, detail in fails:
        print("FAIL %s\n  %s" % (name, detail.replace("\n", "\n  ")))
    print("package selftest: %d/%d passed" % (len(results) - len(fails), len(results)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
