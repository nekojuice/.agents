# Component catalog

> TEMPLATE: Write in the project's language. Generate the catalog rows from `component-tokens.json` (`components[*].group`, `name`, `anchor`, `variants`, `sizes`, `summary`); write the reading notes by hand. Groups are by function, not by source page.

This is the single catalog of components and patterns. Components do not ship class names: each spec gives purpose, parts (anatomy), appearance tokens, states (variants and ARIA), a non-normative Tailwind example, accessibility, and Do/Don't.

## How to read

- Mapping source: `component-tokens.json` (component × part × state × property → token). Specs and preview are generated from it.
- Keys and anchors: a component is `<component>`; a variant is `<component>--<variant>`. The same string is the spec anchor, the preview card `id`, and the mapping key.
- Value forms in appearance tables: a token (`` `name` `` with its resolved value), a token list (shorthand order), `literal` (structural value registered in the mapping), an asset (relative link to `../assets/`), `typography` (family, size, line height, weight, letter spacing).
- State keys: `default`, `hover`, `active`, `focus`, `disabled`, `invalid`, `checked`, `selected`, `expanded`; conditions `@min:<breakpoint>` and similar are written next to the state.
- Variant, size and state names are spec vocabulary, not class names.
- Web projects write Tailwind per each spec (entry: `../tailwind/index.css`); other stacks write CSS with `--<prefix>-*` variables from `../tokens.css` (DESIGN.md § 7).
- Values are original values; contrast figures are facts (DESIGN.md § 3.3).
- Preview: every variant has a card in `../preview/` whose `id` equals the anchor.

## <group: actions>

| Component | Variants | Size | Summary |
| --- | --- | --- | --- |
| [<component name> `<component>`](<component>.md) | `<component>--<variant>`, `<component>--<variant>` | <sizes or —> | <one-line appearance and use> |

## <group: inputs>

| Component | Variants | Size | Summary |
| --- | --- | --- | --- |
| [<component name> `<component>`](<component>.md) | `<component>--<variant>` | — | <summary> |

## <group: feedback / navigation / content / containers / layout / overlays>

| Component | Variants | Size | Summary |
| --- | --- | --- | --- |
| [<component name> `<component>`](<component>.md) | `<component>--<variant>` | — | <summary> |

## Patterns

> TEMPLATE: Keep only if the brand has pattern specs; otherwise delete this section.

| Pattern | Components | Summary |
| --- | --- | --- |
| [<pattern name> `<pattern>`](../patterns/<pattern>.md) | `<component>`, `<component>` | <summary> |
