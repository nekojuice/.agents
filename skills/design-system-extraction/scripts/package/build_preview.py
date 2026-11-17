#!/usr/bin/env python3
"""Build preview.html and preview/tailwind.css: a one-way overview page (no network, no
scripts, opens straight from the local file system).

Usage:
  python -I build_preview.py --package <package-dir> [--tailwind-cli <path>] [--check]

Reads (all relative to the package root):
  tokens.json, components/component-tokens.json, data/contrast.json, data/gaps.json,
  assets/README.md, preview/foundations/*.html, preview/components/<id>.html,
  preview/patterns/<id>.html, tailwind/index.css
Writes:
  preview.html; with a Tailwind CLI also preview/tailwind.css (--check compares only and
  writes nothing; exit 1 on any difference)

Tailwind CLI (v4):
- pass the executable with --tailwind-cli or the TAILWIND_CLI environment variable
  (e.g. <project>/node_modules/.bin/tailwindcss). When it sits under a node_modules folder,
  that folder is put on NODE_PATH so the entry's @import "tailwindcss" resolves.
- without a CLI nothing is compiled: preview.html is built, preview/tailwind.css is left as
  it is, and --check compares preview.html only and says so.
- this script installs nothing and never goes online; the maintainer provides the CLI.

Rules:
- preview fragments are the only HTML source; component markup inside them is the Tailwind
  notation. Only the content between the fragment begin/end markers is used, and paths
  starting with ../../ are rewritten relative to the package root.
- swatches, type, scales, assets, contrast and known gaps are embedded from the data files at
  build time; the page does not fetch and contains no script.
- every card (id = anchor) gets a parts / states / token-mapping table; a component-map
  anchor without a card exits 1.
- the output depends only on the inputs; reruns are byte-identical.

Page wording is English by default. component-tokens.json `preview_rules` may override:
  labels        {key: text} for any key of LABELS below
  group_labels  {group id: text}
  type_sample   sample string for type specimens
  lang          <html lang> value (default "en")
  favicon       package-relative icon path (omitted when absent)
  inverse_markers  substrings of an asset's usage cell that mark it as drawn on a dark tile
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GROUP_LABELS = {
    "actions": "Actions",
    "inputs": "Inputs",
    "feedback": "Feedback",
    "navigation": "Navigation",
    "content": "Content",
    "containers": "Containers",
    "layout": "Layout",
    "overlays": "Overlays",
}
TYPE_SAMPLE = "Aa Bb Cc 0123 The quick brown fox"
IMAGE_FORMATS = {"PNG", "JPG", "JPEG", "GIF", "SVG", "ICO", "WEBP"}
LABELS = {
    "list_sep": ", ",
    "clause_sep": "; ",
    "lead_sep": " ",
    "tier_primitive": "Raw palette: palette-&lt;family&gt;-&lt;step&gt;; a larger step is darker; alpha colours keep their value. Not part of the Tailwind theme.",
    "tier_semantic": "Role colours: components use this tier or the component tier. Tailwind colour name = token name without <code>color-</code>.",
    "tier_component": "Component-only colours, created only when a component needs its own value; Tailwind references them as <code>bg-(--{p}-&#8230;)</code>.",
    "ratio_pair": "on white %.2f:1 / on black %.2f:1",
    "show_component_colors": "Show %d component colours",
    "colors_lead": "Swatches render the CSS variables; on-white / on-black ratios are WCAG 2.x (translucent colours over white). Brand pairs are listed under Contrast.",
    "font_stacks": "Font stacks",
    "type_heads": "token / utility|sample|value|usage",
    "f_size": "size", "f_line": "line height", "f_weight": "weight", "f_spacing": "letter spacing",
    "bp_and_up": "%s and up: %s",
    "family": "family %s",
    "scale_summary": "%s scale (%d)",
    "scale_heads": "token|tier|value|usage",
    "type_lead": ("Tailwind uses <code>text-&lt;role&gt;-&lt;size&gt;</code> with a <code>font-*</code> stack; other stacks use "
                  "<code>.{p}-type-&lt;role&gt;-&lt;size&gt;</code>. Samples render with the latter; breakpoint overrides follow the "
                  "window width and are listed under each name."),
    "lead_space": "The number in space-&lt;px&gt; is px; Tailwind step = px / 4 (<code>p-4</code> = space-16).",
    "lead_radius": "Tailwind: <code>rounded-&lt;name&gt;</code>.",
    "lead_shadow": "Elevation and focus ring (<code>shadow-&lt;name&gt;</code>); component shadows belong to their component only.",
    "lead_size": "Control heights use min-height; layout widths keep the source values (<code>max-w-&lt;name&gt;</code>).",
    "lead_duration": "Tailwind: <code>duration-(--{p}-duration-&lt;ms&gt;)</code>. With a reduced-motion preference the base stylesheet shortens durations to near zero.",
    "lead_easing": "",
    "lead_breakpoint": "Always mobile-first min-width; Tailwind variants <code>sm:</code>&#8230;<code>2xl:</code> share these values.",
    "title_space": "Spacing", "title_radius": "Radius", "title_shadow": "Elevation", "title_size": "Size",
    "title_duration": "Motion &#183; duration", "title_easing": "Motion &#183; easing", "title_breakpoint": "Breakpoint",
    "scales_heads": "token|tier|value|preview|usage",
    "min_width": "minimum supported width %s (not a token)",
    "scales_title": "Spacing / Radius / Elevation / Size / Motion",
    "parts": "parts: %s",
    "sizes": "size: %s",
    "states": "states: %s",
    "spec": "spec",
    "scope_shared": "shared",
    "mapping_summary": "token mapping (component-tokens.json, %d rows)",
    "mapping_heads": "scope|part|state|property|value",
    "components_lead": ("%d components, grouped. Each card id is its anchor (&lt;component&gt;--&lt;variant&gt;); a card shows the "
                        "variant x state matrix in Tailwind markup. Interactive states (hover, active, focus) are shown statically "
                        "(elements carry data-preview-state); width conditions follow the window width. Parts, states and token "
                        "mapping follow each card."),
    "composed_of": "composed of: %s",
    "patterns_lead": "%d patterns built only from component Tailwind markup; content is neutral placeholder.",
    "asset_meta": "%s &#183; %s px &#183; %s bytes",
    "asset_used": "used by components: %s",
    "sample_text": "Text Aa",
    "pairs_title": "Brand and reference pairs (%d)",
    "pairs_heads": "id|kind|sample|foreground|background|class|ratio|result|context",
    "added_pass": "pass %.1f",
    "added_fail": "fail",
    "added_title": "Added-state acceptance (%d)",
    "added_heads": "state|surface|foreground|ring|ratio|result",
    "contrast_lead": "%s Method: %s. Class: %s.",
    "toc_cover": "Cover",
    "page_title": "%s %s preview",
    "toc_label": "Contents",
}


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def esc(s):
    return html.escape(str(s), quote=True)


def code(s):
    return "<code>%s</code>" % esc(s)


def rich(s):
    """Escape, then turn `x` into <code>x</code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(s))


