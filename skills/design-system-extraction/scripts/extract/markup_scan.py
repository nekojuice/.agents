#!/usr/bin/env python3
"""Markup scan for component inventory (standard library only).

Scans view/template files (server templates, SPA single-file components, plain HTML) and
script files for class usage, conditional classes, inline styles, <style> blocks and
script-driven class/style writes. Output is a JSON index; it does not decide which pattern
is a component.

Usage:
  python -I markup_scan.py --root <web-root> --views <rel-dir> [<rel-dir> ...] --out <index.json>
         [--scripts <rel-dir> ...] [--view-ext .<ext> ...] [--script-ext .<ext> ...]
         [--exclude <dir-name> ...] [--skip-script <regex>] [--template-expr <regex>]
  python -I markup_scan.py --selftest

Defaults: view extensions .vue .html .htm; script extensions .js .vue. Add a server template
extension with --view-ext (and --script-ext when its files carry inline scripts).
A class attribute holding a match of --template-expr (a regex matching one whole expression of the
server template engine, e.g. "{=[^}]*}" for an invented syntax; no default; matches are left out
of the class tokens) is recorded as "template-conditional"; `:class` / `v-bind:class` bindings as "vue-class". JSX `className="..."` is read like `class`;
`className={...}` expressions are recorded as "jsx-class".
Skipped directory names default to node_modules dist build .git; pass --exclude to replace
the list (for example to add the project's build-output folders or a folder of vendored libraries). Component folders such as
src/lib are scanned unless excluded.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_EXCLUDE = {"node_modules", "dist", "build", ".git"}
VIEW_EXT = {".vue", ".html", ".htm"}
SCRIPT_EXT = {".js", ".vue"}
DEFAULT_SKIP_SCRIPT = r"\.min\.js$|(^|/)jquery[^/]*$"

RE_CLASS = re.compile(r'(?<![\w:-])(?:class|className)\s*=\s*("([^"]*)"|\'([^\']*)\')', re.S)
RE_JSXCLASS = re.compile(r'(?<![\w:-])className\s*=\s*\{')
RE_VCLASS = re.compile(r'(?:\s:class|\sv-bind:class)\s*=\s*"([^"]*)"', re.S)
RE_STYLE_ATTR = re.compile(r'(?<![\w:-])style\s*=\s*("([^"]*)"|\'([^\']*)\')', re.S)
RE_VSTYLE = re.compile(r'(?:\s:style|\sv-bind:style)\s*=\s*"([^"]*)"', re.S)
RE_STYLE_BLOCK = re.compile(r'<style\b([^>]*)>(.*?)</style>', re.S | re.I)
RE_JS_CLASS = re.compile(
    r'\.(addClass|removeClass|toggleClass|css|attr\(\s*["\']style["\'])\s*\(?'
    r'|classList\.(add|remove|toggle)\s*\(|\.style\.(\w+)\s*=|\.className\s*=')


def line_of(text, pos, starts):
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def line_starts(text):
    starts = [0]
    for m in re.finditer("\n", text):
        starts.append(m.end())
    return starts


def walk(root, rel_dirs, exts, exclude):
    for rel in rel_dirs:
        base = os.path.join(root, rel)
        if os.path.isfile(base):
            yield base
            continue
        for dp, dns, fns in os.walk(base):
            dns[:] = sorted(d for d in dns if d not in exclude)
            for fn in sorted(fns):
                if os.path.splitext(fn)[1].lower() in exts:
                    yield os.path.join(dp, fn)


def tokens(raw, template_expr=None):
    # strip template expressions (the engine's, then {{ ... }} interpolation), keep static tokens
    static = re.sub(template_expr, ' ', raw) if template_expr else raw
    static = re.sub(r'\{\{.*?\}\}', ' ', static)
    return [t for t in static.split() if re.match(r'^[A-Za-z_][\w-]*$', t)]


def scan(root, views, scripts, exclude, view_ext, script_ext, skip_script, template_expr=None):
    out = {"root": root, "files": {}, "class_index": {}, "style_blocks": [],
           "inline_styles": [], "vue_class": [], "vue_style": [], "script_writes": []}
    cls_idx = defaultdict(list)
    skip_rx = re.compile(skip_script, re.I) if skip_script else None
    for path in walk(root, views, view_ext, exclude):
        rel = os.path.relpath(path, root).replace("\\", "/")
        text = open(path, encoding="utf-8-sig", errors="replace").read()
        st = line_starts(text)
        nclass = 0
        for m in RE_CLASS.finditer(text):
            raw = m.group(2) if m.group(2) is not None else m.group(3)
            ln = line_of(text, m.start(), st)
            cond = bool(template_expr and re.search(template_expr, raw))
            for t in tokens(raw, template_expr):
                cls_idx[t].append(f"{rel}:{ln}")
                nclass += 1
            if cond:
                out["vue_class"].append({"src": f"{rel}:{ln}", "kind": "template-conditional", "expr": raw.strip()[:200]})
        for m in RE_VCLASS.finditer(text):
            ln = line_of(text, m.start(), st)
            out["vue_class"].append({"src": f"{rel}:{ln}", "kind": "vue-class", "expr": m.group(1).strip()[:200]})
        for m in RE_JSXCLASS.finditer(text):
            ln = line_of(text, m.start(), st)
            expr = text[m.end() - 1:m.end() + 199].split("\n")[0].strip()
            out["vue_class"].append({"src": f"{rel}:{ln}", "kind": "jsx-class", "expr": expr})
        for m in RE_STYLE_ATTR.finditer(text):
            raw = m.group(2) if m.group(2) is not None else m.group(3)
            ln = line_of(text, m.start(), st)
            out["inline_styles"].append({"src": f"{rel}:{ln}", "style": raw.strip()[:200]})
        for m in RE_VSTYLE.finditer(text):
            ln = line_of(text, m.start(), st)
            out["vue_style"].append({"src": f"{rel}:{ln}", "expr": m.group(1).strip()[:200]})
        for m in RE_STYLE_BLOCK.finditer(text):
            l1 = line_of(text, m.start(), st)
            l2 = line_of(text, m.end(), st)
            body = m.group(2)
            sels = re.findall(r'([^{}]+)\{', body)
            out["style_blocks"].append({"src": f"{rel}:{l1}-{l2}", "attrs": m.group(1).strip(),
                                        "lines": l2 - l1 + 1,
                                        "selectors": [s.strip()[:80] for s in sels][:40]})
        out["files"][rel] = {"class_tokens": nclass}
    for path in walk(root, scripts, script_ext, exclude):
        rel = os.path.relpath(path, root).replace("\\", "/")
        if skip_rx and skip_rx.search(rel):
            continue
        text = open(path, encoding="utf-8-sig", errors="replace").read()
        st = line_starts(text)
        for m in RE_JS_CLASS.finditer(text):
            ln = line_of(text, m.start(), st)
            s = text[st[ln - 1]: st[ln] if ln < len(st) else len(text)].strip()
            out["script_writes"].append({"src": f"{rel}:{ln}", "code": s[:200]})
    out["class_index"] = {k: {"count": len(v), "files": len({x.rsplit(':', 1)[0] for x in v}), "refs": v}
                          for k, v in sorted(cls_idx.items(), key=lambda kv: (-len(kv[1]), kv[0]))}
    return out


def exts(defaults, extra):
    return set(defaults) | {e.lower() if e.startswith(".") else "." + e.lower() for e in extra or []}


def selftest():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "v"))
        os.makedirs(os.path.join(d, "js"))
        open(os.path.join(d, "v", "a.tpl"), "w", encoding="utf-8").write(
            '<div class="x-card {= on ? \'x-on\' : \'\' }" style="margin:0">\n<style>.x-card{color:#336699}</style>\n</div>\n')
        open(os.path.join(d, "v", "b.vue"), "w", encoding="utf-8").write(
            '<template><p class="x-card x-note" :class="{ x-on: isOn }"></p></template>\n')
        open(os.path.join(d, "v", "c.tsx"), "w", encoding="utf-8").write(
            '<p className="x-note" />\n<p className={on ? "x-on" : ""} />\n')
        os.makedirs(os.path.join(d, "v", "lib"))
        open(os.path.join(d, "v", "lib", "d.html"), "w", encoding="utf-8").write('<i class="x-note"></i>\n')
        open(os.path.join(d, "js", "app.js"), "w", encoding="utf-8").write("el.classList.add('x-on');\n")
        open(os.path.join(d, "js", "vendor.min.js"), "w", encoding="utf-8").write("el.className = 'x';\n")
        res = scan(d, ["v"], ["js"], DEFAULT_EXCLUDE, exts(VIEW_EXT, [".tpl", ".tsx"]), SCRIPT_EXT, DEFAULT_SKIP_SCRIPT, r"\{=[^}]*\}")
    checks = [
        ("class index", {k: v["count"] for k, v in res["class_index"].items()}, {"x-card": 2, "x-note": 3}),
        ("dynamic kinds", sorted(x["kind"] for x in res["vue_class"]), ["jsx-class", "template-conditional", "vue-class"]),
        ("inline styles", len(res["inline_styles"]), 1),
        ("style blocks", res["style_blocks"][0]["selectors"], [".x-card"]),
        ("script writes skip minified", [x["src"] for x in res["script_writes"]], ["js/app.js:1"]),
    ]
    fails = [c for c in checks if c[1] != c[2]]
    for name, got, want in fails:
        print("FAIL %s\n  got:  %r\n  want: %r" % (name, got, want))
    print("markup_scan selftest: %d/%d passed" % (len(checks) - len(fails), len(checks)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="web root; reported paths are relative to it")
    ap.add_argument("--out", help="output JSON path")
    ap.add_argument("--views", nargs="+", help="view directories or files, relative to --root")
    ap.add_argument("--scripts", nargs="*", default=[], help="script directories or files, relative to --root")
    ap.add_argument("--view-ext", nargs="*", default=[], help="extra view extensions (added to .vue .html .htm)")
    ap.add_argument("--script-ext", nargs="*", default=[], help="extra script extensions (added to .js .vue)")
    ap.add_argument("--exclude", nargs="*", default=sorted(DEFAULT_EXCLUDE), help="directory names to skip")
    ap.add_argument("--skip-script", default=DEFAULT_SKIP_SCRIPT, help="regex on script relative path to skip (vendor bundles)")
    ap.add_argument("--template-expr", help="regex matching one whole template expression inside class attributes (no default)")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    missing = [n for n in ("root", "out", "views") if not getattr(a, n)]
    if missing:
        ap.error("missing: " + ", ".join("--" + m for m in missing))
    res = scan(os.path.abspath(a.root), a.views, a.scripts, set(a.exclude),
               exts(VIEW_EXT, a.view_ext), exts(SCRIPT_EXT, a.script_ext), a.skip_script,
               a.template_expr)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"files={len(res['files'])} classes={len(res['class_index'])} "
          f"inline={len(res['inline_styles'])} style_blocks={len(res['style_blocks'])} "
          f"dyn_class={len(res['vue_class'])} script_writes={len(res['script_writes'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
