#!/usr/bin/env python3
"""Self-test for rationalize.py: runs it on a minimal neutral v1 fixture in a temporary folder
(standard library only).

Usage:
  python -I selftest.py [--keep <scratch-dir>]

Checks:
- a passing fixture exits 0 and --check reproduces both outputs (decisions file = lineage file)
- the v1 space family is read as `space`
- components carry part keys and state names only (no class names)
- a failing hard rule (H4) gives a nonzero exit after the outputs are written
- decisions without note_syntax stop with a message
- a v1 without `used_by` (Phase 1 keeps it in the research data) gives the same output as a
  v1 that carries it
- package-shaped map: a component without variants and a pattern keep the primitives only
  they reference, and the variant map must cover them; read_tokens leaves its input unchanged
- H1 with opacity, a pair with no rebuilt value (fails unless excluded), no added states,
  a missing state token, an H3 inversion across conditions, a nine-step scale the plan allows
- end to end: the Phase 1 snapshot fixture of ../package/selftest.py is built with the package
  scripts and passes check_package --stage data --allow-orphans; rationalize reads that package
  as it stands (package map, build_contrast output with computed ratios); the result, packaged
  as layered tokens, builds and passes check_package --stage data without --allow-orphans
--keep writes the fixture under <scratch-dir>/rationalize-selftest and leaves it there.
Exit 0 when every check passes.
"""
import argparse
import copy
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
PKG = HERE.parent / "package"


def tk(name, value, tier="primitive", usage="sample", **extra):
    return dict({"name": name, "value": value, "tier": tier, "origin": "source", "usage": usage}, **extra)


V1 = {
    "css": {"prefix": "x"}, "themes": [{"id": "default"}],
    "color": {"tokens": [
        tk("brand-main", "#336699", "semantic"),
        tk("text-main", "#222222", "semantic"),
        tk("surface-main", "#ffffff", "semantic", group="surface"),
        tk("surface-alt", "#f0f0f0", "semantic", group="surface"),
        tk("border-invalid", "#cc3333", "semantic"),
    ]},
    "type": {
        "families": {"sans": {"value": "system-ui, sans-serif", "tier": "primitive", "origin": "source", "usage": "ui"}},
        "scales": {},
        "groups": [{"name": "Body", "styles": [
            {"name": "type-body", "family": "{font-family-sans}", "fontSize": "16px", "lineHeight": 1.5,
             "fontWeight": 400, "letterSpacing": "normal", "tier": "semantic", "origin": "source", "usage": "body"},
            {"name": "type-small", "family": "{font-family-sans}", "fontSize": "14px", "lineHeight": 1.5,
             "fontWeight": 400, "letterSpacing": "normal", "tier": "semantic", "origin": "source", "usage": "note"},
        ]}]},
    "space": {"tokens": [tk("space-a", "8px"), tk("space-b", "16px")]},
    "radius": {"tokens": [tk("radius-a", "4px")]},
    "size": {"tokens": [tk("size-button", "40px")]},
    "duration": {"tokens": [tk("duration-a", "150ms")]},
    "easing": {"tokens": [tk("easing-a", "ease")]},
    "breakpoint": {"tokens": [tk("breakpoint-sm", "576px")]},
}

USED_BY = {
    "brand-main": ["button--primary"], "text-main": ["button--primary"], "surface-main": ["button--primary"],
    "surface-alt": ["button--primary"], "border-invalid": ["button--primary"],
    "type-body": ["button--primary"], "type-small": ["button--primary"],
    "space-a": ["button--primary"], "space-b": ["button--primary"], "radius-a": ["button--primary"],
}

USAGE = {"color": {"tokens": [{"name": n, "used_by": USED_BY[n], "decl_count": 1}
                              for n in ("brand-main", "text-main", "surface-main", "surface-alt", "border-invalid")]},
         "type": {"tokens": [{"name": n, "used_by": USED_BY[n]} for n in ("type-body", "type-small")]},
         "space": {"tokens": [{"name": n, "used_by": USED_BY[n]} for n in ("space-a", "space-b")]},
         "radius": {"tokens": [{"name": "radius-a", "used_by": USED_BY["radius-a"]}]}}

CMAP = {
    "registry": {"main": ["button--primary"], "non_brand": []},
    "variants": {"button--primary": {"parts": {"root": {"default": {
        "background-color": {"token": "brand-main"}, "color": {"token": "surface-main"},
        "padding": {"tokens": ["space-a", "space-b"]}, "border-radius": {"token": "radius-a"},
        "min-height": {"token": "size-button"}, "font": {"token": "type.type-body"},
        "transition": {"tokens": ["duration-a", "easing-a"]}},
        "hint": {"font": {"token": "type.type-small"}}}}}},
}

