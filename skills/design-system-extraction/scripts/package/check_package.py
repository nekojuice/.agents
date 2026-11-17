#!/usr/bin/env python3
"""Design-system package check (standard library only).

Usage:
  python -I check_package.py --stage {data,full} --package <package-dir>
         [--forbid-list <forbid-list.txt>] [--tailwind-cli <path>]
         [--expect-version <x.y>] [--plan-id-regex <regex>] [--forbidden-key <key>]...
         [--must-not-exist <rel-path>]... [--assets-total-format "<fmt>"]
         [--design-max-lines <n>] [--section-allow-heading <regex>] [--section-allow-entries <regex>]
         [--invocation {explicit,auto,any}] [--allow-orphans]

stage:
- data: data layer, component map, generator scripts (tokens, theme, contrast), assets
  (DESIGN.md, component specs and preview are not required yet)
- full: everything in data, plus DESIGN.md / SKILL.md / agents, component and pattern specs,
  preview, anchors in three places, links, invocation policy, and the Tailwind notation checks:
  every utility exists in preview/tailwind.css, no block-element-modifier or forced-state
  classes, theme whitelist, no arbitrary values, spacing steps.

Every path is an argument or relative to --package; nothing is looked up elsewhere.
--forbid-list: forbidden-word list ([allow] / [substring] / [class] / [regex] sections).
  Without it the forbid check is SKIP. Keep the list outside the package.
--tailwind-cli: Tailwind v4 CLI (or the TAILWIND_CLI environment variable), the approved pinned
  version. At the full stage a package with a tailwind/ folder must be given one: preview/tailwind.css
  is compared with a fresh compile, and a missing CLI is a FAIL.
--expect-version: SKILL.md frontmatter version to require (SKIP when absent).
--plan-id-regex: identifiers of the extraction plan that must not leak into data/*.json.
--forbidden-key: extra JSON keys that must not appear in tokens.json / the component map
  (added to the built-in research-field list).
--must-not-exist: package-relative files that must be gone (e.g. retired generated files).
--assets-total-format: printf format with (file count, byte total) that assets/README.md must
  contain (default "%d files, %d bytes").
--section-allow-heading / --section-allow-entries: inside DESIGN.md sections whose "## " heading
  matches the first regex, [class] hits and the [regex] entries matching the second regex
  (default: all) are allowed, e.g. a usage section that names the legacy framework's classes.

--invocation: invocation policy the full stage requires of the package. explicit (default):
  disable-model-invocation true and allow_implicit_invocation false; auto: false and true;
  any: only that the two values are inverse. Change it only on the user's decision.
--allow-orphans: report orphan primitives (H5) and unused component tokens as information
  instead of failures. For the Phase 1 snapshot only, which keeps every source value before
  the rebuild decides its layer; never for a rebuilt package.

Generator scripts are loaded from <package>/scripts/ when present, otherwise from the folder
of this checker. Each item prints PASS / FAIL / SKIP with details, then the counts; exit 1 on
any FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
TEXT_EXT = {".md", ".json", ".css", ".html", ".htm", ".js", ".py", ".yaml", ".yml", ".txt", ".svg"}
TIERS = {"primitive", "semantic", "component"}
ORIGINS = {"source", "added"}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
REF = re.compile(r"\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}")
FORBIDDEN_KEYS = {"source", "sources", "v1", "v1_name", "anchor_v1", "lineage", "members", "rep_v1", "markup_source",
                  "summary_source", "used_by"}
COLOR_FAMILIES = {"color"}
TYPE_FAMILIES = {"type", "font-family", "font-size", "line-height", "font-weight", "letter-spacing"}
RESTRICTED = re.compile(r"^(color|background(-color)?|border(-(top|right|bottom|left|block|inline)(-(start|end))?)?-color|"
                        r"outline(-color)?|accent-color|scrollbar-color|caret-color|fill|stroke|text-decoration-color|"
                        r"font(-size|-family|-weight)?|line-height|letter-spacing|"
                        r"(padding|margin)(-(top|right|bottom|left|block|inline)(-(start|end))?)?|gap|row-gap|column-gap|"
                        r"border(-(top|right|bottom|left)-(left|right)?)?-radius|border-radius|"
                        r"box-shadow|text-shadow|"
                        r"(min-|max-)?(width|height)|inset(-(block|inline)(-(start|end))?)?|top|right|bottom|left|text-indent)$")
COLOR_LIT = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(rgb|rgba|hsl|hsla|oklch|lab|lch)\(")
XMLNS = re.compile(r"""\bxmlns(:\w+)?\s*=\s*("[^"]*"|'[^']*')""")  # XML namespace URIs are not external resources
LEN_LIT = re.compile(r"(?<![\w.-])-?\d*\.?\d+(px|rem)\b")
LICENSE_BANNER = re.compile(r"\A/\*![^*]*\*/")  # licence banner of the generated preview/tailwind.css, not a resource load


# ---------------------------------------------------------------- report

class Report:
    def __init__(self):
        self.rows = []

    def add(self, ok, title, detail=""):
        self.rows.append(("PASS" if ok else "FAIL", title, detail))

    def skip(self, title, detail):
        self.rows.append(("SKIP", title, detail))

    def print(self):
        for st, title, detail in self.rows:
            print("[%s] %s%s" % (st, title, (": " + detail) if detail else ""))
        c = {k: sum(1 for r in self.rows if r[0] == k) for k in ("PASS", "FAIL", "SKIP")}
        print("")
        print("PASS %d / FAIL %d / SKIP %d (%d checks)" % (c["PASS"], c["FAIL"], c["SKIP"], len(self.rows)))
        return c["FAIL"] == 0


def short(items, n=8):
    items = list(items)
    s = ", ".join(str(x) for x in items[:n])
    return s + ("... (%d total)" % len(items) if len(items) > n else "")


def prefix_of(tok):
    p = (tok.get("css") or {}).get("prefix")
    if not p:
        raise SystemExit("tokens.json has no css.prefix")
    return p


