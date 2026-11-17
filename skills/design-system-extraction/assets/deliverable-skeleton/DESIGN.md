# <brand> design handbook v<version>

> TEMPLATE: Write in the project's language; keep token names, keys and anchors as they are.
> TEMPLATE: Every section opens with imperative rules that name tokens, then a small representative table. No research narrative (cascade, declaration counts, overrides, source lines).
> TEMPLATE: Every hex and px in this file must appear in `tokens.json` or `components/component-tokens.json`. Counts point to data files instead of hard-coded numbers.
> TEMPLATE: Values below (`#000000`, `0px`, `0`, `0ms`) are placeholders. Replace each with the value copied verbatim from `tokens.json`.
> TEMPLATE: Keep core + web layer within 500 lines (checker default); component detail belongs in `components/`.

## Contents

0. Opening · 1. Principles · 2. Core layer · 3. Web layer foundations · 4. Component selection · 5. Pattern selection · 6. Accessibility · 7. Usage · 8. Reserved media · 9. Known Gaps · 10. Version log

## 0. Opening

<One paragraph: what the brand is for, who reads this file, and how to read it (rules first, tables second; values live in `tokens.json`).>

Representative-table columns used throughout: role, token, value, usage, source (`source` or `added` origin).

## 1. Principles

- <Principle as an imperative sentence, e.g. "Take every value from tokens; never derive one.">
- Keep original values. Contrast figures are facts; do not recolor to raise contrast.
- <Principle on what the brand never does.>

## 2. Core layer

Medium-independent rules. Non-web media (slides, motion, print) apply only this layer.

### 2.1 Voice and content

- <Rule on tone, with wording taken from the source's real copy.>
- Button labels: <length and form rule>. Error messages: <sentence pattern>.

### 2.2 Layout rhythm and surfaces

- <How sections are separated (background, spacing, rules), naming surface tokens; write "none" if the brand uses no section rhythm.>

### 2.3 Color roles and proportion

- <Rule on dominant, accent and action colors and their share of a screen, naming `<role>` tokens.>

### 2.4 Type personality and hierarchy

- <Rule on families and role hierarchy (display, headline, title, body, label, caption).>

### 2.5 Spacing rhythm

- <Rule on the base step and how density changes across contexts.>

### 2.6 Shape

- <Rule on corner radius per context.>

### 2.7 Depth

- <Rule on when elevation is used.>

### 2.8 Imagery and icons

- <Rule on logo use, icon style, monochrome colors; files in `assets/`.>

### 2.9 Do's and Don'ts

| Do | Don't |
| --- | --- |
| <imperative, naming a token> | <imperative, naming a token> |

## 3. Web layer foundations

### 3.1 Color: primitive

- Do not use primitives directly in components; go through semantic or component tokens.

| Role | Token | Value | Usage | Source |
| --- | --- | --- | --- | --- |
| <palette step> | `<palette-family-step>` | #000000 | <referenced by> | source |

Full list: `tokens.json` → `color`.

### 3.2 Color: semantic

- <Rule, e.g. "Body text uses `color-text-default` on `color-surface-canvas`.">

