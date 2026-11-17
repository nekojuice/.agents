# Phase 2: Rebuild

Rebuild the raw snapshot into a cross-project design system: three token tiers, components merged by function, a lineage back to every original value, and the hard rules H1–H5 as proof that nothing drifted. The Phase 1 package is the input, not the end. Start only after the baseline is frozen (SKILL.md, Gates).

## Contents

- [Fidelity criterion](#fidelity-criterion)
- [Inputs](#inputs)
- [Decisions file](#decisions-file)
- [Token tiers](#token-tiers)
- [Color](#color)
- [Type](#type)
- [Spacing, radius, shadow, size](#spacing-radius-shadow-size)
- [Components](#components)
- [Hard rules](#hard-rules)
- [Layered packaging](#layered-packaging)
- [Outputs](#outputs)

## Fidelity criterion

Brand fidelity and "do not carry degraded design" look opposed. Apply this split:

| Aspect | Rule |
| --- | --- |
| Values (color, size, spacing, radius, shadow, type, duration) | Keep the original value. Contrast below WCAG is recorded as fact, never recolored |
| Element structure and interaction mechanism | When an element's form is a late patch or degrades the established pattern, do not carry it. Rewrite appearance and interaction needs with a common accessible pattern (for example the WAI-ARIA Authoring Practices Guide) |
| Legacy interactive components | Never reuse the legacy DOM or script. Keep the appearance values; take structure, keyboard behavior and ARIA from the pattern |
| Record | Every replacement goes into the DESIGN.md version log: element, reason, replacement pattern, values kept |

Do not add states or accessibility colors the source never had; unbranded states stay residue unless the user decides otherwise.

## Inputs

| Input | Use |
| --- | --- |
| Phase 1 `tokens.json` (layered list schema, every entry `origin: source`; residue values are semantic entries named `residue-*`) | Values to rationalize; residue values leave through decisions `color.removed` or get a role |
| Phase 1 component map (package map schema) | Usage per component; same-variant type order (H3); reference check (H5) |
| Phase 1 contrast data (`build_contrast.py` output) | Regression baseline (H1); unrounded ratios are recomputed from the token values |
| Token candidates with `used_by` and declaration counts (P1 research data) | Usage: component count first, declaration count second; `rationalize.py` copies `used_by` from them onto Phase 1 tokens, which do not carry it |
| Forbid list (`[substring]`, `[class]`) | Collision check for new component ids, pattern ids, asset names |
| Decisions file | Human judgment; see below |

## Decisions file

Put judgment in a run-local decisions file; scripts hold only algorithms.

- Colors: a role draft per original color (`<category>-<role>`, e.g. `text-default`, `surface-accent-subtle`, `border-subtle`); merges of very light surfaces; alpha base and percentage; the semantic list, each anchored on one original token (`from`); the component token list.
- Type: each style assigned to a role cell `<role>-<lg|md|sm>`; breakpoint styles as `{of, when}`; emphasis styles listed apart.
- Sizes: each size token in one class: control, icon, layout, component, project, structural.
- Components: the new catalog (neutral kebab-case ids, variants, sizes, states, parts), the pattern registry, and the target list of every original variant (component × variant, pattern, or removed; 1:N allowed with roles). A Phase 1 component without variants and a Phase 1 pattern with parts are each one original unit keyed by their id; list them too.
- Note markers: `note_syntax` (required) gives the `open`, `close`, `sep` and `merged` markers the run's size-class notes and `used_by` entries use, for example `{"open": "(", "close": ")", "sep": "/", "merged": "merged"}`. Use the markers the notes are actually written with.
- When the user delegates design decisions to the agent, write each decision with its reason into the plan's decision table and keep it reversible.

The Phase 1 package feeds this step directly: pass its `tokens.json`, `components/component-tokens.json` and `data/contrast.json` as they are. `rationalize.py` detects each input's shape and also still reads the older per-variant map and `pairs` contrast file (`--help`). H2 takes surfaces from the role drafts that start with `surface` when the Phase 1 colors carry no `group`.

The decisions file is `<run>/data/decisions.json`; the lineage is a separate output file, `<run>/data/lineage.json`, which carries a copy of the decisions. Run twice and compare hashes; `--check` must pass.

```text
python -I scripts/rebuild/rationalize.py --tokens <p1-pkg>/tokens.json --component-map <p1-pkg>/components/component-tokens.json --contrast <p1-pkg>/data/contrast.json --usage <candidates.json> --decisions <run>/data/decisions.json --out-consolidation <run>/data/consolidation.json --out-lineage <run>/data/lineage.json [--forbid-list <forbid-list.txt>] [--check]
python -I scripts/rebuild/selftest.py
python -I scripts/rebuild/colormetrics.py selftest | lab <color>... | de <color> <color> | contrast <fg> <bg>
```

The consolidation output is internal run data, not markup. Its components list part keys and state names only, never class names; its `v1_*` / `v2_*` / `rep_v1` keys mean "snapshot" and "rebuilt" only; never copy them into the package. The component map and the P2 specs are written in utility notation (Layered packaging, item 4).

`rationalize.py` exits 1 when any check (H1–H5, `added_states`, ID forbid list, variant coverage) fails; it still writes both outputs so the failures can be read. It fails at once, producing nothing, when a semantic resolves to a demoted value or an orphan. Treat such a failure as evidence that the rules, applied literally, would distort the result; resolve with the smallest deviation, record it as an item to decide, and do not invent a new rule. Write mid-plan rulings back to the plan's revision notes.

## Token tiers

| Tier | Holds | May reference |
| --- | --- | --- |
| primitive | Raw scales: palette, alpha, font size, line height, weight, letter spacing, family, space, radius, size, duration, easing, breakpoint | Nothing |
| semantic | Roles: color, radius, elevation, focus | Primitives; a composite (shadow) may reference semantic colors |
| component | Values one component needs beyond semantics | Semantics or primitives; tokens of the same component may reference each other |

Any other cross-tier reference fails the package check.

## Color

1. Usage = number of components; ties by declaration count, then by value.
2. Within a role: the most used value is the center; absorb values within ΔE2000 ≤ 2; no chaining. Very light surfaces (L\* > 90) never merge automatically, only through the decisions file.
3. Across roles: merge only when members share a value or representatives differ by ΔE < 1.
4. Families: C\* below a threshold is neutral; named hue ranges, defined in CIELAB; others by 30° bins. Pure white and pure black are special entries.
5. Step = round((100 − L\*) / 5) × 50, limited to 25–950. Same family and step: same role merges; different roles demote the later one to component tier.
6. Alpha colors skip ΔE; name them `palette-<base>-alpha-<pct>`; shadows reference the primitive.
7. In the component layer, merged variants take the representative value; framework-default near-duplicates may use the same-role semantic; a component token pointing at the same primitive as a semantic of its class becomes that semantic. Delete primitives nobody references (H5).

Three CIELAB traps:

| Trap | Handling |
| --- | --- |
| CIELAB hue differs from HSL hue (pure red sits near 40°) | Define hue ranges with CIELAB values |
| C\* alone calls a light but tinted surface neutral | Use a low-chroma hue override in the decisions file |
| L\* has low resolution near white; light surfaces collide on one step | Give special entries to white and black; give a collision its own intermediate step; never demote it to a component-layer original |

## Type

1. Round non-integer px to the nearest integer.
2. Roles follow a common type-scale convention (display, headline, title, body, label, plus caption), each with lg, md, sm.
3. A cell's size is its most used size; line height, weight, letter spacing and family are the cell's mode; members that differ become component-layer overrides.
4. The representative style's narrow variant becomes the style's `breakpoints` (mobile first: base is the small-screen value); other breakpoint styles become component-layer `@min` switches at the nearest existing size.
5. Text line heights collapse to the unitless values the decisions file lists (tolerance `line_height_threshold`); px line heights that set control height become `size-control-*`.
6. A "used by at least two styles" threshold would merge single-use display sizes; the role ladder (H3) protects them.
7. After merging, recompute contrast with the new size and weight: a color that did not change can still move from large to normal text and fail.

## Spacing, radius, shadow, size

| Family | Rule |
| --- | --- |
| Spacing | Collect px values that occur and are multiples of 4, plus a 2px half step; convert em by the type size in place; split shorthands; nearest step, ties go up; deviations over 4px are listed as exceptions. Controls use `min-height`; their vertical padding is not carried |
| Radius | Round, merge within ±1px; names none, xs, sm, md, lg, xl, pill, full |
| Shadow | Outer shadows become `elevation-1..n`; focus becomes `focus-ring`; the rest goes to components |
| Size | Control and icon each take at most the steps `size.max_steps` sets (required in the decisions file, from the plan's threshold table; line-height controls count toward control), at nearest values (a third column may pin alignment so one size does not vary by variant); layout stays; component sizes go to the component tier; project sizes are generalized when they can be described neutrally, else removed |
| Breakpoint | Original max-width conditions shift by 1px when rewritten as min-width; merge stray breakpoints into the nearest standard one |

## Components

- Merge by function, not by page. One component carries three axes: variant (purpose), size, state.
- Give components and patterns neutral ids; check them against the forbid list.
- Patterns (page sections composed of components) live in a registry with id, name, components, anchor, preview and spec file.
- Every original variant maps to a target or to "removed"; the lineage records it.
- Content that varies per flow (step names, panel widths) is recorded with all observed cases, not one.
- Apply the fidelity criterion to every interactive component before writing its parts.

## Hard rules

The rationalize script writes these to `checks` and exits 1 on any failure; a failure sends you back to the decisions file.

| Rule | Computation |
| --- | --- |
| H1 contrast does not regress | Recompute every original pair with new tokens and the pair's own opacity; re-judge large or normal text by the new size and weight; a passing pair must still pass. A pair whose foreground or background has no new value fails unless `h1_excluded_pairs` lists it with a reason |
| H2 surfaces stay distinct | Opaque surface colors with different role drafts must keep different new values |
| H3 type order holds | Within each role lg > md > sm strictly; within one original variant, among the sizes in effect at each checked width and context (`@ctx:<name>`) combination, per part, state and property (an active override replaces only its own declaration; base declarations still apply when a context is on), a smaller style stays strictly smaller. A condition the check cannot parse makes H3 UNVERIFIED, which fails. A global "never invert" check only produces noise |
| H4 control box height | New control height differs from the original by less than 4px |
| H5 no orphan primitive | Color primitives referenced by a semantic or component token; scale primitives referenced by a part of a kept variant |

Added states (origin `added`): only the states the decisions add are checked, and none added means nothing to check. Focus ring against every surface where a focusable element can sit; input error border and checked color against surfaces that hold controls; threshold 3:1; on dark surfaces use an inverted ring. A token named in `state_check_tokens` that does not exist fails the check. Also check new ids and file names against the forbid list, and that every original variant has a legal target. Box heights here are computed from tokens; confirm them in a browser during verification.

## Layered packaging

1. `tokens.json`: every family `{"tokens": [...]}`; type has `families`, `scales`, `groups[].styles[]` with mobile-first `breakpoints`. Each entry: `name`, `value`, `tier`, `origin`, `usage`; component tier also names its component. Aliases are `{name}`; composites embed `{name}`. Values only: no source paths, old names or lineage. Reserve `themes` (one theme now). Conditional sizes become two tokens (base and `-narrow`), switched by the map with `@min:<bp>`.
2. Usage sentences are composed by script from references and contrast results: primitives (step, referencing tokens, ratio on white), semantics (purpose, surfaces with ratios, lowest accepted, components), component tokens (component, contrast, users).
3. Component map per component: `anatomy` (parts), `anchor` (`<component>--<variant>`), `semantic_states`, `parts` → state key → property → value, `variants` (key = anchor), `sizes`, `compound`. Value forms: `{token}`, `{tokens}`, `{literal, note}`, `{template}`, `{asset}`; `typography` expands to five font properties. State key: `<state>[+<state>][::<pseudo>][@min:<bp>][@has:<part>]`; a host field says whether the state sits on the part, the root, an ancestor part, or a part inside the root through `:has()`. Top level: `patterns`, `layout`, a `literals` registry, preview rules.
4. Notation: the package is delivered in Tailwind notation (SKILL.md, Iron rules 6): specs and preview use utilities, and the map stores no legacy-style class names or forced-state classes.
5. Generate `tokens.css` and a DTCG export from `tokens.json`; recompute contrast; generate twice and compare hashes.
6. DTCG 2025.10 has no type for %, em, vh or keywords: emit those without `$type` and list them under root `$extensions`; never force a conversion.
7. Breakpoints are literal px in output; `@media` cannot read variables. States that depend on `:has()` (for example a parent styled by a child's state) need a fallback on the root for browsers without it.
8. Contrast file is definition and result at once: keep definition fields, recompute value fields (`--check` for idempotence). Original pairs keep the old size class and are recorded as they are.
9. Assets: brand layer only, copied under neutral names; the old-to-new name table stays in the run.
10. Run the data stage of `check_package.py` now and the full stage after authoring, with the approved pinned Tailwind CLI (`--tailwind-cli`); the full stage fails without it when `tailwind/` exists. Give it the forbid list; without one the forbid item reports SKIP.

```text
python -I scripts/package/build_tokens.py --tokens <pkg>/tokens.json --css <pkg>/tokens.css --dtcg <pkg>/tokens.dtcg.json [--check]
python -I scripts/package/build_contrast.py --tokens <pkg>/tokens.json --contrast <pkg>/data/contrast.json [--check]
python -I scripts/package/check_package.py --stage data|full --package <pkg> --forbid-list <run>/forbid-list.txt [--tailwind-cli <path>]
```

The package's `scripts/` are copies of this skill's `scripts/package/`, never edited inside a run. A check that disagrees with the notation rules (for example flagging a function wrapper such as `drop-shadow(var(...))` as an unregistered literal) blocks correct output: report it as a finding for this skill. The fix is made in this skill's `scripts/package/`, then copied into the package again.

Generation order matters in emitted styles: the disabled state comes last in a component, after variant hover and pressed states; variant and size rules on a shared part override by output order.

## Outputs

| Output | Content | Lives in |
| --- | --- | --- |
| Consolidation JSON | `primitives`, `semantics`, `type`, `component_tokens_draft`, `components`, `patterns`, `assets`, `gaps`, `removed`, `checks` | Run |
| Lineage JSON | `decisions`; per original color, style, space, radius, size, shadow, motion and variant: new name, new value, deviation, reason | Run only, never in the package |
| Conclusion note | Ladders, semantic table, catalog and variant map, patterns, removals, asset map, hard-rule results, exceptions, items to decide | Run |
| Package | `tokens.json`, `tokens.css`, `tokens.dtcg.json`, component map, `data/contrast.json`, `data/gaps.json`, assets with README | Staging, then swap |