# ---------------------------------------------------------------- tokens

class Tokens:
    def __init__(self, doc):
        self.doc = doc
        self.prefix = (doc.get("css") or {}).get("prefix")
        if not self.prefix:
            raise SystemExit("tokens.json has no css.prefix")
        self.index = {}
        for fam, node in doc.items():
            if isinstance(node, dict) and isinstance(node.get("tokens"), list):
                for t in node["tokens"]:
                    self.index[t["name"]] = t
        tp = doc.get("type") or {}
        for key, t in (tp.get("families") or {}).items():
            self.index["font-family-" + key] = dict(t, name="font-family-" + key)
        for scale in (tp.get("scales") or {}).values():
            for t in scale.get("tokens") or []:
                self.index[t["name"]] = t

    def var(self, name):
        return "var(--%s-%s)" % (self.prefix, name)

    def resolve(self, value, depth=0):
        if depth > 20:
            return str(value)
        s = str(value)

        def rep(m):
            t = self.index.get(m.group(1))
            return self.resolve(t["value"], depth + 1) if t else m.group(0)
        return re.sub(r"\{([A-Za-z0-9_.-]+)\}", rep, s)


def parse_color(v):
    v = v.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (1.0,)
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", v)
    if m:
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    return None


def luminance(rgba):
    r, g, b, a = rgba
    # translucent colours are composited over white first
    r, g, b = (c * a + 255 * (1 - a) for c in (r, g, b))

    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast_pair(rgba):
    L = luminance(rgba)
    return 1.05 / (L + 0.05), (L + 0.05) / 0.05


# ---------------------------------------------------------------- fragments

class Fragments:
    def __init__(self, pkg, prefix):
        self.pkg = pkg
        self.begin = "<!-- %s-preview:begin -->" % prefix
        self.end = "<!-- %s-preview:end -->" % prefix

    def body(self, rel):
        t = (self.pkg / rel).read_text(encoding="utf-8")
        a = t.index(self.begin) + len(self.begin)
        b = t.index(self.end)
        body = t[a:b].strip("\n")
        return re.sub(r'(src|href)="\.\./\.\./', r'\1="', body)


