#!/usr/bin/env python3
"""CSS rule index (standard library only).

Subcommands:
  index  Scan stylesheets, <style> blocks and inline style attributes of markup files
         (plain HTML, SPA single-file components, server templates) and write a rule index JSON.
  query  Look rules up by class, id, selector fragment or property; optionally order them by
         the global cascade order of a stack profile (and a page's own <style> blocks).

Usage:
  python -I css_index.py index --root <product-root> --include <rel-path> [--include ...]
         [--exclude <dir-or-glob>]... [--ext .css]... [--markup-ext .<ext>]...
         [--template-ext .<ext>]... [--template-comment <regex>]... [--template-expr <regex>]
         [--template-unescape <text>=<text>]... [--fallback-encoding <codec>]...
         [--tag <glob>=<label>]... [--profiles <profiles.json>] [--ref-prefix <dir>]...
         [--root-alias <prefix>] [--split-mb <n>] --out <index.json>
  python -I css_index.py query --index <index.json> [--class <name>]... [--id <name>]...
         [--selector <fragment>]... [--property <name>]... [--profile <id>] [--page <view>]
         [--tag <label>]... [--media <substring>|none] [--include-inline] [--limit <n>] [--json]

Markup handling: .vue, .html and .htm are markup by default; add others with --markup-ext.
Server template files are listed with --template-ext; the engine's syntax is given as
arguments, with no built-in engine: --template-comment (blocks treated as comments),
--template-expr (an expression marker; inline styles holding one are flagged dynamic) and
--template-unescape (an escape inside <style> replaced before parsing, columns kept). Example
for an invented syntax: --template-comment "{!.*?!}" --template-expr "{=" --template-unescape "{@}=@".
Vue `<style scoped>` selectors get a compiled specificity (+1 attribute) next to the source one.

Profile paths: a leading `/` is dropped; --root-alias names the template engine's prefix for
the application root (no default), which is dropped too.

Encoding: files are read as UTF-8 (a BOM is allowed). A file that is not valid UTF-8 is decoded
with each --fallback-encoding in order; without one, or when none fits, the scan stops and names
the file. There is no built-in fallback.

This script only indexes rules and computes specificity; it does not decide final values.
"""
from __future__ import annotations

import argparse
import bisect
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCHEMA = "css-index/1"

DEFAULT_EXTS = (".css", ".vue")
MARKUP_EXTS = (".vue", ".html", ".htm")

GROUP_AT_RULES = {"media", "supports", "document", "layer", "container", "scope", "starting-style"}
LEGACY_PSEUDO_ELEMENTS = {"before", "after", "first-line", "first-letter"}
MAX_ARG_PSEUDOS = {"is", "matches", "any", "not", "has"}
TRANSPARENT_PSEUDOS = {"deep", "v-deep", "global", "slotted", "v-global", "v-slotted"}


# ---------------------------------------------------------------------------
# basics
# ---------------------------------------------------------------------------
class LineMap:
    def __init__(self, text: str):
        self.starts = [0] + [m.end() for m in re.finditer("\n", text)]

    def line(self, off: int) -> int:
        return bisect.bisect_right(self.starts, off)

    def col(self, off: int) -> int:
        return off - self.starts[self.line(off) - 1] + 1


def read_text(path: Path, fallbacks=()):
    """Decode as UTF-8 (BOM allowed), then each fallback encoding; stop with a message otherwise."""
    data = path.read_bytes()
    for enc in ("utf-8-sig",) + tuple(fallbacks):
        try:
            return data.decode(enc).replace("\r\n", "\n").replace("\r", "\n"), enc
        except (UnicodeDecodeError, LookupError):
            continue
    raise SystemExit("cannot decode %s as UTF-8%s; pass --fallback-encoding <codec> for the project's legacy encoding"
                     % (path, (" or " + ", ".join(fallbacks)) if fallbacks else ""))


def skip_string(t: str, i: int) -> int:
    q = t[i]
    n = len(t)
    j = i + 1
    while j < n:
        c = t[j]
        if c == "\\":
            j += 2
            continue
        if c == q:
            return j + 1
        if c == "\n":
            return j
        j += 1
    return n


def _is_ident_char(c: str) -> bool:
    return c.isalnum() or c in "-_" or ord(c) > 127


def blank_comments(text: str):
    """Blank /* */ comments (newlines kept, offsets unchanged). Return (new text, comment spans)."""
    out = list(text)
    n = len(text)
    i = 0
    comments = []
    while i < n:
        c = text[i]
        if c in "\"'":
            i = skip_string(text, i)
            continue
        if c == "/" and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            end = n if j < 0 else j + 2
            for k in range(i, end):
                if out[k] != "\n":
                    out[k] = " "
            comments.append((i, end, j < 0))
            i = end
            continue
        if c in "uU" and text[i:i + 4].lower() == "url(" and (i == 0 or not _is_ident_char(text[i - 1])):
            j = i + 4
            while j < n and text[j] in " \t\n\f":
                j += 1
            if j < n and text[j] not in "\"'":
                while j < n and text[j] != ")":
                    j += 2 if text[j] == "\\" else 1
                i = j + 1
                continue
            i = j
            continue
        i += 1
    return "".join(out), comments


def scan_to(t: str, i: int, stops: str) -> int:
    """First position from i of a `stops` character at bracket depth 0 outside strings; len(t) if none."""
    n = len(t)
    depth = 0
    while i < n:
        c = t[i]
        if c in "\"'":
            i = skip_string(t, i)
            continue
        if c == "\\":
            i += 2
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            if depth:
                depth -= 1
        elif depth == 0 and c in stops:
            return i
        i += 1
    return n


