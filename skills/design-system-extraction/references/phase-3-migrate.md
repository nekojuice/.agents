# Phase 3: Migrate

Move the web layer from `<legacy framework>` notation to `<utility framework>` notation, utility first. Token values do not change; only the way they are expressed. Phase 3 is only for an existing layered package whose web layer is not yet in utility notation; a Phase 2 package is already delivered in Tailwind notation. Freeze the baseline first (SKILL.md, Gates).

## Contents

- [Choose the target notation](#choose-the-target-notation)
- [Residue inventory](#residue-inventory)
- [Tokens to theme](#tokens-to-theme)
- [Entry stylesheet and layers](#entry-stylesheet-and-layers)
- [Component map to utilities](#component-map-to-utilities)
- [Static states in previews](#static-states-in-previews)
- [Whitelist and arbitrary values](#whitelist-and-arbitrary-values)
- [Checks](#checks)
- [Pitfalls](#pitfalls)

## Choose the target notation

| Target | Class rule | Preview state | Mechanism check |
| --- | --- | --- | --- |
| Utility CSS (default; Tailwind is the notation, SKILL.md, Iron rules 6) | No legacy mechanism classes in specs or previews; theme names come only from tokens | Marker attribute on the element | Scan for structural component classes and forced-state classes: 0 hits |
| Non-utility CSS (option) | Every class in new CSS and markup carries the brand prefix; prefixing is more reliable than listing forbidden words | Forced-state class next to the matching pseudo-class in one rule | Scan for unprefixed classes |

Only a framework the user names is a target (SKILL.md, Iron rules 5); cross-framework portability comes from shared CSS variables, not from per-library mappings.

## Residue inventory

Inventory before rewriting. Legacy residue hides in values, tokens and data structures, not only in class strings; a class-string scan on an already cleaned version returns 0 and proves nothing.

Scope: component and pattern specs, `tokens.json`, the component map, generated component CSS, base CSS, DESIGN.md, preview fragments and page, and any skill text or script that references these mechanisms.

| ID | Category | Judged as | Action |
| --- | --- | --- | --- |
| `brand-value` | Brand appearance value | Visible color, width, type, spacing, radius, shadow, even when equal to a `<legacy framework>` default | Keep the value and its token; stop describing it as a framework mapping |
| `mechanism-bound-value` | Appearance value bound to a mechanism element | Serves only one framework structure (for example em spacing of a dropdown arrow) | Keep while the element stays in the spec; delete only with the element, and list the deletion in the DESIGN.md version log |
| `motion` | Motion duration | Framework transition values (collapse, slide change) | Keep as duration and easing tokens, referenced by the spec's transition row |
| `mechanism` | Mechanism | Structural component classes, forced-state classes, plugin data attributes, script component DOM, collapse markup, override tables | Remove; replace with anatomy + variant + ARIA |

Steps:

1. Scan: `residue_scan.py` counts per file structural parts and modifiers, forced-state classes and framework words, and lists mechanism fields in the component map.
2. Inventory values by hand against a table of framework defaults: brand values equal to a default, values that serve only a framework element, transition values. Record location and content.
3. Decide per row with the table. The action and the "location after action" are both required; the location names file and section, relative to the skill root.
4. Rewrite: mechanism fields become semantic fields (`anatomy`, state → variant map); specs become parts + appearance + states + example notation; DESIGN.md gets a version log entry listing every deletion.
5. Verify: `residue_ledger_check.py` confirms each row has a category ID, an action and a location after action, that the location file exists, and that a `delete-file` row's file is gone.

```text
python -I scripts/migrate/residue_scan.py --package <pkg> [--prefix <prefix>] [--framework-words <regex>] [--json <out>]
python -I scripts/migrate/residue_ledger_check.py <ledger.md> --package <pkg> [--section "## <heading>"] [--categories "<id>,<id>,..."] [--delete-disposition <action>] [--ignore-prefix <rel-prefix>]...
```

Ledger columns come from `assets/residue-ledger.template.md`. The check reads the six-column table under `## Ledger`, accepts the category IDs `brand-value`, `mechanism-bound-value`, `motion` and `mechanism`, and treats the action `delete-file` as "file deleted". A ledger that translates the heading, IDs or action word passes them with `--section`, `--categories` and `--delete-disposition`. "Equal to a framework default" never means "mechanism": a value the user can see stays.

## Tokens to theme

`build_tailwind.py` writes `tailwind/theme.css` (`@theme inline`) from `tokens.json`; the file is generated, never edited.

1. Reset defaults first: set `--color-*`, `--font-*`, `--text-*`, `--font-weight-*`, `--leading-*`, `--tracking-*`, `--radius-*`, `--shadow-*`, `--ease-*`, `--breakpoint-*`, `--container-*`, `--text-shadow-*` to `initial`, so stock names (a default palette step, a default radius, a default text size) stop compiling.
2. Brand names only:
   - Semantic colors become `--color-<name without color->`. Primitives and component tokens stay out of the theme; reach them with `bg-(--<prefix>-...)`.
   - Spacing: `--spacing: var(--<prefix>-space-4)`; allowed steps = each space token's px ÷ 4.
   - Type styles become `--text-<role>-<size>` with `--line-height`, `--font-weight`, `--letter-spacing` sub-values; families pair with `font-*`.
   - Families, weights, line heights, tracking, radius, shadows (the focus ring is `--shadow-focus`), text shadows, easing and layout widths keep their names without the family prefix.
   - Breakpoints are literal values (media queries cannot read `var()`); the check script compares them with `tokens.json`.
   - Durations get no namespace; write `duration-(--<prefix>-duration-<n>)`.
3. Values always point to `var(--<prefix>-...)`; the prefix comes from `tokens.json` `css.prefix`. Breakpoint variants come from the token names: `breakpoint-<step>` becomes `<step>:`; the generator stops with an error when breakpoint tokens exist but none can be mapped, and writes an empty breakpoint section for a brand without breakpoints. Layout widths come from `size-layout-*` tokens by default. Brand naming it cannot infer (breakpoints named otherwise, shadow and text-shadow names, container prefixes, the spacing token) comes from the optional `tokens.json` `tailwind` block; keys and defaults: `build_tailwind.py --help`.
4. Legacy variable aliases: when the consuming product still reads the source's old variable names, hand the alias lines (`--<old-name>: var(--<prefix>-<new-name>);`, one per old name, built from the lineage's old-to-new table) and the replacement table to the product's owner; they stay out of the reusable package because old names are project content. Write them into the product only when the plan names the authorized path and who writes it. List the hand-off in the version log; the aliases are removed once the product no longer reads the old names.
5. Run `theme_name_diff.py` against the framework's default theme: it lists names the brand theme shares with the defaults and whether the values differ. Publish the "same name, different value" rows in the package's DESIGN.md usage section, so readers never assume a stock meaning.

```text
python -I scripts/package/build_tailwind.py --tokens <pkg>/tokens.json --out <pkg>/tailwind/theme.css [--check]
python -I scripts/migrate/theme_name_diff.py --theme <pkg>/tailwind/theme.css --framework-theme <framework default theme.css> --tokens-css <pkg>/tokens.css [--rem-px 16]
```

## Entry stylesheet and layers

Order in `tailwind/index.css` (template in `assets/deliverable-skeleton/tailwind/index.css`):

```css
@import "tailwindcss" source(none);
@import "../tokens.css" layer(base);
@import "./theme.css";
@import "../base.css" layer(base);
@source "<explicit content globs>";
@source not inline("<utility name that collides with a brand layout name>");
```

- `source(none)` makes output independent of the working directory; list every content path with `@source`.
- Exclude built-in utilities whose names collide with brand layout names with `@source not inline(...)`.
- Base and Preflight: delete resets Preflight already does; keep only brand rules. Put generated type classes in the base layer so utilities win over them.

## Component map to utilities

Phase 2 should already write the map in a form that emits utilities directly. When a run still holds a legacy intermediate notation, write a run-local converter on this algorithm; it does not ship with the skill.

1. Expand rules: shorthands to longhands (padding, margin, inset, the three border families, gap, overflow, flex, transition, outline); `typography` to five properties.
2. For each element, collect the rules of every root, part and modifier it belongs to; compute the winner at each condition point (breakpoint × state set × pseudo-element) by specificity and order.
3. Emit only the utilities needed, in the framework's application order: more variants later, larger breakpoints later. Explicit line-height, weight and tracking utilities beat the sub-values of a text style, so when a later condition returns to the style's own value, emit it explicitly (for example `leading-(--<prefix>-<style>-line-height)`).
4. Map states to variants:

| Source state | Variant |
| --- | --- |
| hover, pressed, focus | hover, active, focus-visible |
| disabled | disabled plus aria-disabled |
| invalid, selected, current | aria-invalid, aria-selected, aria-[current=page] |
| checked, expanded, complete | checked, aria-expanded, data-complete |
| read only, placeholder, first, last | read-only, placeholder, first, last |

5. A state carried by another element uses a named group (`group/<name>` on the host, `group-<variant>/<name>:` on the child); "root contains a part in a state" uses `group-has-<variant>/<name>:`.
6. Structural values without a utility (percentage offsets, border triangles, `calc()`) use arbitrary values; they may hold no color and only lengths registered as structural in the map.

## Static states in previews

- Utility target: previews show a state by emitting that state's values as the element's defaults and marking the element with a marker attribute (`data-preview-state="<state>"`). Spec examples use the live, non-forced version, so a display device never becomes the norm.
- Non-utility target: use forced-state classes (`.<prefix>-is-<state>`) in the same rule as the pseudo-class; an ancestor carrying the class applies it to child parts.

## Whitelist and arbitrary values

- Theme-type utilities must name something defined in `theme.css`.
- Arbitrary values contain no color and no unregistered length; spacing uses allowed steps only.
- When the run's forbid list contains a class that equals a utility name, the worker does not edit the list: use the equivalent arbitrary property (for example `[text-align:center]`) and report it; the orchestrator decides whether to move the word to `[allow]`.

## Checks

| Item | How |
| --- | --- |
| Theme in sync | Regenerated `theme.css` is byte-identical; breakpoint literals equal `tokens.json` |
| Utilities exist | Every class in specs and previews has a selector in the compiled CSS (unescape CSS selectors first) |
| Whitelist | Theme utilities defined; arbitrary values legal; spacing steps allowed |
| Appearance unchanged | Old and new previews with the same DOM, element-by-element `getBoundingClientRect` with `scripts/verify/boxdiff.py`; explain each difference, first excluding Preflight effects (list padding, button padding, table border collapse) |
| Tokens unchanged | Regenerated token CSS and DTCG are byte-identical to the previous version except descriptions and version |
| Mechanism gone | Mechanism scan in specs and previews is 0 (preview frame classes excepted) |
| Ledger | Every row handled; an independent verifier samples rows |

`check_package.py --stage full` runs the notation checks: utilities present in the compiled preview CSS, no structural or forced-state classes, theme whitelist, arbitrary-value limits, spacing steps. The package's `scripts/` are copies of this skill's `scripts/package/` and are not edited in the run. When the target needs a different check (for example dropping the brand-prefix rule when moving to utilities), report it as a finding for this skill; the change is made in this skill's script and copied into the package again.

## Pitfalls

- Compile a test page with representative utilities first to confirm type hints for variable values: font size `text-(length:--x)`, family `font-(family-name:--x)`, outline width `outline-(length:--x)`; plain `font-(--x)` is weight and `border-(--x)` is color.
- The CLI resolves `@import "tailwindcss"` from the entry file's folder; when the entry is outside the package folder, set `NODE_PATH` to that `node_modules`.
- The first line of compiled output is a license comment with a URL; exclude it from external-resource checks.
- Escaped selectors (`.<state>\:bg-<name>`) must be unescaped before forbid-list matching, or the state prefix is read as a forbidden class.
- Export the baseline with line-ending conversion off, or text and asset hashes differ (SKILL.md, Gates).