# ---------------------------------------------------------------- page parts

class Page:
    """Labels and options for one build."""

    def __init__(self, T, rules):
        self.T = T
        self.p = T.prefix
        self.L = dict(LABELS, **(rules.get("labels") or {}))
        self.groups = dict(GROUP_LABELS, **(rules.get("group_labels") or {}))
        self.type_sample = rules.get("type_sample") or TYPE_SAMPLE
        self.lang = rules.get("lang") or "en"
        self.favicon = rules.get("favicon")
        self.inverse_markers = rules.get("inverse_markers") or ["inverse"]

    def t(self, key):
        return self.L[key].replace("{p}", self.p)

    def heads(self, key):
        return self.t(key).split("|")


def section(sid, title, body, lead, prefix):
    p = prefix
    ld = '<p class="%s-preview-lead">%s</p>\n' % (p, lead) if lead else ""
    return '<section class="%s-preview-section" id="%s">\n<h2 class="%s-preview-h2">%s</h2>\n%s%s\n</section>' % (p, sid, p, title, ld, body)


def table(prefix, heads, rows):
    p = prefix
    th = "".join("<th>%s</th>" % h for h in heads)
    tr = "\n".join("<tr>%s</tr>" % "".join(c if c.startswith("<td") else "<td>%s</td>" % c for c in r) for r in rows)
    return '<div class="%s-preview-table-wrap"><table class="%s-preview-table"><thead><tr>%s</tr></thead><tbody>\n%s\n</tbody></table></div>' % (p, p, th, tr)


def origin_tag(prefix, t):
    if t.get("origin") == "added":
        return ' <span class="%s-preview-tag %s-preview-tag--added">added</span>' % (prefix, prefix)
    return ""


def render_colors(P):
    T, p = P.T, P.p
    toks = (T.doc.get("color") or {}).get("tokens") or []
    out = []
    note = (T.doc.get("color") or {}).get("note")
    tiers = [("primitive", "Primitive", P.t("tier_primitive")),
             ("semantic", "Semantic", P.t("tier_semantic")),
             ("component", "Component", P.t("tier_component"))]
    for tier, title, lead in tiers:
        items = [t for t in toks if t.get("tier") == tier]
        if not items:
            continue
        cards = []
        for t in items:
            resolved = T.resolve(t["value"])
            rgba = parse_color(resolved)
            ratio = (P.t("ratio_pair") % contrast_pair(rgba)) if rgba else ""
            raw = "" if resolved == t["value"] else " &#8592; %s" % code(t["value"])
            cards.append(
                '<figure class="%s-preview-swatch"><div class="%s-preview-swatch__chip" style="background-color: %s"></div>'
                '<figcaption class="%s-preview-swatch__body"><span class="%s-preview-swatch__name">%s%s</span>'
                '<span>%s%s</span><span class="%s-preview-meta">%s</span><span>%s</span></figcaption></figure>' % (
                    p, p, T.var(t["name"]), p, p, esc(t["name"]), origin_tag(p, t), code(resolved), raw, p, esc(ratio), rich(t.get("usage", ""))))
        grid = '<div class="%s-preview-swatches">\n%s\n</div>' % (p, "\n".join(cards))
        head = '<h3 class="%s-preview-h3" id="colors-%s">%s (%d)</h3>\n<p class="%s-preview-lead">%s</p>\n' % (p, tier, title, len(items), p, lead)
        if tier == "component":
            out.append(head + '<details><summary>%s</summary>\n%s\n</details>' % (P.t("show_component_colors") % len(items), grid))
        else:
            out.append(head + grid)
    lead = P.t("colors_lead")
    if note:
        lead += " " + esc(note)
    return section("colors", "Colors", "\n".join(out), lead, p)


def bp_label(T, name):
    t = T.index.get(name)
    return "%s (&#8805;%s)" % (esc(name), esc(T.resolve(t["value"]))) if t else esc(name)


