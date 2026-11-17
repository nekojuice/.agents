#!/usr/bin/env python3
"""Rationalise extracted (v1) tokens into a layered (v2) token set (standard library only).

Naming: "v1" is the snapshot this script reads and "v2" the rebuilt set it proposes; keys such
as v1_*, v2_* and rep_v1 use these two words only in that sense.

v1 is the faithful phase-1 package (tokens, component map, contrast data); v2 is the
primitive / semantic / component rebuild. This script holds only the algorithm; every human
judgement (colour role drafts, type cells, variant map, asset classes, naming) is read from
the external decision file passed with --decisions.

Usage:
  python -I rationalize.py --tokens <v1 tokens.json> --component-map <v1 component-tokens.json>
         --contrast <v1 contrast.json> --usage <token candidates JSON>
         --decisions <JSON with a "decisions" object> --out-consolidation <out.json>
         --out-lineage <out.json> [--forbid-list <forbid-list.txt>]
         [--color-families color] [--removed-families <family,...>] [--check]

--decisions and --out-lineage may be the same file: the script keeps "decisions" and rewrites
every other field, so a second run must reproduce the file byte for byte. --check computes
both outputs without writing and exits 1 when either differs from the file on disk.

Exit status: 1 when any check (H1-H5, added_states, ID forbid-list, variant coverage) fails, after the
outputs are written so the failures can be read; with --check also when an output is stale.

v1 research fields: a Phase 1 package keeps `used_by` in the research data, not in
tokens.json. Entries of --tokens without `used_by` take it from the --usage entry of the same
name, so a v1 with or without `used_by` gives the same result.

v1 input shapes (detected by shape, read into one view; the algorithm is the same):
  --tokens         the Phase 1 package tokens.json (type styles reference scales with {name},
                   font stacks are objects) or a per-value snapshot (type styles hold values).
  --component-map  the package map written for the package scripts (`components`, each with
                   `parts` and `variants` keyed <component>--<variant>; optional `layout` units
                   and `patterns`; `brand: false` on a unit or variant marks it non-brand), or a
                   per-variant map (top-level `variants` and `registry`). A component without
                   variants and a pattern with parts are each one unit keyed by their id, so their
                   references count for H5 and the variant map must cover them.
  --contrast       build_contrast.py output (`source_pairs`; kind `reference` marks reference
                   pairs, `exempt` marks exempt pairs; the unrounded ratio is computed from the
                   token values when `ratio_raw` is absent), or a `pairs` / `reference` file.
  H2 surfaces      v1 colours with group "surface"; when no v1 colour carries `group`, the
                   colours whose role draft starts with "surface".

Algorithm summary:
  colour   opaque colours grouped by role draft -> within a role, the most used value is the
           centre and absorbs values with ΔE2000 <= 2 (no chaining); surface colours with
           L* > 90 are not merged automatically but follow decisions.surface_merges ->
           across roles only identical hex (member level) or ΔE < 1 merge -> family (C*, hue)
           and step (L* formula) -> same family+step collision: same role merges, a different
           role takes a free neighbouring step or is demoted to component tier.
  type     cells from decisions; non-integer px rounded; the cell's representative size is
           the most used one; a size used by a single style moves to the nearest step unless a
           hard rule protects it.
  space    4px base plus a 2px half step, only values that occur; nearest step, ties go up;
           shorthands split into four sides.
  radius   rounded, then merged within +-merge_px. size: control heights and icons snap to
           the decision scales.
  checks   H1 contrast does not regress, H2 surfaces stay distinct, H3 type order, H4 control
           box height, H5 orphan primitives, added_states (added-state contrast), ID forbid-list,
           variant coverage.

Required decision keys:
  size.max_steps             {"control": n, "icon": n}: the most steps each scale may keep (the plan's
                             threshold table; line-height controls count toward control)
  note_syntax                {"open", "close", "sep", "merged"}: the markers the run's size-class
                             notes and used_by entries use, e.g. {"open": "(", "close": ")",
                             "sep": "/", "merged": "merged"} for notes written like
                             "button-height/input-height (md, merged)". No default: the
                             markers follow the language the notes are written in.

Decision keys that replace former built-in values (all optional):
  type.mobile_variant_when   breakpoint "when" values that make a mobile-first base size;
                             required when type.breakpoint_variants is not empty (no default)
  type.mobile_variant_when_always  same, but applied even when sizes are equal (default [])
  type.mobile_min_breakpoint breakpoint token used for the restored wide-screen size;
                             required when type.breakpoint_variants is not empty (no default)
  color.extra_surface_tokens v1 colour names treated as surfaces for H2 besides group=surface
  color.property_prefixes    {"color"|"background"|"border": [semantic name prefixes]}
  color.component_categories [[keywords], [semantic prefixes]] used to drop redundant
                             component colours; the last entry is the fallback (default:
                             border/divider -> color-border-, -bg -> surface/action, else text)
  color.state_check_tokens   semantic names checked by added_states (focus_ring, focus_ring_inverse,
                             invalid_border, checked_control)
  size.layout_tokens         {name: value} layout widths copied into the size primitives
  radius.semantics           {name: "{radius-x}"} scale semantics
  shadow.<focus>.width/offset focus ring geometry (default 2px / 2px); a focus ring is optional
  h1_excluded_pairs          {pair id: reason}: approved exclusions from H1; any other pair whose
                             foreground or background has no rebuilt value fails H1

Check details:
  H1  rebuilt ratio uses the pair's own opacity, composited as in build_contrast.py.
  H3  per variant, the type sizes in effect at each checked width keep their relative order. Each
      declaration (part, state, property) contributes the value in effect there: a conditional
      entry replaces the plain one and an active narrow-screen style replaces its base, only
      within that declaration. Every combination of checked width and declared context
      (`ctx:<name>`) is resolved; base declarations still apply when a context is on unless that
      declaration has a matching override. Conditions are max:/lt:/min:<b> and <a>..<b>, where a bound
      is a breakpoint token or a number (px optional),
      or ctx:<name>, on the style or on the map key (`<state>@<condition>`). Any other condition
      makes H3 UNVERIFIED (listed under checks.H3.unverified) and the run exits 1.
  added_states  checks only the states the decisions add (semantic tokens with origin "added");
      none added means nothing to check; each surface is measured against the ring it actually
      uses (inverse on focus_inverse_surfaces when an inverse ring exists); an added ring or state
      with no surface to verify it on, or a token named in state_check_tokens that does not exist,
      fails.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("colormetrics", HERE / "colormetrics.py")
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Decision-note micro-syntax; filled from the required decisions.note_syntax.
NOTE = {}
NOTE_KEYS = ("open", "close", "sep", "merged")

DEFAULT_PROPERTY_PREFIXES = {"color": ["color-text-", "color-feedback-"],
                             "background": ["color-surface-", "color-action-"],
                             "border": ["color-border-"]}
DEFAULT_COMPONENT_CATEGORIES = [[["border", "divider"], ["color-border-"]],
                                [["-bg"], ["color-surface-", "color-action-"]],
                                [[], ["color-text-", "color-feedback-"]]]
DEFAULT_STATE_TOKENS = {"focus_ring": "color-focus-ring", "focus_ring_inverse": "color-focus-ring-inverse",
                        "invalid_border": "color-border-invalid", "checked_control": "color-action-checked"}


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def px(v, base=16.0):
    """'12px', '0.75rem', '1.5em' (em relative to base) -> float; None when not convertible."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s in ("0", "0px"):
        return 0.0
    m = re.fullmatch(r"(-?[\d.]+)(px|rem|em)?", s)
    if not m:
        return None
    n = float(m.group(1))
    u = m.group(2) or "px"
    return n if u == "px" else n * 16.0 if u == "rem" else n * base


def comp_count(used_by):
    return len({u.split("--")[0].split(NOTE["open"])[0].strip() for u in used_by or []})


# ============================================================ color