# The same references in the package map shape, split over a variant, a component without
# variants (space-b) and a pattern (radius-a).
CMAP_PKG = {
    "components": {
        "button": {"anatomy": ["root", "hint"],
                   "parts": {"root": {"default": {"color": {"token": "surface-main"}, "padding": {"tokens": ["space-a"]},
                                                  "min-height": {"token": "size-button"}, "font": {"token": "type-body"},
                                                  "transition": {"tokens": ["duration-a", "easing-a"]}}},
                             "hint": {"default": {"font": {"token": "type-small"}}}},
                   "variants": {"button--primary": {"parts": {"root": {"default": {"background-color": {"token": "brand-main"}}}}}}},
        "divider": {"anatomy": ["root"], "parts": {"root": {"default": {"margin": {"tokens": ["space-b"]}}}}, "variants": {}}},
    "patterns": [{"id": "panel", "name": "Panel", "components": ["button"],
                  "parts": {"root": {"default": {"border-radius": {"token": "radius-a"}}}}}],
}

CONTRAST = {"pairs": [{"id": "pair-1", "fg": {"token": "text-main"}, "bg": {"token": "surface-main"},
                       "class": "normal", "ratio_raw": 15.91}]}

DECISIONS = {"schema": "selftest", "decisions": {
    "css_prefix": "x",
    "note_syntax": {"open": "(", "close": ")", "sep": "/", "merged": "merged"},
    "color": {
        "family_rules": {"special": {"#ffffff": "white"}, "neutral_chroma_max": 8,
                         "named_hue_ranges": [["blue", 200, 300], ["red", 340, 400]], "fallback_bin_deg": 30},
        "roles": {"brand-main": "action-primary", "text-main": "text-default", "surface-main": "surface-canvas",
                  "surface-alt": "surface-subtle", "border-invalid": "border-invalid"},
        "alpha": {}, "removed": {},
        "semantics": [
            {"name": "color-action-primary", "from": "brand-main", "usage": "primary action"},
            {"name": "color-text-default", "from": "text-main", "usage": "body text"},
            {"name": "color-surface-canvas", "from": "surface-main", "usage": "page"},
            {"name": "color-surface-subtle", "from": "surface-alt", "usage": "alternate surface"},
            {"name": "color-border-invalid", "from": "border-invalid", "usage": "invalid input"},
            {"name": "color-focus-ring", "from": "brand-main", "usage": "focus", "origin": "added"},
            {"name": "color-action-checked", "from": "brand-main", "usage": "checked", "origin": "added"}],
        "component_tokens": [],
        "added_state_control_surfaces": ["color-surface-canvas"]},
    "type": {"breakpoint_variants": {}, "cells": {"body-md": ["type-body"], "body-sm": ["type-small"]},
             "line_heights": {"normal": 1.5}, "line_height_threshold": 0.1,
             "families": {"sans": "sans", "{font-family-sans}": "sans"},
             "weights": {"400": "font-weight-regular"}, "letter_spacing": {}},
    "space": {"base": 4, "half_step": 2, "exception_over_px": 4, "component_only": {}},
    "radius": {"merge_px": 1, "names": ["none", "xs", "sm", "md", "lg", "xl", "pill", "full"]},
    "size": {"classes": {"size-button": ["control", "button height"]}, "control_scale": [40], "icon_scale": [16], "max_steps": {"control": 8, "icon": 8}},
    "shadow": {"focus-ring": {"to": "focus-ring", "value": "0 0 0 2px {color-focus-ring}"}},
    "motion": {"map": {"duration-a": ["duration-150", "easing-standard"]}, "durations": [150],
               "easings": {"easing-standard": "ease"}, "removed": []},
    "breakpoint": {"tokens": {"breakpoint-sm": 576}, "max_to_min": {}},
    "variant_map": {"button--primary": [{"kind": "component", "component": "button", "variant": "primary"}]},
    "components": [{"id": "button", "group": "actions", "summary": "Action", "variants": ["primary"], "sizes": [],
                    "states": ["hover", "selected"], "parts": ["root", "hint"]}],
    "patterns": [], "assets": [], "gaps": [],
}}


# End to end: the Phase 1 snapshot fixture of package/selftest.py, built with the package
# scripts, is read by rationalize as it stands; its result is packaged as a layered P2 package.
E2E_USAGE = {"color": {"tokens": [{"name": n, "used_by": ["sample-button--primary"], "decl_count": 1}
                                  for n in ("color-action-primary", "color-surface-canvas", "color-text-default",
                                            "color-sample-button-border")]},
             "type": {"tokens": [{"name": "type-body-md", "used_by": ["sample-button--primary"]}]}}