def render_type(P):
    T, p = P.T, P.p
    tp = T.doc.get("type") or {}
    out = []
    fam_rows = []
    for key, t in (tp.get("families") or {}).items():
        fam_rows.append([code("font-family-" + key) + "<br>" + code("font-" + key),
                         '<span style="font-family: %s">%s</span>' % (T.var("font-family-" + key), esc(P.type_sample)),
                         code(t["value"]), rich(t.get("usage", ""))])
    out.append('<h3 class="%s-preview-h3">%s</h3>\n' % (p, P.t("font_stacks")) + table(p, P.heads("type_heads"), fam_rows))
    for g in tp.get("groups") or []:
        rows = []
        for st in g.get("styles") or []:
            vals = []
            for field, label in [("fontSize", "f_size"), ("lineHeight", "f_line"), ("fontWeight", "f_weight"), ("letterSpacing", "f_spacing")]:
                vals.append("%s %s" % (P.t(label), esc(T.resolve(st.get(field, "")))))
            fam = st.get("family", "")
            bps = []
            for bp in st.get("breakpoints") or []:
                ov = P.t("list_sep").join("%s %s" % (k, esc(T.resolve(v))) for k, v in bp.items() if k != "min")
                bps.append(P.t("bp_and_up") % (bp_label(T, bp.get("min", "")), ov))
            util = "text-" + st["name"][len("type-"):]
            rows.append(
                '<div class="%s-preview-type"><div><p class="%s-preview-card__title">%s%s</p><p class="%s-preview-meta">%s %s<br>%s<br>%s%s</p></div>'
                '<p class="%s-preview-type__sample %s-%s">%s</p></div>' % (
                    p, p, code(st["name"]), origin_tag(p, st), p, code(util), code("." + p + "-" + st["name"]), " / ".join(vals),
                    P.t("family") % esc(fam), ("<br>" + "<br>".join(bps)) if bps else "", p, p, esc(st["name"]), esc(P.type_sample)))
        out.append('<h3 class="%s-preview-h3">%s</h3>\n<p class="%s-preview-lead">%s</p>\n%s' % (
            p, esc(g.get("name", "")), p, esc(g.get("note", "")), "\n".join(rows)))
    for key, scale in (tp.get("scales") or {}).items():
        rows = []
        for t in scale.get("tokens") or []:
            rows.append([code(t["name"]), esc(t.get("tier", "")),
                         code(t["value"]) + ("" if T.resolve(t["value"]) == t["value"] else " &#8594; " + code(T.resolve(t["value"]))),
                         rich(t.get("usage", ""))])
        out.append('<details><summary>%s</summary>\n%s\n</details>' % (P.t("scale_summary") % (esc(key), len(rows)),
                                                                        table(p, P.heads("scale_heads"), rows)))
    return section("typography", "Typography", "\n".join(out), P.t("type_lead"), p)


def scale_visual(T, fam, t):
    p = T.prefix
    v = T.var(t["name"])
    resolved = T.resolve(t["value"])
    if fam == "space":
        return '<span class="%s-preview-bar" style="width: %s"></span>' % (p, v)
    if fam == "radius":
        return '<span class="%s-preview-box" style="border-radius: %s"></span>' % (p, v)
    if fam == "shadow":
        return '<span class="%s-preview-box %s-preview-box--shadow" style="box-shadow: %s"></span>' % (p, p, v)
    if fam == "size" and re.fullmatch(r"\d+(\.\d+)?px", resolved) and float(resolved[:-2]) <= 1200:
        return '<span class="%s-preview-bar" style="width: %s"></span>' % (p, v)
    return ""


SCALES = ["space", "radius", "shadow", "size", "duration", "easing", "breakpoint"]


def render_scales(P, layout_body):
    T, p = P.T, P.p
    out = []
    for fam in SCALES:
        node = T.doc.get(fam) or {}
        toks = node.get("tokens") or []
        if not toks:
            continue
        rows = []
        for t in toks:
            val = code(t["value"])
            r = T.resolve(t["value"])
            if r != t["value"]:
                val += " &#8594; " + code(r)
            rows.append([code(t["name"]) + origin_tag(p, t), esc(t.get("tier", "")), val, scale_visual(T, fam, t), rich(t.get("usage", ""))])
        extra = []
        if node.get("note"):
            extra.append(esc(node["note"]))
        if fam == "breakpoint" and node.get("min_supported_width"):
            extra.append(P.t("min_width") % esc(node["min_supported_width"]))
        ld = P.t("lead_sep").join(x for x in [P.t("lead_" + fam)] + extra if x)
        out.append('<h3 class="%s-preview-h3" id="scale-%s">%s (%d)</h3>\n%s%s' % (
            p, fam, P.t("title_" + fam), len(rows), ('<p class="%s-preview-lead">%s</p>\n' % (p, ld)) if ld else "",
            table(p, P.heads("scales_heads"), rows)))
    out.append('<h3 class="%s-preview-h3" id="scale-layout">Layout</h3>\n%s' % (p, layout_body))
    return section("scales", P.t("scales_title"), "\n".join(out), "", p)


# ---------------------------------------------------------------- cards

