# Tailwind Notation

Tailwind class syntax is this skill's general notation for style, in any medium; tokens remain the only source of values (SKILL.md, Iron rules 6). The notation is Tailwind v4 (`@theme`, `(--variable)` shorthand). Agents read it reliably because the underlying models know its semantics well; it applies to any CSS-like framework and, through equivalent writing, to media that are not CSS.

## Contents

- [Rules](#rules)
- [Writing a style](#writing-a-style)
- [Same name, different value](#same-name-different-value)
- [Media that are not CSS](#media-that-are-not-css)
- [Unit conversion](#unit-conversion)
- [Limits](#limits)

## Rules

| Rule | Detail |
| --- | --- |
| Values come from tokens | A class names a theme entry generated from `tokens.json`, or a variable `(--<prefix>-...)`. Never a number that exists only in prose |
| Stock names are off | The theme resets stock namespaces to `initial`; `rounded-2xl` or a default palette step does not exist in a brand package |
| Arbitrary values are structural only | `[...]` values hold no color and only lengths registered as structural in the component map |
| One notation per package | Specs, previews, DESIGN.md and briefs for other media use the same class strings |
| Equivalent, not literal, outside CSS | In a slide or print file, the class string is the description; the medium's own properties carry the converted numbers |

## Writing a style

Write the role, then the classes, then (outside CSS) the converted values.

| Context | Example |
| --- | --- |
| Web component | Primary action: `bg-<action-color> text-<on-action> rounded-<radius> px-4 min-h-(--<prefix>-size-control-md) text-<label-style>` |
| Variable without theme entry | Component token: `bg-(--<prefix>-<component>-surface)` |
| Type style | `text-<role>-<size>` carries size, line height, weight and tracking from the token's sub-values |
| State | Variant prefixes (hover, focus-visible, disabled, aria-*) as in the package's state table |
| Slide title | `text-<role>-lg text-<brand color>`; then "= `<type token>` → N pt, `<brand color>`" |

Use placeholders like `<action-color>` exactly as the theme names them; the theme is generated, so the names are the token names without the family prefix.

## Same name, different value

A reader that knows stock Tailwind will assume stock meanings. When the brand theme defines a name that also exists in the stock theme, the assumption is wrong whenever the values differ.

1. Generate the list with `scripts/migrate/theme_name_diff.py` (brand `theme.css`, the stock `theme.css` of the pinned framework version, `tokens.css`). It resolves brand values through `tokens.css` and converts rem at 16px.
2. Keep two groups: same name with a different value (publish), same name with the same value (keep in the run as evidence).
3. Publish the first group in DESIGN.md's usage section: name, brand value, stock value, note ("`<name>` here is N px, not the stock value").
4. Regenerate the list whenever tokens or the framework version change; a stale list is worse than none.

## Media that are not CSS

Slides, print, documents and image templates use the core layer of DESIGN.md plus the converted numbers.

1. Describe each element with the class string (role, tokens).
2. Convert lengths with the table below, from the token's px value.
3. Colors carry over as values from `tokens.json`; the medium may need another format (for example hex without `#`).
4. Fonts: use the family list and fallback order from DESIGN.md; the medium embeds or substitutes by its own rules.
5. Record each converted value next to the token it came from, so a token change can be traced.

## Unit conversion

Basis: CSS absolute lengths. W3C CSS Values and Units Module Level 4, section 6.2 (Absolute Lengths), defines 1in = 96px and 1pt = 1/72 of 1in, so 1pt = 4/3px. Microsoft's Office Open XML documentation ("Use Office Open XML in your Word add-in") gives English Metric Units as 914,400 EMU to an inch. 1px = 9525 EMU is derived from the two (914400 / 96); it is not stated by either source.

Convention: treating every token px as a CSS px at 96px per inch is this skill's convention, not a requirement of any standard. Physical screens and printers differ; the convention only makes conversions repeatable. A rem token converts at a 16px root unless `tokens.json` states another root; that is also a convention.

| From | in | pt | EMU |
| --- | --- | --- | --- |
| 1px | 1/96 | 0.75 | 9525 (derived) |
| 1pt | 1/72 | 1 | 12700 (derived) |
| 1in | 1 | 72 | 914400 |

Worked checks:

| Token value | Conversion |
| --- | --- |
| 16px text | 12pt; 152400 EMU |
| 1px border | 0.75pt; 9525 EMU |
| 1280 × 720px canvas | 13.333 × 7.5in; 12192000 × 6858000 EMU, the common 16:9 slide size |

Office formats store some properties in their own fractions (for example halves or hundredths of a point for text size, twentieths of a point for spacing). Convert to pt first, then to the property's unit as the Microsoft documentation lists it.

## Limits

- Tailwind has no notation for some medium features (slide placeholders, page masters, print bleed). Describe them in prose and point to tokens; never invent a utility name.
- `@media` and breakpoints do not apply outside the web; choose the layout variant by the target canvas size.
- The notation does not carry behavior: keyboard, ARIA and motion rules come from the component spec, not from the class string.