def split_top(s: str, sep: str = ","):
    parts = []
    depth = 0
    i = 0
    start = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c in "\"'":
            i = skip_string(s, i)
            continue
        if c == "\\":
            i += 2
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            if depth:
                depth -= 1
        elif c == sep and depth == 0:
            parts.append((start, s[start:i]))
            start = i + 1
        i += 1
    parts.append((start, s[start:]))
    return parts


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Specificity (Selectors Level 4)
# ---------------------------------------------------------------------------
def _read_ident(s: str, i: int):
    n = len(s)
    j = i
    while j < n:
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if _is_ident_char(c):
            j += 1
            continue
        break
    return s[i:j], j


def _read_parens(s: str, i: int):
    """s[i] == '('; return (text inside the parentheses, end position)."""
    depth = 0
    n = len(s)
    j = i
    while j < n:
        c = s[j]
        if c in "\"'":
            j = skip_string(s, j)
            continue
        if c == "\\":
            j += 2
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], n


def _add(x, y):
    return (x[0] + y[0], x[1] + y[1], x[2] + y[2])


def _max_of_list(arg: str, notes: set):
    best = (0, 0, 0)
    for _, part in split_top(arg):
        part = part.strip()
        if not part:
            continue
        sp = _spec(part, notes)
        if sp > best:
            best = sp
    return best


def _spec(sel: str, notes: set):
    sel = sel.replace(">>>", " ").replace("/deep/", " ")
    a = b = c = 0
    extra = (0, 0, 0)
    i = 0
    n = len(sel)
    while i < n:
        ch = sel[i]
        if ch == "#":
            _, i = _read_ident(sel, i + 1)
            a += 1
        elif ch == ".":
            _, i = _read_ident(sel, i + 1)
            b += 1
        elif ch == "[":
            j = i + 1
            while j < n and sel[j] != "]":
                j = skip_string(sel, j) if sel[j] in "\"'" else j + 1
            i = j + 1
            b += 1
        elif ch == ":":
            is_elem = i + 1 < n and sel[i + 1] == ":"
            name, j = _read_ident(sel, i + (2 if is_elem else 1))
            lname = name.lower()
            arg = None
            if j < n and sel[j] == "(":
                arg, j = _read_parens(sel, j)
            i = j
            if lname in TRANSPARENT_PSEUDOS:
                notes.add("transparent-pseudo:" + lname)
                if arg is not None:
                    extra = _add(extra, _max_of_list(arg, notes))
                continue
            if is_elem:
                c += 1
                if arg is not None and lname in ("slotted", "part", "cue", "highlight"):
                    if lname == "slotted":
                        extra = _add(extra, _max_of_list(arg, notes))
                continue
            if lname == "where":
                notes.add(":where=0")
                continue
            if lname in MAX_ARG_PSEUDOS or lname.endswith("-any"):
                notes.add(":%s=max-of-args" % lname)
                if arg is not None:
                    extra = _add(extra, _max_of_list(arg, notes))
                continue
            if lname in ("nth-child", "nth-last-child") and arg is not None:
                b += 1
                m = re.search(r"\bof\b", arg)
                if m:
                    notes.add(":%s(of S)" % lname)
                    extra = _add(extra, _max_of_list(arg[m.end():], notes))
                continue
            if lname in ("host", "host-context"):
                b += 1
                if arg is not None:
                    extra = _add(extra, _max_of_list(arg, notes))
                continue
            if lname in LEGACY_PSEUDO_ELEMENTS:
                c += 1
                continue
            b += 1
        elif ch == "*":
            i += 1
        elif ch in "\"'":
            i = skip_string(sel, i)
        elif ch == "\\" or _is_ident_char(ch):
            name, j = _read_ident(sel, i)
            if j < n and sel[j] == "|" and not sel.startswith("|=", j):
                i = j + 1
                continue
            if name and not re.fullmatch(r"-?\d.*", name):
                c += 1
            i = j if j > i else i + 1
        else:
            i += 1
    return _add((a, b, c), extra)


def specificity(sel: str):
    notes = set()
    sp = _spec(sel, notes)
    return list(sp), sorted(notes)


# ---------------------------------------------------------------------------
# CSS parsing
# ---------------------------------------------------------------------------
DECL_RE = re.compile(r"\s*([*_]?-{0,2}[A-Za-z_][-\w]*|--[-\w]+)\s*:(.*)\Z", re.S)
IMPORTANT_RE = re.compile(r"!\s*important\s*\Z", re.I)