def fmt_val(T, v):
    if not isinstance(v, dict):
        return code(v)
    if "token" in v:
        s = code(v["token"])
        if v.get("wrap"):
            s += " <span class=\"%s-preview-meta\">wrap %s</span>" % (T.prefix, esc(v["wrap"]))
        return s
    if "tokens" in v:
        return " ".join(code(x) for x in v["tokens"])
    if "literal" in v:
        return "%s <span class=\"%s-preview-meta\">literal%s</span>" % (code(v["literal"]), T.prefix, (": " + esc(v["note"])) if v.get("note") else "")
    if "template" in v:
        return "%s <span class=\"%s-preview-meta\">template</span>" % (code(v["template"]), T.prefix)
    if "asset" in v:
        return code(v["asset"])
    return code(json.dumps(v, ensure_ascii=False))


def part_rows(T, scope, parts):
    rows = []
    for part, states in (parts or {}).items():
        host = states.get("$host") if isinstance(states, dict) else None
        for st, props in states.items():
            if st.startswith("$") or not isinstance(props, dict):
                continue
            for prop, val in props.items():
                if prop.startswith("$"):
                    continue
                rows.append([esc(scope), code(part) + (" <span class=\"%s-preview-meta\">host %s</span>" % (T.prefix, esc(host)) if host else ""),
                             code(st), code(prop), fmt_val(T, val)])
    return rows


def card_meta(P, unit, key, kind, states_def):
    T, p = P.T, P.p
    lines = []
    var = (unit.get("variants") or {}).get(key) if kind == "component" else None
    if unit.get("anatomy"):
        lines.append("<p>%s</p>" % (P.t("parts") % " ".join(code(c) for c in unit["anatomy"])))
    if unit.get("sizes"):
        lines.append("<p>%s</p>" % (P.t("sizes") % " ".join(code(c) for c in unit["sizes"])))
    sem = unit.get("semantic_states") or {}
    if sem:
        bits = []
        for name, s in sem.items():
            sel = P.t("list_sep").join(s.get("selectors") or []) or "-"
            tw = " ".join(code(v + ":") for v in (states_def.get(name) or {}).get("tailwind") or [])
            bits.append("%s %s &#8594; %s" % (esc(name), code(sel), tw or "-"))
        lines.append("<p>%s</p>" % (P.t("states") % P.t("clause_sep").join(bits)))
    if unit.get("spec"):
        lines.append('<p>%s: <a href="%s">%s</a></p>' % (P.t("spec"), esc(unit["spec"]), esc(unit["spec"])))
    rows = part_rows(T, P.t("scope_shared"), unit.get("parts"))
    if var:
        rows += part_rows(T, key, var.get("parts"))
    for sname, s in (unit.get("sizes") or {}).items():
        rows += part_rows(T, "size " + sname, s.get("parts"))
    for c in unit.get("compound") or []:
        rows += part_rows(T, "+".join(c.get("classes") or []), c.get("parts"))
    if rows:
        lines.append('<details><summary>%s</summary>\n%s\n</details>' % (
            P.t("mapping_summary") % len(rows), table(p, P.heads("mapping_heads"), rows)))
    return '<div class="%s-preview-card__meta">\n%s\n</div>' % (p, "\n".join(lines))


def enrich(P, body, lookup, seen, states_def):
    rx = re.compile(r'(<article class="%s-preview-card" id="([^"]+)"[^>]*>)(.*?)(</article>)' % re.escape(P.p), re.S)

    def rep(m):
        key = m.group(2)
        seen.append(key)
        if key not in lookup:
            return m.group(0)
        unit, kind = lookup[key]
        return m.group(1) + m.group(3) + card_meta(P, unit, key, kind, states_def) + "\n" + m.group(4)
    return rx.sub(rep, body)


def render_components(P, cmap, frags, lookup, seen):
    p = P.p
    comps = cmap.get("components") or {}
    sd = cmap.get("state_selectors") or {}
    groups = []
    for uid, u in comps.items():
        g = u.get("group", "other")
        if g not in groups:
            groups.append(g)
    nav = []
    out = []
    for g in groups:
        label = P.groups.get(g, g)
        nav.append('<a href="#group-%s">%s</a>' % (esc(g), esc(label)))
        units = []
        for uid, u in comps.items():
            if u.get("group", "other") != g:
                continue
            body = enrich(P, frags.body((u.get("preview") or {}).get("file")), lookup, seen, sd)
            units.append('<div class="%s-preview-unit" id="unit-%s">\n<div class="%s-preview-unit__head"><h3 class="%s-preview-h3">%s %s</h3>'
                         '<p class="%s-preview-lead">%s</p></div>\n%s\n</div>' % (
                             p, esc(uid), p, p, esc(u.get("name", uid)), code(uid), p, esc(u.get("summary", "")), body))
        out.append('<section class="%s-preview-group" id="group-%s">\n<h3 class="%s-preview-h3">%s &#183; %s</h3>\n%s\n</section>' % (
            p, esc(g), p, esc(label), esc(g), "\n".join(units)))
    return section("components", "Components", '<nav class="%s-preview-subnav">%s</nav>\n%s' % (p, "".join(nav), "\n".join(out)),
                   P.t("components_lead") % len(comps), p)