E2E_DECISIONS = {"schema": "selftest-e2e", "decisions": {
    "css_prefix": "x",
    "note_syntax": {"open": "(", "close": ")", "sep": "/", "merged": "merged"},
    "color": {
        "family_rules": DECISIONS["decisions"]["color"]["family_rules"],
        "roles": {"color-action-primary": "action-primary", "color-surface-canvas": "surface-canvas",
                  "color-text-default": "text-default", "color-sample-button-border": "border-button"},
        "alpha": {}, "removed": {"residue-focus-glow": "unbranded residue, not rebuilt"},
        "semantics": [
            {"name": "color-action-primary", "from": "color-action-primary", "usage": "primary action"},
            {"name": "color-surface-canvas", "from": "color-surface-canvas", "usage": "page"},
            {"name": "color-text-default", "from": "color-text-default", "usage": "body text"},
            {"name": "color-focus-ring", "from": "color-action-primary", "usage": "focus", "origin": "added"}],
        "component_tokens": [{"name": "sample-button-border", "component": "sample-button", "from": "color-sample-button-border"}],
        "state_check_tokens": {"invalid_border": "color-focus-ring", "checked_control": "color-action-primary"},
        "added_state_control_surfaces": ["color-surface-canvas"]},
    "type": {"breakpoint_variants": {}, "cells": {"body-md": ["type-body-md"]}, "line_heights": {"normal": 1.5},
             "line_height_threshold": 0.1, "families": {"sans": "sans"}, "weights": {"400": "font-weight-regular"},
             "letter_spacing": {"0px": "letter-spacing-normal"}},
    "space": {"base": 4, "half_step": 2, "exception_over_px": 4, "component_only": {}},
    "radius": {"merge_px": 1, "names": ["none", "xs", "sm", "md", "lg", "xl", "pill", "full"]},
    "size": {"classes": {"size-control-40": ["control", "control height"]}, "control_scale": [40], "icon_scale": [16], "max_steps": {"control": 8, "icon": 8}},
    "shadow": {"focus-ring": {"to": "focus-ring", "value": "0 0 0 2px {color-focus-ring}"}},
    "motion": {"map": {"duration-150": ["duration-150", "easing-standard"]}, "durations": [150],
               "easings": {"easing-standard": "ease"}, "removed": []},
    "breakpoint": {"tokens": {"breakpoint-sm": 576, "breakpoint-md": 768}, "max_to_min": {}},
    "variant_map": {"sample-button--primary": [{"kind": "component", "component": "sample-button", "variant": "primary"}]},
    "components": [{"id": "sample-button", "group": "actions", "summary": "Primary action", "variants": ["primary"],
                    "sizes": [], "states": ["hover"], "parts": ["root"]}],
    "patterns": [], "assets": [], "gaps": [],
}}

E2E_BASE_CSS = """/* tokens in use: var(--x-breakpoint-sm) var(--x-breakpoint-md) */
body { color: var(--x-color-text-default); background-color: var(--x-color-surface-canvas); }
"""


