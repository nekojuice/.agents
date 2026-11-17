#!/usr/bin/env python3
"""Group template-rendered pages by their stylesheet stack (static scan, standard library only).

Usage:
  python -I stack_scan.py --root <app-root> --webroot <web-root-rel> --ext <template-ext>
         --preset <name> [--preset-file <presets.json>]
         [--exclude <dir-name>]... [--entry-call <helper-name>] --out <scan.json>
  python -I stack_scan.py --list-presets
  python -I stack_scan.py --selftest

What it does (no execution of the application):
  1. Lists template files matching --ext; resolves each page's layout (explicit layout
     assignment in the page, or the nearest default-layout file walking up to --root).
  2. For each layout: ordered stylesheet <link>s in document order, with enclosing condition
     text, plus positions of slot-output and body-output markers. Simple conditions of the
     form `<condition_var> == "X"` are evaluated per page scope.
  3. For each page: slot blocks -> stylesheet links, <style> line ranges, bundler entry
     calls (`<entry-call>("name")`); links/<style> outside slots (body-inline);
     <style> blocks of the includes and widgets it calls (one level).
  4. Resolves root-relative hrefs (the preset's root alias, and `/`) to the web root, strips
     query strings, checks existence.
  5. Optional route scan: render calls inside route handlers -> reachable page files.
  6. Groups pages whose ordered list of existing stylesheet files is identical.
Template comments are blanked before parsing (line numbers preserved).
Output is evidence for a human; it does not compute cascade results.

Engine syntax is data, not code. --preset is required: there is no default engine, so a scan
never applies one engine's rules to another engine's files. The only built-in preset is
  plain-html    Static HTML: no layouts or slots; each file with <html> is its own document;
                relative hrefs resolve against the file's directory.
Any template engine is described in a preset file (--preset-file, JSON {"<name>": {<key>: <value>}};
keys left out keep the plain-html value). Keys (regular expressions unless noted):
  comment_patterns      list; blanked before parsing
  layout_assign         layout chosen in a page; group 2 = layout name, group 1 = the "no layout" word
  layout_null           text: the "no layout" word
  layout_defaults_file   text: basename of the file that sets the default layout for its folder tree
  skip_basenames        list of basenames that are not pages
  section_open          opens a named slot ending in `{`; group 1 = slot name (brace-balanced body)
  slot_output        slot output in a layout; group 1 = slot name
  body_output           page body output in a layout
  condition_open        conditional block ending in `{`; group 1 = condition text
  condition_var         text: variable name in simple conditions `<var> == "X"`, compared with the
                        page scope (the folder below scope_dir)
  string_var / var_ref  string assignment (group 1 name, group 2 value) / href that is a variable
  url_helper            href helper; group 1 = the path inside it
  root_alias            text: prefix meaning "application root" in hrefs and include names
  include_calls / widget_calls   lists; group 1 = include name / widget name
  component_dir         text: folder holding one sub-folder per widget
  shared_dir_name / root_shared_dir text: shared folder name searched upward / at the root
  scope_dir             text: folder whose sub-folders are page scopes
  partial_prefix / partial_dir_names  marks include files that are not pages
  resolve_relative      bool: resolve relative hrefs against the file's folder
  route_scan            object or null: file_suffix (text), scope_attr, class, action, render_call
An example preset file for an invented engine (syntax made up for illustration):
  assets/stack-preset.example.json in this skill; the self-test runs it.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from collections import OrderedDict, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PRESETS = {
    "plain-html": {
        "comment_patterns": [r"<!--.*?-->"],
        "layout_assign": None,
        "layout_null": None,
        "layout_defaults_file": None,
        "skip_basenames": [],
        "section_open": None,
        "slot_output": None,
        "body_output": None,
        "condition_open": None,
        "condition_var": None,
        "string_var": None,
        "var_ref": None,
        "url_helper": None,
        "root_alias": None,
        "include_calls": [],
        "widget_calls": [],
        "component_dir": None,
        "shared_dir_name": None,
        "root_shared_dir": None,
        "scope_dir": None,
        "partial_prefix": None,
        "partial_dir_names": [],
        "resolve_relative": True,
        "route_scan": None,
    },
}

EXAMPLE_PRESET = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                              "assets", "stack-preset.example.json")
LINK_RE = re.compile(r"<link\b[^>]*>", re.I)
STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.I | re.S)
HREF_RE = re.compile(r"""href\s*=\s*(["'])(.*?)\1""", re.I | re.S)


def blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


class Engine:
    """Compiled preset plus the template extension."""

    def __init__(self, preset: dict, ext: str):
        self.p = preset
        self.ext = ext if ext.startswith(".") else "." + ext
        self.comments = [re.compile(x, re.S) for x in preset.get("comment_patterns") or []]

        def rx(key, flags=0):
            v = preset.get(key)
            return re.compile(v, flags) if v else None

        self.layout_assign = rx("layout_assign")
        self.section_open = rx("section_open")
        self.slot_output = rx("slot_output")
        self.body_output = rx("body_output")
        self.condition_open = rx("condition_open", re.S)
        self.string_var = rx("string_var")
        self.var_ref = preset.get("var_ref")
        self.url_helper = rx("url_helper")
        self.include_calls = [re.compile(x) for x in preset.get("include_calls") or []]
        self.widget_calls = [re.compile(x) for x in preset.get("widget_calls") or []]
        self.routes = preset.get("route_scan")
        self.alias = preset.get("root_alias")

    def clean(self, text):
        for c in self.comments:
            text = c.sub(blank, text)
        return text


def read(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def match_brace(text, open_pos):
    depth = 0
    for i in range(open_pos, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def is_stylesheet(tag):
    return re.search(r"rel\s*=\s*[\"']?stylesheet", tag, re.I) is not None


def string_vars(eng, text):
    out = {}
    if not eng.string_var:
        return out
    for m in eng.string_var.finditer(text):
        lits = re.findall(r'"([^"]*)"', m.group(2))
        if lits:
            out[m.group(1)] = lits[-1]
    return out


def rel(p, root):
    return os.path.relpath(p, root).replace("\\", "/")


def resolve_href(eng, href, webroot, root, svars, file_dir=None):
    raw = href
    if eng.var_ref:
        m = re.fullmatch(eng.var_ref, href.strip())
        if m and m.group(1) in svars:
            href = "/" + svars[m.group(1)].lstrip("/")
    if eng.url_helper:
        m = eng.url_helper.search(href)
        if m:
            href = m.group(1)
    if href.startswith(("http://", "https://", "//")):
        return {"href": raw, "path": None, "exists": None, "external": True}
    if eng.alias and href.startswith(eng.alias):
        href = "/" + href[len(eng.alias):]
    if not href.startswith("/"):
        if eng.p.get("resolve_relative") and file_dir is not None:
            relp = href.split("?")[0].split("#")[0]
            full = os.path.normpath(os.path.join(file_dir, *relp.split("/")))
            return {"href": raw, "path": rel(full, root), "exists": os.path.isfile(full), "external": False}
        return {"href": raw, "path": None, "exists": None, "external": False, "note": "unresolved-relative"}
    r = href[1:]
    r = r.split("?")[0].split("#")[0]
    full = os.path.join(root, webroot, *r.split("/"))
    wr = webroot.replace("\\", "/").strip("/")
    return {
        "href": raw,
        "path": r if wr in ("", ".") else wr + "/" + r,
        "exists": os.path.isfile(full),
        "external": False,
    }


def enclosing_ifs(eng, text, pos):
    conds = []
    if not eng.condition_open:
        return conds
    for m in eng.condition_open.finditer(text, 0, pos):
        ob = m.end() - 1
        cb = match_brace(text, ob)
        if ob < pos < cb:
            conds.append(re.sub(r"\s+", " ", m.group(1)).strip())
    return conds


def collect_assets(eng, text, start, end, webroot, root, svars, base_line_text, file_dir=None):
    items = []
    seg = text[start:end]
    for m in LINK_RE.finditer(seg):
        tag = m.group(0)
        if not is_stylesheet(tag):
            continue
        h = HREF_RE.search(tag)
        if not h:
            continue
        pos = start + m.start()
        r = resolve_href(eng, h.group(2), webroot, root, svars, file_dir)
        r.update({"kind": "link", "line": line_of(base_line_text, pos), "pos": pos})
        items.append(r)
    for m in STYLE_RE.finditer(seg):
        pos = start + m.start()
        items.append({
            "kind": "style-block",
            "line": line_of(base_line_text, pos),
            "end_line": line_of(base_line_text, start + m.end()),
            "pos": pos,
        })
    items.sort(key=lambda x: x["pos"])
    return items


def layout_sequence(eng, path, root, webroot):
    text = eng.clean(read(path))
    svars = string_vars(eng, text)
    head_end = text.lower().find("</head>")
    markers = []
    if eng.slot_output:
        for m in eng.slot_output.finditer(text):
            markers.append({"kind": "section", "name": m.group(1), "pos": m.start(), "line": line_of(text, m.start())})
    if eng.body_output:
        for m in eng.body_output.finditer(text):
            markers.append({"kind": "body", "pos": m.start(), "line": line_of(text, m.start())})
    assets = collect_assets(eng, text, 0, len(text), webroot, root, svars, text, os.path.dirname(path))
    for a in assets:
        a["conditions"] = enclosing_ifs(eng, text, a["pos"])
        a["position"] = "head" if head_end < 0 or a["pos"] < head_end else "body"
    for mk in markers:
        mk["position"] = "head" if head_end < 0 or mk["pos"] < head_end else "body"
    seq = sorted(assets + markers, key=lambda x: x["pos"])
    return {"file": rel(path, root), "sequence": seq}


def eval_condition(conds, scope, cond_var):
    """Return True/False if all conditions are simple scope tests, else None."""
    if not cond_var:
        return None
    result = True
    for c in conds:
        m = re.fullmatch(r"%s\s*(==|!=)\s*\"([^\"]+)\"" % re.escape(cond_var), c)
        if not m:
            return None
        ok = (scope == m.group(2)) if m.group(1) == "==" else (scope != m.group(2))
        result = result and ok
    return result


def page_scope(eng, relpath):
    ad = eng.p.get("scope_dir")
    parts = relpath.split("/")
    if ad and parts[0] == ad and len(parts) > 1:
        return parts[1]
    return None


def layout_from(eng, text):
    if not eng.layout_assign:
        return None
    m = eng.layout_assign.search(text)
    if not m:
        return None
    return m.group(2) if m.group(2) else eng.p.get("layout_null") or "null"


def layout_for_view(eng, view_path, root, explicit):
    d = os.path.dirname(view_path)
    null = eng.p.get("layout_null") or "null"
    vs_name = eng.p.get("layout_defaults_file")
    if explicit is None and vs_name:
        cur = d
        while True:
            vs = os.path.join(cur, vs_name + eng.ext)
            if os.path.isfile(vs):
                found = layout_from(eng, eng.clean(read(vs)))
                if found:
                    explicit = found
                    break
            if os.path.abspath(cur) == os.path.abspath(root):
                break
            cur = os.path.dirname(cur)
    if explicit in (None, null):
        return None
    name = explicit if explicit.endswith(eng.ext) else explicit + eng.ext
    cands = [os.path.join(d, name)]
    shared = eng.p.get("shared_dir_name")
    p = d
    while shared and os.path.abspath(p) != os.path.abspath(root):
        cands.append(os.path.join(p, shared, name))
        p = os.path.dirname(p)
    if eng.p.get("root_shared_dir"):
        cands.append(os.path.join(root, *eng.p["root_shared_dir"].split("/"), name))
    for c in cands:
        if os.path.isfile(c):
            return c
    return "missing:" + explicit


def parse_view(eng, path, root, webroot, entry_call):
    text = eng.clean(read(path))
    svars = string_vars(eng, text)
    explicit = None
    if eng.layout_assign:
        m = re.search(eng.layout_assign.pattern + r"\s*;", text)
        if m:
            explicit = m.group(2) if m.group(2) else eng.p.get("layout_null") or "null"
    fdir = os.path.dirname(path)
    sections = OrderedDict()
    spans = []
    if eng.section_open:
        for sm in eng.section_open.finditer(text):
            ob = sm.end() - 1
            cb = match_brace(text, ob)
            spans.append((sm.start(), cb))
            name = sm.group(1)
            items = collect_assets(eng, text, ob, cb, webroot, root, svars, text, fdir)
            entries = []
            if entry_call:
                entries = [
                    {"entry": e.group(1), "line": line_of(text, ob + e.start())}
                    for e in re.finditer(re.escape(entry_call) + r"\(\s*\"([^\"]+)\"", text[ob:cb])
                ]
            sections.setdefault(name, {"line": line_of(text, sm.start()), "assets": [], "entries": []})
            sections[name]["assets"] += items
            sections[name]["entries"] += entries
    body_assets = []
    for a in collect_assets(eng, text, 0, len(text), webroot, root, svars, text, fdir):
        if not any(s <= a["pos"] <= e for s, e in spans):
            body_assets.append(a)
    invokes = []
    for rx in eng.widget_calls:
        for im in rx.finditer(text):
            invokes.append({"kind": "component", "name": im.group(1), "line": line_of(text, im.start())})
    for rx in eng.include_calls:
        for im in rx.finditer(text):
            invokes.append({"kind": "partial", "name": im.group(1), "line": line_of(text, im.start())})
    has_html = re.search(r"<html\b", text, re.I) is not None
    return {
        "layout_explicit": explicit,
        "sections": sections,
        "body_assets": body_assets,
        "invokes": invokes,
        "has_own_html": has_html,
    }


def resolve_invoke(eng, inv, view_path, root):
    if inv["kind"] == "component":
        cd = eng.p.get("component_dir")
        if not cd:
            return []
        base = os.path.join(root, *cd.split("/"), inv["name"])
        if os.path.isdir(base):
            return [os.path.join(base, f) for f in sorted(os.listdir(base)) if f.endswith(eng.ext)]
        return []
    n = inv["name"]
    if eng.alias and n.startswith(eng.alias):
        p = os.path.join(root, *n[len(eng.alias):].split("/"))
        return [p] if os.path.isfile(p) else []
    nm = n if n.endswith(eng.ext) else n + eng.ext
    cands = [os.path.join(os.path.dirname(view_path), nm)]
    if eng.p.get("root_shared_dir"):
        cands.append(os.path.join(root, *eng.p["root_shared_dir"].split("/"), nm))
    for c in cands:
        if os.path.isfile(c):
            return [c]
    return []


def scan_routes(eng, root, excludes):
    reach = defaultdict(list)
    c = eng.routes
    if not c:
        return reach
    scope_rx = re.compile(c["scope_attr"]) if c.get("scope_attr") else None
    class_rx = re.compile(c["class"])
    action_rx = re.compile(c["action"])
    view_rx = re.compile(c["render_call"])
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d not in excludes)
        for f in sorted(fn):
            if not f.endswith(c["file_suffix"]):
                continue
            p = os.path.join(dp, f)
            t = read(p)
            am = scope_rx.search(t) if scope_rx else None
            scope = am.group(1) if am else None
            cm = class_rx.search(t)
            if not cm:
                continue
            group = cm.group(1)
            meths = [(m.start(), m.group(1)) for m in action_rx.finditer(t)]
            for vm in view_rx.finditer(t):
                if vm.start() > 0 and (t[vm.start() - 1].isalnum() or t[vm.start() - 1] == "_"):
                    continue
                owner = None
                for pos, name in meths:
                    if pos < vm.start():
                        owner = name
                name = vm.group(2) or owner
                if not name:
                    continue
                key = ((scope or "").lower(), group.lower(), name.lower())
                reach[key].append("%s:%d" % (rel(p, root), line_of(t, vm.start())))
    return reach


def is_partial_like(eng, base, rv):
    pre = eng.p.get("partial_prefix")
    if pre and base.startswith(pre):
        return True
    return any(("/%s/" % d) in rv for d in eng.p.get("partial_dir_names") or [])


def scan(eng, root, webroot, excludes, entry_call):
    views = []
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d not in excludes)
        for f in fn:
            if f.endswith(eng.ext):
                views.append(os.path.join(dp, f))
    views.sort()
    skip = {b + eng.ext for b in eng.p.get("skip_basenames") or []}

    reach = scan_routes(eng, root, excludes)
    cond_var = eng.p.get("condition_var")
    layouts = {}
    result = {"root": root, "ext": eng.ext, "layouts": {}, "views": {}, "groups": []}
    for v in views:
        rv = rel(v, root)
        base = os.path.basename(v)
        if base in skip:
            continue
        partial_like = is_partial_like(eng, base, rv)
        info = parse_view(eng, v, root, webroot, entry_call)
        scope = page_scope(eng, rv)
        parts = rv.split("/")
        group = parts[-2].lower() if len(parts) >= 2 else ""
        key = ((scope or "").lower(), group, os.path.splitext(base)[0].lower())
        info["scope"] = scope
        info["partial_like"] = partial_like
        info["reached_by"] = reach.get(key, [])
        lay = None if partial_like else layout_for_view(eng, v, root, info["layout_explicit"])
        if lay and not lay.startswith("missing:") and lay not in layouts:
            layouts[lay] = layout_sequence(eng, lay, root, webroot)
        info["layout"] = rel(lay, root) if lay and not lay.startswith("missing:") else lay
        stack = []
        if lay and lay in layouts:
            for item in layouts[lay]["sequence"]:
                if item["kind"] == "link":
                    ok = eval_condition(item["conditions"], scope, cond_var) if item["conditions"] else True
                    if ok is False:
                        continue
                    stack.append({"path": item["path"], "href": item["href"], "exists": item["exists"],
                                  "position": item["position"], "from": "%s:%d" % (layouts[lay]["file"], item["line"]),
                                  "condition": None if ok is True else " && ".join(item["conditions"])})
                elif item["kind"] == "section":
                    sec = info["sections"].get(item["name"])
                    if sec:
                        for s in sec["assets"]:
                            if s["kind"] == "link":
                                stack.append({"path": s["path"], "href": s["href"], "exists": s["exists"],
                                              "position": item["position"], "from": "%s:%d" % (rv, s["line"]),
                                              "condition": None, "via_section": item["name"]})
                        for e in sec["entries"]:
                            stack.append({"path": None, "entry": e["entry"], "exists": None,
                                          "position": item["position"], "from": "%s:%d" % (rv, e["line"]),
                                          "condition": "bundler-entry", "via_section": item["name"]})
                elif item["kind"] == "body":
                    for s in info["body_assets"]:
                        if s["kind"] == "link":
                            stack.append({"path": s["path"], "href": s["href"], "exists": s["exists"],
                                          "position": "body", "from": "%s:%d" % (rv, s["line"]),
                                          "condition": None, "via_section": "body"})
        elif not partial_like:
            for s in info["body_assets"]:
                if s["kind"] == "link":
                    stack.append({"path": s["path"], "href": s["href"], "exists": s["exists"],
                                  "position": "own-document", "from": "%s:%d" % (rv, s["line"]), "condition": None})
        blocks = []
        for name, sec in info["sections"].items():
            for s in sec["assets"]:
                if s["kind"] == "style-block":
                    blocks.append({"path": rv, "lines": [s["line"], s["end_line"]], "via": "section:" + name})
        for s in info["body_assets"]:
            if s["kind"] == "style-block":
                blocks.append({"path": rv, "lines": [s["line"], s["end_line"]], "via": "body"})
        for inv in info["invokes"]:
            for pf in resolve_invoke(eng, inv, v, root):
                pt = eng.clean(read(pf))
                for sm in STYLE_RE.finditer(pt):
                    blocks.append({"path": rel(pf, root), "lines": [line_of(pt, sm.start()), line_of(pt, sm.end())],
                                   "via": "%s:%s@%s:%d" % (inv["kind"], inv["name"], rv, inv["line"])})
        info["stack"] = stack
        info["style_blocks"] = blocks
        for sec in info["sections"].values():
            for s in sec["assets"]:
                s.pop("pos", None)
        for s in info["body_assets"]:
            s.pop("pos", None)
        result["views"][rv] = info

    for lay, d in layouts.items():
        for it in d["sequence"]:
            it.pop("pos", None)
        result["layouts"][d["file"]] = d

    groups = OrderedDict()
    for rv, info in result["views"].items():
        if info["partial_like"]:
            continue
        sig = tuple(
            (s.get("path") or ("entry:" if s.get("entry") else s.get("href")), s["position"], s.get("condition"))
            for s in info["stack"] if s.get("exists") or s.get("entry")
        )
        sig = (info["layout"],) + sig
        groups.setdefault(sig, []).append(rv)
    for sig, pages in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        result["groups"].append({"layout": sig[0], "files": [list(x) for x in sig[1:]], "pages": pages})
    return result, len(layouts)


def load_preset(name, preset_file):
    presets = copy.deepcopy(PRESETS)
    if preset_file:
        with open(preset_file, encoding="utf-8-sig") as fh:
            extra = json.load(fh)
        for k, v in extra.items():
            base = presets.get(k, copy.deepcopy(PRESETS["plain-html"]))
            base.update(v)
            presets[k] = base
    if name not in presets:
        sys.exit("unknown preset: %s (known: %s)" % (name, ", ".join(sorted(presets))))
    return presets[name]


# ---------------------------------------------------------------- selftest

def selftest():
    checks = []
    with tempfile.TemporaryDirectory() as d:
        def w(relp, text):
            p = os.path.join(d, *relp.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
        w("web/css/base.css", ".x-a{}")
        w("web/css/extra.css", ".x-b{}")
        w("templates/common/_main.tpl",
          '<html><head>\n<link rel="stylesheet" href="$root/css/base.css">\n'
          ':if (scope == "staff") {\n<link rel="stylesheet" href="$root/css/extra.css">\n}\n'
          ':yield styles\n</head><body>:yield-body</body></html>\n')
        w("templates/_defaults.tpl", ':layout "_main"\n')
        w("templates/home/index.tpl", ':slot styles {\n<link rel="stylesheet" href="$root/css/extra.css?v=1">\n}\n<p>x</p>\n')
        w("templates/home/about.tpl", '{! <link rel="stylesheet" href="$root/css/extra.css"> !}\n<p>y</p>\n')
        w("templates/home/bare.tpl", ':layout none;\n<html><head><link rel="stylesheet" href="/css/base.css"></head></html>\n')
        w("routes/home_routes.txt", 'group home\n route index { render() }\n route other { render("about") }\n')
        eng = Engine(load_preset("slots", str(EXAMPLE_PRESET)), ".tpl")
        res, nlay = scan(eng, os.path.abspath(d), "web", set(), None)
        v = res["views"]
        checks.append(("layouts", nlay, 1))
        checks.append(("index stack", [s["path"] for s in v["templates/home/index.tpl"]["stack"]],
                       ["web/css/base.css", "web/css/extra.css"]))
        checks.append(("conditional link dropped outside its scope", [s["path"] for s in v["templates/home/about.tpl"]["stack"]],
                       ["web/css/base.css"]))
        checks.append(("own document", [(s["path"], s["position"]) for s in v["templates/home/bare.tpl"]["stack"]],
                       [("web/css/base.css", "own-document")]))
        checks.append(("route reach", (bool(v["templates/home/index.tpl"]["reached_by"]),
                                       bool(v["templates/home/about.tpl"]["reached_by"])), (True, True)))
        checks.append(("groups", sorted(len(g["pages"]) for g in res["groups"]), [1, 1, 1]))
        w("site/a.html", '<html><head><link rel="stylesheet" href="css/s.css"></head></html>\n')
        w("site/css/s.css", ".x-c{}")
        eng2 = Engine(load_preset("plain-html", None), ".html")
        res2, _ = scan(eng2, os.path.abspath(d), ".", set(), None)
        checks.append(("plain-html relative", [(s["path"], s["exists"]) for s in res2["views"]["site/a.html"]["stack"]],
                       [("site/css/s.css", True)]))
    fails = [c for c in checks if c[1] != c[2]]
    for name, got, want in fails:
        print("FAIL %s\n  got:  %r\n  want: %r" % (name, got, want))
    print("stack_scan selftest: %d/%d passed" % (len(checks) - len(fails), len(checks)))
    return 1 if fails else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="application root to scan")
    ap.add_argument("--webroot", help="static web root, relative to --root ('.' when hrefs resolve from --root)")
    ap.add_argument("--ext", help="template file extension, e.g. .html")
    ap.add_argument("--preset", help="engine preset name (required for a scan; see --list-presets)")
    ap.add_argument("--preset-file", help="JSON file adding or overriding presets")
    ap.add_argument("--exclude", action="append", default=None,
                    help="directory name to skip (repeatable; default node_modules dist build .git; add the "
                         "project's build-output folders)")
    ap.add_argument("--entry-call", help="bundler helper name whose string argument is recorded as an entry")
    ap.add_argument("--out", help="output JSON path")
    ap.add_argument("--list-presets", action="store_true", help="print the built-in presets as JSON and exit")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.list_presets:
        print(json.dumps(PRESETS, ensure_ascii=False, indent=1))
        return 0
    missing = [n for n in ("root", "webroot", "ext", "preset", "out") if not getattr(a, n)]
    if missing:
        ap.error("missing: " + ", ".join("--" + m for m in missing))
    eng = Engine(load_preset(a.preset, a.preset_file), a.ext)
    root = os.path.abspath(a.root)
    excludes = set(a.exclude or ["node_modules", "dist", "build", ".git"])
    result, nlay = scan(eng, root, a.webroot, excludes, a.entry_call)
    result["preset"] = a.preset
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    print("views=%d groups=%d layouts=%d" % (
        sum(1 for v in result["views"].values() if not v["partial_like"]), len(result["groups"]), nlay))
    return 0


if __name__ == "__main__":
    sys.exit(main())