def render_patterns(P, cmap, frags, lookup, seen):
    p = P.p
    comps = cmap.get("components") or {}
    sd = cmap.get("state_selectors") or {}
    out = []
    nav = []
    for pt in cmap.get("patterns") or []:
        pid = pt["id"]
        nav.append('<a href="#%s">%s</a>' % (esc(pid), esc(pt.get("name", pid))))
        body = enrich(P, frags.body((pt.get("preview") or {}).get("file")), lookup, seen, sd)
        used = P.t("list_sep").join('<a href="#unit-%s">%s</a>' % (esc(c), esc((comps.get(c) or {}).get("name", c))) for c in pt.get("components") or [])
        out.append('<div class="%s-preview-unit" id="unit-%s">\n<div class="%s-preview-unit__head"><h3 class="%s-preview-h3">%s %s</h3>'
                   '<p class="%s-preview-lead">%s</p></div>\n%s\n</div>' % (p, esc(pid), p, p, esc(pt.get("name", pid)), code(pid), p,
                                                                          P.t("composed_of") % used, body))
    return section("patterns", "Patterns", '<nav class="%s-preview-subnav">%s</nav>\n%s' % (p, "".join(nav), "\n".join(out)),
                   P.t("patterns_lead") % len(cmap.get("patterns") or []), p)


# ---------------------------------------------------------------- assets, contrast, gaps

def parse_assets(text):
    rows = []
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        rows.append(cells)
    return rows


def render_assets(P, pkg):
    p = P.p
    readme = (pkg / "assets" / "README.md").read_text(encoding="utf-8")
    tiles = []
    for cells in parse_assets(readme):
        path = cells[0].strip("`")
        fmt, dim, size, usage, used = cells[1], cells[2], cells[3], cells[4], cells[5]
        inverse = any(m in usage for m in P.inverse_markers)
        view = ('<img src="assets/%s" alt="" loading="lazy">' % esc(path)) if fmt.upper() in IMAGE_FORMATS else esc(fmt)
        tiles.append('<figure class="%s-preview-asset"><div class="%s-preview-asset__view%s">%s</div>'
                     '<figcaption class="%s-preview-asset__body"><strong>%s</strong><br>%s<br>%s<br><span class="%s-preview-meta">%s</span></figcaption></figure>' % (
                         p, p, " %s-preview-asset__view--inverse" % p if inverse else "", view, p, code("assets/" + path),
                         P.t("asset_meta") % (esc(fmt), esc(dim), esc(size)), rich(usage), p, P.t("asset_used") % esc(used)))
    intro = [ln for ln in readme.splitlines() if ln and not ln.startswith("|") and not ln.startswith("#")]
    lead = " ".join(rich(ln.lstrip("- ")) for ln in intro[:2])
    return section("assets", "Assets", '<div class="%s-preview-assets">\n%s\n</div>' % (p, "\n".join(tiles)), lead, p)


def chip(T, name):
    return '<span class="%s-preview-chip" style="background-color: %s" title="%s"></span>' % (T.prefix, T.var(name), esc(name))


