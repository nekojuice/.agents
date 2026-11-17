# Phase 1: Extract

Produce a faithful, traceable snapshot of the brand as `<target frontend>` renders it today. CSS analysis is only the means of getting values; the deliverable is a design specification (SKILL.md, opening). Product code is read-only for the whole phase.

## Contents

- [Before starting](#before-starting)
- [Step map](#step-map)
- [Evidence fields](#evidence-fields)
- [Guards](#guards)
- [1 Style sources and stack profiles](#1-style-sources-and-stack-profiles)
- [2 Component and asset inventory](#2-component-and-asset-inventory)
- [3 Visual language and layout](#3-visual-language-and-layout)
- [4 Rule index and contrast tools](#4-rule-index-and-contrast-tools)
- [5 Component-level values](#5-component-level-values)
- [6 Render check](#6-render-check)
- [7 Token synthesis](#7-token-synthesis)
- [8 Packaging](#8-packaging)

## Before starting

Settle these with the user before any worker reads code; record them in the phase plan (`assets/plan-phase-1.md`).

| Item | Settle |
| --- | --- |
| Brand frontend | Which frontend carries the brand; which are excluded (for example a back-office area with its own look) |
| Targets | Only what the user names as a target. An example the user gives to illustrate a situation is not a target; when it is unclear, put it on the open list instead of promoting it (SKILL.md, Iron rules 5) |
| Deliverable | A design specification packaged as a brand skill; delivery location; assets copied, never linked |
| Reference format | A sample DESIGN.md and preview structure, if the user has one; take structure only, never brand content |
| Fidelity | Values stay as they are; contrast failures are recorded, not fixed (SKILL.md, Iron rules 2) |
| Locality | Everything runs locally; nothing is published; tool downloads need approval (SKILL.md, Iron rules 4) |

## Step map

| # | Step | Answers | Output |
| --- | --- | --- | --- |
| 1 | Style sources | Which stylesheets each page loads, in which order | `stack-profiles.json`, sources note |
| 2 | Inventory | Which components, variants, states and assets exist | `components.json`, inventory and asset notes |
| 3 | Visual language | Overall look, page anatomy, grid, wording and tone | Visual-language note |
| 4 | Rule index | Every rule with location, specificity, order | `css-index.json`, contrast tool self-tested |
| 5 | Component values | The winning value of each property per component | Component-value notes |
| 6 | Render check | Which code readings hold in a real browser | Render-check note, captures |
| 7 | Token synthesis | Which design roles exist and their candidate values | Token candidates (JSON + Markdown) |
| 8 | Packaging | The deliverable data layer | `tokens.json`, component map, data files, assets |

Run step 6 before step 7 when step 5 leaves many `runtime-dependent` values, so that synthesis uses measured values.

## Evidence fields

Every value carries three fields from step 5 onward.

| Field | Values |
| --- | --- |
| `source` | `measured: <path:line>` (winning declaration); `measured: render <page> @<width>`; `estimated: <basis>` |
| `resolved` | `direct`, `cascade`, `inherit`, `var`, `framework-default` |
| `confidence` | `static-certain`, `runtime-dependent`, `unresolved` |

Re-open the cited line once before using a value; component notes are often one or two lines off. `runtime-dependent` and `unresolved` items go to Known Gaps.

## Guards

- Resolve values per component, never by global frequency. Components often solve the same role differently; a single declaration can repeat a color a hundred times.
- Include layout in the property list: container alignment (`align-items`, `justify-content`), column widths, gaps. Components that look right can still sit in the wrong arrangement.
- When several versions of one framework load on a page, determine the effective one by rendering; without rendering, mark the affected values `runtime-dependent`.
- List pages that cannot be reached without input data, login or messages as Known Gaps. Never bypass them.
- When a verification route the agent devised itself (for example comparing a vendored file against an upstream original) finds nothing, decide, mark `estimated`, record a Known Gap, and move on; do not turn it into a user question (`need-ask-user-guide`). When the missing evidence is needed for a required verification, the worker returns it to the orchestrator as a blocker instead.
- Wording, text content and column widths that vary per page are marked "varies by page" with every observed case; never freeze one flow's text into a general rule.

## 1 Style sources and stack profiles

Group pages by the exact stylesheets they load and the order, so later steps resolve per profile instead of per page, and dead files never become specification.

Two source kinds exist; handle both.

| Kind | Load chain lives in |
| --- | --- |
| Server-rendered templates | Whatever the engine offers, for example layouts or template inheritance, includes, named blocks or slots, a default-layout setting, static-asset helpers |
| Bundled frontends (SPA or islands) | Bundler entry, CSS imports, component style blocks, and how the built files reach the page (generated HTML, a plugin, or a server that reads the bundler's manifest) |

Do:

1. List templates, excluding build output and package folders. Resolve each page's layout: explicit declaration, else the engine's default. Pages that opt out of the layout are standalone documents; their own head is the whole chain.
2. Record the layout load order: every stylesheet link, the condition around it, each block or slot pages fill, head or body position.
3. Record per page: links and style blocks inside the blocks it fills, links written directly in the body, style blocks carried by included templates. Blank out server and HTML comments first, keeping line numbers.
4. Resolve every reference: replace a root alias or asset helper with the web root, drop the query string, check the target exists. Restore variable hrefs from string assignments in the same file.
5. Judge reachability: scan route handlers for template returns (named and implicit). Templates nobody returns are unreachable. Note pages behind feature flags that are still reachable by URL.
6. Group by signature: layout + ordered existing files + position + condition. Page-level style blocks and component styles are page extras, not part of the signature. Same files in a different order is a different profile.
7. Bundled frontends: trace CSS imports and component style blocks from the entry, find how the output reaches the page and in which order, read the chunk split. Infer build and dev order separately. Never run a build to get artifacts; infer and mark `runtime-dependent`.
8. Classify profiles: main brand, variant (sub-brand, product line, white label), marketing, tool, leftover. Specify only the main brand; record variants as differences; record marketing and tool pages only.
9. Vendored framework files without an original to compare: check header version, size, line count, line endings, non-header comments, non-ASCII lines (local edits leave traces), root variables, rule count; list classes absent from another version of the same framework; sample core selectors against that version's defaults. Mark every conclusion `estimated`.
10. List inactive sources with the reason: unreferenced, missing target, unreferenced isolation output, misplaced copies, build-output copies.

Scripts (every path is an argument; exact flags: `--help`):

```text
python -I scripts/extract/stack_scan.py --list-presets
python -I scripts/extract/stack_scan.py --root <app-root> --webroot <web-root-rel> --ext <template-ext> --preset <name> [--preset-file <presets.json>] --out <scan.json>
python -I scripts/extract/framework_structure.py --css <vendored.css> [--reference <other-version.css>] [--probe "<selector>"]... --out <report.json>
```

Template syntax (layout, slot, include and comment patterns) comes from a preset; `--preset` is required. The only built-in preset is `plain-html`; describe any template engine in a preset file (keys: `stack_scan.py --help`; an invented example: `assets/stack-preset.example.json`) instead of editing the script. `stack_scan.py` evaluates only simple equality conditions; other conditions are kept verbatim for a human. Turning groups into the final profile file (labels, bundle entries, page classes) is manual.

Limits: conditions that depend on settings or session, helpers that build hrefs, redirect chains, dynamic template names, nested documents whose head lands in the body, runtime style generators (mark `unresolved`).

Output: `stack-profiles.json` with `profiles[]` (`id`, `label`, `files[]` with `path`, `position`, `order`, `condition`, `kind`, `ref`, `lines`), `pages`, `page_extras`, `page_meta` (`reachable`, `reached_by`, `category`). Note sections: summary, layout order, profiles, page map, page extras, reference verdicts, inactive sources, coexisting-variant facts, framework structure, Known Gaps.

## 2 Component and asset inventory

Answer "what exists, where, and when it changes appearance". Do not decide effective values here.

Components:

1. Index markup with `markup_scan.py`: class token counts with `path:line`, conditional class expressions, framework class and style bindings, inline styles, page style blocks, script writes (class toggles, style writes, image swaps, disabled toggles).
2. Read shared skeleton first: layout, includes, shared dialogs. Then sample at least one page per page type found in the source (for example landing, listing, detail, settings, multi-step form; the set varies by project).
3. Cross-check against stylesheets: styled with markup is a component; styled without markup is "CSS-only style", not a component; markup without styles is a component marked "no CSS".
4. Merge by visual purpose into components; markedly different structure or modifiers become variants. Tag scope: `main`, `<variant-scope>`, `marketing`.
5. Per variant record: root markup `path:line`, classes and their triggers, pages (search the variant's signature string; replace partials by the pages that include them), states that actually exist with trigger kind (`css`, `js`, `template`, `binding`), dynamic sources.
6. Print every cited line with a script and confirm it is the component root or the matching rule.
7. Write one sentence per component: what it looks like, where it is used.
8. Collect inconsistencies: several patterns for one purpose, states with no trigger, unused partials, duplicate ids.

Assets:

1. Run `asset_scan.py`: format, size, bytes, hash, references; CSS `url()` and data URIs with SVG colors.
2. Check how brand assets load (a logo may be a CSS background; favicon and share images live in the head). List broken references separately.
3. Classify by hand: brand, UI icon, key visual, advertising. Do not force other files (documents, PDFs) into the four classes.
4. Carry over only assets the main brand uses that contain no campaign text or project content; spare sizes of the brand mark are the exception. Advertising is excluded.
5. Record the color of single-color icons loaded as images (they cannot inherit text color); mark undecodable ones `unresolved`.
6. Icon fonts: record version and the glyph names used; do not copy the font. Special-purpose fonts are noted, not brand fonts.
7. Duplicate image folders: compare hashes and list only unique files.

```text
python -I scripts/extract/markup_scan.py --root <web-root> --views <dir>... --scripts <dir>... [--view-ext .<template-ext>] [--exclude <dir-name>...] [--template-expr <regex>] --out <markup.json>
python -I scripts/extract/asset_scan.py --root <web-root> --assets <dir>... --refs <dir>... --css <dir>... [--ref-ext .<template-ext>] --out <assets.json>
```

`markup_scan.py` reads `class` and JSX `className`; `className={...}` expressions are listed as dynamic. Class attributes holding a template expression (`--template-expr`, the engine's syntax; no default) are listed as conditional. The default skip list holds only generic build and package folders; `--exclude` replaces it, so add the project's build-output and vendored-library folders.

Limits: classes passed as helper arguments, id-styled components, whole-block conditional output (record as template state), regex false hits on stylesheet links and bundled third-party scripts, file names matched on path boundaries only, so duplicate folders holding the same file name share its references.

Output: inventory note grouped by component group, one variant table per component; `components.json` (`components[].variants[]` with `id`, `markup`, `classes`, `conditional_classes`, `pages`, `states`, `dynamic_sources`, `brand_scope`); asset note with the carry-over list.

## 3 Visual language and layout

Collect evidence for the medium-independent core of DESIGN.md. Output is described evidence, not a value table.

1. Read the layout: header, navigation, footer, global masks, conditional display.
2. List pages and type them by the categories the source has (for example landing, listing, detail, settings, multi-step form, marketing, tool; the set varies by project); find standalone pages; drop unreachable ones.
3. Read one or two representative pages per type top to bottom: block order, outer element (background), inner wrapper (width), columns, headings, button arrangement.
4. Count how many pages use each layout pattern to separate skeleton from one-offs.
5. Write how sections are separated on each page (background, spacing, rules), when the brand has a section rhythm, then find each surface's rule.
6. Look at images with an image-reading tool: scene, tone, composition, burned-in text, crops. Mark every description `estimated: <image path>`.
7. Classify icon use (raster, icon font, CSS-drawn, background) and how the selected state switches.
8. Extract wording with counted greps: button labels, validation messages, system and error messages, tone markers (form of address, sign-offs, recurring prefixes). Cite one `path:line` per representative sentence. Keep regulated or legal text separate; it uses a different register.
9. Repeat steps 3, 7, 8 briefly for variants; compare duplicated image folders byte by byte.
10. Write Known Gaps: no design source files, text in images, coexisting styles, order-dependent values, nothing rendered yet.

Every claim carries `measured: <path:line>` or `estimated: <basis>`. Wording must be findable in the source. Do not write subjective impressions as brand positioning.

Output sections: overall impression, key visuals and illustration, image and icon use, page layout and section rhythm, container and grid, shape and depth summary, wording and tone, variant differences, marketing variant, Known Gaps.

## 4 Rule index and contrast tools

Build one queryable index of every rule so step 5 can cite fixed data. The index never decides effective values.

1. Choose scan scope and exclusions; third-party folders are base reference only.
2. Tag sources by path: `third-party-base` (framework the project overrides), `third-party`, `known-inactive-*`; the rest is `project`. Tags classify; they do not decide effect.
3. Run the self-test; use the tools only when every case passes.
4. Run `index`; check `stats` (rules plus group at-rules roughly equal closing braces after comment removal) and read every warning.
5. Re-run with `--profiles` once profiles exist; read each profile's `found:false` list.

```text
python -I scripts/extract/selftest.py
python -I scripts/extract/css_index.py index --root <root> --include <dir>... --exclude <dir>... --tag "<glob>=<label>" [--markup-ext .<ext>] [--template-ext .<ext> --template-comment <regex> --template-expr <regex> --template-unescape <text>=<text>] [--fallback-encoding <codec>]... [--profiles <stack-profiles.json> [--root-alias <prefix>]] --out <css-index.json>
python -I scripts/extract/css_index.py query --index <css-index.json> --class <name> [--profile <id> | --page <page>] [--property <prop>] [--media <text>|none]
python -I scripts/extract/batch_query.py --index <css-index.json> --queries <queries.txt> --out <result.txt>
python -I scripts/extract/contrast.py <fg> <bg> [--base <opaque>] | --batch <pairs.json> --out <result.json>
```

Files are read as UTF-8; a file that is not UTF-8 stops the scan with its name until the project's legacy encoding is given with `--fallback-encoding`. Server template syntax is given with the `--template-*` options; there is no built-in engine.

Index facts: specificity follows Selectors Level 4 (`:where()` is 0; `:is()`, `:not()`, `:has()` take the largest argument); scoped component styles add one attribute; preprocessors are read as plain CSS with a warning; `@import` is recorded, not followed; inline styles are listed apart (they beat every sheet rule except `!important`).

Contrast facts: WCAG 2.x relative luminance; compare unrounded ratios; thresholds AA normal 4.5, AA large 3, AAA 7 and 4.5, non-text UI 3. Translucent colors composite background on `--base` (default white), then foreground on the result.

## 5 Component-level values

Key every value by component variant × profile × media × state. For each appearance property, find the winning declaration with the index, then record value plus the three evidence fields.

1. Write the appearance description of the component first, then its values.
2. Property list: color, background, border (width, style, color), radius, font family, size, line height, weight, letter spacing, padding, margin, width and height, shadow, opacity, transition, display and position, container alignment, column widths, gaps.
3. Use `query` per class; judge order, specificity, `!important` and media by hand.
4. Use `profile_diff.py` to see how two profiles differ for the same selector and media; use `sheet_residue.py` when two copies of one sheet load, to list declarations of the first copy the second does not override.
5. Mark as `runtime-dependent` anything set by script, template conditions, bindings, viewport, `var()` resolution, or em/rem conversion.

```text
python -I scripts/extract/profile_diff.py --index <css-index.json> --a <profile> --b <profile> [--class <name>]...
python -I scripts/extract/sheet_residue.py --index <css-index.json> --first <sheet> --second <sheet> [--grep <fragment>]...
```

Both compare identical selector text and media only; different selectors still need human judgment.

## 6 Render check

Upgrade code readings to measurements. Measurement is a check; the specification keeps design values.

1. Confirm authorization: which services may start, whether build output may be written, which interactions are allowed. Read the build target; if starting would install packages, stop and report. Start backend services only when a page needs them.
2. Start in the background; if the "listening" line is buffered, probe the port.
3. Probe candidate GET routes; record status and the template actually rendered. Exclude handlers that send messages, write data or call outside.
4. Set the viewport width, then reload; a hidden pane loads at width 0 and media queries may not re-evaluate.
5. Inject a measuring function: for a list of name → selector (pseudo-element, nth), read `getComputedStyle` fields and the bounding rect; omit defaults and body-equal font family.
6. Store one full capture per page at the first width; for others store differences only.
7. When a measurement disagrees, walk `document.styleSheets` (including matching nested rules) to list every rule that hits the element and declares the property.
8. States: hover through the tool's pointer, then confirm `el.matches(':hover')`; focus with `el.focus()` and accept only if `:focus` matches; `:visited` is unreadable, screenshot only.
9. Dialogs and hidden components: open them through the page's own method; fill placeholder text if layout needs it; submit nothing. `display:none` gives values, not layout.
10. Wait for images (`complete` and `naturalWidth > 0`) before measuring.
11. Fonts: list `document.fonts`, trigger loads, read resource entries; detect system fonts by comparing canvas text widths against a generic fallback.
12. Measure at least desktop, the tablet breakpoint exactly, and phone.
13. Screenshot only for layout questions, at low scale.
14. Clean up: delete temporary storage keys, reset emulation, stop every started service, confirm no listening port, confirm the product repo has no new changes.

```js
window.__measure = (spec) => spec.map(([name, sel, pseudo, i]) => {
  const el = document.querySelectorAll(sel)[i || 0];
  if (!el) return [name, '(not found)'];
  const cs = getComputedStyle(el, pseudo || null);
  const r = el.getBoundingClientRect();
  return [name, { rect: [r.x, r.y, r.width, r.height].map(Math.round), color: cs.color,
    bg: cs.backgroundColor, font: `${cs.fontSize}/${cs.lineHeight} w${cs.fontWeight}` }];
});
```

Record each item as consistent, inconsistent (correct the research value from the measurement) or not verifiable. Measured values become `measured: render <page> @<width>` with `static-certain`.

Limits: reduced-motion preference zeroes transitions (record `matchMedia` first); emulated width includes the scrollbar; system-font presence is local only, so the specification lists families and fallback order.

## 7 Token synthesis

Lift component values into design-role candidates. Keep every original value; propose a primary value with reasons.

1. List roles per family: color (brand, accent, text, surface, border, mask, semantic states), type, spacing, radius, shadow, size, breakpoint.
2. Collect rows "value, component, part, condition, source" per component.
3. Merge equal value and equal role into one candidate with `used_by`. Split one value serving two roles (for example a text color that is also a border color) into two candidates.
4. Name by role, not by color or number (`text-subtle`, `border-subtle`); scale families may use steps (`space-16`). Names match `^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$`; prefix non-color families with the family names the package scripts use (`space-`, `radius-`, `shadow-`, `size-`, `duration-`, `easing-`, `breakpoint-`). Check duplicates by script.
5. Count declarations as a secondary signal only: main-brand sheets, page blocks and inline styles; one declaration counts once; exclude framework bodies, variants, marketing.
6. Multi-value roles: list every value with components and counts; recommend a primary by component count, identity use (brand marks, icons), existing variable, contrast, variant sharing.
7. Contrast: every text color on every real background plus state-bearing non-text UI; note size and weight. Large text is at least 24px, or at least 18.66px with weight 700 or more (WCAG defines no 600; state the rule if 600 is adopted). Disabled controls are listed as exempt. Run the batch once.
8. Residue: framework defaults the project never branded (focus glow, input focus, selection, pressed color, native controls) go to a residue table, not brand tokens. Dead or overridden declarations go to "not adopted" with the reason.
9. Variants: list only values that differ from the main brand, pointing to the matching main token.
10. Write one data file; generate JSON and Markdown tables from it.

## 8 Packaging

Turn candidates into the data layer every later author reads instead of the research notes. The snapshot uses the same layered package schema as Phase 2, so the same scripts build and check it; it stays a snapshot because nothing is merged, renamed or added.

1. `tokens.json` in list schema (each family `{"tokens": [...]}`; type has `families`, `scales`, `groups`). Each entry has `name`, `value`, `tier`, `origin`, `usage`; a component-tier entry also names its `component`. Every entry is `origin: source`. Research fields (`source`, `confidence`, `used_by`, `used_by_note`, declaration counts) stay in the token candidates in the run, where Phase 2 reads them. Top level: `css.prefix` and the other configuration blocks below.
2. Assign `tier` without merging or deleting any original:

   | Snapshot value | `tier` | Note |
   | --- | --- | --- |
   | Recommended value of a role | `semantic` | Role name; the literal value, no alias yet |
   | Coexisting original one component uses | `component`, with `component: <id>` | Usage ends "component-specific; primary is `<name>`" |
   | Unbranded residue (focus glow, selection, pressed color, native controls) | `semantic`, named `residue-<role>` | Usage "unbranded residue, do not use in new work"; one value per token |
   | Scale step (space, radius, size, duration, easing, breakpoint, type scales, font stacks) | `primitive` | Type styles are `semantic` and reference the scales |

   Primitives nothing references yet are expected in a snapshot; the package check reports them with `--allow-orphans` and Phase 2 removes them (H5).
3. Usage states numbers only ("on `<surface>` N:1, below WCAG 4.5"); never "fails" or "must fix".
4. Color values are lowercase `#rrggbb`, or `rgb()` / `rgba()` for translucent colors: expand `#rgb`, write `#rgba` and `#rrggbbaa` as `rgba()`. The value is the same; only the notation is normalized.
5. Fonts carry no file ("not bundled, loaded by the project"); icon font families stay with the required version.
6. Durations and easings are `duration-*` and `easing-*` tokens; their `runtime-dependent` notes stay in the research data.
7. Component map in the package map schema (`references/phase-2-rebuild.md`, Layered packaging, item 3): per component `anatomy`, `anchor`, shared `parts`, and `variants` keyed `<component>--<variant>`, one per main-brand variant; `parts` → state → property → value. Value forms: `{token}`, `{tokens}` (shorthand order, `0` and `auto` allowed), `{literal, note}` registered in `literals`, `{asset}`; a type style is a `{token}`. Mark a non-brand component or variant `brand: false`. State keys may carry conditions (`@max:<bp>`, `@lt:<bp>`, `@min:<bp>`, `@<a>..<b>`, `@ctx:<name>`).
8. Literal policy: color, type, spacing, radius, shadow and size always point to tokens; add a component-specific token when one is missing. Border width, opacity, z-index, layout percentages, offsets and keywords may be literals with a note; their source lines stay in the research data.
9. Return the `used_by` of tokens added during packaging in the worker's `USED_BY` return field, derived from map references, not by hand; the orchestrator appends them to the token candidates. The packaging worker never writes research files.
10. Contrast data: rewrite pairs as token plus value, recompute, confirm equal to the research table; add accessibility `reference` pairs from existing tokens, not adopted by default. The snapshot adds no states, so it has no `added_states` block.
11. Gaps: merge every Known Gap under new ids with `source_ids`; obsolete ids go to `excluded` with a reason; each original id appears exactly once.
12. Assets: copy bytes unchanged, hash before and after (SHA-256), decode CSS data URIs to `.svg` with the source line; the asset README lists file, origin, hash, format, pixel size, bytes, use, components, single color, totals.
13. Theme and scripts: `build_tailwind.py` writes `tailwind/theme.css` (breakpoint tokens named `breakpoint-<step>` give the variants); copy `tailwind/index.css` from the skeleton and this skill's `scripts/package/` into `scripts/`.
14. Generate and check; regenerate and confirm identical output; run the package check.

```text
python -I scripts/package/build_tokens.py --tokens <pkg>/tokens.json --css <pkg>/tokens.css --dtcg <pkg>/tokens.dtcg.json [--check]
python -I scripts/package/build_tailwind.py --tokens <pkg>/tokens.json --out <pkg>/tailwind/theme.css [--check]
python -I scripts/package/build_contrast.py --tokens <pkg>/tokens.json --contrast <pkg>/data/contrast.json [--check]
python -I scripts/package/check_package.py --stage data --package <pkg> --allow-orphans [--forbid-list <run>/forbid-list.txt]
```

The snapshot feeds Phase 2 directly: `rationalize.py` reads this `tokens.json`, component map and `data/contrast.json` as they are, with the token candidates as `--usage`; no conversion step sits between the phases.

`check_package.py --stage data --allow-orphans` gates the snapshot with the same schema, tier-direction, generator, contrast, asset and path checks as later phases; primitives nothing references yet are reported instead of failed. Phase 2 runs it without `--allow-orphans`. The full stage adds the utility-notation checks; run it on a snapshot only when its specs and preview are already written in utility notation. `build_preview.py` shows the snapshot's colors in the semantic, component and primitive swatch groups; when the default group leads describe a rebuilt package, override them with `preview_rules.labels` (`tier_primitive`, `tier_semantic`, `tier_component`).

Configuration blocks the scripts read. No script fixes a prefix or brand name; the skeleton `assets/deliverable-skeleton/tokens.json` shows the `tokens.json` blocks with placeholders.

| Block | File | Read by | Keys |
| --- | --- | --- | --- |
| `css.prefix` | `tokens.json` | `build_tokens.py`, `build_tailwind.py`, `build_preview.py`, `check_package.py`; default of `residue_scan.py --prefix` | CSS custom-property prefix; required, no fallback |
| `themes` | `tokens.json` | `build_tokens.py`, `check_package.py` | Theme list, at least one; the first id is written as `[data-theme="<id>"]` |
| `tailwind` | `tokens.json` | `build_tailwind.py` | All optional: `breakpoints` {breakpoint token: variant}, only for breakpoint tokens not named `breakpoint-<step>` (the generator fails when breakpoint tokens exist but none can be mapped; no breakpoint family gives an empty section), `shadow_names` {shadow token: theme name}, `text_shadow` {shadow token: theme name, emitted as `--text-shadow-*`; `{}` when the brand has none}, `container_prefixes` [size-token prefixes that become `max-w-*`; default `size-layout-`, and a given prefix that matches no size token fails], `spacing_token` (space token behind `--spacing`). Defaults: `build_tailwind.py --help` |
| `preview_rules` | `components/component-tokens.json` | `build_preview.py` | All optional: `layout_file`, `labels`, `group_labels`, `type_sample`, `lang`, `favicon`, `inverse_markers`. Defaults: `build_preview.py --help` |