def script_path(pkg: Path, name: str) -> Path:
    """Generator script: <package>/scripts/<name> when present, else next to this checker."""
    p = pkg / "scripts" / name
    return p if p.exists() else HERE / name


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def text_files(skill: Path):
    for p in sorted(skill.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_EXT and "__pycache__" not in p.parts:
            yield p


# ---------------------------------------------------------------- tokens

def token_index(tok):
    """name -> (family, entry); font stacks are font-family-<key>."""
    idx = {}
    dup = []

    def add(name, fam, e):
        if name in idx:
            dup.append(name)
        idx[name] = (fam, e)

    for fam in ["color", "space", "radius", "shadow", "size", "duration", "easing", "breakpoint"]:
        for t in (tok.get(fam) or {}).get("tokens", []):
            add(t.get("name"), fam, t)
    ty = tok.get("type") or {}
    for k, v in (ty.get("families") or {}).items():
        add("font-family-" + k, "font-family", v)
    for sc, lst in (ty.get("scales") or {}).items():
        for t in lst.get("tokens", []):
            add(t.get("name"), sc, t)
    for g in ty.get("groups", []):
        for s in g.get("styles", []):
            add(s.get("name"), "type", s)
    return idx, dup


def walk_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield path + "." + k, k
            yield from walk_keys(v, path + "." + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_keys(v, "%s[%d]" % (path, i))


def value_refs(v):
    if isinstance(v, str):
        return REF.findall(v)
    return []


def check_tokens(rep, tok):
    idx, dup = token_index(tok)
    problems = []
    if dup:
        problems.append("duplicate names: " + short(dup))
    for name, (fam, e) in idx.items():
        where = "%s(%s)" % (name, fam)
        if not isinstance(name, str) or not NAME_RE.match(name):
            problems.append("name format: %s" % where)
        if fam != "type" and "value" not in e:
            problems.append("missing value: " + where)
        if e.get("tier") not in TIERS:
            problems.append("tier: " + where)
        if e.get("origin") not in ORIGINS:
            problems.append("origin: " + where)
        if not (isinstance(e.get("usage"), str) and e["usage"].strip()):
            problems.append("empty usage: " + where)
        if e.get("tier") == "component" and not e.get("component"):
            problems.append("component tier without component: " + where)
        if e.get("tier") == "primitive" and value_refs(e.get("value")):
            problems.append("primitive must not be an alias: " + where)
        if fam == "color" and isinstance(e.get("value"), str) and not REF.fullmatch(e["value"]):
            if not re.fullmatch(r"#[0-9a-f]{6}|rgba?\([\d.,\s]+\)", e["value"]):
                problems.append("colour value format: " + where)
    bad_keys = sorted({k for _p, k in walk_keys(tok) if k in FORBIDDEN_KEYS})
    if bad_keys:
        problems.append("forbidden keys: " + short(bad_keys))
    themes = tok.get("themes") or []
    if len(themes) < 1:
        problems.append("themes not reserved")
    rep.add(not problems, "tokens.json schema", short(problems) if problems else
            "%d tokens, %d themes" % (len(idx), len(themes)))

    unresolved, cycles = [], []

    def resolve(n, seen):
        if n in seen:
            cycles.append(n)
            return
        seen.add(n)
        fam, e = idx[n]
        vals = [e.get("value")] if fam != "type" else [e.get(k) for k in ("family", "fontSize", "lineHeight", "fontWeight", "letterSpacing")]
        if fam == "type":
            for b in e.get("breakpoints") or []:
                if b.get("min") not in idx:
                    unresolved.append("%s→%s" % (n, b.get("min")))
                vals += [v for k, v in b.items() if k != "min"]
        for v in vals:
            for r in value_refs(v):
                if r not in idx:
                    unresolved.append("%s→%s" % (n, r))
                else:
                    resolve(r, set(seen))

    for n in idx:
        resolve(n, set())
    rep.add(not unresolved and not cycles, "alias resolution", short(unresolved + cycles) if (unresolved or cycles) else "every alias resolves, no cycles")
    return idx


def map_units(cmap):
    for uid, u in (cmap.get("layout") or {}).items():
        yield "layout", uid, u
    for uid, u in (cmap.get("components") or {}).items():
        yield "component", uid, u
    for p in cmap.get("patterns") or []:
        if p.get("parts"):
            yield "pattern", p["id"], p


def unit_parts(u):
    yield "", u.get("parts")
    for k, v in (u.get("variants") or {}).items():
        yield k, v.get("parts")
    for k, v in (u.get("sizes") or {}).items():
        yield "size:" + k, v.get("parts")
    for v in u.get("compound") or []:
        yield "+".join(v.get("classes", [])), v.get("parts")


def walk_map_values(cmap):
    for kind, uid, u in map_units(cmap):
        for scope, parts in unit_parts(u):
            for part, pdef in (parts or {}).items():
                for key, props in pdef.items():
                    if key.startswith("$"):
                        continue
                    for prop, v in props.items():
                        yield kind, uid, scope, part, key, prop, v


def map_refs(v, keywords):
    out = []
    if "token" in v:
        out.append(v["token"])
    if "tokens" in v:
        out += [x for x in v["tokens"] if x not in keywords and not re.fullmatch(r"-?\d+(\.\d+)?%?", x)]
    if "template" in v:
        out += [m.group(2) for m in re.finditer(r"\{(asset:)?([A-Za-z0-9][A-Za-z0-9_./-]*)\}", v["template"]) if not m.group(1)]
    return out


def check_direction(rep, idx, cmap):
    bad = []
    for name, (fam, e) in idx.items():
        tier = e.get("tier")
        vals = [e.get("value")] if fam != "type" else [e.get(k) for k in ("family", "fontSize", "lineHeight", "fontWeight", "letterSpacing")]
        for v in vals:
            for r in value_refs(v):
                if r not in idx:
                    continue
                rt = idx[r][1].get("tier")
                if tier == "semantic" and rt != "primitive":
                    # a composite semantic (shadow) may reference semantic colours: the focus ring is built from focus colours
                    if not (fam == "shadow" and idx[r][0] == "color" and rt == "semantic"):
                        bad.append("%s(semantic)→%s(%s)" % (name, r, rt))
                if tier == "component" and rt == "component" and idx[r][1].get("component") != e.get("component"):
                    bad.append("%s(component)->%s(component of another component)" % (name, r))
    kw = set(cmap.get("keywords") or [])
    for kind, uid, scope, part, key, prop, v in walk_map_values(cmap):
        for r in map_refs(v, kw):
            if r not in idx:
                continue
            fam, e = idx[r]
            if (fam in COLOR_FAMILIES or fam in TYPE_FAMILIES) and e.get("tier") == "primitive":
                bad.append("%s %s.%s.%s->%s (%s primitive)" % (uid, part, key, prop, r, fam))
            if e.get("tier") == "component" and e.get("component") != uid:
                bad.append("%s %s.%s->%s (token owned by %s)" % (uid, part, prop, r, e.get("component")))
    rep.add(not bad, "tier reference direction (semantic->primitive; component->semantic/primitive; component colour and type never use primitives)",
            short(bad) if bad else "")


def check_orphans(rep, idx, tok, cmap, skill, allow_orphans=False):
    used = set()
    for name, (fam, e) in idx.items():
        vals = [e.get("value")] if fam != "type" else [e.get(k) for k in ("family", "fontSize", "lineHeight", "fontWeight", "letterSpacing")]
        if fam == "type":
            for b in e.get("breakpoints") or []:
                used.add(b.get("min"))
                vals += [x for k, x in b.items() if k != "min"]
        for v in vals:
            used.update(value_refs(v))
    kw = set(cmap.get("keywords") or [])
    for kind, uid, scope, part, key, prop, v in walk_map_values(cmap):
        used.update(map_refs(v, kw))
        used.update(re.findall(r"@min:([A-Za-z0-9_-]+)", key))
    for f in ["base.css"]:
        p = skill / f
        if p.exists():
            used.update(re.findall(r"var\(--%s-([A-Za-z0-9_-]+)\)" % prefix_of(tok), p.read_text(encoding="utf-8")))
    used_styles = {u.replace("-font-family", "").replace("-font-size", "").replace("-line-height", "")
                   .replace("-font-weight", "").replace("-letter-spacing", "") for u in used}
    orphan_p = [n for n, (fam, e) in idx.items() if e.get("tier") == "primitive" and n not in used]
    orphan_c = [n for n, (fam, e) in idx.items() if e.get("tier") == "component" and n not in used]
    if allow_orphans:
        rep.add(True, "orphan primitives (info, --allow-orphans)", short(orphan_p) if orphan_p else "every primitive is referenced")
        rep.add(True, "unused component tokens (info, --allow-orphans)", short(orphan_c) if orphan_c else "every component token is used by the map or another token")
    else:
        rep.add(not orphan_p, "orphan primitives (H5)", short(orphan_p) if orphan_p else "every primitive is referenced")
        rep.add(not orphan_c, "unused component tokens", short(orphan_c) if orphan_c else "every component token is used by the map or another token")
    unused_styles = [n for n, (fam, e) in idx.items() if fam == "type" and n not in used and n not in used_styles]
    if unused_styles:
        rep.add(True, "type style usage (info)", "not used directly by the map: " + short(unused_styles) + "; available through .%s-type-* classes" % prefix_of(tok))


# ---------------------------------------------------------------- component map

MECH_KEYS = {"bem", "states", "forced_state_classes", "outer_frame_class"}


def check_map(rep, cmap, skill, pfx):
    probs = []
    states = cmap.get("state_selectors") or {}
    for k in sorted({k for _p, k in walk_keys(cmap) if k in MECH_KEYS}):
        probs.append("forbidden mechanism key: %s" % k)
    for st, d in states.items():
        if "class" in d:
            probs.append("state %s must not carry a class" % st)
        if not d.get("tailwind"):
            probs.append("state %s has no tailwind variant" % st)
    for kind, uid, u in map_units(cmap):
        need = ("name", "group", "summary", "anchor", "spec", "preview", "anatomy", "parts", "variants") if kind == "component" else ("anatomy", "parts")
        for n in need:
            if n not in u:
                probs.append("%s: missing %s" % (uid, n))
        for s in (u.get("semantic_states") or {}).values():
            if "class" in s:
                probs.append("%s: semantic_states must not carry a class" % uid)
        for akey, vd in list((u.get("variants") or {}).items()) + list((u.get("sizes") or {}).items()):
            if "class" in vd:
                probs.append("%s: %s must not carry a class" % (uid, akey))
        declared = set(u.get("anatomy") or [])
        for scope, parts in unit_parts(u):
            for part, pdef in (parts or {}).items():
                if part not in declared:
                    probs.append("%s: part %s not listed in anatomy" % (uid, part))
                for key in pdef:
                    if key.startswith("$"):
                        continue
                    for st in re.split(r"[+:@]", key.split("::")[0].split("@")[0]):
                        if st != "default" and st not in states:
                            probs.append("%s: undefined state %s" % (uid, st))
    rep.add(not probs, "component map structure (anatomy, anchor, states; no block-element-modifier / forced-class keys)", short(probs) if probs else
            "%d components, %d patterns" % (len(cmap.get("components") or {}), len(cmap.get("patterns") or [])))

    # literal policy
    bad = []
    registered = {(e["property"], str(e["value"])) for e in cmap.get("literals") or [] if e.get("structural")}
    all_reg = {(e["property"], str(e["value"])) for e in cmap.get("literals") or []}
    for kind, uid, scope, part, key, prop, v in walk_map_values(cmap):
        lit = v.get("literal") if "literal" in v else v.get("template") if "template" in v else None
        if lit is None:
            continue
        lit_s = str(lit)
        if (prop, lit_s) not in all_reg:
            bad.append("%s %s.%s not registered" % (uid, part, prop))
        body = re.sub(r"\{[^}]*\}", "", lit_s)
        if COLOR_LIT.search(body):
            bad.append("%s %s.%s colour literal %s" % (uid, part, prop, lit_s))
        if RESTRICTED.match(prop) and LEN_LIT.search(body):
            if not ((prop, lit_s) in registered and v.get("structural")):
                bad.append("%s %s.%s length literal %s" % (uid, part, prop, lit_s))
            if not v.get("note"):
                bad.append("%s %s.%s structural value without note" % (uid, part, prop))
    rep.add(not bad, "literal policy (colour / type / spacing / radius / shadow / size use var; structural values registered)", short(bad) if bad else
            "%d literal kinds registered" % len(all_reg))

    # anchors (internal)
    ap = []
    seen = set()
    rules = cmap.get("preview_rules") or {}
    for kind, uid, u in [("component", k, v) for k, v in (cmap.get("components") or {}).items()]:
        anchors = (u.get("preview") or {}).get("anchors") or []
        if list(u.get("variants", {}).keys()) != anchors:
            ap.append("%s: variants keys differ from preview.anchors" % uid)
        if u.get("anchor") != (anchors[0] if anchors else None):
            ap.append("%s: anchor is not the first variant" % uid)
        for a in anchors:
            if not re.fullmatch(r"%s--[a-z0-9-]+" % re.escape(uid), a):
                ap.append("%s: anchor format %s" % (uid, a))
            if a in seen:
                ap.append("duplicate anchor " + a)
            seen.add(a)
        if (u.get("preview") or {}).get("file") != "preview/components/%s.html" % uid:
            ap.append("%s: preview file name" % uid)
        if u.get("spec") != "components/%s.md" % uid:
            ap.append("%s: spec file name" % uid)
    for p in cmap.get("patterns") or []:
        for need in ("id", "name", "components", "anchor", "preview", "spec"):
            if need not in p:
                ap.append("pattern %s missing %s" % (p.get("id"), need))
        if p.get("anchor") != p.get("id"):
            ap.append("pattern %s anchor" % p.get("id"))
        if p.get("anchor") in seen:
            ap.append("duplicate anchor " + str(p.get("anchor")))
        seen.add(p.get("anchor"))
        for c in p.get("components") or []:
            if c not in (cmap.get("components") or {}):
                ap.append("pattern %s uses an unknown component: %s" % (p.get("id"), c))
        if (p.get("preview") or {}).get("file") != "preview/patterns/%s.html" % p.get("id"):
            ap.append("pattern %s preview file name" % p.get("id"))
    rep.add(not ap and bool(rules), "anchor and preview file-name rules (component map is self-consistent)", short(ap) if ap else "%d anchors" % len(seen))
    return seen


def css_decls(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for m in re.finditer(r"([^{};]+)\{([^{}]*)\}", text):
        sel = m.group(1).strip()
        for d in m.group(2).split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                yield sel, k.strip(), v.strip()


def css_selectors(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"url\([^)]*\)", "url()", text)
    text = re.sub(r"\"[^\"]*\"|'[^']*'", '""', text)
    for m in re.finditer(r"([^{}]+)\{", text):
        sel = m.group(1).strip()
        if sel.startswith("@"):
            continue
        yield sel


def check_css(rep, skill, cmap, tok):
    prefix = prefix_of(tok)
    defined = set(re.findall(r"--%s-([A-Za-z0-9_-]+)\s*:" % prefix, (skill / "tokens.css").read_text(encoding="utf-8")))
    registered = {(e["property"], str(e["value"])) for e in cmap.get("literals") or [] if e.get("structural")}
    probs = []
    for f in ["base.css", "tailwind/theme.css", "preview/preview.css"]:
        p = skill / f
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for v in re.findall(r"var\(--%s-([A-Za-z0-9_-]+)\)" % prefix, text):
            if v not in defined:
                probs.append("%s: undefined variable --%s-%s" % (f, prefix, v))
        if f == "tailwind/theme.css":
            for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", text):
                if v.strip() != "initial" and not k.startswith("--breakpoint-") and not re.fullmatch(r"var\(--%s-[\w-]+\)" % prefix, v.strip()):
                    probs.append("%s: %s is not var(--%s-*)" % (f, k, prefix))
            continue
        if f == "preview/preview.css":
            continue
        for sel, k, v in css_decls(text):
            body = re.sub(r"var\([^)]*\)", "", v)
            body = re.sub(r"url\([^)]*\)", "", body)
            if COLOR_LIT.search(body):
                probs.append("%s: %s colour literal" % (f, k))
            if RESTRICTED.match(k) and LEN_LIT.search(body) and (k, v) not in registered:
                probs.append("%s: %s: %s length literal" % (f, k, v))
    rep.add(not probs, "CSS uses only var(--%s-*) (base.css, tailwind/theme.css; breakpoints excepted)" % prefix, short(probs) if probs else "")


# ---------------------------------------------------------------- tailwind

THEME_NS = {"color": "--color-", "text": "--text-", "font": "--font-", "font-weight": "--font-weight-", "leading": "--leading-",
            "tracking": "--tracking-", "radius": "--radius-", "shadow": "--shadow-", "text-shadow": "--text-shadow-",
            "ease": "--ease-", "breakpoint": "--breakpoint-", "container": "--container-"}
COLOR_PREFIX = ["bg", "text", "border", "border-x", "border-y", "border-t", "border-r", "border-b", "border-l", "border-s", "border-e",
                "outline", "accent", "fill", "stroke", "decoration", "ring", "caret", "divide", "placeholder", "from", "via", "to"]
COLOR_SPECIAL = {"transparent", "current", "inherit"}
SPACING_PREFIX = {"p", "px", "py", "pt", "pr", "pb", "pl", "ps", "pe", "m", "mx", "my", "mt", "mr", "mb", "ml", "ms", "me",
                  "gap", "gap-x", "gap-y", "space-x", "space-y", "indent"}
SIZE_PREFIX = {"w", "h", "min-w", "min-h", "max-w", "max-h", "size"}
TEXT_STATIC = {"left", "center", "right", "start", "end", "justify", "ellipsis", "clip", "wrap", "nowrap", "balance", "pretty"}


def theme_names(text):
    names = {k: set() for k in THEME_NS}
    body = text
    for k, head in THEME_NS.items():
        for m in re.finditer(r"%s([\w.-]+)\s*:" % re.escape(head), body):
            n = m.group(1)
            if n == "*" or "--" in n:
                continue
            names[k].add(n)
    # --font-weight-* and --text-shadow-* are also caught by --font- / --text-; separate them
    names["font"] -= {"weight-" + x for x in names["font-weight"]}
    names["font"] = {x for x in names["font"] if not x.startswith("weight-")}
    names["text"] = {x for x in names["text"] if not x.startswith("shadow-")}
    return names


def spec_files(skill):
    out = []
    for d in ("components", "patterns"):
        out += sorted((skill / d).glob("*.md"))
    out += sorted((skill / "preview").rglob("*.html"))
    return out


def class_attr_tokens(text):
    for m in re.finditer(r"\bclass\s*=\s*\"([^\"]*)\"|\bclass\s*=\s*'([^']*)'", text):
        for c in (m.group(1) or m.group(2) or "").split():
            yield c


def split_variants(c):
    """'md:hover:bg-x' -> (['md','hover'], 'bg-x'); colons inside brackets do not split."""
    parts, depth, cur = [], 0, ""
    for ch in c:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == ":" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    return parts, cur


def css_escape(c):
    out = []
    for i, ch in enumerate(c):
        if re.match(r"[A-Za-z0-9_-]", ch):
            out.append("\\3%s " % ch if i == 0 and ch.isdigit() else ch)
        else:
            out.append("\\" + ch)
    return "." + "".join(out)


def registered_literal_values(cmap, prefix):
    vals = set()
    for e in cmap.get("literals") or []:
        v = str(e["value"])
        v = re.sub(r"\{asset:([^}]+)\}", r"url(../\1)", v)
        v = re.sub(r"\{([A-Za-z0-9_.-]+)\}", r"var(--%s-\1)" % prefix, v)
        vals.add(re.sub(r"\s+", "", v))
    return vals


def check_arbitrary(val, literals):
    """Arbitrary value (inside [], underscore = space): no colour values; a px / rem / em length must be a registered structural value."""
    v = val.replace("_", " ")
    v = re.sub(r"^(length|image|position|color|family-name):", "", v)
    if COLOR_LIT.search(re.sub(r"var\([^)]*\)", "", v)):
        return " with a colour value"
    if re.search(r"(?<![\w-])-?\d*\.?\d+(px|rem|em)\b", re.sub(r"var\([^)]*\)", "", v)):
        if re.sub(r"\s+", "", v) not in literals:
            return " with an unregistered length"
    return None


def check_tailwind(rep, skill, stage, cmap, tok):
    if stage != "full":
        for t in ["theme.css in sync with tokens.json (breakpoint literals included)", "every utility of specs and preview exists in preview/tailwind.css",
                  "specs and preview have no block-element-modifier or forced-state classes", "theme whitelist and arbitrary values", "spacing utilities use allowed steps only"]:
            rep.skip(t, "stage data has no specs or preview")
        return
    prefix = prefix_of(tok)
    theme = skill / "tailwind" / "theme.css"
    ttext = theme.read_text(encoding="utf-8") if theme.exists() else ""
    probs = []
    try:
        bt = load_module(script_path(skill, "build_tailwind.py"), "chk_build_tailwind")
        if bt.render(tok) != ttext:
            probs.append("theme.css differs from build_tailwind.py output")
    except Exception as ex:  # noqa: BLE001
        probs.append(repr(ex))
    bps = {t["name"]: t["value"] for t in (tok.get("breakpoint") or {}).get("tokens", [])}
    tw_bps = dict(re.findall(r"--breakpoint-([\w]+)\s*:\s*([^;]+);", ttext))
    try:
        bp_map = load_module(script_path(skill, "build_tailwind.py"), "chk_build_tailwind_cfg").config(tok)["breakpoints"]
    except (Exception, SystemExit) as ex:  # noqa: BLE001
        bp_map = {}
        probs.append("breakpoints: %s" % ex)
    for name, tw in bp_map.items():
        if tw_bps.get(tw, "").strip() != bps.get(name):
            probs.append("breakpoint %s: theme %s / tokens %s" % (tw, tw_bps.get(tw), bps.get(name)))
    rep.add(not probs, "theme.css in sync with tokens.json (breakpoint literals included)", short(probs) if probs else "%d breakpoints" % len(tw_bps))

    files = spec_files(skill)
    uses = {}
    bem, forced = [], []
    bem_rx = re.compile(r"(?<![\w-])\.?%s-(?!preview-)[a-z0-9]+(?:-[a-z0-9]+)*(?:__|--)[a-z0-9]" % prefix)
    forced_rx = re.compile(r"(?<![\w-])\.?is-(hover|active|focus|disabled|invalid)(?![\w-])")
    for p in files + [skill / "preview.html", skill / "DESIGN.md", skill / "SKILL.md"]:
        if not p.exists():
            continue
        rel = p.relative_to(skill).as_posix()
        text = p.read_text(encoding="utf-8")
        for m in bem_rx.finditer(text):
            bem.append("%s: %s" % (rel, m.group(0)))
        for c in class_attr_tokens(text):
            if forced_rx.fullmatch(c):
                forced.append("%s: %s" % (rel, c))
        for m in forced_rx.finditer(text):
            forced.append("%s: %s" % (rel, m.group(0)))
        if p in files:
            for c in class_attr_tokens(text):
                if not c.startswith(prefix + "-preview-"):
                    uses.setdefault(c, rel)
    rep.add(not bem and not forced, "specs and preview have no block-element-modifier or forced-state classes (%s-preview-* excepted)" % prefix,
            short(sorted(set(bem + forced))) if (bem or forced) else "%d files scanned" % (len(files) + 3))

    css = skill / "preview" / "tailwind.css"
    if not css.exists():
        rep.add(False, "every utility of specs and preview exists in preview/tailwind.css", "preview/tailwind.css missing")
    else:
        ctext = css.read_text(encoding="utf-8")
        miss = sorted(c for c in uses if not c.startswith(prefix + "-type-") and css_escape(c) not in ctext)
        rep.add(not miss, "every utility of specs and preview exists in preview/tailwind.css", short("%s (%s)" % (c, uses[c]) for c in miss) if miss else "%d classes" % len(uses))

    names = theme_names(ttext)
    defined = set(re.findall(r"--%s-([A-Za-z0-9_-]+)\s*:" % prefix, (skill / "tokens.css").read_text(encoding="utf-8")))
    literals = registered_literal_values(cmap, prefix)
    bad, steps_bad = [], []
    allowed_steps = {"0"} | {("%g" % (int(t["name"].split("-")[1]) / 4)) for t in tok["space"]["tokens"]}
    for c, rel in sorted(uses.items()):
        variants, u = split_variants(c)
        for v in variants:
            if v in set(bp_map.values()) and v not in names["breakpoint"]:
                bad.append("%s: breakpoint %s undefined" % (c, v))
        u = u.lstrip("!").lstrip("-")
        for m in re.finditer(r"\(--([\w-]+)\)|\((?:length|color|image|family-name):--([\w-]+)\)|var\(--([\w-]+)\)", u):
            n = m.group(1) or m.group(2) or m.group(3)
            if n.startswith(prefix + "-") and n[len(prefix) + 1:] not in defined:
                bad.append("%s: undefined variable --%s" % (c, n))
        for m in re.finditer(r"\[([^\]]*)\]", u):
            why = check_arbitrary(m.group(1), literals)
            if why:
                bad.append("%s: arbitrary value%s" % (c, why))
        if "[" in u or "(" in u:
            continue
        if "-" not in u or re.fullmatch(r"border(-[xytrblse])?", u):
            continue
        # colour names
        for pre in sorted(COLOR_PREFIX, key=len, reverse=True):
            if u.startswith("text-shadow-"):
                break
            if u.startswith(pre + "-"):
                val = u[len(pre) + 1:]
                if pre == "text" and (val in names["text"] or val in TEXT_STATIC):
                    break
                if pre.startswith("border") and re.fullmatch(r"\d+|solid|dashed|dotted|double|none|collapse|separate", val):
                    break
                if pre == "outline" and re.fullmatch(r"\d+|solid|dashed|dotted|double|none|hidden|offset-.*", val):
                    break
                if pre in ("bg",) and re.fullmatch(r"cover|contain|auto|center|top|bottom|left|right|no-repeat|repeat|repeat-x|repeat-y|fixed|scroll|local|clip-.*|origin-.*|size-.*|none", val):
                    break
                if pre == "decoration" and re.fullmatch(r"\d+|solid|dashed|dotted|wavy|double|clone|slice|from-font|auto", val):
                    break
                if val in COLOR_SPECIAL or val in names["color"]:
                    break
                bad.append("%s: colour name %s not defined in the theme" % (c, val))
                break
        for rx, ns, extra in [(r"^rounded(?:-(?:t|r|b|l|s|e|tl|tr|br|bl|ss|se|es|ee))?-(.+)$", "radius", set()),
                              (r"^shadow-(.+)$", "shadow", {"none"}), (r"^text-shadow-(.+)$", "text-shadow", {"none"}),
                              (r"^leading-(.+)$", "leading", {"none"}), (r"^tracking-(.+)$", "tracking", set()),
                              (r"^ease-(.+)$", "ease", {"linear", "initial"})]:
            m2 = re.match(rx, u)
            if m2 and m2.group(1) not in names[ns] and m2.group(1) not in extra:
                bad.append("%s: %s name %s not defined in the theme" % (c, ns, m2.group(1)))
        if u.startswith("font-"):
            val = u[5:]
            if val not in names["font"] and val not in names["font-weight"]:
                bad.append("%s: font name %s not defined in the theme" % (c, val))
        m3 = re.match(r"^(min-w|min-h|max-w|max-h|w|h|size)-(.+)$", u)
        if m3:
            val = m3.group(2)
            if not (re.fullmatch(r"\d+(\.\d+)?|\d+/\d+|full|auto|screen|min|max|fit|px|dvh|svh|lvh|dvw|none", val) or val in names["container"]):
                bad.append("%s: width/height name %s not defined in the theme" % (c, val))
        m4 = re.match(r"^([a-z]+(?:-[xy])?)-(.+)$", u)
        if m4 and m4.group(1) in SPACING_PREFIX:
            val = m4.group(2)
            if val not in ("auto",) and val not in allowed_steps:
                steps_bad.append(c)
    rep.add(not bad, "theme whitelist and arbitrary values (theme utility names exist in theme.css; arbitrary values hold no colours or unregistered lengths)", short(sorted(set(bad))) if bad else
            "%d classes" % len(uses))
    rep.add(not steps_bad, "spacing utilities use allowed steps only (%s)" % ", ".join(sorted(allowed_steps, key=float)), short(sorted(set(steps_bad))) if steps_bad else "")


# ---------------------------------------------------------------- builds

def check_builds(rep, skill, stage, tailwind_cli=None):
    tok_path = skill / "tokens.json"
    try:
        bt = load_module(script_path(skill, "build_tokens.py"), "chk_build_tokens")
        tok = load_json(tok_path)
        a1, b1 = bt.build(tok)
        a2, b2 = bt.build(load_json(tok_path))
        same = a1 == a2 and b1 == b2
        fcss = (skill / "tokens.css").read_text(encoding="utf-8")
        fdt = (skill / "tokens.dtcg.json").read_text(encoding="utf-8")
        rep.add(same and a1 == fcss and b1 == fdt, "build_tokens.py idempotent and equal to tokens.css / tokens.dtcg.json",
                "" if (same and a1 == fcss and b1 == fdt) else "rerun or comparison differs; rerun build_tokens.py")
    except Exception as ex:  # noqa: BLE001
        rep.add(False, "build_tokens.py idempotent", repr(ex))
    try:
        bt2 = load_module(script_path(skill, "build_tailwind.py"), "chk_build_tailwind2")
        t1 = bt2.render(load_json(tok_path))
        ok = t1 == bt2.render(load_json(tok_path)) and t1 == (skill / "tailwind" / "theme.css").read_text(encoding="utf-8")
        rep.add(ok, "build_tailwind.py idempotent and equal to tailwind/theme.css", "" if ok else "rerun build_tailwind.py")
    except Exception as ex:  # noqa: BLE001
        rep.add(False, "build_tailwind.py idempotent", repr(ex))
    try:
        bk = load_module(script_path(skill, "build_contrast.py"), "chk_build_contrast")
        cpath = skill / "data" / "contrast.json"
        doc = load_json(cpath)
        r1 = bk.render(load_json(tok_path), doc)
        r2 = bk.render(load_json(tok_path), json.loads(r1))
        ok = r1 == r2 and r1 == cpath.read_text(encoding="utf-8")
        rep.add(ok, "build_contrast.py idempotent and equal to data/contrast.json", "" if ok else "rerun build_contrast.py")
    except Exception as ex:  # noqa: BLE001
        rep.add(False, "build_contrast.py idempotent", repr(ex))
    bp = script_path(skill, "build_preview.py")
    if stage == "full":
        if not bp.exists():
            rep.add(False, "build_preview.py --check", "build_preview.py not found")
        else:
            cmd = [sys.executable, "-I", str(bp), "--package", str(skill), "--check"]
            if (skill / "tailwind").is_dir():
                rep.add(bool(tailwind_cli), "Tailwind CLI given for the full-stage recompile",
                        "" if tailwind_cli else "tailwind/ exists: pass --tailwind-cli (or TAILWIND_CLI) so preview/tailwind.css is recompiled and compared")
            if tailwind_cli:
                cmd += ["--tailwind-cli", tailwind_cli]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            out = (r.stdout + r.stderr).strip().splitlines()
            rep.add(r.returncode == 0, "build_preview.py --check (preview.html matches the fragments; with a CLI also preview/tailwind.css)", "; ".join(out[-2:]) if out else "")
    else:
        rep.skip("build_preview.py --check", "stage data has no preview")


def check_dtcg(rep, skill, idx):
    p = skill / "tokens.dtcg.json"
    doc = load_json(p)
    probs = []
    leaves = {}

    def walk(node, path):
        if isinstance(node, dict) and "$value" in node:
            leaves[".".join(path)] = node
            return
        if isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("$"):
                    continue
                if any(ch in k for ch in "{}."):
                    probs.append("name contains reserved characters: " + k)
                walk(v, path + [k])

    walk(doc, [])
    allowed = {"color", "dimension", "fontFamily", "fontWeight", "duration", "cubicBezier", "number", "shadow", "typography"}
    for path, node in leaves.items():
        t = node.get("$type")
        v = node["$value"]
        if isinstance(v, str) and re.fullmatch(r"\{[^}]+\}", v):
            if v[1:-1] not in leaves:
                probs.append("unresolved alias: %s -> %s" % (path, v))
            continue
        if t is None:
            if path not in (doc.get("$extensions") or {}).get("unrepresentable", []):
                probs.append("no $type and not listed as unrepresentable: " + path)
            continue
        if t not in allowed:
            probs.append("unknown $type: %s %s" % (path, t))
        if t == "color" and not (isinstance(v, dict) and v.get("colorSpace") and len(v.get("components", [])) == 3):
            probs.append("color format: " + path)
        if t == "dimension" and not (isinstance(v, dict) and v.get("unit") in ("px", "rem") and isinstance(v.get("value"), (int, float))):
            probs.append("dimension format: " + path)
        if t == "duration" and not (isinstance(v, dict) and v.get("unit") in ("ms", "s")):
            probs.append("duration format: " + path)
        if t == "cubicBezier" and not (isinstance(v, list) and len(v) == 4):
            probs.append("cubicBezier format: " + path)
        if t == "typography":
            for k, x in v.items():
                if isinstance(x, str) and re.fullmatch(r"\{[^}]+\}", x) and x[1:-1] not in leaves:
                    probs.append("typography alias: %s.%s" % (path, k))
    if len(leaves) != len(idx):
        probs.append("token count differs: dtcg %d / tokens.json %d" % (len(leaves), len(idx)))
    rep.add(not probs, "DTCG 2025.10 structure ($value, $type, {group.token})", short(probs) if probs else "%d tokens" % len(leaves))


# ---------------------------------------------------------------- data, assets, paths

def check_data(rep, skill, plan_id_regex=None, idx=None):
    c = load_json(skill / "data" / "contrast.json")
    probs = []
    for pr in c.get("source_pairs", []):
        for k in ("id", "kind", "fg", "bg", "class", "context", "ratio", "threshold", "result"):
            if k not in pr:
                probs.append("%s missing %s" % (pr.get("id"), k))
    ad = c.get("added_states") or {}
    added = sorted(n for n, (_f, e) in (idx or {}).items() if e.get("origin") == "added")
    if "added_states" not in c and not added:
        pass  # nothing added (for example a Phase 1 snapshot): no added-state acceptance to check
    elif not ad.get("rows"):
        probs.append("added_states has no rows" + (" (tokens with origin added: %s)" % short(added) if added else ""))
    fails = [r for r in ad.get("rows", []) if not r.get("pass")]
    if ad and (fails or not ad.get("pass")):
        probs.append("added states below %s: %s" % (ad.get("threshold"), short("%s/%s" % (r["state"], r["surface"]) for r in fails)))
    rep.add(not probs, "data/contrast.json (source pairs recorded as they are; added states >= %s:1)" % ad.get("threshold", "?"),
            short(probs) if probs else "%d source pairs, %d added-state rows" % (len(c.get("source_pairs", [])), len(ad.get("rows", []))))
    g = load_json(skill / "data" / "gaps.json")
    gp = []
    ids = [x.get("id") for x in g.get("gaps", [])]
    if len(ids) != len(set(ids)):
        gp.append("duplicate id")
    for x in g.get("gaps", []):
        for k in ("id", "title", "detail"):
            if not x.get(k):
                gp.append("%s missing %s" % (x.get("id"), k))
    if plan_id_regex:
        old_ids = re.compile(plan_id_regex)
        for f in ["data/gaps.json", "data/contrast.json"]:
            t = (skill / f).read_text(encoding="utf-8")
            hits = sorted(set(m.group(0) for m in old_ids.finditer(t)))
            if hits:
                gp.append("%s holds source or plan identifiers: %s" % (f, short(hits)))
    rep.add(not gp, "data/gaps.json complete%s" % (" and data/*.json free of plan identifiers" if plan_id_regex else ""),
            short(gp) if gp else "%d gaps" % len(ids))


def check_assets(rep, skill, cmap, total_fmt="%d files, %d bytes"):
    adir = skill / "assets"
    readme = adir / "README.md"
    probs = []
    files = [p for p in sorted(adir.rglob("*")) if p.is_file() and p.name != "README.md"]
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    total = 0
    for p in files:
        rel = p.relative_to(adir).as_posix()
        data = p.read_bytes()
        total += len(data)
        sha = hashlib.sha256(data).hexdigest()
        row = [ln for ln in text.splitlines() if ("`%s`" % rel) in ln]
        if not row:
            probs.append("README does not list " + rel)
        elif sha not in row[0] or ("| %d |" % len(data)) not in row[0]:
            probs.append("README SHA-256 or size mismatch " + rel)
    if (total_fmt % (len(files), total)) not in text:
        probs.append("README total mismatch (expected '%s')" % (total_fmt % (len(files), total)))
    for kind, uid, scope, part, key, prop, v in walk_map_values(cmap):
        paths = ([v["asset"]] if "asset" in v else []) + re.findall(r"\{asset:([^}]+)\}", v.get("template", ""))
        for ap in paths:
            if not (skill / ap).exists():
                probs.append("%s references a missing asset %s" % (uid, ap))
    rep.add(not probs, "assets (README lists format / size / SHA-256 / total per file; map references exist)",
            short(probs) if probs else total_fmt % (len(files), total))


def check_paths(rep, skill):
    url = re.compile(r"\bhttps?://|(?<![\w:])//[a-z0-9.-]+\.[a-z]{2,}/|\bfile:/" + "/", re.I)
    absp = re.compile(r"(?<![\w])[A-Za-z]:[\\/][\w]|(?:url\(|src=|href=)[\"']?/(?!/)")
    imp = re.compile(r"@import\s+url\(\s*[\"']?https?:|<script[^>]+src=[\"']https?:|<link[^>]+href=[\"']https?:", re.I)
    hits = []
    for p in text_files(skill):
        t = p.read_text(encoding="utf-8", errors="replace")
        t = XMLNS.sub("", t)
        t = LICENSE_BANNER.sub("", t)
        rel = p.relative_to(skill).as_posix()
        for rx, label in [(url, "external URL"), (absp, "absolute path"), (imp, "external resource load")]:
            m = rx.search(t)
            if m:
                hits.append("%s: %s (%s)" % (rel, label, m.group(0)[:30]))
    rep.add(not hits, "external resources and absolute paths (offline, relative paths only)", short(hits) if hits else "")


# ---------------------------------------------------------------- forbid list

def parse_forbid(path: Path):
    sec = None
    out = {"allow": [], "substring": [], "class": [], "regex": [], "section-allow": []}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"\[([a-z-]+)\]", line.strip())
        if m:
            sec = m.group(1)
            continue
        if sec in out:
            out[sec].append(line.strip())
    return out


def allowed_section_spans(text, heading_rx):
    """Character spans of DESIGN.md sections whose "## " heading matches heading_rx (up to the next "## ")."""
    spans = []
    if not heading_rx:
        return spans
    for m in re.finditer(r"^## [^\n]*$", text, flags=re.M):
        if not re.search(heading_rx, m.group(0)[3:]):
            continue
        nxt = re.search(r"^## ", text[m.end():], flags=re.M)
        spans.append((m.start(), m.end() + (nxt.start() if nxt else len(text) - m.end())))
    return spans


def mask_allow(text, allows):
    for a in sorted(allows, key=len, reverse=True):
        text = text.replace(a, " " * len(a))
    return text


CSS_CLASS = re.compile(r"(?<![\w\\-])\.(-?(?:[A-Za-z_]|\\.)(?:[\w-]|\\[0-9a-fA-F]{1,6} ?|\\.)*)")


def css_unescape(s):
    s = re.sub(r"\\([0-9a-fA-F]{1,6}) ?", lambda m: chr(int(m.group(1), 16)), s)
    return re.sub(r"\\(.)", r"\1", s)


def class_tokens(rel, text):
    toks = []
    if rel.endswith(".css"):
        for sel in css_selectors(text):
            toks += [css_unescape(x) for x in CSS_CLASS.findall(sel)]
    for m in re.finditer(r"\bclass(?:Name)?\s*=\s*\"([^\"]*)\"|\bclass(?:Name)?\s*=\s*'([^']*)'", text):
        toks += (m.group(1) or m.group(2) or "").split()
    for st in re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
        for sel in css_selectors(st):
            toks += re.findall(r"(?<![\w-])\.(-?[A-Za-z_][\w-]*)", sel)
    return toks


def check_forbid(rep, skill, forbid_path, section_heading=None, section_entries=None):
    if not forbid_path:
        rep.skip("forbid-list check", "no --forbid-list given (keep the list outside the package)")
        return
    fp = Path(forbid_path)
    if not fp.exists():
        rep.add(False, "forbid-list check", "list file not found")
        return
    released = re.compile(section_entries) if section_entries else None
    fl = parse_forbid(fp)
    subs = [s.lower() for s in fl["substring"]]
    cls = set(fl["class"])
    rxs = [(r, re.compile(r)) for r in fl["regex"]]
    hits = []
    names = [p.relative_to(skill).as_posix() for p in sorted(skill.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
    for rel in names:
        low = mask_allow(rel, fl["allow"]).lower()
        for s in subs:
            if s in low:
                hits.append("file name %s: %s" % (rel, s))
        for r, rx in rxs:
            if rx.search(mask_allow(rel, fl["allow"])):
                hits.append("file name %s: /%s/" % (rel, r))
    for p in text_files(skill):
        rel = p.relative_to(skill).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        masked = mask_allow(text, fl["allow"])
        low = masked.lower()
        for s in subs:
            i = low.find(s)
            if i >= 0:
                hits.append("%s: %s (line %d)" % (rel, s, text.count("\n", 0, i) + 1))
        spans = allowed_section_spans(text, section_heading) if rel == "DESIGN.md" else []

        def in_allowed(pos):
            return any(a <= pos < b for a, b in spans)

        for r, rx in rxs:
            for m in rx.finditer(masked):
                if (released is None or released.search(r)) and in_allowed(m.start()):
                    continue
                hits.append("%s: /%s/ -> %s (line %d)" % (rel, r, m.group(0), text.count("\n", 0, m.start()) + 1))
                break
        if spans:
            scan = "".join(ch if not in_allowed(i) else " " for i, ch in enumerate(text))
        else:
            scan = text
        for c in class_tokens(rel, scan):
            if c in cls:
                hits.append("%s: class %s" % (rel, c))
    rep.add(not hits, "forbid-list check (file names, text, SVG, scripts, preview; [allow] masked first)", short(hits, 12) if hits else
            "%d file names, %d text files scanned" % (len(names), len(list(text_files(skill)))))


# ---------------------------------------------------------------- full-only

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    return m.group(1) if m else ""


POLICIES = {"explicit": ("true", "false"), "auto": ("false", "true")}


def check_policy(rep, skill, stage, expect_version=None, invocation="explicit"):
    if stage != "full":
        rep.skip("SKILL.md and agents/openai.yaml invocation policies are inverse", "stage data has no SKILL.md")
        return
    sk = skill / "SKILL.md"
    oy = skill / "agents" / "openai.yaml"
    if not sk.exists() or not oy.exists():
        rep.add(False, "SKILL.md and agents/openai.yaml invocation policies are inverse", "file missing")
        return
    fm = frontmatter(sk.read_text(encoding="utf-8"))
    dis = re.search(r"^disable-model-invocation:[ \t]*(\w+)", fm, flags=re.M)
    alw = re.search(r"allow_implicit_invocation:[ \t]*(\w+)", oy.read_text(encoding="utf-8"))
    pair = (dis.group(1).lower(), alw.group(1).lower()) if (dis and alw) else None
    ok = pair in POLICIES.values() if invocation == "any" else pair == POLICIES[invocation]
    ver = re.search(r'version:[ \t]*"?([\d.]+)"?', fm)
    rep.add(ok, "SKILL.md and agents/openai.yaml invocation policies are inverse (required: %s)" % invocation,
            "disable-model-invocation=%s, allow_implicit_invocation=%s" % (dis.group(1) if dis else "?", alw.group(1) if alw else "?"))
    if expect_version:
        rep.add(bool(ver and ver.group(1) == expect_version), "SKILL.md frontmatter version %s" % expect_version,
                ver.group(1) if ver else "no version found")
    else:
        rep.skip("SKILL.md frontmatter version", "no --expect-version given")


def html_ids(path: Path):
    return set(re.findall(r"\bid\s*=\s*[\"']([^\"']+)[\"']", path.read_text(encoding="utf-8")))


def check_full_docs(rep, skill, stage, cmap, design_max_lines=500):
    if stage != "full":
        for t in ["DESIGN.md, component and pattern specs exist", "anchors agree in three places (spec heading, preview card id, map key)", "Markdown relative links resolve",
                  "preview.html exists and is offline"]:
            rep.skip(t, "stage data has no DESIGN.md, component specs or preview")
        return
    missing = []
    for f in ["DESIGN.md", "SKILL.md", "agents/openai.yaml", "components/README.md", "preview.html"]:
        if not (skill / f).exists():
            missing.append(f)
    for uid, u in (cmap.get("components") or {}).items():
        for f in [u.get("spec"), (u.get("preview") or {}).get("file")]:
            if f and not (skill / f).exists():
                missing.append(f)
    for p in cmap.get("patterns") or []:
        for f in [p.get("spec"), (p.get("preview") or {}).get("file")]:
            if f and not (skill / f).exists():
                missing.append(f)
    for uid, u in (cmap.get("layout") or {}).items():
        f = (u.get("preview") or {}).get("file")
        if f and not (skill / f).exists():
            missing.append(f)
    dl = (skill / "DESIGN.md").read_text(encoding="utf-8").count("\n") + 1 if (skill / "DESIGN.md").exists() else 0
    rep.add(not missing and dl <= design_max_lines, "DESIGN.md, component and pattern specs exist",
            short(sorted(set(missing))) if missing else "DESIGN.md %d lines" % dl +
            (" (over %d lines)" % design_max_lines if dl > design_max_lines else ""))

    ap = []
    units = [(u.get("spec"), (u.get("preview") or {}).get("file"), (u.get("preview") or {}).get("anchors") or [])
             for u in (cmap.get("components") or {}).values()]
    units += [(p.get("spec"), (p.get("preview") or {}).get("file"), (p.get("preview") or {}).get("anchors") or [])
              for p in cmap.get("patterns") or []]
    for spec, pv, anchors in units:
        st = (skill / spec).read_text(encoding="utf-8") if spec and (skill / spec).exists() else ""
        heads = set(re.findall(r"^#{1,6}\s+.*?`?([a-z0-9-]+(?:--[a-z0-9-]+)?)`?\s*$", st, flags=re.M))
        ids = html_ids(skill / pv) if pv and (skill / pv).exists() else set()
        for a in anchors:
            if a not in heads:
                ap.append("%s heading missing %s" % (spec, a))
            if a not in ids:
                ap.append("%s missing id=%s" % (pv, a))
    rep.add(not ap, "anchors agree in three places (spec heading, preview card id, map key)", short(ap) if ap else "")

    broken = []
    for p in sorted(skill.rglob("*.md")):
        t = p.read_text(encoding="utf-8")
        for m in re.finditer(r"\]\(([^)\s]+)\)", t):
            href = m.group(1)
            if re.match(r"[a-z]+:", href) or href.startswith("#"):
                continue
            path, _, frag = href.partition("#")
            tgt = (p.parent / path).resolve()
            if not tgt.exists():
                broken.append("%s -> %s" % (p.relative_to(skill).as_posix(), href))
            elif frag and tgt.suffix in (".html", ".htm") and frag not in html_ids(tgt):
                broken.append("%s -> %s (anchor missing)" % (p.relative_to(skill).as_posix(), href))
    rep.add(not broken, "Markdown relative links resolve", short(broken) if broken else "")
    pv = skill / "preview.html"
    rep.add(pv.exists(), "preview.html exists and is offline", "" if pv.exists() else "preview.html missing")


def check_files(rep, skill, stage, must_not_exist=()):
    need = ["tokens.json", "tokens.css", "tokens.dtcg.json", "base.css", "components/component-tokens.json",
            "tailwind/theme.css", "tailwind/index.css", "data/contrast.json", "data/gaps.json", "assets/README.md",
            "scripts/build_tokens.py", "scripts/build_tailwind.py", "scripts/build_contrast.py", "scripts/check_package.py"]
    miss = [f for f in need if not (skill / f).exists()]
    gone = [f for f in must_not_exist if (skill / f).exists()]
    rep.add(not miss and not gone, "required files: data layer and scripts%s" % (" (retired files removed)" if must_not_exist else ""),
            short(miss + ["must not exist: " + g for g in gone]) if (miss or gone) else "%d files" % len(need))
    if stage == "full":
        extra = ["SKILL.md", "agents/openai.yaml", "DESIGN.md", "components/README.md", "preview.html",
                 "preview/tailwind.css", "preview/preview.css", "scripts/build_preview.py"]
        m2 = [f for f in extra if not (skill / f).exists()]
        rep.add(not m2, "required files: manual, specs and preview", short(m2) if m2 else "%d files" % len(extra))
    else:
        rep.skip("required files: manual, specs and preview", "not part of stage data")
    return not miss


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["data", "full"], required=True)
    ap.add_argument("--package", required=True, help="package root (the folder holding tokens.json)")
    ap.add_argument("--forbid-list", dest="forbid_list", help="forbidden-word list kept outside the package")
    ap.add_argument("--tailwind-cli", dest="tailwind_cli", default=os.environ.get("TAILWIND_CLI"),
                    help="Tailwind v4 CLI (default: TAILWIND_CLI environment variable)")
    ap.add_argument("--expect-version", help="required SKILL.md frontmatter version")
    ap.add_argument("--plan-id-regex", help="regex of plan identifiers that must not appear in data/*.json")
    ap.add_argument("--forbidden-key", action="append", default=[], help="extra JSON key that must not appear (repeatable)")
    ap.add_argument("--must-not-exist", action="append", default=[], help="package-relative file that must be gone (repeatable)")
    ap.add_argument("--assets-total-format", default="%d files, %d bytes",
                    help="printf format (count, bytes) that assets/README.md must contain")
    ap.add_argument("--design-max-lines", type=int, default=500, help="maximum DESIGN.md length")
    ap.add_argument("--section-allow-heading", help="regex of DESIGN.md '## ' headings whose sections may name forbidden classes")
    ap.add_argument("--section-allow-entries", help="regex selecting the [regex] forbid entries released inside those sections (default: all)")
    ap.add_argument("--invocation", choices=["explicit", "auto", "any"], default="explicit",
                    help="invocation policy required at the full stage (default explicit)")
    ap.add_argument("--allow-orphans", action="store_true",
                    help="Phase 1 snapshot only: orphan primitives and unused component tokens are information, not failures")
    a = ap.parse_args(argv)
    skill = Path(a.package).resolve()
    FORBIDDEN_KEYS.update(a.forbidden_key)
    rep = Report()
    print("package: %s / stage: %s" % (skill.name, a.stage))
    if not check_files(rep, skill, a.stage, a.must_not_exist):
        rep.print()
        return 1
    tok = load_json(skill / "tokens.json")
    cmap = load_json(skill / "components" / "component-tokens.json")
    idx = check_tokens(rep, tok)
    check_direction(rep, idx, cmap)
    check_orphans(rep, idx, tok, cmap, skill, a.allow_orphans)
    check_map(rep, cmap, skill, prefix_of(tok))
    check_css(rep, skill, cmap, tok)
    check_tailwind(rep, skill, a.stage, cmap, tok)
    check_builds(rep, skill, a.stage, a.tailwind_cli)
    check_dtcg(rep, skill, idx)
    check_data(rep, skill, a.plan_id_regex, idx)
    check_assets(rep, skill, cmap, a.assets_total_format)
    check_paths(rep, skill)
    check_forbid(rep, skill, a.forbid_list, a.section_allow_heading, a.section_allow_entries)
    check_policy(rep, skill, a.stage, a.expect_version, a.invocation)
    check_full_docs(rep, skill, a.stage, cmap, a.design_max_lines)
    return 0 if rep.print() else 1


if __name__ == "__main__":
    sys.exit(main())