def render_contrast(P, cdoc):
    T, p = P.T, P.p
    rows = []
    for r in cdoc.get("source_pairs") or []:
        fail = r.get("ratio", 0) < r.get("threshold", 0) and not r.get("exempt")
        op = "; opacity: %s" % r["opacity"] if "opacity" in r else ""
        sample = '<span class="%s-preview-sample" style="color: %s; background-color: %s%s">%s</span>' % (
            p, T.var(r["fg"]), T.var(r["bg"]), op, esc(P.t("sample_text")))
        res = esc(r.get("result", ""))
        if fail:
            res = '<span class="%s-preview-tag %s-preview-tag--fail">%s</span>' % (p, p, res)
        if r.get("exempt"):
            res += '<br><span class="%s-preview-meta">%s</span>' % (p, esc(r["exempt"]))
        rows.append([esc(r.get("id", "")), esc(r.get("kind", "")), sample, chip(T, r["fg"]) + " " + code(r["fg"]), chip(T, r["bg"]) + " " + code(r["bg"]),
                     esc(r.get("class", "")), '<td class="%s-preview-num">%.2f:1</td>' % (p, r.get("ratio", 0)), res, rich(r.get("context", ""))])
    out = ['<h3 class="%s-preview-h3">%s</h3>' % (p, P.t("pairs_title") % len(rows)), table(p, P.heads("pairs_heads"), rows)]
    added = cdoc.get("added_states") or {}
    if added:
        arows = []
        for r in added.get("rows") or []:
            ok = r.get("pass")
            res = (P.t("added_pass") % added.get("threshold", 3.0)) if ok else \
                '<span class="%s-preview-tag %s-preview-tag--fail">%s</span>' % (p, p, P.t("added_fail"))
            arows.append([esc(r.get("state", "")), chip(T, r["surface"]) + " " + code(r["surface"]), chip(T, r["fg"]) + " " + code(r["fg"]),
                          esc(r.get("ring", "")), '<td class="%s-preview-num">%.2f:1</td>' % (p, r.get("ratio", 0)), res])
        out.append('<h3 class="%s-preview-h3">%s</h3>\n<p class="%s-preview-lead">%s</p>\n%s' % (
            p, P.t("added_title") % len(arows), p, esc(added.get("focus_ring", "")), table(p, P.heads("added_heads"), arows)))
    lead = P.t("contrast_lead") % (esc(cdoc.get("note", "")), esc(cdoc.get("method", "")), esc(cdoc.get("class_rule", "")))
    return section("contrast", "Contrast", "\n".join(out), lead, p)


def render_gaps(P, gdoc):
    p = P.p
    items = "\n".join('<li id="%s"><strong>%s</strong> %s<br>%s</li>' % (esc(g["id"]), esc(g.get("title", "")), code(g["id"]), rich(g.get("detail", "")))
                      for g in gdoc.get("gaps") or [])
    return section("gaps", "Known Gaps", '<ul class="%s-preview-gaps">\n%s\n</ul>' % (p, items), esc(gdoc.get("note", "")), p)


# ---------------------------------------------------------------- page

def build(pkg):
    T = Tokens(load_json(pkg / "tokens.json"))
    p = T.prefix
    cmap = load_json(pkg / "components" / "component-tokens.json")
    cdoc = load_json(pkg / "data" / "contrast.json")
    gdoc = load_json(pkg / "data" / "gaps.json")
    frags = Fragments(pkg, p)
    rules = cmap.get("preview_rules") or {}
    P = Page(T, rules)
    layout_file = rules.get("layout_file", "preview/foundations/layout.html")
    cover_file = str(Path(layout_file).parent / "cover.html").replace("\\", "/")
    sd = cmap.get("state_selectors") or {}

    lookup = {}
    expected = []
    for uid, u in (cmap.get("components") or {}).items():
        for a in (u.get("preview") or {}).get("anchors") or []:
            lookup[a] = (u, "component")
            expected.append(a)
    for pt in cmap.get("patterns") or []:
        for a in (pt.get("preview") or {}).get("anchors") or []:
            lookup[a] = (pt, "pattern")
            expected.append(a)
    for lid, u in (cmap.get("layout") or {}).items():
        for a in (u.get("preview") or {}).get("anchors") or []:
            lookup[a] = (u, "layout")
            expected.append(a)

    seen = []
    layout_body = enrich(P, frags.body(layout_file), lookup, seen, sd)
    components = render_components(P, cmap, frags, lookup, seen)
    patterns = render_patterns(P, cmap, frags, lookup, seen)
    title = P.t("page_title") % (T.doc.get("name", ""), T.doc.get("version", ""))
    toc_items = [("cover", P.t("toc_cover")), ("colors", "Colors"), ("typography", "Typography"), ("scales", P.t("scales_title")),
                 ("components", "Components"), ("patterns", "Patterns"), ("assets", "Assets"), ("contrast", "Contrast"), ("gaps", "Known Gaps")]
    toc = '<nav class="%s-preview-toc" aria-label="%s">%s</nav>' % (p, esc(P.t("toc_label")), "".join('<a href="#%s">%s</a>' % (i, n) for i, n in toc_items))
    head = ["<!doctype html>", '<html lang="%s">' % esc(P.lang), "<head>", '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">', "<title>%s</title>" % esc(title.strip())]
    if P.favicon:
        head.append('<link rel="icon" href="%s">' % esc(P.favicon))
    parts = head + [
        '<link rel="stylesheet" href="preview/tailwind.css">',
        '<link rel="stylesheet" href="preview/preview.css">',
        "</head>",
        '<body class="%s-preview-page">' % p,
        "<!-- Generated by build_preview.py from preview/ fragments and data files. Do not edit by hand. -->",
        toc,
        '<main class="%s-preview-main">' % p,
        '<section class="%s-preview-section" id="cover">\n%s\n</section>' % (p, frags.body(cover_file)),
        render_colors(P),
        render_type(P),
        render_scales(P, layout_body),
        components,
        patterns,
        render_assets(P, pkg),
        render_contrast(P, cdoc),
        render_gaps(P, gdoc),
        "</main>",
        "</body>",
        "</html>",
    ]
    page = "\n".join(parts) + "\n"
    missing = [a for a in expected if a not in seen]
    extra = sorted({a for a in seen if a not in lookup})
    dup = sorted({a for a in seen if seen.count(a) > 1})
    return page, missing, extra, dup, len(seen)