def p2_package(cons, cmap_p1, contrast_p1):
    """tokens.json, component map and contrast definition of the layered package, written from
    the consolidation the way the construction worker does (fixture helper, not a converter)."""
    pr, se = cons["primitives"], cons["semantics"]

    def t(name, value, tier, origin="source", **extra):
        return dict({"name": name, "value": value, "tier": tier, "origin": origin, "usage": "selftest"}, **extra)

    def flat(d, tier="primitive"):
        return {"tokens": [t(n, v, tier) for n, v in d.items()]}

    color = [t(n, e["value"], "primitive") for n, e in pr["color"]["palette"].items()]
    color += [t(n, e["value"], "primitive") for n, e in pr["color"]["alpha"].items()]
    color += [t(n, "{%s}" % e["ref"], "semantic", e.get("origin", "source")) for n, e in se["color"].items()]
    rename = {}
    for n, e in cons["component_tokens_draft"]["color"].items():
        color.append(t(n, "{%s}" % e["ref"] if e["ref"] else e["value"], "component", component=e["component"]))
        rename[e["anchor_v1"]] = n
    styles = [{"name": st["name"], "family": st["family"], "fontSize": st["fontSize"], "lineHeight": st["lineHeight"],
               "fontWeight": st["fontWeight"], "letterSpacing": st["letterSpacing"], "breakpoints": st["breakpoints"],
               "tier": "semantic", "origin": "source", "usage": "selftest"} for st in cons["type"]["styles"]]
    size = merged_dicts(pr["size"]["control"], pr["size"]["icon"], pr["size"]["layout"])
    tokens = {
        "name": "x-sample", "version": "0.2", "css": {"prefix": "x"}, "themes": [{"id": "default"}],
        "tailwind": {"spacing_token": next(iter(pr["space"]))},
        "color": {"tokens": color},
        "type": {"families": {k: {"value": v, "tier": "primitive", "origin": "source", "usage": "selftest"}
                              for k, v in pr["font_family"].items()},
                 "scales": {"font-family": {"tokens": []}, "font-size": flat(pr["font_size"]),
                            "line-height": flat(pr["line_height"]), "font-weight": flat(pr["font_weight"]),
                            "letter-spacing": flat(pr["letter_spacing"])},
                 "groups": [{"name": "Type", "styles": styles}]},
        "space": flat(pr["space"]), "radius": flat(pr["radius"]), "size": flat(size),
        "shadow": {"tokens": [t(n, e["value"], "semantic", e.get("origin", "source")) for n, e in se["focus"].items()]
                   + [t(n, e["value"], "semantic") for n, e in se["elevation"].items()]},
        "duration": flat(pr["duration"]), "easing": flat(pr["easing"]), "breakpoint": flat(pr["breakpoint"]),
    }
    cmap = json.loads(json.dumps(cmap_p1))
    blob = json.dumps(cmap)
    for old, new in rename.items():
        blob = blob.replace('"%s"' % old, '"%s"' % new)
    cmap = json.loads(blob)
    contrast = dict(contrast_p1, added_states={
        "threshold": 3.0, "focus_ring": "2px ring",
        "surfaces": [{"surface": "color-surface-canvas", "controls": True, "ring": "default"}],
        "checks": [{"state": "focus-visible", "fg": "color-focus-ring", "scope": "all"}]})
    return tokens, cmap, contrast