class ColorEngine:
    def __init__(self, v1, usage_src, dec, color_families=("color",), removed_families=()):
        self.dec = dec
        self.rules = dec["family_rules"]
        self.entries = OrderedDict()   # id -> entry
        usage_by_name = {t["name"]: t for t in usage_src.get("color", {}).get("tokens", [])}
        self.removed_families = set(removed_families)
        for fam in tuple(color_families) + tuple(removed_families):
            for t in v1.get(fam, {}).get("tokens", []):
                self.entries[t["name"]] = {
                    "id": t["name"], "value": t["value"], "fam": fam, "tier": t.get("tier"),
                    "usage": len(usage_by_name[t["name"]]["used_by"]) if t["name"] in usage_by_name else comp_count(t.get("used_by")),
                    "decl": (usage_by_name.get(t["name"]) or {}).get("decl_count") or 0,
                    "v1_used_by": t.get("used_by", []),
                }
        for x in dec.get("extra_values", []):
            self.entries[x["id"]] = {"id": x["id"], "value": x["value"], "fam": "extra", "tier": None,
                                     "usage": x.get("usage", 1), "decl": 0, "v1_used_by": []}
        for k, a in dec.get("alpha", {}).items():
            if k not in self.entries:
                self.entries[k] = {"id": k, "value": a["value"], "fam": "extra", "tier": None, "usage": 1, "decl": 0, "v1_used_by": []}

    # ---------------------------------------------------------- family/step
    def family(self, hexv):
        sp = self.rules.get("special", {})
        if hexv.lower() in sp:
            return sp[hexv.lower()]
        L, a, b = cm.to_lab(cm.parse_color(hexv))
        _, C, h = cm.lch((L, a, b))
        ov = self.rules.get("low_chroma_hue_override")
        if C < self.rules["neutral_chroma_max"]:
            if ov and ov["hue_from"] <= h < ov["hue_to"] and C >= ov["chroma_min"]:
                return ov["family"]
            return "neutral"
        for name, a0, b0 in self.rules["named_hue_ranges"]:
            hh = h if h >= a0 else h + 360
            if a0 <= hh < b0:
                return name
        w = self.rules["fallback_bin_deg"]
        start = str(int(h // w * w))
        return self.rules.get("bin_names", {}).get(start, "hue-" + start)

    def step(self, hexv):
        if hexv.lower() in self.rules.get("special", {}):
            return None
        return cm.step_of(hexv)

    # ---------------------------------------------------------- clustering
    def run(self):
        dec = self.dec
        roles = dec["roles"]
        removed_ids, alias_ids, alpha_ids = set(), set(dec.get("alias", {})), set(dec.get("alpha", {}))
        for e in self.entries.values():
            if e["fam"] in self.removed_families or e["id"] in dec.get("removed", {}):
                removed_ids.add(e["id"])
        work = []
        for e in self.entries.values():
            if e["id"] in removed_ids or e["id"] in alias_ids or e["id"] in alpha_ids:
                continue
            role = roles.get(e["id"])
            if role is None:
                for x in dec.get("extra_values", []):
                    if x["id"] == e["id"]:
                        role = x["role"]
            if role is None:
                raise SystemExit(f"color role missing for {e['id']}")
            if not cm.is_opaque(e["value"]):
                raise SystemExit(f"non-opaque color needs alpha decision: {e['id']}")
            hexv = cm.to_hex(cm.parse_color(e["value"]))
            L = cm.to_lab(cm.parse_color(hexv))[0]
            work.append(dict(e, role=role, hex=hexv, L=L))

        def key(e):
            return (-e["usage"], -e["decl"], e["hex"])

        # 1) within-role centroid clustering
        clusters = []
        by_role = defaultdict(list)
        for e in work:
            by_role[e["role"]].append(e)
        smerge = dec.get("surface_merges", {})
        for role, items in by_role.items():
            items = sorted(items, key=key)
            assigned = {}
            # explicit surface merges (L*>90 role judgment) first
            for src, dst in smerge.items():
                if any(i["id"] == src for i in items) and any(i["id"] == dst for i in items):
                    assigned[src] = dst
            centers = []
            for it in items:
                if it["id"] in assigned:
                    continue
                if it["L"] > 90 and it["role"].startswith("surface"):
                    centers.append({"rep": it, "members": [it], "how": {}})
                    continue
                hit = None
                for c in centers:
                    if c["rep"]["L"] > 90 and c["rep"]["role"].startswith("surface"):
                        continue
                    d = cm.de(c["rep"]["hex"], it["hex"])
                    if d <= 2.0:
                        hit = c
                        break
                if hit:
                    hit["members"].append(it)
                    hit["how"][it["id"]] = "same-role ΔE≤2"
                else:
                    centers.append({"rep": it, "members": [it], "how": {}})
            for src, dst in assigned.items():
                for c in centers:
                    if any(mm["id"] == dst for mm in c["members"]):
                        c["members"].append(next(i for i in items if i["id"] == src))
                        c["how"][src] = "surface role judgment (L*>90)"
            for c in centers:
                c["role"] = role
                clusters.append(c)

        # 2) cross-role: same hex (member level) or rep ΔE<1
        clusters.sort(key=lambda c: key(c["rep"]))
        merged = True
        while merged:
            merged = False
            for i, a in enumerate(clusters):
                for b in clusters[i + 1:]:
                    hexes_a = {m["hex"] for m in a["members"]}
                    hexes_b = {m["hex"] for m in b["members"]}
                    same = bool(hexes_a & hexes_b)
                    d = cm.de(a["rep"]["hex"], b["rep"]["hex"])
                    if same or d < 1.0:
                        for mm in b["members"]:
                            a["members"].append(mm)
                            a["how"][mm["id"]] = ("cross-role same hex" if same else f"cross-role ΔE {d:.2f}<1") + \
                                (f" via {b['rep']['id']}" if mm is not b["rep"] else "")
                        a.setdefault("roles", {a["role"]}).add(b["role"])
                        a["roles"] |= b.get("roles", {b["role"]})
                        clusters.remove(b)
                        merged = True
                        break
                if merged:
                    break
        for c in clusters:
            c.setdefault("roles", {c["role"]})

        # 3) family / step / collisions
        clusters.sort(key=lambda c: key(c["rep"]))
        slots = OrderedDict()
        demoted = []
        for c in clusters:
            hexv = c["rep"]["hex"]
            fam = self.family(hexv)
            st = self.step(hexv)
            c["family"], c["step"] = fam, st
            slot = (fam, st)
            if slot in slots:
                other = slots[slot]
                if other["roles"] & c["roles"]:
                    for mm in c["members"]:
                        other["members"].append(mm)
                        other["how"][mm["id"]] = f"step collision same role → merged into {other['rep']['hex']}"
                    other["roles"] |= c["roles"]
                    c["merged_into"] = other
                else:
                    # different-role collision: new primitive on the half step (+25, -25), else the next free step
                    c["collided_with"] = other["rep"]["hex"]
                    c["base_step"] = st
                    cand = [st + 25, st - 25] + [st + 50 * k for k in range(1, 20)] + [st - 50 * k for k in range(1, 20)]
                    for nst in cand:
                        if 25 <= nst <= 950 and (fam, nst) not in slots:
                            c["step"] = nst
                            slots[(fam, nst)] = c
                            break
                    else:
                        c["demoted"] = True
                        demoted.append(c)
            else:
                slots[slot] = c
        prims = OrderedDict()
        for (fam, st), c in slots.items():
            name = f"palette-{fam}" if st is None else f"palette-{fam}-{st}"
            c["name"] = name
            prims[name] = c
        for c in demoted:
            c["name"] = None
        self.clusters = clusters
        self.prims = prims
        self.demoted = demoted
        self.removed_ids = removed_ids
        # member -> cluster
        self.member = {}
        for c in clusters:
            target = c.get("merged_into") or c
            for mm in c["members"]:
                self.member[mm["id"]] = target
        return self

    def alpha_prims(self):
        out = OrderedDict()
        for k, a in self.dec.get("alpha", {}).items():
            name = f"palette-{a['base']}-alpha-{a['pct']}"
            val = self.entries[k]["value"]
            if name in out and out[name]["value"].replace(" ", "") != val.replace(" ", ""):
                raise SystemExit(f"alpha name collision {name}")
            out.setdefault(name, {"value": val, "members": []})["members"].append(k)
        return out

    def resolve_from(self, ident):
        """v1 token / extra id -> (kind, name, value); kind: primitive|alpha|demoted."""
        al = self.dec.get("alpha", {})
        if ident in al:
            a = al[ident]
            return ("alpha", f"palette-{a['base']}-alpha-{a['pct']}", self.entries[ident]["value"])
        if ident in self.dec.get("alias", {}):
            return self.resolve_from(self.dec["alias"][ident])
        c = self.member.get(ident)
        if c is None:
            raise SystemExit(f"cannot resolve color {ident}")
        if c.get("demoted"):
            return ("demoted", None, c["rep"]["hex"])
        return ("primitive", c["name"], c["rep"]["hex"])


# ============================================================ type

def type_engine(v1, dec):
    styles = OrderedDict()
    for g in v1["type"]["groups"]:
        for s in g["styles"]:
            styles[s["name"]] = s
    bpv = dec["breakpoint_variants"]
    em = dec.get("em_styles", {})
    cells = dec["cells"]
    lh_steps = dec["line_heights"]
    thr = dec["line_height_threshold"]
    ctrl_lh = dec.get("control_line_heights", {})
    keep = dec.get("h1_size_keep", {})
    mobile_when = dec.get("mobile_variant_when")
    mobile_when_always = dec.get("mobile_variant_when_always", [])
    mobile_bp = dec.get("mobile_min_breakpoint")
    if bpv and (mobile_when is None or not mobile_bp):
        raise SystemExit("decisions.type.mobile_variant_when and mobile_min_breakpoint are required "
                         "when type.breakpoint_variants is not empty")
    mobile_when = mobile_when or []

    def size_px(s):
        v = s["fontSize"]
        if isinstance(v, str) and v.endswith("%"):
            return None
        return px(v)

    def lh_unitless(s):
        v = s["lineHeight"]
        fs = size_px(s)
        if isinstance(v, (int, float)):
            return float(v)
        if v == "normal":
            return None
        if v.endswith("em") and not v.endswith("rem"):
            return float(v[:-2])
        p = px(v)
        return p / fs if (p is not None and fs) else None

    # global usage count by rounded integer size (all styles incl. breakpoint variants)
    int_count = Counter()
    for n, s in styles.items():
        p = size_px(s)
        if p is not None:
            int_count[int(math.floor(p + 0.5))] += 1

    member_cell = {}
    for cell, mem in cells.items():
        for n in mem:
            member_cell[n] = cell
    out_styles = OrderedDict()
    lineage = OrderedDict()
    lh_map = {}
    for cell, mem in cells.items():
        sizes = Counter()
        weight = Counter()
        lhs = Counter()
        ls = Counter()
        fams = Counter()
        for n in mem:
            s = styles[n]
            p = size_px(s)
            r = int(math.floor(p + 0.5))
            w = max(1, len(s.get("used_by", [])))
            sizes[r] += 1
            weight[str(s["fontWeight"])] += 1
            u = lh_unitless(s)
            if n not in ctrl_lh and u is not None:
                near = min(lh_steps.items(), key=lambda kv: (abs(kv[1] - u), -kv[1]))
                lhs[near[0]] += 1
            ls[str(s["letterSpacing"])] += 1
            fams[s["family"]] += 1
        # representative size: most used within cell; tie → used_by sum, then larger
        def score(r):
            ub = sum(max(1, len(styles[n].get("used_by", []))) for n in mem if int(math.floor(size_px(styles[n]) + 0.5)) == r)
            return (sizes[r], ub, r)
        rep = max(sizes, key=score)
        def mode(c, order):
            if not c:
                return None
            best = max(c.values())
            for n in order:
                if n in c and c[n] == best:
                    return n
            return max(c, key=c.get)
        mem_order_w = [str(styles[n]["fontWeight"]) for n in mem]
        mem_order_ls = [str(styles[n]["letterSpacing"]) for n in mem]
        lh_order = []
        for n in mem:
            u = lh_unitless(styles[n])
            if n not in ctrl_lh and u is not None:
                lh_order.append(min(lh_steps.items(), key=lambda kv: (abs(kv[1] - u), -kv[1]))[0])
        out_styles[cell] = {
            "name": f"type-{cell}", "role": cell.split("-")[0], "size": cell.split("-")[1],
            "fontSize": rep, "lineHeight": mode(lhs, lh_order) or "normal",
            "fontWeight": int(mode(weight, mem_order_w)), "letterSpacing": mode(ls, mem_order_ls),
            "family": dec["families"].get(mode(fams, [styles[n]["family"] for n in mem]), "sans"),
            "members": list(mem), "rep_count": sizes[rep], "breakpoints": [],
        }
    # breakpoint overrides: from rep member only (most used_by) if it has a narrow-screen variant
    for cell, st in out_styles.items():
        mem = st["members"]
        rep_member = max(mem, key=lambda n: (int(math.floor(size_px(styles[n]) + 0.5)) == st["fontSize"],
                                             len(styles[n].get("used_by", []))))
        st["rep_member"] = rep_member
        for bn, b in bpv.items():
            if b["of"] == rep_member and b["when"] in mobile_when:
                mob = int(math.floor(size_px(styles[bn]) + 0.5))
                if mob == st["fontSize"]:
                    continue
                st["breakpoints"] = [{"min": mobile_bp, "fontSize": st["fontSize"]}]
                st["fontSize_base"] = mob
                st["fontSize_note"] = f"mobile-first: base {mob}px, @min {mobile_bp} {st['fontSize']}px"
            elif b["of"] == rep_member and b["when"] in mobile_when_always:
                mob = int(math.floor(size_px(styles[bn]) + 0.5))
                st["breakpoints"] = [{"min": mobile_bp, "fontSize": st["fontSize"]}]
                st["fontSize_base"] = mob
    # threshold: rep used by <2 styles globally → nearest other cell size unless hard rule (role ladder)
    exceptions = []
    for cell, st in out_styles.items():
        if int_count[st["fontSize"]] < 2:
            role = st["role"]
            sib = [o for o in out_styles.values() if o["role"] == role and o is not st]
            exceptions.append({"cell": cell, "fontSize": st["fontSize"], "count": int_count[st["fontSize"]],
                               "rule": "H3 role ladder lg>md>sm strictly decreasing; snapping to the nearest step would equal another cell of the same role",
                               "siblings": {o["name"]: o["fontSize"] for o in sib}})
    avail = sorted({o["fontSize"] for o in out_styles.values()} |
                   {o["fontSize_base"] for o in out_styles.values() if o.get("fontSize_base")})
    # lineage per v1 style
    for n, s in styles.items():
        p = size_px(s)
        if n in em:
            lineage[n] = {"v2": em[n]["to"], "kind": "em", "v1_size": s["fontSize"], "v2_size": em[n]["value"],
                          "deviation_px": 0, "note": em[n]["note"]}
            continue
        switched = False
        if n in bpv:
            base = bpv[n]["of"]
            cell = member_cell.get(n) or member_cell.get(base)
        else:
            cell = member_cell.get(n)
            base = n
        if cell is None:
            lineage[n] = {"v2": None, "kind": "unmapped", "v1_size": s["fontSize"]}
            continue
        st = out_styles[cell]
        v2size = st["fontSize"]
        if n in bpv and n not in member_cell:
            if st.get("fontSize_base") is not None and base == st["rep_member"]:
                v2size = st["fontSize_base"]
            else:
                # component-level switch to the nearest existing v2 size (prefer same role)
                r = int(math.floor(p + 0.5))
                if r == int(math.floor(size_px(styles[base]) + 0.5)):
                    v2size = st["fontSize"]  # breakpoint style has the base size: keep the base v2 size
                else:
                    v2size = min(avail, key=lambda x: (abs(x - r), -x))
                if v2size != st["fontSize"]:
                    cands = [o for o in out_styles.values() if o["fontSize"] == v2size]
                    same = [o for o in cands if o["role"] == st["role"]]
                    if cands:
                        st = (same or cands)[0]
                        cell = st["name"][5:]
                    switched = True
        if base in keep:
            v2size_keep = keep[base]["keep_px"] if n == base else None
        else:
            v2size_keep = None
        u = lh_unitless(s)
        if n in ctrl_lh:
            lh_v2 = ctrl_lh[n]
            lh_dev = None
        elif u is None:
            lh_v2, lh_dev = st["lineHeight"], None
        else:
            near = min(lh_steps.items(), key=lambda kv: (abs(kv[1] - u), -kv[1]))
            lh_v2, lh_dev = near[0], round(near[1] - u, 3)
        entry = {"v2": st["name"], "cell": cell, "kind": "breakpoint" if n in bpv else "style",
                 "v1_size_px": round(p, 2), "v2_size_px": v2size_keep or v2size,
                 "deviation_px": round((v2size_keep or v2size) - p, 2),
                 "v1_line_height": s["lineHeight"], "v2_line_height": lh_v2, "line_height_deviation": lh_dev,
                 "v1_weight": s["fontWeight"], "v2_weight": st["fontWeight"],
                 "v1_letter_spacing": s["letterSpacing"], "v2_letter_spacing": st["letterSpacing"],
                 "v1_family": s["family"], "v2_family": dec["families"].get(s["family"])}
        if n in bpv:
            entry["v1_when"] = bpv[n]["when"]
            entry["override_of"] = base
            if switched:
                entry["switch"] = "component level switches to this style with an @min condition"

        if v2size_keep:
            entry["exception"] = keep[base]["reason"]
        if lh_dev is not None and abs(lh_dev) > thr + 1e-9:
            entry["line_height_exception"] = f"beyond the ±{thr} threshold; snapped to the nearest value (at most 4 text line heights)"
        overrides = {}
        if str(s["fontWeight"]) != str(st["fontWeight"]):
            overrides["fontWeight"] = s["fontWeight"]
        if str(s["letterSpacing"]) != str(st["letterSpacing"]):
            overrides["letterSpacing"] = s["letterSpacing"]
        if isinstance(lh_v2, str) and lh_v2 in lh_steps and lh_v2 != st["lineHeight"]:
            overrides["lineHeight"] = lh_v2
        if dec["families"].get(s["family"]) != st["family"]:
            overrides["family"] = dec["families"].get(s["family"])
        if overrides:
            entry["component_override"] = overrides
        lineage[n] = entry
    return out_styles, lineage, exceptions, styles


# ============================================================ space / radius

def space_engine(v1, dec):
    toks = v1["space"]["tokens"]
    em_ctx = dec.get("em_contexts_px", {})
    vals = set()
    parsed = {}
    for t in toks:
        parts = str(t["value"]).split()
        ctx = em_ctx.get(t["name"], 16)
        bases = ctx if isinstance(ctx, list) else [ctx]
        rows = []
        for b in bases:
            if b is None:
                rows = None
                break
            rows.append([px(p, b) for p in parts])
        parsed[t["name"]] = (parts, rows, bases)
        if rows:
            for r in rows:
                for v in r:
                    if v is not None and v > 0 and abs(v - round(v)) < 1e-9 and round(v) % dec["base"] == 0:
                        vals.add(int(round(v)))
    scale = sorted(vals | {dec["half_step"]})

    def snap(v):
        if v == 0:
            return 0
        best = min(scale, key=lambda s: (abs(s - v), -s))
        return best

    lineage = OrderedDict()
    for t in toks:
        parts, rows, bases = parsed[t["name"]]
        if rows is None:
            lineage[t["name"]] = {"v1": t["value"], "v2": None, "kind": "component-only",
                                  "note": dec["component_only"].get(t["name"])}
            continue
        out = []
        for b, r in zip(bases, rows):
            sn = [snap(v) if v is not None else None for v in r]
            dev = [round(s - v, 2) if v is not None else None for s, v in zip(sn, r)]
            out.append({"context_font_px": b, "v1_px": [round(v, 2) if v is not None else None for v in r],
                        "v2": [f"space-{s}" if s else "0" for s in sn], "deviation_px": dev,
                        "exception": any(d is not None and abs(d) > dec["exception_over_px"] for d in dev)})
        lineage[t["name"]] = {"v1": t["value"], "kind": "scale", "contexts": out}
    used = set()
    for e in lineage.values():
        for c in e.get("contexts", []):
            used |= {v for v in c["v2"] if v != "0"}
    return scale, lineage


def radius_engine(v1, dec):
    toks = v1["radius"]["tokens"]
    items = []
    for t in toks:
        v = t["value"]
        if v == "50%":
            items.append((t, "full", None))
            continue
        p = px(v)
        if t["name"].endswith("pill"):
            items.append((t, "pill", p))
            continue
        items.append((t, "px", int(math.floor(p + 0.5)) if dec.get("integer_rounding") else p))
    groups = []
    for t, k, p in sorted([i for i in items if i[1] == "px"], key=lambda i: (-comp_count(i[0].get("used_by")), i[0]["value"])):
        hit = None
        for g in groups:
            if abs(g["rep"] - p) <= dec["merge_px"]:
                hit = g
                break
        if hit:
            hit["members"].append((t, p))
        else:
            groups.append({"rep": p, "members": [(t, p)]})
    groups.sort(key=lambda g: g["rep"])
    names = [n for n in dec["names"] if n not in ("pill", "full")]
    out = OrderedDict()
    lineage = OrderedDict()
    for g, n in zip(groups, names):
        nm = f"radius-{n}"
        out[nm] = {"value": f"{g['rep']}px" if g["rep"] else "0", "members": [m[0]["name"] for m in g["members"]]}
        for t, p in g["members"]:
            lineage[t["name"]] = {"v1": t["value"], "v2": nm, "v2_value": out[nm]["value"],
                                  "deviation_px": round(g["rep"] - px(t["value"]), 2)}
    if len(groups) > len(names):
        raise SystemExit("radius steps exceed names")
    for t, k, p in items:
        if k in ("pill", "full"):
            nm = f"radius-{k}"
            out[nm] = {"value": t["value"], "members": [t["name"]]}
            lineage[t["name"]] = {"v1": t["value"], "v2": nm, "v2_value": t["value"], "deviation_px": 0}
    return out, lineage


def size_engine(v1, dec):
    toks = {t["name"]: t for t in v1["size"]["tokens"]}
    cls = dec["classes"]
    out = {"control": OrderedDict(), "icon": OrderedDict(), "layout": OrderedDict()}
    lineage = OrderedDict()
    for name, t in toks.items():
        spec = cls.get(name)
        if spec is None:
            raise SystemExit(f"size class missing: {name}")
        c, note = spec[0], spec[1]
        v = px(t["value"])
        if c in ("control", "icon"):
            scale = dec[f"{c}_scale"]
            # an optional third column pins the value on the shared size axis (a size does not vary by variant)
            s = spec[2] if len(spec) > 2 else min(scale, key=lambda x: (abs(x - v), -x))
            nm = f"size-{c}-{s}"
            out[c].setdefault(nm, {"value": f"{s}px", "members": []})["members"].append(name)
            lineage[name] = {"v1": t["value"], "class": c, "v2": nm, "deviation_px": round(s - v, 2), "role": note}
        elif c == "layout":
            lineage[name] = {"v1": t["value"], "class": c, "v2": None, "role": note, "deviation_px": 0}
        else:
            lineage[name] = {"v1": t["value"], "class": c, "v2": None, "role": note,
                             "deviation_px": 0 if c != "project" else None}
    caps = dec.get("max_steps") or {}
    if not all(isinstance(caps.get(c), int) and caps[c] > 0 for c in ("control", "icon")):
        raise SystemExit('decisions.size.max_steps is required: {"control": n, "icon": n} from the plan\'s threshold table')
    for c in ("control", "icon"):
        if len(out[c]) > caps[c]:
            raise SystemExit(f"{c} scale has {len(out[c])} steps, more than decisions.size.max_steps.{c} = {caps[c]}")
    return out, lineage


# ============================================================ checks

def text_class(px_, weight):
    if px_ >= 24 or (px_ >= 18.66 and int(weight) >= 700):
        return "large"
    return "normal"


ALIAS = re.compile(r"\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}")


def read_tokens(v1):
    """v1 tokens in the view the engines read: type-style fields as values, the style family as
    its key, font stacks as strings. Works on a copy; the loaded input is never modified."""
    v1 = copy.deepcopy(v1)
    ty = v1.get("type") or {}
    vals = {}
    for node in v1.values():
        if isinstance(node, dict) and isinstance(node.get("tokens"), list):
            for t in node["tokens"]:
                vals[t["name"]] = t.get("value")
    for sc in (ty.get("scales") or {}).values():
        for t in (sc or {}).get("tokens", []):
            vals[t["name"]] = t.get("value")

    def value(v, depth=0):
        m = ALIAS.fullmatch(v) if isinstance(v, str) else None
        if m and m.group(1) in vals and depth < 20:
            return value(vals[m.group(1)], depth + 1)
        return v

    if ty.get("families"):
        ty["families"] = OrderedDict((k, f["value"] if isinstance(f, dict) else f) for k, f in ty["families"].items())
    for g in ty.get("groups", []):
        for st in g.get("styles", []):
            fam = st.get("family")
            m = re.fullmatch(r"\{font-family-([\w-]+)\}", fam) if isinstance(fam, str) else None
            if m:
                st["family"] = m.group(1)
            for k in ("fontSize", "lineHeight", "fontWeight", "letterSpacing"):
                if k in st:
                    st[k] = value(st[k])
    return v1


def read_component_map(cmap, v1):
    """Per-variant view {"variants": {key: {"parts": ...}}, "registry": {"main", "non_brand"}}.
    A per-variant map is returned unchanged; a package map is unfolded: each variant carries the
    component's shared parts, size and compound parts and its own parts, and a token reference
    to a type style is written type.<style> as in the per-variant map."""
    if "variants" in cmap and "registry" in cmap:
        return cmap
    styles = {st["name"] for g in (v1.get("type") or {}).get("groups", []) for st in g.get("styles", [])}

    def typeref(o):
        if isinstance(o, dict):
            return OrderedDict((k, "type." + x if k == "token" and isinstance(x, str) and x in styles else typeref(x))
                               for k, x in o.items())
        if isinstance(o, list):
            return [typeref(x) for x in o]
        return o

    variants, main, non = OrderedDict(), [], []

    class _Units(OrderedDict):
        def __setitem__(self, k, val):
            if k in self:
                raise SystemExit("rationalize: unit id %r is used by more than one layout, "
                                 "component variant or pattern; ids must be unique" % k)
            OrderedDict.__setitem__(self, k, val)

    variants = _Units()
    for uid, u in (cmap.get("layout") or {}).items():
        variants[uid] = {"parts": typeref({"layout": u.get("parts") or {}})}
        (non if u.get("brand") is False else main).append(uid)
    for cid, c in (cmap.get("components") or {}).items():
        shared = OrderedDict([("component", c.get("parts") or {})])
        for k, sz in (c.get("sizes") or {}).items():
            shared["size:" + k] = (sz or {}).get("parts") or {}
        for i, cp in enumerate(c.get("compound") or []):
            shared["compound:%d" % i] = (cp or {}).get("parts") or {}
        if not c.get("variants"):
            variants[cid] = {"component": cid, "parts": typeref(shared)}
            (non if c.get("brand") is False else main).append(cid)
        for key, v in (c.get("variants") or {}).items():
            variants[key] = {"component": cid, "parts": typeref(OrderedDict(shared, variant=(v or {}).get("parts") or {}))}
            (non if (v or {}).get("brand") is False or c.get("brand") is False else main).append(key)
    for pt in cmap.get("patterns") or []:
        if pt.get("parts"):
            variants[pt["id"]] = {"pattern": pt["id"], "parts": typeref({"pattern": pt["parts"]})}
            (non if pt.get("brand") is False else main).append(pt["id"])
    return {"registry": {"main": main, "non_brand": non}, "variants": variants}


def with_opacity(colour, opacity):
    """Colour with an element opacity multiplied into its alpha (as build_contrast.py does)."""
    if opacity == 1:
        return colour
    c = cm.parse_color(colour)
    return "rgba(%.6f, %.6f, %.6f, %.6f)" % (c[0], c[1], c[2], c[3] * opacity)


def read_contrast(doc, v1):
    """{"pairs": [...], "reference": [...]} with fg/bg {token, value}, class and ratio_raw.
    A file in that shape is returned unchanged; build_contrast.py output is converted, computing
    the unrounded ratio from the token values when ratio_raw is absent."""
    if "pairs" in doc:
        return doc
    colours = {t["name"]: t["value"] for t in (v1.get("color") or {}).get("tokens", [])}

    def value(n, depth=0):
        v = colours[n]
        m = ALIAS.fullmatch(v) if isinstance(v, str) else None
        return value(m.group(1), depth + 1) if m and depth < 20 else v

    pairs, ref = [], []
    for p in doc.get("source_pairs") or []:
        fv, bv = value(p["fg"]), value(p["bg"])
        raw = p.get("ratio_raw")
        if raw is None:
            f = fv
            raw = cm.contrast(with_opacity(fv, p.get("opacity", 1.0)), bv)
        q = {"id": p["id"], "fg": {"token": p["fg"], "value": fv}, "bg": {"token": p["bg"], "value": bv},
             "class": "disabled" if p.get("exempt") else p["class"], "ratio_raw": raw}
        if p.get("opacity", 1.0) != 1:
            q["opacity"] = p["opacity"]
        if p.get("kind") == "reference":
            q["reference"] = True
            ref.append(q)
        else:
            pairs.append(q)
    return {"pairs": pairs, "reference": ref}


def overlay_used_by(v1, usage):
    """Copy `used_by` from the research data onto v1 entries that do not carry it (by name)."""
    found = {}

    def collect(o):
        if isinstance(o, dict):
            if isinstance(o.get("name"), str) and isinstance(o.get("used_by"), list):
                found.setdefault(o["name"], o["used_by"])
            for x in o.values():
                collect(x)
        elif isinstance(o, list):
            for x in o:
                collect(x)

    def fill(o):
        if isinstance(o, dict):
            if isinstance(o.get("name"), str) and "used_by" not in o and o["name"] in found:
                o["used_by"] = list(found[o["name"]])
            for x in o.values():
                fill(x)
        elif isinstance(o, list):
            for x in o:
                fill(x)

    collect(usage)
    fill(v1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--component-map", required=True)
    ap.add_argument("--contrast", required=True)
    ap.add_argument("--usage", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--out-consolidation", required=True)
    ap.add_argument("--out-lineage", required=True)
    ap.add_argument("--forbid-list")
    ap.add_argument("--color-families", default="color", help="v1 families holding colours (comma separated)")
    ap.add_argument("--removed-families", default="", help="v1 families dropped entirely from v2 (comma separated, e.g. residue families)")
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 when an output differs from the regenerated result")
    args = ap.parse_args()

    v1 = read_tokens(load(args.tokens))
    cmap = read_component_map(load(args.component_map), v1)
    contrast = read_contrast(load(args.contrast), v1)
    usage = load(args.usage)
    D = load(args.decisions)["decisions"]
    ns = D.get("note_syntax") or {}
    if any(not isinstance(ns.get(k), str) or not ns.get(k) for k in NOTE_KEYS):
        raise SystemExit("decisions.note_syntax must give the markers %s (see --help)" % ", ".join(NOTE_KEYS))
    NOTE.update({k: ns[k] for k in NOTE_KEYS})
    overlay_used_by(v1, usage)

    # ---------------- color
    ce = ColorEngine(v1, usage, D["color"], args.color_families.split(","),
                     [x for x in args.removed_families.split(",") if x]).run()
    alpha = ce.alpha_prims()
    sem = OrderedDict()
    for s in D["color"]["semantics"]:
        kind, name, val = ce.resolve_from(s["from"])
        if kind == "demoted":
            raise SystemExit(f"semantic {s['name']} resolves to demoted value")
        sem[s["name"]] = {"ref": name, "value": val, "origin": s.get("origin", "source"), "usage": s["usage"],
                          "anchor_v1": s["from"]}
    ctok = OrderedDict()
    for t in D["color"]["component_tokens"]:
        kind, name, val = ce.resolve_from(t["from"])
        ctok[t["name"]] = {"component": t["component"], "ref": name, "value": val,
                           "raw": kind == "demoted", "anchor_v1": t["from"]}
    # a component token exists only when it needs its own value; when a semantic of the same
    # category already points at the same primitive, the semantic is used instead
    cats = D["color"].get("component_categories") or DEFAULT_COMPONENT_CATEGORIES

    def _cat(n):
        for kws, prefixes in cats[:-1]:
            if any(k in n for k in kws):
                return tuple(prefixes)
        return tuple(cats[-1][1])
    redundant = OrderedDict()
    for n, t in list(ctok.items()):
        if t["raw"] or not t["ref"]:
            continue
        hit = [s for s, v in sem.items() if v["ref"] == t["ref"] and s.startswith(_cat(n))]
        if hit:
            redundant[n] = {"use": hit[0], "value": t["value"], "anchor_v1": t["anchor_v1"], "component": t["component"]}
            del ctok[n]
    # referenced primitives (H5)
    ref = set(v["ref"] for v in sem.values() if v["ref"]) | set(v["ref"] for v in ctok.values() if v["ref"])
    shadow_refs = set(re.findall(r"\{(palette-[\w-]+)\}", json.dumps(D["shadow"])))
    ref |= shadow_refs
    prim_out = OrderedDict()
    orphans = []
    for name, c in ce.prims.items():
        rec = {"value": c["rep"]["hex"], "family": c["family"], "step": c["step"], "roles": sorted(c["roles"]),
               "rep_v1": c["rep"]["id"], "members": [m["id"] for m in c["members"]]}
        if name in ref:
            prim_out[name] = rec
        else:
            orphans.append(dict(rec, name=name))
    alpha_out = OrderedDict((k, v) for k, v in alpha.items() if k in ref)
    alpha_orphans = [dict(v, name=k) for k, v in alpha.items() if k not in ref]

    # v1 color token → v2 mapping (value-level, for lineage, H1, contrast pair translation)
    sem_by_anchor = defaultdict(list)
    for n, s in sem.items():
        sem_by_anchor[s["anchor_v1"]].append(n)
    ct_by_anchor = defaultdict(list)
    for n, t in ctok.items():
        ct_by_anchor[t["anchor_v1"]].append(n)
    color_lineage = OrderedDict()
    v2_value_of = {}
    prop_prefixes = dict(DEFAULT_PROPERTY_PREFIXES, **(D["color"].get("property_prefixes") or {}))
    fdm = D["color"].get("framework_default_merges", {})
    vm = D["color"].get("variant_merges", {})
    for tid, e in ce.entries.items():
        if tid.startswith("shadow:"):
            continue
        rec = {"v1_value": e["value"], "v1_tier": e["tier"], "usage": e["usage"]}
        if tid in ce.removed_ids:
            rec.update(v2=None, status="removed",
                       reason=D["color"]["removed"].get(tid) or D["color"]["removed"].get("*family"))
            color_lineage[tid] = rec
            continue
        kind, pname, val = ce.resolve_from(tid)
        rec["role"] = D["color"]["roles"].get(tid, "alpha" if kind == "alpha" else "alias")
        if tid in fdm or tid in vm:
            tgt = (fdm.get(tid) or vm.get(tid))
            s = sem[tgt["to"]]
            rec.update(v2=tgt["to"], v2_value=s["value"], status="merged-by-component", reason=tgt["reason"],
                       delta_e=round(cm.de(cm.to_hex(cm.parse_color(e["value"])), s["value"]), 2),
                       primitive_status="orphan-removed" if pname not in prim_out else "kept")
            v2_value_of[tid] = s["value"]
        else:
            cands = sem_by_anchor.get(tid, []) + ct_by_anchor.get(tid, [])
            c = ce.member.get(tid)
            rec.update(v2_primitive=pname, v2_value=val,
                       v2=(cands or [None])[0], v2_all=cands,
                       delta_e=round(cm.de(cm.to_hex(cm.parse_color(e["value"])), val), 2) if cm.is_opaque(e["value"]) else 0.0,
                       how=(c["how"].get(tid) if c else None) or ("representative" if c and c["rep"]["id"] == tid else None),
                       status="demoted-component-tier" if kind == "demoted" else "kept")
            same = [n for n, s in sem.items() if s["ref"] == pname and pname] + \
                   [n for n, t in ctok.items() if (t["ref"] == pname and pname) or (t["raw"] and t["value"] == val)]
            allc = list(OrderedDict.fromkeys(cands + same))
            role = rec["role"]

            def pref(n):
                return (n not in cands, n != f"color-{role}", not n.startswith(f"color-{role.split('-')[0]}-"),
                        allc.index(n))
            ordered = sorted(allc, key=pref)
            rec["v2"] = (ordered or [None])[0]
            rec["v2_all"] = ordered
            bycat = {}
            for prop, prefixes in prop_prefixes.items():
                hit = [n for n in ordered if n.startswith(tuple(prefixes))]
                if hit:
                    bycat[prop] = hit[0]
            if bycat:
                rec["v2_by_property"] = bycat
            v2_value_of[tid] = val
        color_lineage[tid] = rec
    # removed-value replacements for H1
    removed_repl = {k: sem[v]["value"] for k, v in D["color"].get("removed_replacements", {}).items()}
    v2_value_of.update(removed_repl)

    # ---------------- type
    tstyles, tlineage, texc, v1styles = type_engine(v1, D["type"])

    # ---------------- space / radius / size
    sscale, slineage = space_engine(v1, D["space"])
    rad, rlineage = radius_engine(v1, D["radius"])
    sizes, zlineage = size_engine(v1, D["size"])
    for n, e in tlineage.items():
        lh = e.get("v2_line_height")
        if isinstance(lh, str) and lh.startswith("size-control-"):
            sizes["control"].setdefault(lh, {"value": lh.rsplit("-", 1)[1] + "px", "members": []})["members"].append(f"type.{n}.lineHeight")
    if len(sizes["control"]) > D["size"]["max_steps"]["control"]:
        raise SystemExit("control scale has %d steps after line-height controls, more than decisions.size.max_steps.control = %d"
                         % (len(sizes["control"]), D["size"]["max_steps"]["control"]))

    # ================= checks
    checks = OrderedDict()
    # H1
    h1 = []
    tl = tlineage
    pair_text = D.get("h1_pair_text_styles", {})  # v1 pair id → v1 type styles whose v2 size decides text class

    def v2_class(pid, v1cls):
        if v1cls in ("ui", "disabled") or pid not in pair_text:
            return v1cls
        classes = []
        for sn in pair_text[pid]:
            e = tl.get(sn)
            if not e or e.get("kind") == "em":
                continue
            w = (e.get("component_override") or {}).get("fontWeight", e["v2_weight"])
            classes.append(text_class(e["v2_size_px"], w))
        return "normal" if "normal" in classes else (classes[0] if classes else v1cls)

    thr = {"normal": 4.5, "large": 3.0, "ui": 3.0}
    h1_excluded = D.get("h1_excluded_pairs") or {}
    for p in contrast["pairs"] + contrast.get("reference", []):
        fg_t, bg_t = p["fg"]["token"], p["bg"]["token"]
        if p["id"] in h1_excluded:
            h1.append({"id": p["id"], "status": "excluded", "fg": fg_t, "bg": bg_t, "reason": h1_excluded[p["id"]]})
            continue
        fg2 = v2_value_of.get(fg_t)
        bg2 = v2_value_of.get(bg_t)
        if fg2 is None or bg2 is None:
            h1.append({"id": p["id"], "status": "MISSING", "fg": fg_t, "bg": bg_t,
                       "reason": "foreground or background has no rebuilt value; give it a replacement or list the pair "
                                 "in decisions.h1_excluded_pairs with a reason"})
            continue
        r2 = cm.contrast(with_opacity(fg2, p.get("opacity", 1.0)), bg2)
        c1 = p["class"]
        if c1 == "disabled":
            h1.append({"id": p["id"], "status": "exempt", "v1": round(p["ratio_raw"], 2), "v2": round(r2, 2)})
            continue
        c2 = v2_class(p["id"], c1)
        pass1 = p["ratio_raw"] >= thr[c1]
        pass2 = r2 >= thr[c2]
        st = "ok" if (not pass1 or pass2) else "REGRESSION"
        h1.append({"id": p["id"], "fg": fg_t, "bg": bg_t, "v1": round(p["ratio_raw"], 2), "v1_class": c1,
                   "v1_pass": pass1, "v2_fg": fg2, "v2_bg": bg2, "v2": round(r2, 2), "v2_class": c2,
                   "v2_pass": pass2, "status": st, "reference": bool(p.get("reference"))})
    checks["H1"] = {"pass": all(x["status"] not in ("REGRESSION", "MISSING") for x in h1), "pairs": h1}

    # H2 surfaces
    extra_surf = set(D["color"].get("extra_surface_tokens") or [])
    has_group = any("group" in t for t in v1["color"]["tokens"])

    def is_surface(t):
        if has_group:
            return t.get("group") == "surface"
        return str(D["color"]["roles"].get(t["name"], "")).startswith("surface")
    surf = [t for t in v1["color"]["tokens"] if is_surface(t) or t["name"] in extra_surf]
    h2 = []
    roles = D["color"]["roles"]
    for i, a in enumerate(surf):
        for b in surf[i + 1:]:
            ra, rb = roles.get(a["name"]), roles.get(b["name"])
            if a["name"] in D["color"]["alpha"] or b["name"] in D["color"]["alpha"]:
                continue
            if ra == rb:
                continue
            va, vb = v2_value_of[a["name"]], v2_value_of[b["name"]]
            if va.lower() == vb.lower():
                h2.append({"a": a["name"], "b": b["name"], "value": va})
    checks["H2"] = {"pass": not h2, "collisions": h2,
                    "rule": "opaque v1 surface colours with different role drafts must keep different v2 values (solid action fills included)"}

    # H3 role ladder + per-variant order
    ladder = []
    byrole = defaultdict(dict)
    for cell, st in tstyles.items():
        byrole[st["role"]][st["size"]] = st["fontSize"]
    for role, d in byrole.items():
        seq = [d[k] for k in ("lg", "md", "sm") if k in d]
        ok = all(seq[i] > seq[i + 1] for i in range(len(seq) - 1))
        ladder.append({"role": role, "sizes": seq, "ok": ok})
    var_viol = []
    bp_px = {t["name"]: px(t["value"]) for t in (v1.get("breakpoint") or {}).get("tokens", [])}

    def bound(x):
        """(px, named): a breakpoint token name, or a number with optional px; None otherwise."""
        if x in bp_px and bp_px[x] is not None:
            return bp_px[x], True
        m = re.fullmatch(r"(\d+(?:\.\d+)?)(px)?", x)
        return (float(m.group(1)), False) if m else None

    def active_at(when, w):
        """True / False when a condition holds at width w; None when it cannot be parsed.
        max:<b> is below a named breakpoint, or up to and including a number; lt:<b> is below;
        min:<b> is from <b> on; <a>..<b> includes both numbers, or runs from breakpoint a to
        just below breakpoint b."""
        if not when:
            return True
        m = re.fullmatch(r"(max|lt|min):(.+)", when)
        if m:
            b = bound(m.group(2))
            if b is None:
                return None
            if m.group(1) == "min":
                return w >= b[0]
            if m.group(1) == "lt" or b[1]:
                return w < b[0]
            return w <= b[0]
        m = re.fullmatch(r"(.+?)\.\.(.+)", when)
        if m:
            lo, hi = bound(m.group(1)), bound(m.group(2))
            if lo is None or hi is None:
                return None
            return lo[0] <= w and (w < hi[0] if hi[1] else w <= hi[0])
        return None

    def widths_for(whens):
        ws = {1.0, 100000.0}
        for when in whens:
            for part in re.split(r"\.\.|:", when or ""):
                b = bound(part)
                if b is not None:
                    ws |= {b[0] - 1, b[0], b[0] + 1}
        return sorted(w for w in ws if w > 0)

    def type_refs(node, path=()):
        """(slot, key conditions, style) for every type-style reference; the slot is the path
        to the declaration with conditions stripped from its keys (part, state, property)."""
        if isinstance(node, dict):
            tokv = node.get("token")
            if isinstance(tokv, str) and tokv.startswith("type."):
                slot = tuple(k.split("@")[0] for k in path)
                conds = tuple(c for k in path for c in k.split("@")[1:])
                yield slot, conds, tokv[len("type."):]
            for k, x in node.items():
                if k != "token":
                    yield from type_refs(x, path + (str(k),))
        elif isinstance(node, list):
            for i, x in enumerate(node):
                yield from type_refs(x, path + (str(i),))

    seen_viol = set()
    unverified = []

    def order_check(vk, effective, width):
        """effective: [(slot, style)] in effect together; sizes must keep their v1 order in v2."""
        for i, (sa, a) in enumerate(effective):
            for sb, b in effective[i + 1:]:
                if a == b:
                    continue
                for x, y in ((a, b), (b, a)):
                    ex, ey = tl[x], tl[y]
                    if ex["v1_size_px"] < ey["v1_size_px"] and not ex["v2_size_px"] < ey["v2_size_px"]:
                        if (vk, x, y) in seen_viol:
                            continue
                        seen_viol.add((vk, x, y))
                        var_viol.append({"variant": vk, "a": x, "b": y, "width": width,
                                         "v1": [ex["v1_size_px"], ey["v1_size_px"]],
                                         "v2": [ex["v2_size_px"], ey["v2_size_px"]]})

    for vk, v in cmap["variants"].items():
        # one condition set per reference: the map key's conditions plus the style's own `when`;
        # support checks, context collection and activeness all read this set
        # duplicates are dropped so a condition written in both places counts once for precedence
        refs = [(slot, tuple(dict.fromkeys(tuple(conds) + ((tl[st]["v1_when"],) if tl[st].get("v1_when") else ()))), st)
                for slot, conds, st in type_refs(v["parts"])
                if st in tl and tl[st].get("kind") in ("style", "breakpoint")]
        whens = [c for _s, conds, _st in refs for c in conds]

        def kind(c):
            if c.startswith("ctx:") and len(c) > 4:
                return "ctx"
            return "width" if active_at(c, 0) is not None else "unparsed"
        bad = sorted({c for _s, conds, _st in refs for c in conds if kind(c) == "unparsed"})
        if bad:
            unverified.append({"variant": vk, "conditions": bad})
            continue
        contexts = sorted({c[4:] for _s, conds, _st in refs for c in conds if kind(c) == "ctx"})
        if len(contexts) > 8:
            unverified.append({"variant": vk, "conditions": ["ctx:" + c for c in contexts],
                               "note": "more than 8 contexts; combinations not enumerated"})
            continue
        combos = [frozenset(c for i, c in enumerate(contexts) if mask >> i & 1) for mask in range(1 << len(contexts))]
        for w in widths_for(whens):
            for on_ctx in combos:
                by_slot = defaultdict(list)
                for slot, conds, st in refs:
                    ok = all((c[4:] in on_ctx) if kind(c) == "ctx" else active_at(c, w) for c in conds)
                    if ok:
                        by_slot[slot].append((len(conds), st))
                effective = []
                for slot, cands in by_slot.items():
                    # inside one declaration a conditional entry replaces the plain one, and an active
                    # narrow-screen style replaces its own base style; other declarations keep theirs
                    top = max(n for n, _st in cands)
                    names = [st for n, st in cands if n == top]
                    replaced = {tl[st].get("override_of") for st in names if tl[st].get("kind") == "breakpoint"}
                    effective += [(slot, st) for st in dict.fromkeys(names) if st not in replaced]
                order_check(vk, effective, w if not on_ctx else "%s ctx:%s" % (w, "+".join(sorted(on_ctx))))
    checks["H3"] = {"pass": all(x["ok"] for x in ladder) and not var_viol and not unverified, "ladder": ladder,
                    "variant_violations": var_viol,
                    "status": "UNVERIFIED" if unverified else ("PASS" if all(x["ok"] for x in ladder) and not var_viol else "FAIL"),
                    "unverified": unverified,
                    "rule": "(a) every role lg>md>sm strictly decreasing; (b) within one v1 variant, among the sizes in effect at each checked width and context combination (per part, state and property; an override replaces only its own declaration; base declarations still apply when a context is on), a smaller v1 size stays strictly smaller in v2; a condition that cannot be parsed makes H3 UNVERIFIED"}

    # H4 control box heights
    h4 = []
    for name, e in zlineage.items():
        if e["class"] == "control":
            v = px(zlineage[name]["v1"])
            h4.append({"v1_token": name, "role": e["role"], "v1_px": v, "v2": e["v2"],
                       "v2_px": v + e["deviation_px"], "deviation_px": e["deviation_px"],
                       "ok": abs(e["deviation_px"]) < 4})
    for n, e in tl.items():
        if isinstance(e.get("v2_line_height"), str) and e["v2_line_height"].startswith("size-control-"):
            v1lh = px(v1styles[n]["lineHeight"])
            v2 = int(e["v2_line_height"].rsplit("-", 1)[1])
            h4.append({"v1_token": f"type.{n}.lineHeight", "role": "control height carried by line-height", "v1_px": v1lh,
                       "v2": e["v2_line_height"], "v2_px": v2, "deviation_px": v2 - v1lh, "ok": abs(v2 - v1lh) < 4})
    checks["H4"] = {"pass": all(x["ok"] for x in h4), "controls": h4}

    # H5 orphans
    # scale families: a v2 primitive survives only if some kept v1 variant part references a v1 token mapped to it
    removed_v = {v for v, ts in D["variant_map"].items() if all(t["kind"] == "removed" for t in ts)}
    v1_refs = set()
    for vk, v in cmap["variants"].items():
        if vk in removed_v:
            continue
        blob = json.dumps(v["parts"], ensure_ascii=False)
        v1_refs |= set(re.findall(r'"token": "([\w.-]+)"', blob))
        for lst in re.findall(r'"tokens": \[([^\]]*)\]', blob):
            v1_refs |= set(re.findall(r'"([\w.-]+)"', lst))
    scale_used = defaultdict(set)
    for n, e in slineage.items():
        if n in v1_refs:
            for c in e.get("contexts", []):
                scale_used["space"] |= {x for x in c["v2"] if x != "0"}
    for n, e in rlineage.items():
        if n in v1_refs:
            scale_used["radius"].add(e["v2"])
    for n, e in zlineage.items():
        if n in v1_refs and e.get("v2"):
            scale_used["size"].add(e["v2"])
    for n, e in tlineage.items():
        lh = e.get("v2_line_height")
        if isinstance(lh, str) and lh.startswith("size-control-"):
            scale_used["size"].add(lh)
    for n, pair in D["motion"]["map"].items():
        if n in v1_refs:
            scale_used["duration"].add(pair[0])
            scale_used["easing"].add(pair[1])
    scale_orphans = {
        "space": sorted(set(f"space-{x}" for x in sscale) - scale_used["space"], key=lambda x: int(x.split("-")[1])),
        "radius": sorted(set(rad) - scale_used["radius"]),
        "size": sorted((set(sizes["control"]) | set(sizes["icon"])) - scale_used["size"]),
        "duration": sorted(set(f"duration-{k}" for k in D["motion"]["durations"]) - scale_used["duration"]),
        "easing": sorted(set(D["motion"]["easings"]) - scale_used["easing"]),
    }
    used_space = scale_used["space"]
    checks["H5"] = {"pass": True, "removed_orphans": orphans + alpha_orphans, "removed_scale_orphans": scale_orphans,
                    "rule": "primitives not referenced by a semantic or component token are removed; scale families are judged by part references of kept variants"}

    # added states: focus / invalid / checked vs every surface semantic
    surfaces = {n: s["value"] for n, s in sem.items() if n.startswith("color-surface-")}
    added_rows = []
    explicit_stk = D["color"].get("state_check_tokens") or {}
    stk = dict(DEFAULT_STATE_TOKENS, **explicit_stk)
    missing_state_tokens = sorted("%s=%s" % (k, t) for k, t in explicit_stk.items() if t not in sem)

    def added(role):
        t = stk.get(role)
        return t if t in sem and sem[t].get("origin") == "added" else None
    ring, inv_ring, invalid_tok, checked_tok = (added("focus_ring"), added("focus_ring_inverse"),
                                                added("invalid_border"), added("checked_control"))
    inv_s = set(D["color"].get("focus_inverse_surfaces", []))
    ring_any = stk["focus_ring"] if stk["focus_ring"] in sem else None
    inv_any = stk["focus_ring_inverse"] if stk["focus_ring_inverse"] in sem else None
    any_added = bool(ring or inv_ring or invalid_tok or checked_tok)
    ring_uses = {"focus_ring": 0, "focus_ring_inverse": 0}
    ctrl_s = set(D["color"].get("added_state_control_surfaces", []))
    for n, v in surfaces.items():
        # the ring a surface actually uses (source or added); measured when that ring is added
        use_inv = n in inv_s and inv_any is not None
        applied = inv_ring if use_inv else ring
        if applied:
            ring_uses["focus_ring_inverse" if use_inv else "focus_ring"] += 1
            o = sem[applied]["value"]
            r_out = cm.contrast(o, v)
            added_rows.append({"state": "focus-visible", "surface": n, "ring": "inverse" if use_inv else "default",
                               "outer": o, "outer_vs_surface": round(r_out, 2), "pass_outer": r_out >= 3})
        if invalid_tok:
            r_inv = cm.contrast(sem[invalid_tok]["value"], v)
            added_rows.append({"state": "invalid-border", "surface": n, "ratio": round(r_inv, 2), "pass": r_inv >= 3})
        if checked_tok:
            r_chk = cm.contrast(sem[checked_tok]["value"], v)
            added_rows.append({"state": "checked-control", "surface": n, "ratio": round(r_chk, 2), "pass": r_chk >= 3})
    for r in added_rows:
        r["control_surface"] = r["surface"] in ctrl_s
    # an added state with no surface it can be verified on is missing data, not a pass
    no_surface = [r for r, t in (("focus_ring", ring), ("focus_ring_inverse", inv_ring)) if t and not ring_uses[r]]
    no_surface += [r for r, t in (("invalid_border", invalid_tok), ("checked_control", checked_tok))
                   if t and not (ctrl_s & set(surfaces))]
    checks["added_states"] = {"rows": added_rows, "control_surfaces": sorted(ctrl_s),
                    "inverse_ring_surfaces": sorted(inv_s),
                    "checked": [r for r, t in (("focus_ring", ring), ("focus_ring_inverse", inv_ring),
                                                ("invalid_border", invalid_tok), ("checked_control", checked_tok)) if t],
                    "missing_tokens": missing_state_tokens,
                    "no_surface": no_surface,
                    "pass": not missing_state_tokens and not no_surface and
                            all(r["pass_outer"] for r in added_rows if r["state"] == "focus-visible") and
                            all(r["pass"] for r in added_rows if r["state"] != "focus-visible" and r["control_surface"]),
                    "rule": "focus outer ring >= 3:1 on every surface (inverse ring on dark surfaces); invalid border and checked colour only on control surfaces"}

    # ID forbid check
    ids = [c["id"] for c in D["components"]] + [p["id"] for p in D["patterns"]]
    forbid_hits = []
    class_equal = []
    if args.forbid_list:
        sec = None
        subs, cls = [], []
        for line in Path(args.forbid_list).read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("[") and s.endswith("]"):
                sec = s[1:-1]
                continue
            if sec == "substring":
                subs.append(s.lower())
            elif sec == "class":
                cls.append(s)
        names = ids + [f"{c['id']}--{v}" for c in D["components"] for v in c["variants"]] + \
            sorted({p for c in D["components"] for p in c["parts"]})
        for n in names:
            for s in subs:
                if s in n.lower():
                    forbid_hits.append({"id": n, "hit": s, "section": "substring"})
            for c in cls:
                if n == c:
                    class_equal.append({"id": n, "hit": c, "note": "[class] only matches CSS selectors and class attributes; prefixed block names do not trigger it"})
        for a in D["assets"]:
            if a["v2"]:
                for s in subs:
                    if s in a["v2"].lower():
                        forbid_hits.append({"id": a["v2"], "hit": s, "section": "substring"})
    checks["forbid_ids"] = {"pass": not forbid_hits, "hits": forbid_hits, "info_class_equal": class_equal}

    # variant coverage
    vmap = D["variant_map"]
    allv = list(dict.fromkeys(list(cmap["registry"]["main"]) + list(cmap["registry"]["non_brand"])))
    missing = [v for v in allv if v not in vmap]
    comp_ids = {c["id"]: c for c in D["components"]}
    pat_ids = {p["id"] for p in D["patterns"]}
    bad = []
    for v, ts in vmap.items():
        for t in ts:
            if t["kind"] == "component":
                c = comp_ids.get(t["component"])
                if not c or (t.get("variant") and t["variant"] not in c["variants"]) or \
                        (t.get("size") and t["size"] not in c["sizes"]) or \
                        (t.get("state") and t["state"] not in c["states"]) or \
                        (t.get("part") and t["part"] not in c["parts"]):
                    bad.append({"v1": v, "target": t})
            elif t["kind"] == "pattern" and t["pattern"] not in pat_ids:
                bad.append({"v1": v, "target": t})
    checks["coverage"] = {"pass": not missing and not bad, "v1_variants": len(allv), "mapped": len(vmap),
                          "missing": missing, "invalid_targets": bad}
    unused_comp = [c for c in comp_ids if not any(t.get("component") == c for ts in vmap.values() for t in ts)]
    checks["coverage"]["components_without_source"] = unused_comp

    # ================= outputs
    components = []
    for c in D["components"]:
        src = [v for v, ts in vmap.items() for t in ts if t.get("component") == c["id"]]
        components.append(dict(c, anchors=[f"{c['id']}--{v}" for v in c["variants"]], v1_sources=src))

    font_sizes = sorted({st["fontSize"] for st in tstyles.values()} |
                        {st.get("fontSize_base") for st in tstyles.values() if st.get("fontSize_base")} |
                        {e["v2_size_px"] for e in tl.values() if e.get("exception")})
    type_out = {
        "families": {D["type"]["families"][k]: v for k, v in v1["type"]["families"].items() if k in D["type"]["families"]},
        "font_sizes": [f"font-size-{s}" for s in font_sizes],
        "font_size_values": {f"font-size-{s}": f"{s}px" for s in font_sizes},
        "line_heights": {f"line-height-{k}": v for k, v in D["type"]["line_heights"].items()},
        "font_weights": {v: int(k) for k, v in D["type"]["weights"].items()},
        "letter_spacing": {v: k for k, v in D["type"]["letter_spacing"].items()},
        "styles": [],
        "threshold_exceptions": texc,
    }
    for cell, st in tstyles.items():
        base = st.get("fontSize_base", st["fontSize"])
        type_out["styles"].append({
            "name": st["name"], "role": st["role"], "size": st["size"], "family": f"{{font-family-{st['family']}}}",
            "fontSize": f"{{font-size-{base}}}", "lineHeight": f"{{line-height-{st['lineHeight']}}}",
            "fontWeight": f"{{{D['type']['weights'][str(st['fontWeight'])]}}}",
            "letterSpacing": "normal" if st["letterSpacing"] in ("normal", "0") else f"{{{D['type']['letter_spacing'][st['letterSpacing']]}}}",
            "breakpoints": [{"min": b["min"], "fontSize": f"{{font-size-{b['fontSize']}}}"} for b in st["breakpoints"]],
            "v1_members": st["members"],
        })

    prim_space = [f"space-{s}" for s in sscale]
    elevation = OrderedDict()
    comp_shadow = OrderedDict()
    for k, s in D["shadow"].items():
        if s.get("to") and s["to"].startswith("elevation"):
            elevation[s["to"]] = {"value": s["value"], "v1": k}
        elif s.get("to") and s["to"].startswith("component:"):
            comp_shadow[s["to"].split(":", 1)[1]] = {"value": s["value"], "v1": k}
    durations = OrderedDict((f"duration-{k}", f"{k}ms") for k in D["motion"]["durations"])

    consolidation = OrderedDict()
    consolidation["schema"] = {
        "about": "rationalisation result used to generate the layered tokens.json / component-tokens.json; single source of values",
        "primitives": "by family; color.palette entries {value, family, step, roles}; alpha listed apart; other families {name: value}",
        "semantics": "color: {name: {ref, value, origin, usage}}; scale: a few scale semantics from decisions.radius.semantics; elevation; focus-ring",
        "type": "families, font_sizes, line_heights, font_weights, letter_spacing, styles ({name, role, size, family, fontSize, lineHeight, fontWeight, letterSpacing, breakpoints[{min, fontSize}]}, values are {primitive} references)",
        "component_tokens_draft": "component tier draft: {name: {component, ref|value, raw}}; raw=true keeps the original value of a step-collision demotion (an exception to review)",
        "components": "{id, group, summary, variants, sizes, states, parts, anchors, v1_sources}; parts are map part keys and states are state names, never class names",
        "patterns": "{id, name, components}",
        "assets": "{v1, v2, class(brand|project|removed), note}",
        "gaps": "{id, item, detail} (neutral wording)",
        "removed": "removed component variants, token family items and parts, with reasons",
        "checks": "H1-H5, added_states, ID forbid-list, variant coverage",
        "references": "{x} names another token in this file; CSS variables are --<css_prefix>-<name>",
    }
    consolidation["css_prefix"] = D["css_prefix"]
    consolidation["primitives"] = OrderedDict([
        ("color", {"palette": prim_out, "alpha": alpha_out}),
        ("font_size", type_out["font_size_values"]),
        ("line_height", type_out["line_heights"]),
        ("font_weight", type_out["font_weights"]),
        ("letter_spacing", type_out["letter_spacing"]),
        ("font_family", type_out["families"]),
        ("space", OrderedDict((n, f"{n.split('-')[1]}px") for n in prim_space if n in used_space)),
        ("radius", OrderedDict((k, v["value"]) for k, v in rad.items() if k not in scale_orphans["radius"])),
        ("size", OrderedDict([("control", OrderedDict((k, v["value"]) for k, v in sorted(sizes["control"].items(), key=lambda kv: int(kv[0].rsplit('-', 1)[1])) if k not in scale_orphans["size"])),
                              ("icon", OrderedDict((k, v["value"]) for k, v in sorted(sizes["icon"].items(), key=lambda kv: int(kv[0].rsplit('-', 1)[1])) if k not in scale_orphans["size"])),
                              ("layout", OrderedDict(D["size"].get("layout_tokens", {})))])),
        ("duration", OrderedDict((k, v) for k, v in durations.items() if k not in scale_orphans["duration"])),
        ("easing", OrderedDict((k, v) for k, v in D["motion"]["easings"].items() if k not in scale_orphans["easing"])),
        ("breakpoint", OrderedDict((k, f"{v}px") for k, v in D["breakpoint"]["tokens"].items())),
    ])
    consolidation["semantics"] = OrderedDict([
        ("color", sem),
        ("radius", OrderedDict(D["radius"].get("semantics", {}))),
        ("elevation", elevation),
        ("focus", {**({"focus-ring": {"value": D["shadow"]["focus-ring"]["value"], "origin": "added",
                                      "width": D["shadow"]["focus-ring"].get("width", "2px"),
                                      "offset": D["shadow"]["focus-ring"].get("offset", "2px")}}
                      if "focus-ring" in D["shadow"] else {}),
                   **({"focus-ring-inverse": {"value": D["shadow"]["focus-ring-inverse"]["value"], "origin": "added",
                                              "width": D["shadow"]["focus-ring-inverse"].get("width", "2px"),
                                              "offset": D["shadow"]["focus-ring-inverse"].get("offset", "2px"),
                                              "surfaces": D["color"].get("focus_inverse_surfaces", [])}}
                      if "focus-ring-inverse" in D["shadow"] else {})}),
    ])
    consolidation["type"] = type_out
    # type overrides / responsive switches, routed to v2 components through the variant map
    def v2_targets(v1_used_by):
        out = set()
        for u in v1_used_by:
            keys = [u] if "--" in u else [k for k in vmap if k.split("--")[0] == u]
            for k in keys:
                for t in vmap.get(k, []):
                    if t["kind"] == "component":
                        out.add(t["component"] + (f"--{t['variant']}" if t.get("variant") else ""))
        return sorted(out)

    bpmap = D["breakpoint"]["max_to_min"]
    type_over = OrderedDict()
    type_resp = []
    for n, e in tl.items():
        if e.get("kind") not in ("style", "breakpoint"):
            continue
        ub = v1styles[n].get("used_by", [])
        if e.get("component_override") or e.get("exception"):
            ov = dict(e.get("component_override") or {})
            if e.get("exception"):
                ov["fontSize"] = f"font-size-{e['v2_size_px']}"
            type_over[n] = {"style": e["v2"], "override": ov, "v2_components": v2_targets(ub),
                            "reason": e.get("exception") or "weight / letter-spacing / line-height / family differ from the cell's representative style; overridden at component level"}
        if e["kind"] == "breakpoint":
            w = e["v1_when"]
            cond = next((v for k, v in bpmap.items() if k.startswith(w) or k.split(" ")[0] == w), None)
            type_resp.append({"v1": n, "override_of": e["override_of"], "v1_when": w, "v2_condition": cond,
                              "v2_style": e["v2"], "v2_font_size": f"font-size-{e['v2_size_px']}",
                              "deviation_px": e["deviation_px"], "v2_components": v2_targets(ub)})
    size_ct = OrderedDict()
    structural = OrderedDict()
    for n, e in zlineage.items():
        if e["class"] == "component":
            role = e["role"]
            cond = None
            o_, c_ = re.escape(NOTE["open"]), re.escape(NOTE["close"])
            m_ = re.search(o_ + r"([^" + c_ + r"]*\d[^" + c_ + r"]*)" + c_, role)
            if m_ and NOTE["merged"] not in m_.group(1) and "font-size" not in m_.group(1):
                cond = m_.group(1)
            base_names = role.split(NOTE["open"])[0].split(NOTE["sep"])
            val = e["v1"]
            if "font-size-" in role:
                val = "{" + re.search(r"(font-size-\d+)", role).group(1) + "}"
            for nm in base_names:
                key = nm if not cond else f"{nm}@{cond}"
                if key in size_ct:
                    if NOTE["merged"] in role:
                        size_ct[key]["merged_v1"].append({"v1": n, "value": e["v1"]})
                        continue
                    size_ct[key]["merged_v1"].append({"v1": n, "value": e["v1"],
                                                      "note": "same value" if size_ct[key]["value"] == val else "same name, different value; first listed wins"})
                    continue
                if NOTE["merged"] in role:
                    continue
                owner = max((c["id"] for c in D["components"] if nm.startswith(c["id"] + "-")), key=len, default=None)
                size_ct[key] = {"component": owner,
                                "value": val, "condition": cond, "v1": n, "merged_v1": []}
        elif e["class"] == "structural":
            structural[n] = e["role"]
    for n, e in zlineage.items():
        if e["class"] == "component" and NOTE["merged"] in e["role"]:
            nm = e["role"].split(NOTE["open"])[0]
            if nm in size_ct:
                size_ct[nm]["merged_v1"] = [x for x in size_ct[nm]["merged_v1"] if x["v1"] != n]
                size_ct[nm]["merged_v1"].append({"v1": n, "value": e["v1"], "note": e["role"]})
    consolidation["component_tokens_draft"] = OrderedDict([("color", ctok), ("color_redundant_use_semantic", redundant),
                                                           ("size", size_ct), ("structural_literals", structural),
                                                           ("space_component_only", {k: v["note"] for k, v in slineage.items() if v.get("kind") == "component-only"}),
                                                           ("shadow", comp_shadow),
                                                           ("type_overrides", type_over),
                                                           ("type_responsive", type_resp)])
    consolidation["components"] = components
    consolidation["patterns"] = D["patterns"]
    consolidation["assets"] = D["assets"]
    consolidation["gaps"] = D["gaps"]
    consolidation["removed"] = {
        "variants": [{"v1": v, "reason": t["reason"]} for v, ts in vmap.items() for t in ts if t["kind"] == "removed"],
        "parts": D.get("removed_parts", []),
        "color": [{"v1": k, "reason": v["reason"]} for k, v in color_lineage.items() if v.get("status") == "removed"],
        "orphan_primitives": [{"name": o["name"], "value": o["value"], "members": o["members"]} for o in orphans + alpha_orphans],
        "motion": D["motion"]["removed"],
        "size": {k: v["role"] for k, v in zlineage.items() if v["class"] == "project"},
        "shadow": {k: v["reason"] for k, v in D["shadow"].items() if v.get("to") is None},
        "type_families": D["type"].get("families_removed", {}),
    }
    consolidation["checks"] = checks

    lineage_out = OrderedDict()
    lineage_out["schema"] = load(args.decisions).get("schema")
    lineage_out["decisions"] = D
    lineage_out["color"] = color_lineage
    lineage_out["color_clusters"] = [
        {"name": c.get("name"), "value": c["rep"]["hex"], "family": c["family"], "step": c["step"],
         "roles": sorted(c["roles"]), "rep_v1": c["rep"]["id"],
         "members": [{"v1": m["id"], "value": m["hex"], "delta_e": round(cm.de(m["hex"], c["rep"]["hex"]), 2),
                      "how": c["how"].get(m["id"], "representative")} for m in c["members"]],
         "status": "demoted" if c.get("demoted") else ("merged" if c.get("merged_into") else
                                                        ("kept" if c.get("name") in prim_out else "orphan-removed"))}
        for c in ce.clusters]
    lineage_out["type"] = tl
    lineage_out["space"] = slineage
    lineage_out["radius"] = rlineage
    lineage_out["size"] = zlineage
    lineage_out["shadow"] = D["shadow"]
    lineage_out["motion"] = D["motion"]["map"]
    lineage_out["variants"] = vmap
    # reverse index: v2 token / component → v1 sources
    rev = defaultdict(set)
    for k, v in color_lineage.items():
        for n in (v.get("v2_all") or ([v["v2"]] if v.get("v2") else [])):
            rev[n].add(k)
        if v.get("v2_primitive"):
            rev[v["v2_primitive"]].add(k)
    for n, v in list(prim_out.items()) + list(alpha_out.items()):
        for m in v["members"]:
            rev[n].add(m)
    for k, v in tl.items():
        if v.get("v2"):
            rev[v["v2"]].add(f"type.{k}")
    for k, v in slineage.items():
        for cx in v.get("contexts", []):
            for n in cx["v2"]:
                if n != "0":
                    rev[n].add(k)
    for k, v in rlineage.items():
        rev[v["v2"]].add(k)
    for k, v in zlineage.items():
        if v.get("v2"):
            rev[v["v2"]].add(k)
    for k, pair in D["motion"]["map"].items():
        for n in pair:
            rev[n].add(k)
    for k, v in D["shadow"].items():
        if v.get("to"):
            rev[v["to"].split(":", 1)[-1]].add(k)
    for vk, ts in vmap.items():
        for t in ts:
            if t["kind"] == "component":
                rev[f"component:{t['component']}"].add(vk)
            elif t["kind"] == "pattern":
                rev[f"pattern:{t['pattern']}"].add(vk)
    lineage_out["v2_to_v1"] = OrderedDict((k, sorted(v)) for k, v in sorted(rev.items()))

    outputs = [(Path(args.out_consolidation), json.dumps(consolidation, ensure_ascii=False, indent=1)),
               (Path(args.out_lineage), json.dumps(lineage_out, ensure_ascii=False, indent=1))]
    failed = [k for k, v in checks.items() if not v.get("pass", True)]
    if args.check:
        rc = 0
        for p, t in outputs:
            same = p.exists() and p.read_bytes() == t.encode("utf-8")
            print("%s %s" % (p.name, "up to date" if same else "differs from regenerated output"))
            rc |= 0 if same else 1
        for k in failed:
            print(k, "FAIL")
        return 1 if failed else rc
    for p, t in outputs:
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(t)

    # console summary
    print("palette kept:", len(prim_out), "alpha kept:", len(alpha_out), "orphans:", len(orphans) + len(alpha_orphans),
          "demoted:", len(ce.demoted))
    print("semantic color:", len(sem), "component color tokens:", len(ctok))
    print("type styles:", len(tstyles), "font sizes:", font_sizes)
    print("space:", [n for n in prim_space if n in used_space], "radius:", {k: v["value"] for k, v in rad.items()})
    print("size control:", list(sizes["control"]), "icon:", list(sizes["icon"]))
    for k, v in checks.items():
        print(k, "PASS" if v.get("pass", True) else "FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
