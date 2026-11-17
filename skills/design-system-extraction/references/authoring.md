# Authoring

Write what people and agents read: DESIGN.md, the deliverable's SKILL.md and policy file, component specs, and the offline preview. Authors read only the packaged data layer (`tokens.json`, component map, `data/`, asset README); they never derive values from research notes. Applies to every phase that ships a package.

## Contents

- [Format choice](#format-choice)
- [Decisions to read first](#decisions-to-read-first)
- [DESIGN.md](#designmd)
- [Deliverable SKILL.md and policy file](#deliverable-skillmd-and-policy-file)
- [Component specs](#component-specs)
- [Offline preview](#offline-preview)
- [Parallel authoring](#parallel-authoring)
- [Self-checks](#self-checks)

## Format choice

| Question | Rule |
| --- | --- |
| Which DESIGN.md format | The one the actual consumer reads (the agents and people who will use the package). Platform formats, such as a design vendor's published DESIGN.md spec, are references only; do not rewrite the package to fit a platform the user does not use |
| Claims about "the standard" | Label each conclusion by its basis, as the `research` skill does: primary source, verbatim (the original read yourself, not via a summary), partially supported, or own design (the agent's proposal). Never present an own design as the standard |
| Package as a skill | Follow Anthropic's skill guidance: SKILL.md body under 500 lines, details in files one level below it, a stated reading order, load only what the task needs |
| Invocation | Explicit invocation by default while the package is experimental; the two hosts' policies are opposite values |

## Decisions to read first

Three user decisions fix the wording of the whole manual; read them before writing.

| Decision | Effect |
| --- | --- |
| Invocation policy | Frontmatter and policy file |
| New-work default: original values or accessibility pairs | With original values, the contrast section states numbers only ("below the threshold"), never "must fix" |
| Add accessible states the source lacks? (yes / no / which) | For states not added, the source states are described as they are and point to residue tokens |

## DESIGN.md

Chapters follow the skeleton `assets/deliverable-skeleton/DESIGN.md`, numbered 0–10; the deliverable SKILL.md and the specs link to these numbers:

0. Opening: brand positioning in one paragraph, how to read the file.
1. Principles.
2. Core layer (medium-independent): voice and content, layout rhythm and surfaces (how sections are separated; optional), color roles and proportion, type, spacing, shape, depth, imagery and icons, Do's and Don'ts.
3. Web layer foundations: color (primitive, semantic), contrast notes, type, spacing, radius, elevation, size, layout and motion, state model, page skeleton.
4. Component selection.
5. Pattern selection.
6. Accessibility (the accessibility reference pairs).
7. Usage: Tailwind, other stacks, reset for projects not on the source framework, fonts and fallback, DTCG export.
8. Reserved media (empty chapters for slides, motion, print).
9. Known Gaps.
10. Version log (Phase 2 and 3: every replaced element and every deletion).

Reserve these sections even when the source is thin; cold-start trials showed readers guess without them:

| Section | Must say |
| --- | --- |
| Container | Max width, side gutters per breakpoint, alignment of the content inside |
| Side-by-side spacing | Gap between two buttons, between label and field, between cards |
| Group spacing | Gap between field groups and between sections |
| Reset for other projects | What a project without the source framework must reset so the tokens look right |
| Font fallback | Family list and fallback order; which fonts are not bundled |
| Full-page skeleton | The page regions the source has, in order (for example header, navigation, content area, footer; the set varies by project), naming component anchors |

Writing rules:

- Open each section with imperative rules that name tokens ("Use `<action-color>` solid with white text for the primary button"); tables follow the rules.
- Representative token table per role: one or two tokens (prefer `semantic`, then common primitives). Columns: role, token, value, use, source. Copy values verbatim from `tokens.json`; the source column says `measured · <token>` or `estimated · <token>`, with confidence in brackets when not `static-certain`. End with one sentence pointing to `tokens.json` and the preview.
- Every hex and px in the manual must exist in `tokens.json` or the component map (values ⊂ JSON).
- Counts point to data files ("see `data/gaps.json`"), never hard-coded numbers that go stale.
- Contrast section: rule first (normal, large, non-text thresholds; translucent on white; weight exception), then only the pairs below threshold, merged when foreground, background and threshold match; end with "all other pairs pass; full list in `data/contrast.json`".
- Accessibility reference: only `reference` pairs, opened with "for projects that must meet WCAG; not adopted by default", shorter than the contrast section.
- Layout: shared frame, main flow anatomy (order inside the content area), section order per page type, column table; name `<component>--<variant>` anchors. Mark text content and column widths "varies by page" with observed cases.
- States: only states the source has; unbranded states point to residue tokens.
- Usage, three parts: (1) any stack: import the generated variables, write only `var(--<prefix>-...)`, write numbers in media queries; (2) compiled framework CSS that ignores variables: an override table "framework selector → property → token", including rows equal to the default, never overriding residue states; (3) other frameworks: map by role, generate theme files by script. In Phase 3 packages, add the utility notation and the same-name list.
- Legacy variable aliases: when the original product still reads its old variable names, say that a transition alias stylesheet (old name → `var(--<prefix>-...)`) is handed to that product's owner, not put in the package, and is removed once the product no longer needs it (`references/phase-3-migrate.md`, Tokens to theme).
- Known Gaps: table of id, item, confidence, handling; details and original ids stay in `data/gaps.json`.
- Fonts outside tokens (special-purpose glyph fonts): family, class, size, purpose, known compatibility issues, not bundled.
- No research narrative (cascade, declaration counts, override wins) in the manual. Keep core plus web layer within 500 lines (the `check_package.py` default); component detail goes to specs. Raise the limit with `--design-max-lines` only when the plan allows a longer manual.

Template: `assets/deliverable-skeleton/DESIGN.md`.

## Deliverable SKILL.md and policy file

- Frontmatter: name, third-person description with purpose, triggers and exclusions, invocation policy, author, version, `last_updated` taken from the OS clock to the second.
- Body: triggers and exclusions; usage rules (new-work default, maintenance inside the original product, non-web media use the core layer only); reading order with each file's actual size measured by command (mark files not yet generated); file map; use in another project (copy the whole folder, relative paths only); scripts are for maintenance.
- `agents/openai.yaml`: `policy.allow_implicit_invocation` is the opposite of `disable-model-invocation`; quote `interface` strings.

Templates: `assets/deliverable-skeleton/SKILL.md`, `assets/deliverable-skeleton/agents/openai.yaml`.

## Component specs

One file per group, plus `components/README.md` as index (template: `assets/deliverable-skeleton/components/`).

1. Anchors: the spec heading, the preview card id and the map key share one form, `<component>--<variant>`; the component itself is `<component>`. Put an explicit `<a id="..."></a>` before the heading; generated heading anchors are unreliable.
2. Order follows the map registry; every key lands in some group file. Non-brand variants are written but marked "non-brand, do not use in new work", without skeleton or preview link.
3. Hand-written content lives in a data file, one record per component: name, one-sentence summary (appearance), use (where and when), content to provide, anatomy (part names equal map `parts` keys), variant names and when to use them, states, Do, Don't, non-main differences. Sample text: a P1 snapshot may show the recorded source wording; P2 and P3 deliverables use marked neutral placeholders that keep the slot and the observed length (for example `[button label, 2–4 words]`), and the real strings stay in the run. Never invent copy.
4. Generate mechanical sections from the map: anatomy, state table, token table, example links. Token table per variant, columns part, state, property, value, source, rows in map order: `{token}` as `` `name` (value) ``; type styles as size / line height / weight (/ tracking); `{tokens}` in shorthand order; `{literal}` as literal; `{asset}` as a relative link; residue tokens flagged; `extends` adds "inherits `<key>`, table lists overrides only" with a link. Clean research numbering and line citations out of map notes before printing them.
5. State table lists every state the target notation defines; a state the component lacks says "not defined".
6. In Phase 3 packages the spec carries appearance tokens, states and ARIA only; the utility example is illustrative, never the norm.
7. README explains keys and anchors, table columns, literal, asset, typography and `extends`, state and condition keys, where non-main variants live, and the "original values" rule.
8. When the map looks wrong (contradicting context values on one part, offsets written as literals, size tokens borrowed across components), do not edit it; report to the map's owner.

## Offline preview

A one-way overview page: shows the current state, offers no editing.

1. Fragments are the only HTML source: one per foundation, component group and pattern; each links tokens CSS, the compiled CSS and the preview frame CSS by relative path and opens on its own. Content sits between begin and end markers.
2. One card per main-brand variant (`<article id="<component>--<variant>">`), cells side by side for states and contexts. Width conditions cannot be forced statically; label them "depends on viewport". Draw unbranded focus or selection as it is and label the cell "unbranded residue". No cards for non-brand or excluded scopes.
3. Static states follow the target notation: marker attribute for utility targets, forced-state class for non-utility targets. With forced classes, emit states in a fixed order (visited, hover, focus, pressed, checked, selected, selected + hover, expanded, disabled, enabled, read only, placeholder, last) so equal-specificity wins match the source.
4. Sample text as in Component specs, item 3 (recorded wording only in a P1 snapshot; neutral placeholders with the observed length in P2 and P3); system values (dates, amounts, codes) as bracketed neutral placeholders; images that carry campaign text or generated or per-user content as marked placeholder boxes.
5. Flow page demo: compose a page from the components only, in the recorded region order of the source (its own regions; they vary by project); step names are neutral placeholders (`[step 1]`, …) in P2 and P3; at least one full-width page type. On narrow screens let demo cells touch the card edges.
6. Fixed-position components sit in a cell with `transform` set, which becomes their containing block.
7. The generator inlines fragments, rewrites relative paths to the skill root, appends to each card its markup source, notes, residue marks and a collapsed token table, and builds the other sections from data files. The page has no scripts and no external resources; the fixed table of contents uses anchors only.
8. Missing map values (padding, gutters) are not filled in the preview; report them to the map's owner. The generator guarantees token consistency, not layout; look at the preview before verification.

```text
python -I scripts/package/build_preview.py --package <pkg> [--tailwind-cli <path>] [--check]
```

Section order of the page: contents, cover, colors, type, spacing, radius, shadow, size, breakpoint, motion, components, patterns, assets, contrast, residue, Known Gaps.

## Parallel authoring

When manual, specs and preview are written in parallel:

- Self-checks count "target not yet produced" apart from "broken link"; the final judgment runs at the full stage.
- Agree file names and anchors (group files and fragments share names) before work starts.
- Measure reading-order file sizes only after every file is final.
- After any map or token change, rerun the token-name check; hand-written Do and Don't may name renamed tokens.

## Self-checks

| Check | How |
| --- | --- |
| Values ⊂ JSON | Extract `#[0-9a-fA-F]{3,8}` and `\d+(\.\d+)?px` from every md; each must occur in `tokens.json` or the map |
| Token names exist | Every backticked token-like name exists (exclude component ids, file names, and the property column, since `border-*` and `text-*` properties look like tokens) |
| Anchors | Every main-brand key appears verbatim with `<a id>` in specs and as a card in the preview |
| Research words | No research vocabulary (override, winner, declaration count, precedence), research step numbers or profile codes |
| Classes exist | Separate "really undefined" from "modifier that only reuses the base style" |
| Excluded ids | Excluded-scope variant ids appear only in "non-main differences" lines |
| External strings | No `file:` or `http(s):` URLs in docstrings or manuals (the external-resource check flags them) |
| Package | `check_package.py` at the phase's stage (P1: `--stage data --allow-orphans`; P2 and P3: `--stage full`); `build_preview.py --check` |