def merged_dicts(*parts):
    out = {}
    for d in parts:
        out.update(d)
    return out


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def py(args):
    r = subprocess.run([sys.executable, "-I", "-B"] + [str(a) for a in args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def write(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, str):
        p.write_bytes(obj.encode("utf-8"))
        return
    p.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def run(d: Path, v1, decisions, check=False, cmap=None, contrast=None):
    write(d / "v1.json", v1)
    write(d / "map.json", cmap or CMAP)
    write(d / "contrast.json", contrast or CONTRAST)
    write(d / "usage.json", USAGE)
    lineage = d / "lineage.json"
    if decisions is not None:
        write(lineage, decisions)
    args = [sys.executable, "-I", "-B", str(HERE / "rationalize.py"), "--tokens", d / "v1.json", "--component-map", d / "map.json",
            "--contrast", d / "contrast.json", "--usage", d / "usage.json", "--decisions", lineage,
            "--out-consolidation", d / "consolidation.json", "--out-lineage", lineage]
    if check:
        args.append("--check")
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", help="scratch directory to keep the fixture in")
    a = ap.parse_args(argv)
    results = []

    def check(name, cond, detail=""):
        results.append((bool(cond), name, detail))

    def body(root: Path):
        with_used = copy.deepcopy(V1)
        for fam in ("color", "space", "radius"):
            for t in with_used[fam]["tokens"]:
                if t["name"] in USED_BY:
                    t["used_by"] = USED_BY[t["name"]]
        for s in with_used["type"]["groups"][0]["styles"]:
            s["used_by"] = USED_BY[s["name"]]

        ok_dir = root / "pass"
        rc, out = run(ok_dir, V1, DECISIONS)
        check("passing fixture exits 0", rc == 0, out[-600:])
        cons = json.loads((ok_dir / "consolidation.json").read_text(encoding="utf-8")) if rc == 0 else {}
        check("every check passes", cons and all(v.get("pass", True) for v in cons["checks"].values()),
              json.dumps({k: v.get("pass") for k, v in cons.get("checks", {}).items()}))
        rc, out = run(ok_dir, V1, None, check=True)
        check("--check reproduces both outputs", rc == 0, out[-300:])
        check("space family read as `space`", list((cons.get("primitives") or {}).get("space", {})) == ["space-8", "space-16"],
              json.dumps((cons.get("primitives") or {}).get("space")))
        comp = (cons.get("components") or [{}])[0]
        blob = json.dumps(cons.get("components"))
        check("components carry part keys and state names, no class names",
              comp.get("parts") == ["root", "hint"] and comp.get("states") == ["hover", "selected"]
              and "bem" not in comp and "__" not in blob and "is-" not in blob, blob[:300])

        used_dir = root / "used-by-in-v1"
        rc, out = run(used_dir, with_used, DECISIONS)
        same = rc == 0 and (used_dir / "consolidation.json").read_bytes() == (ok_dir / "consolidation.json").read_bytes()
        check("v1 without used_by equals v1 with used_by", same, out[-300:])
        spec = importlib.util.spec_from_file_location("rationalize_under_test", HERE / "rationalize.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        filled = copy.deepcopy(V1)
        mod.overlay_used_by(filled, USAGE)
        check("used_by copied from the research data", filled == with_used)

        bad = copy.deepcopy(DECISIONS)
        bad["decisions"]["size"]["control_scale"] = [48]
        fail_dir = root / "h4-fail"
        rc, out = run(fail_dir, V1, bad)
        check("failing hard rule exits nonzero after writing", rc == 1 and "H4 FAIL" in out
              and (fail_dir / "consolidation.json").exists(), out[-300:])

        pkg_dec = copy.deepcopy(DECISIONS)
        pd = pkg_dec["decisions"]
        pd["variant_map"].update({"divider": [{"kind": "component", "component": "divider"}],
                                  "panel": [{"kind": "pattern", "pattern": "panel"}]})
        pd["components"].append({"id": "divider", "group": "content", "summary": "Rule", "variants": [], "sizes": [],
                                 "states": [], "parts": ["root"]})
        pd["patterns"] = [{"id": "panel", "name": "Panel", "components": ["button"]}]
        pm_dir = root / "package-map"
        rc, out = run(pm_dir, V1, pkg_dec, cmap=CMAP_PKG)
        pcons = json.loads((pm_dir / "consolidation.json").read_text(encoding="utf-8")) if rc == 0 else {}
        pprim = pcons.get("primitives") or {}
        check("variant-less component and pattern keep their primitives", rc == 0
              and list(pprim.get("space", {})) == ["space-8", "space-16"] and len(pprim.get("radius", {})) == 1
              and pcons["checks"]["coverage"]["pass"], out[-400:])
        del pd["variant_map"]["divider"], pd["variant_map"]["panel"]
        rc, out = run(root / "package-map-uncovered", V1, pkg_dec, cmap=CMAP_PKG)
        ucons = json.loads((root / "package-map-uncovered" / "consolidation.json").read_text(encoding="utf-8"))
        check("variant map must cover them", rc == 1 and ucons["checks"]["coverage"]["missing"] == ["divider", "panel"],
              json.dumps(ucons["checks"]["coverage"]["missing"]))
        src = copy.deepcopy(V1)
        view = mod.read_tokens(src)
        check("read_tokens leaves its input unchanged", src == V1 and view["type"]["families"]["sans"] == "system-ui, sans-serif")

        def cons_of(d):
            f = d / "consolidation.json"
            return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}

        # H1 uses the pair's opacity: text at 0.75 opacity whose colour is aliased to another value
        alias = copy.deepcopy(DECISIONS)
        alias["decisions"]["color"]["alias"] = {"text-main": "brand-main"}
        raw = mod.cm.contrast(mod.with_opacity("#222222", 0.75), "#ffffff")
        faded = {"pairs": [{"id": "pair-1", "fg": {"token": "text-main"}, "bg": {"token": "surface-main"},
                            "class": "normal", "ratio_raw": raw, "opacity": 0.75}]}
        rc, out = run(root / "h1-opacity", V1, alias, contrast=faded)
        h1 = cons_of(root / "h1-opacity").get("checks", {}).get("H1", {})
        check("H1 judges the rebuilt pair with its opacity", rc == 1 and h1.get("pass") is False
              and h1["pairs"][0]["status"] == "REGRESSION" and h1["pairs"][0]["v2"] == 3.51, json.dumps(h1)[:300])
        opaque = {"pairs": [dict(faded["pairs"][0], ratio_raw=mod.cm.contrast("#222222", "#ffffff"))]}
        del opaque["pairs"][0]["opacity"]
        rc, out = run(root / "h1-opaque", V1, alias, contrast=opaque)
        check("the same pair without opacity passes H1", rc == 0, out[-300:])

        # H1: a pair with no rebuilt value fails unless excluded with a reason
        lost = {"pairs": CONTRAST["pairs"] + [{"id": "pair-2", "fg": {"token": "gone-token"}, "bg": {"token": "surface-main"},
                                               "class": "normal", "ratio_raw": 7.0}]}
        rc, out = run(root / "h1-missing", V1, DECISIONS, contrast=lost)
        h1 = cons_of(root / "h1-missing").get("checks", {}).get("H1", {})
        check("H1 fails on a pair with no rebuilt value", rc == 1 and [p["status"] for p in h1.get("pairs", [])] == ["ok", "MISSING"],
              json.dumps(h1)[:300])
        excl = copy.deepcopy(DECISIONS)
        excl["decisions"]["h1_excluded_pairs"] = {"pair-2": "foreground removed with its component"}
        rc, out = run(root / "h1-excluded", V1, excl, contrast=lost)
        check("an approved exclusion keeps its reason and passes", rc == 0
              and cons_of(root / "h1-excluded")["checks"]["H1"]["pairs"][1]["status"] == "excluded", out[-300:])

        # added states: none added passes; a named token that does not exist fails
        plain = copy.deepcopy(DECISIONS)
        plain["decisions"]["color"]["semantics"] = [x for x in plain["decisions"]["color"]["semantics"] if x.get("origin") != "added"]
        plain["decisions"]["shadow"] = {}
        rc, out = run(root / "no-added-states", V1, plain)
        st = cons_of(root / "no-added-states").get("checks", {}).get("added_states", {})
        check("no added states: nothing to check, passes", rc == 0 and st.get("rows") == [] and st.get("checked") == [], out[-300:])
        plain["decisions"]["color"]["state_check_tokens"] = {"focus_ring": "color-focus-missing"}
        rc, out = run(root / "added-state-missing-token", V1, plain)
        st = cons_of(root / "added-state-missing-token").get("checks", {}).get("added_states", {})
        check("a named state token that does not exist fails", rc == 1 and st.get("missing_tokens") == ["focus_ring=color-focus-missing"],
              json.dumps(st)[:300])

        # H3 compares the sizes in effect at each width, across conditions
        v1x = copy.deepcopy(V1)
        base_style = v1x["type"]["groups"][0]["styles"][0]
        v1x["type"]["groups"][0]["styles"] += [dict(base_style, name="type-big", fontSize="24px", usage="title"),
                                                dict(base_style, name="type-big-narrow", fontSize="15px", usage="title, narrow")]
        mapx = copy.deepcopy(CMAP)
        mapx["variants"]["button--primary"]["parts"]["title"] = {"default": {"font": {"token": "type.type-big"}},
                                                                 "narrow": {"font": {"token": "type.type-big-narrow"}}}
        dx = copy.deepcopy(DECISIONS)
        dx["decisions"]["type"].update({"cells": {"body-md": ["type-body"], "body-sm": ["type-small"], "title-md": ["type-big"]},
                                        "breakpoint_variants": {"type-big-narrow": {"of": "type-big", "when": "max:breakpoint-sm"}},
                                        "mobile_variant_when": [], "mobile_min_breakpoint": "breakpoint-sm"})
        rc, out = run(root / "h3-cross-condition", v1x, dx, cmap=mapx)
        h3 = cons_of(root / "h3-cross-condition").get("checks", {}).get("H3", {})
        viol = [(x["a"], x["b"], x["width"]) for x in h3.get("variant_violations", [])]
        check("H3 catches an order inversion between a narrow-screen style and a base style", rc == 1
              and viol == [("type-big-narrow", "type-body", 1.0)], json.dumps(h3)[:400])

        # H3: two parts share the 24px title; one part switches to 23px below the breakpoint (only
        # inside its own declaration); the rebuild maps 23 to 24, which merges the two sizes
        v1o = copy.deepcopy(V1)
        v1o["type"]["groups"][0]["styles"] += [dict(base_style, name="type-big", fontSize="24px", usage="title"),
                                                dict(base_style, name="type-big-narrow", fontSize="23px", usage="title, narrow")]
        mapo = copy.deepcopy(CMAP)
        mapo["variants"]["button--primary"]["parts"]["head"] = {
            "default": {"font": {"token": "type.type-big"}},
            "default@max:breakpoint-sm": {"font": {"token": "type.type-big-narrow"}}}
        mapo["variants"]["button--primary"]["parts"]["sub"] = {"default": {"font": {"token": "type.type-big"}}}
        rc, out = run(root / "h3-part-override", v1o, dx, cmap=mapo)
        h3 = cons_of(root / "h3-part-override").get("checks", {}).get("H3", {})
        viol = [(x["a"], x["b"]) for x in h3.get("variant_violations", [])]
        check("H3 catches a merge between a part override and another part's base size", rc == 1
              and ("type-big-narrow", "type-big") in viol, json.dumps(h3)[:400])

        # the same override declared under a context: the base declaration of the other part still
        # applies while the context is on, so the 23/24 -> 24/24 merge is still caught
        mapc = copy.deepcopy(mapo)
        head = mapc["variants"]["button--primary"]["parts"]["head"]
        head["default@ctx:compact"] = head.pop("default@max:breakpoint-sm")
        rc, out = run(root / "h3-context-override", v1o, dx, cmap=mapc)
        h3 = cons_of(root / "h3-context-override").get("checks", {}).get("H3", {})
        viol = [(x["a"], x["b"], x["width"]) for x in h3.get("variant_violations", [])]
        check("H3 resolves context declarations together with base declarations", rc == 1
              and ("type-big-narrow", "type-big", "1.0 ctx:compact") in viol, json.dumps(h3)[:400])
        # the equivalent form: the context sits on the style's condition, the breakpoint on the map key
        mapk = copy.deepcopy(mapo)
        head = mapk["variants"]["button--primary"]["parts"]["head"]
        head["default@lt:breakpoint-sm"] = head.pop("default@max:breakpoint-sm")
        dk = copy.deepcopy(dx)
        dk["decisions"]["type"]["breakpoint_variants"] = {"type-big-narrow": {"of": "type-big", "when": "ctx:compact"}}
        rc, out = run(root / "h3-context-on-style", v1o, dk, cmap=mapk)
        h3 = cons_of(root / "h3-context-on-style").get("checks", {}).get("H3", {})
        viol = [(x["a"], x["b"], x["width"]) for x in h3.get("variant_violations", [])]
        check("H3 reads a context on the style's condition like one on the map key", rc == 1
              and ("type-big-narrow", "type-big", "1.0 ctx:compact") in viol, json.dumps(h3)[:400])
        # the same context written in both places counts once: the H3 result is unchanged
        mapd = copy.deepcopy(mapk)
        head = mapd["variants"]["button--primary"]["parts"]["head"]
        head["default@lt:breakpoint-sm@ctx:compact"] = head.pop("default@lt:breakpoint-sm")
        rc2, out = run(root / "h3-context-duplicated", v1o, dk, cmap=mapd)
        h3d = cons_of(root / "h3-context-duplicated").get("checks", {}).get("H3", {})
        viol_d = [(x["a"], x["b"], x["width"]) for x in h3d.get("variant_violations", [])]
        check("a condition repeated on the map key and the style counts once", rc2 == rc
              and viol_d == viol and h3d.get("status") == h3.get("status"), json.dumps(h3d)[:400])
        # a condition H3 cannot parse makes it UNVERIFIED, never PASS
        mapu = copy.deepcopy(mapo)
        head = mapu["variants"]["button--primary"]["parts"]["head"]
        head["default@print-only"] = head.pop("default@max:breakpoint-sm")
        rc, out = run(root / "h3-unverified", v1o, dx, cmap=mapu)
        h3 = cons_of(root / "h3-unverified").get("checks", {}).get("H3", {})
        check("an unparsed condition makes H3 UNVERIFIED and exits 1", rc == 1 and h3.get("status") == "UNVERIFIED"
              and h3.get("unverified") == [{"variant": "button--primary", "conditions": ["print-only"]}], json.dumps(h3)[:400])

        # added states: only an inverse focus ring is added; it is measured on the surfaces that use it
        inv = copy.deepcopy(DECISIONS)
        ic = inv["decisions"]["color"]
        ic["semantics"] = [x for x in ic["semantics"] if x.get("origin") != "added"] + [
            {"name": "color-focus-ring-inverse", "from": "surface-alt", "usage": "focus on the alternate surface", "origin": "added"}]
        ic["focus_inverse_surfaces"] = ["color-surface-subtle"]
        inv["decisions"]["shadow"] = {}
        rc, out = run(root / "inverse-ring-only", V1, inv)
        st = cons_of(root / "inverse-ring-only").get("checks", {}).get("added_states", {})
        rows = [(r["surface"], r["ring"], r["pass_outer"]) for r in st.get("rows", [])]
        check("an added inverse ring alone is measured and a failing ratio fails", rc == 1
              and rows == [("color-surface-subtle", "inverse", False)], json.dumps(st)[:300])
        ic["focus_inverse_surfaces"] = []
        rc, out = run(root / "inverse-ring-no-surface", V1, inv)
        st = cons_of(root / "inverse-ring-no-surface").get("checks", {}).get("added_states", {})
        check("an added ring with no surface to verify it on fails", rc == 1 and st.get("no_surface") == ["focus_ring_inverse"],
              json.dumps(st)[:300])

        # scale caps come from the decisions file: a nine-step control scale the plan allows
        v1s = copy.deepcopy(V1)
        steps = [24, 28, 32, 36, 40, 44, 48, 52, 56]
        v1s["size"]["tokens"] += [tk("size-c%d" % n, "%dpx" % n) for n in steps if n != 40]
        ds = copy.deepcopy(DECISIONS)
        ds["decisions"]["size"]["classes"].update({"size-c%d" % n: ["control", "control %d" % n] for n in steps if n != 40})
        ds["decisions"]["size"].update({"control_scale": steps, "max_steps": {"control": 9, "icon": 8}})
        rc, out = run(root / "nine-steps", v1s, ds)
        check("a nine-step control scale passes when the plan sets nine", rc == 0, out[-300:])
        ds["decisions"]["size"]["max_steps"]["control"] = 8
        rc, out = run(root / "nine-steps-capped", v1s, ds)
        check("the same scale fails against a cap of eight", rc != 0 and "max_steps.control = 8" in out, out[-300:])

        nons = copy.deepcopy(DECISIONS)
        del nons["decisions"]["note_syntax"]
        rc, out = run(root / "no-note-syntax", V1, nons)
        check("missing note_syntax stops with a message", rc != 0 and "note_syntax" in out, out[-300:])

    def body_e2e(root: Path):
        ps = load_module(PKG / "selftest.py", "package_selftest_fixture")
        p1 = root / "p1" / "pkg"
        p1_contrast = {k: v for k, v in ps.CONTRAST.items() if k != "added_states"}
        ps.make_package(p1, ps.TOKENS_P1, ps.CMAP_P1, p1_contrast)
        sc = p1 / "scripts"
        tok = p1 / "tokens.json"
        for args in ([sc / "build_tokens.py", "--tokens", tok, "--css", p1 / "tokens.css", "--dtcg", p1 / "tokens.dtcg.json"],
                     [sc / "build_tailwind.py", "--tokens", tok, "--out", p1 / "tailwind" / "theme.css"],
                     [sc / "build_contrast.py", "--tokens", tok, "--contrast", p1 / "data" / "contrast.json"]):
            rc, out = py(args)
            check("e2e P1 %s" % Path(args[0]).stem, rc == 0, out[-300:])
        rc, out = py([sc / "check_package.py", "--stage", "data", "--package", p1, "--allow-orphans"])
        check("e2e P1 package check", rc == 0, out[-400:])

        work = root / "p2-run"
        write(work / "usage.json", E2E_USAGE)
        write(work / "decisions.json", E2E_DECISIONS)
        rc, out = py([HERE / "rationalize.py", "--tokens", tok, "--component-map", p1 / "components" / "component-tokens.json",
                      "--contrast", p1 / "data" / "contrast.json", "--usage", work / "usage.json",
                      "--decisions", work / "decisions.json", "--out-consolidation", work / "consolidation.json",
                      "--out-lineage", work / "lineage.json"])
        check("e2e rationalize reads the P1 package directly", rc == 0, out[-600:])
        if rc != 0:
            return
        cons = json.loads((work / "consolidation.json").read_text(encoding="utf-8"))
        h1 = cons["checks"]["H1"]["pairs"]
        check("e2e contrast pairs read from source_pairs with computed ratios",
              len(h1) == 1 and h1[0]["v1"] == 15.91 and h1[0]["status"] == "ok", json.dumps(h1))

        p2 = root / "p2" / "pkg"
        tokens2, cmap2, contrast2 = p2_package(cons, ps.CMAP_P1, p1_contrast)
        ps.make_package(p2, tokens2, cmap2, contrast2)
        write(p2 / "base.css", E2E_BASE_CSS)
        sc2 = p2 / "scripts"
        tok2 = p2 / "tokens.json"
        for args in ([sc2 / "build_tokens.py", "--tokens", tok2, "--css", p2 / "tokens.css", "--dtcg", p2 / "tokens.dtcg.json"],
                     [sc2 / "build_tailwind.py", "--tokens", tok2, "--out", p2 / "tailwind" / "theme.css"],
                     [sc2 / "build_contrast.py", "--tokens", tok2, "--contrast", p2 / "data" / "contrast.json"]):
            rc, out = py(args)
            check("e2e P2 %s" % Path(args[0]).stem, rc == 0, out[-300:])
        rc, out = py([sc2 / "check_package.py", "--stage", "data", "--package", p2])
        check("e2e P2 package check (no --allow-orphans)", rc == 0,
              "\n".join(ln for ln in out.splitlines() if ln.startswith("[FAIL]"))[-800:])

    if a.keep:
        d = Path(a.keep) / "rationalize-selftest"
        if d.exists():
            shutil.rmtree(d)
        body(d)
        body_e2e(d / "e2e")
    else:
        with tempfile.TemporaryDirectory() as d:
            body(Path(d))
            body_e2e(Path(d) / "e2e")
    fails = [r for r in results if not r[0]]
    for ok, name, detail in fails:
        print("FAIL %s\n  %s" % (name, detail.replace("\n", "\n  ")))
    print("rationalize selftest: %d/%d passed" % (len(results) - len(fails), len(results)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
