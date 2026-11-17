---
name: <brand>
description: >-
  Provides the <brand> web design system: the brand handbook DESIGN.md, layered
  tokens (tokens.json, tokens.css, tokens.dtcg.json), a Tailwind v4 theme,
  base.css, component specs, assets and an offline preview, so that people and
  agents can build screens in the <brand> style in any project. Use when the
  user explicitly invokes <brand> to design, mock up, implement or maintain
  <brand> screens, or to apply the <brand> style to another medium. Not for
  interfaces that do not use this brand, or internal tools that keep a
  framework or neutral system look.
disable-model-invocation: true
metadata:
  author: <host-product> <model>
  version: "1.0"
  last_updated: "YYYY-MM-DDTHH:mm:ss"
---

> TEMPLATE: Write this file in the project's language. Keep the frontmatter keys in English. `last_updated` comes from an OS command. Delete every `> TEMPLATE:` line when done.

# <brand>

<brand> design system v<version>. It holds rules, tokens and component specs: follow the rules in DESIGN.md, take values from tokens, assemble screens from the component specs. Web screens use Tailwind v4; other stacks use the CSS variables.

## Triggers and exclusions

Use for:

- New screens, mock-ups, prototypes or implementations in the <brand> style, in any project and any stack.
- Maintaining screens that already use this brand: brand colors, type scale, spacing, component appearance or states.
- Applying the <brand> style to slides, motion or print (core layer only: DESIGN.md § 2).

Exclude:

- Interfaces that do not use this brand.
- <Other interfaces the project keeps outside this brand, if any.>
- General CSS or framework questions unrelated to the brand.

Deciding rule: apply when the screen must present this brand. When unsure, check the project's existing screens: if they already use `--<prefix>-*` variables, this skill's Tailwind theme, or the brand colors, apply; otherwise ask the user.

## Defaults

1. **Values only from tokens.json.** DESIGN.md lists representative tokens; look up any other value in `tokens.json`. Do not derive values.
2. **Tailwind first.** Use names defined in `tailwind/theme.css` and `(--<prefix>-…)` variable references. Do not use default palette names, default radius or shadow scales, or arbitrary values that carry colors or unregistered lengths (DESIGN.md § 7.1).
3. **Keep original colors.** Contrast figures are stated as facts (DESIGN.md § 3.3). Projects that must meet WCAG choose the reference combinations in DESIGN.md § 6; never invent a new color.
4. **States per spec.** Focus-visible, disabled, invalid and checked use the tokens in DESIGN.md § 3.9, triggered by native pseudo-classes and ARIA attributes.
5. **Do not add what the source lacks.** No new components, no new hues.
6. **Use original assets.** Logos, patterns and icons come from `assets/` unchanged.
7. **Neutral sample content.** Mock-ups never contain real personal data or business figures.

## Reading order

> TEMPLATE: Measure every size with a command after all files exist. Mark files not yet generated. Keep rows 1–3 so a cold reader reaches the page skeleton, container widths and spacing rules before writing markup.

Read only what the task needs; search large files by key instead of loading them whole.

| Order | File | Size | When |
| --- | --- | --- | --- |
| 1 | [DESIGN.md](DESIGN.md) | <bytes> B | Always: principles, core layer, representative tokens, states, usage |
| 2 | DESIGN.md § 3.8 and § 3.10 | — | Before any full page: container widths, side gutters, page skeleton |
| 3 | DESIGN.md § 3.5 | — | Before placing controls together: side-by-side and group spacing |
| 4 | [components/README.md](components/README.md) | <bytes> B | Component catalog, variants and anchors |
| 5 | `components/<component>.md` (<count> files) | <min>–<max> B | Only the components in use; appearance and states are normative, Tailwind examples are not |
| 6 | [tailwind/index.css](tailwind/index.css), [tailwind/theme.css](tailwind/theme.css) | <bytes> B, <bytes> B | Writing Tailwind: entry order and available theme names |
| 7 | [tokens.css](tokens.css), [base.css](base.css) | <bytes> B, <bytes> B | Writing CSS: load first; Tailwind imports them in `layer(base)` |
| 8 | [tokens.json](tokens.json) | <bytes> B | Look up one token's value, tier, origin, usage (search by name) |
| 9 | [components/component-tokens.json](components/component-tokens.json) | <bytes> B | Which token a part uses in a state (search by `<component>--<variant>`) |
| 10 | [data/contrast.json](data/contrast.json), [data/gaps.json](data/gaps.json) | <bytes> B, <bytes> B | Contrast figures; whether an item is an open gap |
| 11 | [assets/README.md](assets/README.md) | <bytes> B | Using logos, icons, patterns |
| — | [preview.html](preview.html) | <bytes> B | Visual overview for people (generated); agents need not read it |

## File map

```text
<brand>/
├─ SKILL.md / agents/openai.yaml   invocation policy (explicit only)
├─ DESIGN.md                       brand handbook
├─ tokens.json                     single token source
├─ tokens.css                      generated: --<prefix>-* variables, .<prefix>-type-* styles
├─ tokens.dtcg.json                generated: DTCG export
├─ tailwind/                       index.css entry (hand-written), theme.css (generated)
├─ base.css                        global base, link color, focus-visible
├─ components/                     README.md catalog, <component>.md specs, component-tokens.json map
├─ patterns/                       optional: pattern specs
├─ data/                           contrast.json, gaps.json
├─ assets/                         brand assets (original files)
├─ preview/ + preview.html         preview fragments and overview (generated)
└─ scripts/                        maintenance scripts
```

## Use in another project

1. Copy the whole `<brand>/` folder: Claude Code `.claude/skills/<brand>/`; Codex `.agents/skills/<brand>/`. All links are relative.
2. Tailwind projects: copy `tokens.css`, `base.css`, `tailwind/theme.css` into the project's style folder and write the entry per DESIGN.md § 7.1.
3. Projects not built on the source framework: apply the reset in DESIGN.md § 7.3 and the font fallback in § 7.4.
4. Other stacks: DESIGN.md § 7.2; use only `--<prefix>-*` variables and `.<prefix>-type-*` styles.

## scripts

`scripts/` only maintains this skill (Python 3 standard library, no network, no installs); using the skill needs none of them.

> TEMPLATE: These are the extraction skill's `scripts/package/` files, copied unchanged. Keep the lines in the project's language; drop `selftest.py` if it was not copied.

- `scripts/build_tokens.py`: regenerates `tokens.css` and `tokens.dtcg.json` from `tokens.json` (`--tokens --css --dtcg [--check]`).
- `scripts/build_contrast.py`: recomputes `data/contrast.json` from `tokens.json` (`--tokens --contrast [--check]`).
- `scripts/build_tailwind.py`: regenerates `tailwind/theme.css` from `tokens.json` (`--tokens --out [--check]`).
- `scripts/build_preview.py`: rebuilds `preview.html`, and `preview/tailwind.css` when a Tailwind CLI is given (`--package [--tailwind-cli] [--check]`).
- `scripts/check_package.py`: package gate (`--stage data|full --package [--forbid-list] [--tailwind-cli] [--invocation] [--allow-orphans]`; `--allow-orphans` only for a Phase 1 snapshot).
- `scripts/selftest.py`: self-test of the scripts above on a neutral fixture (`[--keep]`).