class CssParser:
    """Parse a CSS text into rules. line_base/col_base map <style> block offsets back to the host file."""

    def __init__(self, text: str, line_base: int = 1, col_base: int = 1):
        self.raw = text
        self.t, self.comments = blank_comments(text)
        self.n = len(self.t)
        self.lm = LineMap(text)
        self.line_base = line_base
        self.col_base = col_base
        self.rules = []
        self.statements = []
        self.warnings = []
        self.order = 0
        for s, e, unterminated in self.comments:
            if unterminated:
                self.warn(s, "unterminated-comment")

    # position mapping
    def line(self, off):
        return self.lm.line(off) + self.line_base - 1

    def col(self, off):
        ln = self.lm.line(off)
        col = self.lm.col(off)
        return col + self.col_base - 1 if ln == 1 else col

    def warn(self, off, msg, detail=None):
        w = {"line": self.line(off), "warning": msg}
        if detail:
            w["detail"] = detail[:200]
        self.warnings.append(w)

    def parse(self):
        self._parse_list(0, False, [], None)
        return self

    def _skip_ws(self, i):
        t = self.t
        while i < self.n:
            if t[i].isspace():
                i += 1
            elif t.startswith("<!--", i):
                i += 4
            elif t.startswith("-->", i):
                i += 3
            else:
                break
        return i

    def _next_order(self):
        self.order += 1
        return self.order

    def _parse_list(self, i, in_block, conds, parent_sels):
        t = self.t
        while True:
            i = self._skip_ws(i)
            if i >= self.n:
                if in_block:
                    self.warn(self.n - 1 if self.n else 0, "unclosed-block")
                return self.n
            if t[i] == "}":
                if in_block:
                    return i + 1
                self.warn(i, "stray-close-brace")
                i += 1
                continue
            start = i
            j = scan_to(t, i, "{;}")
            prelude = t[start:j].strip()
            if j >= self.n:
                if prelude:
                    self.warn(start, "trailing-text-without-block", prelude)
                return self.n
            if t[j] == ";":
                if prelude.startswith("@"):
                    self._statement(start, prelude, conds)
                elif parent_sels is not None:
                    pass
                else:
                    self.warn(start, "declaration-outside-rule", prelude)
                i = j + 1
                continue
            if t[j] == "}":
                if prelude:
                    self.warn(start, "prelude-without-block", prelude)
                i = j
                continue
            i = self._block(start, prelude, j + 1, conds, parent_sels)

    def _statement(self, start, prelude, conds):
        m = re.match(r"@([-\w]+)\s*(.*)\Z", prelude, re.S)
        name = m.group(1).lower() if m else prelude
        self.statements.append({
            "line": self.line(start), "col": self.col(start),
            "at_rule": name, "params": norm_ws(m.group(2)) if m else "",
            "conditions": list(conds),
        })

    def _block(self, start, prelude, body, conds, parent_sels):
        if prelude.startswith("@"):
            m = re.match(r"@([-\w]+)\s*(.*)\Z", prelude, re.S)
            name = m.group(1).lower() if m else "?"
            params = norm_ws(m.group(2)) if m else ""
            base = re.sub(r"^-[a-z]+-", "", name)
            if base in GROUP_AT_RULES:
                cond = {"type": name, "text": params, "line": self.line(start)}
                return self._parse_list(body, True, conds + [cond], parent_sels) \
                    if parent_sels is None else self._decl_block(start, None, body, conds + [cond], parent_sels, kind="nested-group")
            if base == "keyframes":
                return self._keyframes(start, name, params, body, conds)
            order = self._next_order()
            decls, end = self._decls(body, conds, parent_sels=None)
            self.rules.append({
                "kind": "at-rule", "at_rule": name, "prelude": params,
                "line": self.line(start), "col": self.col(start), "order": order,
                "selectors": [], "conditions": list(conds), "decls": decls,
            })
            return end
        sels = self._selectors(start, prelude, parent_sels)
        return self._decl_block(start, sels, body, conds, parent_sels, kind="style")

    def _selectors(self, start, prelude, parent_sels):
        out = []
        for off, part in split_top(prelude):
            text = norm_ws(part)
            if not text:
                continue
            if parent_sels is not None:
                combos = []
                for p in parent_sels:
                    combos.append(text.replace("&", p["text"]) if "&" in text else p["text"] + " " + text)
                texts = combos
            else:
                texts = [text]
            for tx in texts:
                sp, notes = specificity(tx)
                item = {"text": tx, "specificity": sp}
                if notes:
                    item["spec_notes"] = notes
                out.append(item)
        return out

    def _decl_block(self, start, sels, body, conds, parent_sels, kind):
        order = self._next_order()
        use_sels = sels if sels is not None else parent_sels
        rule = {
            "kind": "style",
            "line": self.line(start), "col": self.col(start), "order": order,
            "selectors": use_sels, "conditions": list(conds), "decls": [],
        }
        if parent_sels is not None:
            rule["nested"] = True
        self.rules.append(rule)
        decls, end = self._decls(body, conds, parent_sels=use_sels)
        rule["decls"] = decls
        return end

    def _decls(self, i, conds, parent_sels):
        t = self.t
        decls = []
        while True:
            while i < self.n and (t[i].isspace() or t[i] == ";"):
                i += 1
            if i >= self.n:
                self.warn(self.n - 1 if self.n else 0, "unclosed-declaration-block")
                return decls, self.n
            if t[i] == "}":
                return decls, i + 1
            k = scan_to(t, i, ";{}")
            if k < self.n and t[k] == "{":
                prelude = t[i:k].strip()
                self.warn(i, "nested-rule", prelude)
                if parent_sels is None:
                    k2 = self._parse_list(k + 1, True, conds, None)
                else:
                    k2 = self._block(i, prelude, k + 1, conds, parent_sels)
                i = k2
                continue
            seg = t[i:k]
            d = parse_declaration(seg)
            if d is None:
                if seg.strip():
                    self.warn(i, "invalid-declaration", seg.strip())
            else:
                lead = len(seg) - len(seg.lstrip())
                d["line"] = self.line(i + lead)
                d["col"] = self.col(i + lead)
                decls.append(d)
            if k >= self.n:
                self.warn(i, "unclosed-declaration-block")
                return decls, self.n
            i = k + 1 if t[k] == ";" else k

    def _keyframes(self, start, name, params, i, conds):
        t = self.t
        kf_name = params
        while True:
            i = self._skip_ws(i)
            if i >= self.n:
                self.warn(start, "unclosed-keyframes", kf_name)
                return self.n
            if t[i] == "}":
                return i + 1
            s = i
            j = scan_to(t, i, "{;}")
            if j >= self.n or t[j] != "{":
                self.warn(s, "invalid-keyframe", t[s:j].strip())
                i = j + 1 if j < self.n and t[j] == ";" else j
                continue
            order = self._next_order()
            decls, end = self._decls(j + 1, conds, None)
            self.rules.append({
                "kind": "keyframe", "at_rule": name, "prelude": kf_name,
                "line": self.line(s), "col": self.col(s), "order": order,
                "selectors": [{"text": norm_ws(x), "specificity": None} for _, x in split_top(t[s:j]) if x.strip()],
                "conditions": list(conds), "decls": decls,
            })
            i = end


def parse_declaration(seg: str):
    m = DECL_RE.match(seg)
    if not m:
        return None
    prop = m.group(1)
    value = m.group(2)
    important = False
    mi = IMPORTANT_RE.search(value)
    if mi:
        important = True
        value = value[:mi.start()]
    if prop.startswith("--"):
        value = value.strip()
    else:
        prop = prop.lower()
        value = norm_ws(value)
    return {"property": prop, "value": value, "important": important}


