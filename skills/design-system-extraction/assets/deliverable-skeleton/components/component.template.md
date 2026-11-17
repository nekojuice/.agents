# <component name> `<component>`

> TEMPLATE: Save as `components/<component>.md`. Write prose in the project's language.
> TEMPLATE: Sections marked GENERATED come from `component-tokens.json` by script; do not edit them by hand. Sections marked HAND-WRITTEN are the only prose an author writes.
> TEMPLATE: Sample text is a marked neutral placeholder that keeps the slot and the observed length, such as `[label, 1–2 words]`; the source's real copy stays in the run (a P1 snapshot may show it). Never invent copy.
> TEMPLATE: Values are placeholders until generated. Delete every `> TEMPLATE:` line when done.

<One sentence: what it looks like and its main use.>

## Purpose

> TEMPLATE: HAND-WRITTEN.

Use for:

- <where it goes and when>.

Do not use for:

- <case>: use [<other component>](<other-component>.md).

## Anatomy

> TEMPLATE: GENERATED from `components.<component>.anatomy`. Part names must equal the mapping's `parts` keys. Semantic parts only; no class names, no legacy framework structure.

| Part | Description |
| --- | --- |
| `root` | <element and role> |
| `<part>` | <description; optional or required> |

## Appearance tokens

> TEMPLATE: GENERATED. One table for shared parts, one per variant, one per size. Variants with `extends` list overrides only and link to the parent anchor.

Normative. Values come from `component-tokens.json`; parenthesized values are resolved from `tokens.css` (type shows size / line height / weight). Conditions such as `(≥ <breakpoint>)` map to Tailwind breakpoint variants.

### Variants

| Variant | Use |
| --- | --- |
| `<component>--<variant>` | <when> |

### Sizes

| Size | Use | Main tokens |
| --- | --- | --- |
| `<size>` | <when> | `size-control-<n>`, `type-<role>-<size>` |

### Shared

| Part | State | Property | Value |
| --- | --- | --- | --- |
| `root` | `default` | `display` | literal `<keyword>` |
| `root` | `default` | `padding-inline` | `space-<n>` (0px) |
| `root` | `default` | `typography` | `type-<role>-<size>` (0px / 0 / 0) |

<a id="<component>--<variant>"></a>

### <variant> `<component>--<variant>`

| Part | State | Property | Value |
| --- | --- | --- | --- |
| `root` | `default` | `background-color` | `color-<role>` (#000000) |
| `root` | `hover` | `background-color` | `color-<role>` (#000000) |

## States

> TEMPLATE: GENERATED rows for every state the mapping defines; write "not defined" for a state the component lacks. HAND-WRITTEN notes only for ARIA wiring.

| Part | State | Trigger | ARIA | Tailwind variant |
| --- | --- | --- | --- | --- |
| `root` | `hover` | `:hover` on itself | — | `hover:` |
| `root` | `focus` | `:focus-visible` on itself | — | `focus-visible:` |
| `root` | `disabled` | `:disabled`, `[aria-disabled="true"]` | `aria-disabled` | `disabled:`, `aria-disabled:` |
| `<part>` | `selected` | state on `root` | `aria-selected` / `aria-current` | `group-aria-selected/<name>:` |

## Tailwind example

> TEMPLATE: GENERATED from the preview fragment of the default variant and size. Non-normative: it does not fix the DOM depth; only appearance, states and ARIA are normative.

Example only. Full variant × state examples: links under Examples.

**`<component>--<variant>`** (size `<size>`)

```html
<element class="<utilities from theme names and (--<prefix>-…) references>">[label]</element>
```

## Accessibility

> TEMPLATE: HAND-WRITTEN. For interactive widgets rebuilt from a legacy framework, follow a common accessible pattern (for example WAI-ARIA Authoring Practices) instead of the legacy DOM and script; keep original values.

- Role: <native element or ARIA role>.
- Keyboard: <keys and behavior>.
- Focus: `focus-ring` (<inner / outer tokens>); inverse ring on dark surfaces.
- Contrast (`data/contrast.json`), stated as facts:

| ID | Foreground | Background | Class | Ratio | Result | Context |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | `<role>` | `<role>` | normal | 0.00 | <meets / below> 4.5 | <context> |

## Do / Don't

> TEMPLATE: HAND-WRITTEN. Imperative sentences naming tokens. Contrast only as "`<fg>` on `<bg>` is N:1, below X; kept as original".

**Do**

- <rule>.

**Don't**

- <rule>.

## Examples

- [`<component>--<variant>`](../preview/components/<component>.html#<component>--<variant>)