# ---------------------------------------------------------------- tailwind

def tailwind_cli(arg):
    cli = arg or os.environ.get("TAILWIND_CLI")
    return Path(cli) if cli else None


def compile_tailwind(pkg, cli, out_path):
    """Compile tailwind/index.css to out_path with the Tailwind v4 CLI; return (ok, message)."""
    env = dict(os.environ)
    parts = [x.lower() for x in cli.resolve().parts]
    if "node_modules" in parts:
        i = len(parts) - 1 - parts[::-1].index("node_modules")
        nm = Path(*cli.resolve().parts[:i + 1])
        env["NODE_PATH"] = str(nm) + ((os.pathsep + env["NODE_PATH"]) if env.get("NODE_PATH") else "")
    cmd = [str(cli), "-i", str(pkg / "tailwind" / "index.css"), "-o", str(out_path)]
    if os.name == "nt" and cli.suffix.lower() not in (".cmd", ".exe", ".bat"):
        alt = cli.with_suffix(".cmd")
        if alt.exists():
            cmd[0] = str(alt)
    try:
        r = subprocess.run(cmd, cwd=str(pkg), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as ex:
        return False, "cannot run the Tailwind CLI: %s" % ex
    if r.returncode != 0 or not Path(out_path).exists():
        return False, "Tailwind CLI failed: %s" % (r.stderr or r.stdout).strip()[-400:]
    data = Path(out_path).read_bytes().replace(b"\r\n", b"\n")
    Path(out_path).write_bytes(data)
    return True, ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--package", required=True, help="package root (the folder holding tokens.json)")
    ap.add_argument("--tailwind-cli", dest="tailwind_cli", help="Tailwind v4 CLI executable; falls back to the TAILWIND_CLI environment variable")
    ap.add_argument("--check", action="store_true", help="only compare preview.html (and preview/tailwind.css) with the build result")
    a = ap.parse_args(argv)
    pkg = Path(a.package).resolve()
    page, missing, extra, dup, ncards = build(pkg)
    data = page.encode("utf-8")
    out = pkg / "preview.html"
    css_out = pkg / "preview" / "tailwind.css"
    cli = tailwind_cli(a.tailwind_cli)
    problems = []
    if missing:
        problems.append("missing cards: " + ", ".join(missing))
    if dup:
        problems.append("duplicate cards: " + ", ".join(dup))
    if extra:
        problems.append("cards not in the component map: " + ", ".join(extra))
    if a.check:
        same = out.exists() and out.read_bytes() == data
        css_msg, css_ok = "preview/tailwind.css not compared (no Tailwind CLI given)", True
        if cli:
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "tailwind.css"
                ok, msg = compile_tailwind(pkg, cli, tmp)
                if not ok:
                    css_ok, css_msg = False, msg
                else:
                    css_ok = css_out.exists() and css_out.read_bytes() == tmp.read_bytes()
                    css_msg = "preview/tailwind.css %s" % ("matches the compiled result" if css_ok else
                                                           "differs from the compiled result; rerun build_preview.py --tailwind-cli")
        for x in problems:
            print(x)
        print(css_msg)
        print("preview.html %s (%d bytes, %d cards)" % ("matches the fragments" if same else
                                                       "differs from the build result; rerun build_preview.py", len(data), ncards))
        return 0 if same and css_ok and not missing and not dup else 1
    out.write_bytes(data)
    for x in problems:
        print(x)
    print("preview.html: %d bytes, %d cards" % (len(data), ncards))
    if cli:
        ok, msg = compile_tailwind(pkg, cli, css_out)
        if not ok:
            print(msg)
            return 1
        print("preview/tailwind.css: %d bytes" % css_out.stat().st_size)
    else:
        print("no Tailwind CLI given: preview/tailwind.css not recompiled")
    return 1 if missing or dup else 0


if __name__ == "__main__":
    sys.exit(main())