def parse_inline_declarations(text: str, line: int):
    """Inline style attribute value -> declarations (no syntax beyond comment handling)."""
    t, _ = blank_comments(text)
    lm = LineMap(text)
    decls = []
    for off, seg in split_top(t, ";"):
        if not seg.strip():
            continue
        d = parse_declaration(seg)
        if d is None:
            decls.append({"property": None, "value": norm_ws(seg), "important": False,
                          "line": line + lm.line(off) - 1, "invalid": True})
            continue
        d["line"] = line + lm.line(off + len(seg) - len(seg.lstrip())) - 1
        decls.append(d)
    return decls


# ---------------------------------------------------------------------------
# Markup extraction (<style> blocks and inline styles)
# ---------------------------------------------------------------------------
STYLE_BLOCK_RE = re.compile(r"<style\b([^>]*)>(.*?)</style\s*>", re.I | re.S)
INLINE_RE = re.compile(r"(?<![\w:.@-])style\s*=\s*(\"([^\"]*)\"|'([^']*)')", re.I)
BINDING_RE = re.compile(r"(?:(?<=\s)|^)(?::|v-bind:)style\s*=\s*(\"([^\"]*)\"|'([^']*)')", re.I | re.M)
ATTR_RE = re.compile(r"([:@]?[\w:.-]+)(?:\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+))?")


def _ranges(text, pattern):
    return [(m.start(), m.end()) for m in re.finditer(pattern, text, re.S | re.I)]


def _in(ranges, off):
    for s, e in ranges:
        if s <= off < e:
            return True
    return False


def _tag_context(text, off):
    s = text.rfind("<", 0, off)
    if s < 0:
        return {}
    e = text.find(">", off)
    seg = text[s:e if e > 0 else len(text)]
    m = re.match(r"<\s*([\w:.-]+)", seg)
    ctx = {"tag": m.group(1).lower() if m else None}
    for attr in ("id", "class", ":class", "v-bind:class"):
        ma = re.search(r"(?<![\w:.-])" + re.escape(attr) + r"\s*=\s*(\"([^\"]*)\"|'([^']*)')", seg)
        if ma:
            ctx[attr.replace("v-bind:", ":")] = norm_ws(ma.group(2) if ma.group(2) is not None else ma.group(3))
    return ctx


def _style_attrs(attr_text):
    attrs = {}
    for m in ATTR_RE.finditer(attr_text):
        k = m.group(1).lower()
        v = m.group(2)
        if v and v[0] in "\"'":
            v = v[1:-1]
        attrs[k] = True if v is None else v
    return attrs


class TemplateSyntax:
    """Template-engine syntax from the command line; empty unless given."""

    def __init__(self, comments=(), expr=None, unescape=()):
        self.comments = list(comments)
        self.expr = re.compile(expr) if expr else None
        self.unescape = []
        for pair in unescape:
            old, sep, new = pair.partition("=")
            if not sep or not old or len(new) > len(old):
                raise SystemExit("--template-unescape needs <text>=<shorter or equal text>: %r" % pair)
            self.unescape.append((old, new.rjust(len(old))))


def extract_markup(text: str, is_template: bool, is_vue: bool, syntax=None):
    syntax = syntax or TemplateSyntax()
    lm = LineMap(text)
    commented = _ranges(text, r"<!--.*?-->")
    if is_template:
        for rx in syntax.comments:
            commented += _ranges(text, rx)
    scripts = _ranges(text, r"<script\b[^>]*>.*?</script\s*>")
    blocks = []
    style_ranges = []
    for m in STYLE_BLOCK_RE.finditer(text):
        style_ranges.append((m.start(), m.end()))
        attrs = _style_attrs(m.group(1))
        body = m.group(2)
        body_off = m.start(2)
        at_exprs = []
        if is_template:
            if syntax.expr:
                for mm in syntax.expr.finditer(body):
                    at_exprs.append(lm.line(body_off + mm.start()))
            for old, new in syntax.unescape:
                body = body.replace(old, new)
        blocks.append({
            "attrs": attrs,
            "line": lm.line(m.start()),
            "body": body,
            "body_line": lm.line(body_off),
            "body_col": lm.col(body_off),
            "commented_out": _in(commented, m.start()),
            "in_script": _in(scripts, m.start()),
            "template_expression_lines": at_exprs,
        })
    inlines = []
    for m in INLINE_RE.finditer(text):
        if _in(style_ranges, m.start()):
            continue
        val = m.group(2) if m.group(2) is not None else m.group(3)
        line = lm.line(m.start())
        dyn = []
        if is_template and syntax.expr and syntax.expr.search(val):
            dyn.append("template-expression")
        if "{{" in val:
            dyn.append("template-interpolation")
        if re.search(r"['\"]\s*\+|\+\s*['\"]|\$\{", val):
            dyn.append("string-concatenation")
        rec = {
            "kind": "inline-style",
            "line": line, "col": lm.col(m.start()),
            "raw": norm_ws(val),
            "decls": parse_inline_declarations(val, lm.line(m.start(1))),
            "commented_out": _in(commented, m.start()),
            "in_script": _in(scripts, m.start()),
        }
        if dyn:
            rec["dynamic"] = dyn
        rec.update({"element": _tag_context(text, m.start())})
        inlines.append(rec)
    if is_vue:
        for m in BINDING_RE.finditer(text):
            val = m.group(2) if m.group(2) is not None else m.group(3)
            inlines.append({
                "kind": "inline-style-binding",
                "line": lm.line(m.start()), "col": lm.col(m.start()),
                "raw": norm_ws(val), "decls": [], "dynamic": ["vue-binding"],
                "commented_out": _in(commented, m.start()),
                "in_script": _in(scripts, m.start()),
                "element": _tag_context(text, m.start()),
            })
    inlines.sort(key=lambda r: (r["line"], r["col"]))
    return blocks, inlines