| Role | Token | Value | Usage | Source |
| --- | --- | --- | --- | --- |
| <text default> | `color-<role>` | `{<palette-family-step>}` (#000000) | <where> | source |
| <surface canvas> | `color-surface-<role>` | `{<palette-family-step>}` (#000000) | <where> | source |
| <action primary> | `color-action-<role>` | `{<palette-family-step>}` (#000000) | <where> | source |

### 3.3 Contrast notes

Judgement rules: normal text 4.5:1, large text 3:1, non-text 3:1; <rule for translucent colors>; <rule for weight-based large-text exceptions>.

Combinations below the threshold (stated as facts, kept as original):

| IDs | Foreground | Background | Class | Ratio | Threshold |
| --- | --- | --- | --- | --- | --- |
| <id>, <id> | `<role>` | `<role>` | normal | 0.00 | 4.5 |

All other combinations meet their thresholds. Full list: `data/contrast.json`.

### 3.4 Type

- <Rule on which style each role uses; mobile-first breakpoint overrides.>

| Style | Token | Size / line height / weight | Usage | Source |
| --- | --- | --- | --- | --- |
| <body md> | `type-<role>-<size>` | 0px / 0 / 0 | <where> | source |

### 3.5 Spacing

- Allowed steps: the `space-*` tokens only. <Rule on the base step.>
- **Side-by-side buttons**: two or more buttons in one row are separated by `space-<n>`; on narrow screens they <stack / stay in one row> with `space-<n>` between rows.
- **Group spacing**: between fields in one group `space-<n>`; between groups `space-<n>`; between a heading and its group `space-<n>`; between page sections `space-<n>`.
- **Inline spacing**: icon to label `space-<n>`; label to control `space-<n>`.

| Role | Token | Value | Usage | Source |
| --- | --- | --- | --- | --- |
| <button gap> | `space-<n>` | 0px | <where> | source |
| <group gap> | `space-<n>` | 0px | <where> | source |

> TEMPLATE: If the source has no measured value for one of these spacings, write it as a Known Gap with the nearest observed value; never leave the bullet out.

### 3.6 Radius

| Role | Token | Value | Usage | Source |
| --- | --- | --- | --- | --- |
| <control> | `radius-<name>` | 0px | <where> | source |

### 3.7 Elevation

| Role | Token | Value | Usage | Source |
| --- | --- | --- | --- | --- |
| <level 1> | `elevation-<n>` | `0px 0px 0px {<palette-alpha>}` | <where> | source |

### 3.8 Size, layout and motion

- **Container widths**: content sits in a container with max width `size-layout-<name>` per breakpoint (table below), side gutters `space-<n>`, horizontally centered. State what happens below the smallest breakpoint (full width minus gutters).
- **Columns**: <grid columns and gutter>; panel width <full container or centered N/12, by page type>. Mark widths that vary by page as "varies by page" and list the observed cases.
- **Alignment**: <container `align-items` / `justify-content` per region, e.g. headings start-aligned, actions end-aligned>.
- Controls: height from `size-control-*` only; icons `size-icon-*`.
- Motion: durations `duration-*`, easing `easing-*`.
- Breakpoints are reference values; media queries use the literal numbers below.

| Breakpoint | Token | Min width | Container max width | Side gutter |
| --- | --- | --- | --- | --- |
| <sm> | `breakpoint-<name>` | 0px | `size-layout-<name>` (0px) | `space-<n>` (0px) |

| Role | Token | Value | Usage | Source |
| --- | --- | --- | --- | --- |
| <control md> | `size-control-<n>` | 0px | <where> | source |
| <transition> | `duration-<n>` | 0ms | <where> | source |

### 3.9 State model

- Hover, active, focus-visible, disabled, invalid, checked, selected, expanded: which tokens each uses, and which pseudo-class or ARIA attribute triggers it.
- Focus ring: `focus-ring` on light surfaces; inverse ring on dark surfaces (name the attribute or token).
- Disabled rules come last in each component so they win over variant states.

| State | Trigger | Token | Origin |
| --- | --- | --- | --- |
| focus-visible | `:focus-visible` | `focus-ring` | <source or added> |
| disabled | `:disabled`, `[aria-disabled="true"]` | `color-<role>` | <source or added> |

### 3.10 Page skeleton

Every full page uses this order. Name the component anchor for each region so a reader can jump to its spec.

```text
page
├─ header            <component>--<variant>
├─ <navigation>      <component>--<variant>         optional
├─ main
│  ├─ <section wrapper> <component>--<variant>      section rhythm per § 2.2
│  │  └─ container   max width per § 3.8
│  │     ├─ page title
│  │     ├─ <primary content>                        column rule per § 3.8
│  │     └─ <actions>                                button spacing per § 3.5
│  └─ …
└─ footer            <component>--<variant>
```

- <Rule per page type: which regions are required, which are optional.>
- Full example: `preview.html#<page-example-anchor>`.

## 4. Component selection

- <Rule per decision, e.g. "One primary action per screen; others use the secondary variant.">
- Catalog: [components/README.md](components/README.md).

## 5. Pattern selection

- <Rule per pattern; omit this section if the brand has no pattern specs.>

## 6. Accessibility

- Defaults keep original values (§ 3.3). Projects that must meet WCAG use only these reference combinations, built from existing tokens:

| ID | Foreground | Background | Ratio | Replaces |
| --- | --- | --- | --- | --- |
| <ref-id> | `<role>` | `<role>` | 0.00 | <id> |

- Keyboard and ARIA requirements live in each component spec.

## 7. Usage

### 7.1 Tailwind v4 (primary)

Entry order (see [tailwind/index.css](tailwind/index.css)):

```css
@import "tailwindcss" source(none);
@import "<path>/tokens.css" layer(base);
@import "<path>/theme.css";
@import "<path>/base.css" layer(base);
@source "<project templates glob>";
```

- `source(none)` turns off automatic source detection; list every template folder with `@source`.
- `tokens.css` and `base.css` sit in `layer(base)` so utilities can override them.
- The theme resets default namespaces to `initial`; only brand names exist. Use theme names (`bg-<role>`, `text-<role>-<size>`, `rounded-<name>`, `shadow-<name>`) or variable references (`bg-(--<prefix>-<token>)`).
- Spacing utilities accept only the allowed steps: <list of step numbers>.

Allowed arbitrary values (anything else is not allowed):

| Arbitrary value | Where | Reason |
| --- | --- | --- |
| `<utility>-[<structural value>]` | `<component>` | <structural value with no utility; no color, length registered in `component-tokens.json`> |

Same name, different value (Tailwind default meaning differs from this theme):

| Utility | Default Tailwind meaning | Meaning in this theme |
| --- | --- | --- |
| `<utility>` | <default> | <brand meaning or "removed"> |

> TEMPLATE: Fill both lists from the theme generator and the migration check output; write "none" when a list is empty.

### 7.2 Other stacks

- Load `tokens.css` first; write only `var(--<prefix>-…)`; media queries use the literal breakpoint numbers.
- Compiled framework CSS does not read variables: use the override table below when the project keeps such a framework.

| Framework selector | Property | Token |
| --- | --- | --- |
| `<selector>` | `<property>` | `<token>` |

### 7.3 Reset for projects not on the source framework

The values were measured on top of `<legacy-framework>` defaults. A project without that framework applies this baseline before the brand styles:

| Element | Property | Value |
| --- | --- | --- |
| `*, ::before, ::after` | `box-sizing` | `border-box` |
| `body` | `margin` | `0` |
| <element> | <property> | <value from tokens or keyword> |

- With Tailwind, Preflight already covers <list>; add only <list>.

### 7.4 Fonts and fallback

- Fonts are not bundled; the project loads them. Family tokens: `font-<key>`.
- When a font is unavailable, the stack falls back in this order: `<family>, <fallback>, <generic>`. <Note on metric differences, e.g. wider glyphs, and which controls must keep their height.>
- Icon font or special-purpose fonts: <name, purpose, not bundled>.

### 7.5 DTCG export

- `tokens.dtcg.json` is generated; values without a DTCG type are listed in root `$extensions`.

## 8. Reserved media

Express non-CSS sizes with the same Tailwind notation and token names; token px are CSS px (96 px per inch).

### 8.1 Slides

<Reserved.>

### 8.2 Motion

<Reserved.>

### 8.3 Print

<Reserved.>

## 9. Known Gaps

| ID | Item | Confidence | Handling |
| --- | --- | --- | --- |
| <gap-id> | <what is unknown or unverified> | <static-certain / runtime-dependent / unresolved> | <how to proceed> |

Details and original IDs: [data/gaps.json](data/gaps.json).

## 10. Version log

### 10.1 v<version>

- <What changed. Values unchanged unless listed.>
- Removed: <each removed element or mechanism, from the residue ledger>.
- Replaced: <degraded or hand-patched element → common pattern, values kept>.

### 10.2 Earlier versions

- v1.0: raw extraction snapshot. <Where the frozen baseline lives (tag name only); using this version does not depend on it.>