# ---------------------------------------------------------------------------
# scanning and indexing
# ---------------------------------------------------------------------------
def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def iter_files(root: Path, includes, excludes, exts):
    excl = [e.strip("/\\").replace("\\", "/").lower() for e in excludes]

    def excluded(relp: str):
        low = relp.lower()
        parts = low.split("/")
        for e in excl:
            if "/" in e:
                if low == e or low.startswith(e + "/") or fnmatch.fnmatch(low, e):
                    return True
            elif e in parts or fnmatch.fnmatch(parts[-1], e):
                return True
        return False

    seen = set()
    for inc in includes:
        p = (root / inc)
        if p.is_file():
            cands = [p]
        elif p.is_dir():
            cands = []
            for dp, dns, fns in os.walk(p):
                dns.sort()
                rd = rel(Path(dp), root)
                dns[:] = [d for d in dns if not excluded((rd + "/" + d) if rd != "." else d)]
                for fn in sorted(fns):
                    if fn.lower().endswith(tuple(exts)):
                        cands.append(Path(dp) / fn)
        else:
            print("[warn] include not found: %s" % inc, file=sys.stderr)
            continue
        for f in cands:
            r = rel(f, root)
            if (excluded(r) and not p.is_file()) or r.lower() in seen:
                continue
            seen.add(r.lower())
            yield f, r


def classify(relp: str, tags):
    low = relp.lower()
    for pattern, label in tags:
        if fnmatch.fnmatch(low, pattern.lower()):
            return label
    return "project"


def build_index(root: Path, includes, excludes, exts, tags, markup_exts=MARKUP_EXTS, template_exts=(), syntax=None, fallbacks=()):
    sources = []
    rules = []
    inlines = []
    statements = []
    warnings = []

    def add_source(src, parser):
        sid = src["id"]
        for r in parser.rules:
            r["id"] = "%s:R%d" % (sid, r["order"])
            r["source"] = sid
            r["media"] = " and ".join(c["text"] for c in r["conditions"] if c["type"].endswith("media")) or None
            if src.get("scoped"):
                for s in r["selectors"]:
                    if s.get("specificity") is None:
                        continue
                    if any(n == "transparent-pseudo:global" for n in s.get("spec_notes", [])):
                        s["specificity_compiled"] = list(s["specificity"])
                    else:
                        sp = s["specificity"]
                        s["specificity_compiled"] = [sp[0], sp[1] + 1, sp[2]]
            rules.append(r)
        for st in parser.statements:
            st["source"] = sid
            statements.append(st)
        for w in parser.warnings:
            w["source"] = sid
            w["path"] = src["path"]
            warnings.append(w)
        src["rule_count"] = len(parser.rules)
        src["declaration_count"] = sum(len(r["decls"]) for r in parser.rules)
        src["important_count"] = sum(1 for r in parser.rules for d in r["decls"] if d["important"])

    file_count = 0
    for f, r in iter_files(root, includes, excludes, exts):
        file_count += 1
        text, enc = read_text(f, fallbacks)
        label = classify(r, tags)
        low = r.lower()
        if low.endswith(".css"):
            src = {"id": "S%d" % (len(sources) + 1), "path": r, "type": "stylesheet", "tag": label,
                   "encoding": enc, "bytes": f.stat().st_size, "lines": text.count("\n") + 1}
            sources.append(src)
            add_source(src, CssParser(text).parse())
        elif low.endswith(tuple(markup_exts)):
            is_vue = low.endswith(".vue")
            is_template = low.endswith(tuple(template_exts))
            blocks, ins = extract_markup(text, is_template, is_vue, syntax)
            for bi, b in enumerate(blocks, 1):
                src = {"id": "S%d" % (len(sources) + 1), "path": r,
                       "type": "vue-style-block" if is_vue else "template-style-block" if is_template else "html-style-block",
                       "tag": label, "block_index": bi, "line": b["line"], "attrs": b["attrs"],
                       "commented_out": b["commented_out"], "in_script": b["in_script"]}
                if is_vue:
                    src["scoped"] = bool(b["attrs"].get("scoped"))
                    src["lang"] = b["attrs"].get("lang") or "css"
                if b["template_expression_lines"]:
                    src["template_expression_lines"] = b["template_expression_lines"]
                sources.append(src)
                add_source(src, CssParser(b["body"], b["body_line"], b["body_col"]).parse())
                if is_vue and src["lang"] not in ("css",):
                    warnings.append({"source": src["id"], "path": r, "line": b["line"],
                                     "warning": "preprocessor-lang-parsed-as-css", "detail": src["lang"]})
            for k, ins_rec in enumerate(ins, 1):
                ins_rec["id"] = "I%d" % (len(inlines) + 1)
                ins_rec["path"] = r
                ins_rec["tag"] = label
                ins_rec["source_type"] = "vue-inline" if is_vue else "template-inline" if is_template else "html-inline"
                inlines.append(ins_rec)
    return {
        "sources": sources, "rules": rules, "inline_styles": inlines,
        "statements": statements, "warnings": warnings, "scanned_files": file_count,
    }


# ---------------------------------------------------------------------------
# Stack profile
# ---------------------------------------------------------------------------
def _norm_ref(p: str, root_alias=None) -> str:
    p = p.split("?")[0].split("#")[0].replace("\\", "/").strip()
    if root_alias and p.startswith(root_alias):
        p = p[len(root_alias):]
    p = re.sub(r"^/+", "", p)
    return p.lower()


POSITION_RANK = {"head": 0, "body": 1, "body-end": 2}


def build_profiles(idx, prof_doc, ref_prefixes=(), page_token="<page>", root_alias=None):
    by_path = {}
    for s in idx["sources"]:
        by_path.setdefault(s["path"].lower(), []).append(s)
    rule_counts = {s["id"]: s.get("rule_count", 0) for s in idx["sources"]}

    def resolve(f):
        ref = f.get("path") or f.get("file") or ""
        entry = {"path": ref}
        for k in ("position", "order", "condition", "kind", "via", "ref", "lines"):
            if f.get(k) is not None or k in ("position", "order", "condition"):
                entry[k] = f.get(k)
        if ref == page_token:
            entry["page_placeholder"] = True
            return entry, []
        n = _norm_ref(ref, root_alias)
        cands = by_path.get(n) or []
        for pre in ref_prefixes:
            if cands:
                break
            cands = by_path.get(pre.strip("/").lower() + "/" + n) or []
        lines = f.get("lines")
        if lines and len(lines) == 2:
            cands = [s for s in cands if "line" in s and lines[0] <= s["line"] <= lines[1]]
        entry["found"] = bool(cands)
        return entry, cands

    out = []
    for prof in prof_doc.get("profiles", []):
        files = []
        for k, f in enumerate(prof.get("files", []), 1):
            if isinstance(f, str):
                f = {"path": f}
            files.append((f.get("order", k), k, f))
        files.sort(key=lambda x: (x[0] if isinstance(x[0], (int, float)) else x[1], x[1]))
        offset = 0
        entries = []
        for _, _, f in files:
            entry, cands = resolve(f)
            if entry.get("page_placeholder"):
                entry["offset"] = offset
            else:
                entry["sources"] = []
                for s in cands:
                    entry["sources"].append({"source": s["id"], "offset": offset, "rule_count": rule_counts[s["id"]]})
                    offset += rule_counts[s["id"]]
            entries.append(entry)
        out.append({"id": prof.get("id"), "files": entries, "total_rules": offset,
                    "note": prof.get("note") or prof.get("label")})
    res = {"profiles": out, "pages": prof_doc.get("pages", {})}
    if isinstance(prof_doc.get("page_extras"), dict):
        extras = {}
        for view, items in prof_doc["page_extras"].items():
            lst = []
            for f in items:
                if isinstance(f, str):
                    f = {"path": f}
                entry, cands = resolve(f)
                entry["sources"] = [{"source": s["id"], "rule_count": rule_counts[s["id"]]} for s in cands]
                lst.append(entry)
            extras[view] = lst
        res["page_extras"] = extras
    return res


def page_segments(doc, profile, page):
    """Return [(source_id, rule_count, label)]: the profile file sequence plus the page-level styles."""
    profs = doc.get("profiles") or {}
    extras = None
    if page is not None:
        pe = profs.get("page_extras")
        if pe is not None:
            key = next((k for k in pe if k.lower() == _norm_ref(page)), None)
            extras = []
            for e in pe.get(key, []) if key else []:
                for s in e.get("sources", []):
                    extras.append((POSITION_RANK.get(e.get("position"), 1), s["source"], s["rule_count"],
                                   "page-extra:%s" % (e.get("position") or "?")))
        else:
            extras = [(None, s["id"], s.get("rule_count", 0), "page-style-block")
                      for s in doc["sources"]
                      if s["path"].lower() == _norm_ref(page) and s["type"].endswith("style-block")
                      and not s.get("commented_out") and not s.get("in_script")]
    has_placeholder = any(f.get("page_placeholder") for f in profile["files"])
    items = []
    for k, f in enumerate(profile["files"]):
        rank = POSITION_RANK.get(f.get("position"), 1)
        if f.get("page_placeholder"):
            for j, (_, sid, cnt, lab) in enumerate(extras or []):
                items.append(((k, 0, j), sid, cnt, lab))
            continue
        for j, s in enumerate(f.get("sources", [])):
            items.append(((rank, 0, k, j) if not has_placeholder else (k, 0, j), s["source"], s["rule_count"], "profile"))
    if extras and not has_placeholder:
        for j, (rank, sid, cnt, lab) in enumerate(extras):
            r = rank if rank is not None else max(POSITION_RANK.values())
            items.append(((r, 1, j, 0), sid, cnt, lab))
            if rank is None and j == 0:
                print("[warn] no page_extras / <page> placeholder; page <style> blocks appended after profile files",
                      file=sys.stderr)
    items.sort(key=lambda x: x[0])
    return [(sid, cnt, lab) for _, sid, cnt, lab in items]


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------
def _dump_lines(fp, key, items, last=False):
    fp.write(' "%s": [\n' % key)
    for k, it in enumerate(items):
        fp.write("  " + json.dumps(it, ensure_ascii=False, separators=(",", ":")))
        fp.write(",\n" if k < len(items) - 1 else "\n")
    fp.write(" ]" + ("\n" if last else ",\n"))


def write_index(idx, out: Path, meta, split_mb: float):
    out.parent.mkdir(parents=True, exist_ok=True)
    stats = {
        "scanned_files": idx["scanned_files"],
        "sources": len(idx["sources"]),
        "sources_by_type": {},
        "sources_by_tag": {},
        "rules": len(idx["rules"]),
        "selectors": sum(len(r["selectors"]) for r in idx["rules"]),
        "declarations": sum(len(r["decls"]) for r in idx["rules"]),
        "important_declarations": sum(1 for r in idx["rules"] for d in r["decls"] if d["important"]),
        "inline_styles": len(idx["inline_styles"]),
        "warnings": len(idx["warnings"]),
    }
    for s in idx["sources"]:
        stats["sources_by_type"][s["type"]] = stats["sources_by_type"].get(s["type"], 0) + 1
        stats["sources_by_tag"][s["tag"]] = stats["sources_by_tag"].get(s["tag"], 0) + 1
    head = {"schema": SCHEMA, "meta": meta, "stats": stats}
    rules = idx["rules"]
    est = sum(len(json.dumps(r, ensure_ascii=False)) for r in rules)
    chunks = None
    if split_mb and est > split_mb * 1024 * 1024:
        chunks = []
        cur, size = [], 0
        limit = split_mb * 1024 * 1024
        by_src = {}
        for r in rules:
            by_src.setdefault(r["source"], []).append(r)
        for s in idx["sources"]:
            rs = by_src.get(s["id"], [])
            sz = sum(len(json.dumps(r, ensure_ascii=False)) for r in rs)
            if cur and size + sz > limit:
                chunks.append(cur)
                cur, size = [], 0
            cur.extend(rs)
            size += sz
        if cur:
            chunks.append(cur)
    with out.open("w", encoding="utf-8", newline="\n") as fp:
        fp.write("{\n")
        for k, v in head.items():
            fp.write(' "%s": %s,\n' % (k, json.dumps(v, ensure_ascii=False)))
        if "profiles" in idx:
            fp.write(' "profiles": %s,\n' % json.dumps(idx["profiles"], ensure_ascii=False))
        _dump_lines(fp, "sources", idx["sources"])
        _dump_lines(fp, "statements", idx["statements"])
        _dump_lines(fp, "warnings", idx["warnings"])
        _dump_lines(fp, "inline_styles", idx["inline_styles"])
        if chunks is None:
            _dump_lines(fp, "rules", rules, last=True)
        else:
            names = []
            for ci, ch in enumerate(chunks, 1):
                name = "%s.rules-%02d.json" % (out.stem, ci)
                names.append(name)
                with (out.parent / name).open("w", encoding="utf-8", newline="\n") as cf:
                    cf.write("{\n")
                    cf.write(' "schema": "%s#rules-chunk",\n' % SCHEMA)
                    _dump_lines(cf, "rules", ch, last=True)
                    cf.write("}\n")
            fp.write(' "rule_files": %s\n' % json.dumps(names))
        fp.write("}\n")
    return stats, chunks


def load_index(path: Path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    if "rule_files" in doc:
        doc["rules"] = []
        for name in doc["rule_files"]:
            doc["rules"].extend(json.loads((path.parent / name).read_text(encoding="utf-8"))["rules"])
    return doc


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------
def _class_re(name):
    return re.compile(r"\." + re.escape(name) + r"(?![\w-])")


def _id_re(name):
    return re.compile(r"#" + re.escape(name) + r"(?![\w-])")


def run_query(doc, args):
    pats = []
    for c in args.cls or []:
        pats.append(("class", c, _class_re(c)))
    for c in args.id or []:
        pats.append(("id", c, _id_re(c)))
    for s in args.selector or []:
        pats.append(("selector", s, re.compile(re.escape(s), re.I)))
    props = [p.lower() for p in (args.property or [])]
    src_by_id = {s["id"]: s for s in doc["sources"]}

    order_map = None
    profile = None
    if args.profile or args.page:
        profs = doc.get("profiles") or {}
        pid = args.profile
        if args.page and not pid:
            pages = profs.get("pages", {})
            key = next((k for k in pages if k.lower() == _norm_ref(args.page)), None)
            pid = pages.get(key) if key else None
            if pid is None:
                sys.exit("page not mapped to a profile: %s" % args.page)
        profile = next((p for p in profs.get("profiles", []) if p["id"] == pid), None)
        if profile is None:
            sys.exit("profile not found in index: %s" % pid)
        order_map = {}
        offset = 0
        for sid, cnt, lab in page_segments(doc, profile, args.page):
            order_map.setdefault(sid, (offset, lab))
            offset += cnt

    hits = []
    for r in doc["rules"]:
        if order_map is not None and r["source"] not in order_map:
            continue
        src = src_by_id[r["source"]]
        if args.tag and src["tag"] not in args.tag:
            continue
        if args.media is not None:
            if args.media == "none":
                if r.get("media"):
                    continue
            elif args.media.lower() not in (r.get("media") or "").lower():
                continue
        matched = []
        for s in r["selectors"]:
            text = s["text"]
            if not pats or all(p[2].search(text) for p in pats):
                matched.append(s)
        if not matched and pats and r["kind"] != "style":
            pre = "@%s %s" % (r.get("at_rule", ""), r.get("prelude", ""))
            if all(p[2].search(pre) for p in pats):
                matched = r["selectors"] or [{"text": pre, "specificity": None}]
        if not matched:
            continue
        decls = [d for d in r["decls"] if not props or d["property"] in props]
        if props and not decls:
            continue
        g = None
        if order_map is not None:
            off, f = order_map[r["source"]]
            g = off + r["order"]
        hits.append((g, r, src, matched, decls))
    if order_map is not None:
        hits.sort(key=lambda h: h[0])
    inline_hits = []
    if args.include_inline:
        for ins in doc.get("inline_styles", []):
            el = ins.get("element", {})
            ok = True
            for kind, name, rx in pats:
                if kind == "class":
                    ok &= bool(re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])",
                                         (el.get("class") or "") + " " + (el.get(":class") or "")))
                elif kind == "id":
                    ok &= el.get("id") == name
                else:
                    ok &= bool(rx.search(ins["raw"]))
            if args.page:
                ok &= ins["path"].lower() == _norm_ref(args.page)
            if ok:
                decls = [d for d in ins["decls"] if not props or (d.get("property") or "") in props]
                if props and not decls:
                    continue
                inline_hits.append((ins, decls))
    if args.limit:
        hits = hits[:args.limit]
    if args.json:
        res = []
        for g, r, src, matched, decls in hits:
            res.append({"global_order": g, "rule": r["id"], "path": src["path"], "source_type": src["type"],
                        "tag": src["tag"], "line": r["line"], "col": r["col"], "order": r["order"],
                        "conditions": r["conditions"], "selectors": matched, "decls": decls})
        out = {"profile": profile["id"] if profile else None, "page": args.page, "rules": res,
               "inline_styles": [dict(i, decls=d) for i, d in inline_hits]}
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    for g, r, src, matched, decls in hits:
        cond = " | ".join("@%s %s" % (c["type"], c["text"]) for c in r["conditions"])
        head = "%s%s:%d:%d [%s/%s] #%d" % (("g%-6d " % g) if g is not None else "",
                                           src["path"], r["line"], r["col"], src["type"], src["tag"], r["order"])
        print(head + ((" " + cond) if cond else ""))
        for s in matched:
            sp = s.get("specificity")
            spc = s.get("specificity_compiled")
            print("    %s  %s%s" % (s["text"], tuple(sp) if sp else "-",
                                    (" compiled=%s" % (tuple(spc),)) if spc else ""))
        for d in decls:
            print("      %s: %s%s  (L%d)" % (d["property"], d["value"], " !important" if d["important"] else "", d["line"]))
    for ins, decls in inline_hits:
        el = ins.get("element", {})
        print("inline %s:%d [%s] <%s id=%s class=%s>%s" % (
            ins["path"], ins["line"], ins["kind"], el.get("tag"), el.get("id"), el.get("class"),
            (" dynamic=" + ",".join(ins["dynamic"])) if ins.get("dynamic") else ""))
        for d in decls:
            print("      %s: %s%s" % (d.get("property"), d["value"], " !important" if d.get("important") else ""))
    print("-- %d rule(s)%s" % (len(hits), (", %d inline" % len(inline_hits)) if args.include_inline else ""),
          file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("index", help="build the index")
    a.add_argument("--root", required=True, help="product root; every output path is relative to it")
    a.add_argument("--include", action="append", required=True, help="file or directory to scan, relative to root (repeatable)")
    a.add_argument("--exclude", action="append", default=[],
                   help="exclude: a directory name (any depth) or a root-relative path/glob (repeatable)")
    a.add_argument("--ext", action="append", help="file extensions to scan (default .css .vue)")
    a.add_argument("--markup-ext", action="append", default=[],
                   help="extra markup extension whose <style> blocks and inline styles are indexed (repeatable)")
    a.add_argument("--template-ext", action="append", default=[],
                   help="server template extension (repeatable; implies --markup-ext); syntax from the --template-* options")
    a.add_argument("--template-comment", action="append", default=[],
                   help="regex of a template comment block in --template-ext files (repeatable; no default)")
    a.add_argument("--template-expr", help="regex of a template expression marker; inline styles holding one are dynamic")
    a.add_argument("--template-unescape", action="append", default=[], metavar="TEXT=TEXT",
                   help="escape inside <style> of --template-ext files, replaced before parsing (repeatable)")
    a.add_argument("--fallback-encoding", action="append", default=[],
                   help="codec tried after UTF-8 for a file that is not valid UTF-8 (repeatable; no default)")
    a.add_argument("--tag", action="append", default=[], metavar="GLOB=LABEL",
                   help="label sources by relative-path glob (first match wins; default project)")
    a.add_argument("--profiles", help="stack profile JSON")
    a.add_argument("--ref-prefix", action="append", default=[],
                   help="directory prefixes tried in order when a profile path is not found (e.g. the static web root)")
    a.add_argument("--root-alias", help="the template engine's prefix for the application root in profile paths (no default)")
    a.add_argument("--out", required=True, help="output JSON path")
    a.add_argument("--split-mb", type=float, default=0, help="split rules into chunk files above this estimated size in MB (0 = never)")

    q = sub.add_parser("query", help="query the index")
    q.add_argument("--index", required=True)
    q.add_argument("--class", dest="cls", action="append", help="class name (without the dot)")
    q.add_argument("--id", action="append", help="id name (without #)")
    q.add_argument("--selector", action="append", help="selector fragment (case-insensitive substring)")
    q.add_argument("--property", action="append", help="only list declarations of these properties")
    q.add_argument("--profile", help="order by this profile's global order; only rules inside the profile")
    q.add_argument("--page", help="view path; use its profile from 'pages' and add that view's <style> blocks")
    q.add_argument("--tag", action="append", help="only this source label")
    q.add_argument("--media", help="media condition substring; 'none' lists rules without media")
    q.add_argument("--include-inline", action="store_true", help="also list matching inline styles")
    q.add_argument("--limit", type=int)
    q.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    if args.cmd == "index":
        root = Path(args.root)
        tags = []
        for t in args.tag:
            g, _, lab = t.partition("=")
            tags.append((g.replace("\\", "/"), lab or "tagged"))
        def dotted(xs):
            return [e.lower() if e.startswith(".") else "." + e.lower() for e in xs]
        template_exts = tuple(dotted(args.template_ext))
        syntax = TemplateSyntax(args.template_comment, args.template_expr, args.template_unescape)
        markup_exts = tuple(dict.fromkeys(list(MARKUP_EXTS) + dotted(args.markup_ext) + list(template_exts)))
        exts = tuple(dict.fromkeys(dotted(args.ext or DEFAULT_EXTS) + dotted(args.markup_ext) + list(template_exts)))
        idx = build_index(root, args.include, args.exclude, exts, tags, markup_exts, template_exts, syntax, args.fallback_encoding)
        meta = {"generated_by": "css_index.py", "root": root.resolve().as_posix(),
                "include": args.include, "exclude": args.exclude, "ext": list(exts), "template_ext": list(template_exts),
                "tags": [{"glob": g, "label": l} for g, l in tags], "profiles_file": None,
                "ref_prefix": args.ref_prefix}
        if args.profiles:
            pdoc = json.loads(Path(args.profiles).read_text(encoding="utf-8-sig"))
            idx["profiles"] = build_profiles(idx, pdoc, args.ref_prefix, root_alias=args.root_alias)
            meta["profiles_file"] = Path(args.profiles).as_posix()
        stats, chunks = write_index(idx, Path(args.out), meta, args.split_mb)
        print(json.dumps(stats, ensure_ascii=False, indent=1))
        if chunks:
            print("rules split into %d file(s)" % len(chunks), file=sys.stderr)
        if "profiles" in idx:
            for p in idx["profiles"]["profiles"]:
                missing = [f["path"] for f in p["files"] if f.get("found") is False]
                print("profile %s: %d rules%s" % (p["id"], p["total_rules"],
                                                  ("; missing: " + ", ".join(missing)) if missing else ""),
                      file=sys.stderr)
    else:
        run_query(load_index(Path(args.index)), args)


if __name__ == "__main__":
    main()
