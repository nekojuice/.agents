# Residue ledger — `<brand>` <phase>

> TEMPLATE: Write in the project's language; keep the Ledger heading (level 2), the six columns in order, the category IDs and the action words as they are (the ledger check reads them; translated values must be passed with `--section`, `--categories`, `--delete-disposition`). Locations are relative to the skill root. Replace every `<…>`; delete `> TEMPLATE:` lines.
> TEMPLATE: Class-string scans alone prove little in an already de-frameworked version; inventory values, tokens and mapping fields too.

- Skill: `<brand>` (baseline: tag `<tag>` or hashed copy `<run>/baseline/`)
- Scan: `<residue scan command and date>`
- Check: `<ledger check command>` → <PASS / FAIL>

## Categories

| ID | Category | Judgement | Action |
| --- | --- | --- | --- |
| `brand-value` | Brand appearance value | Visible color, width, type, spacing, radius, shadow, even if equal to a `<legacy-framework>` default | Keep the value and its token; stop describing it as a framework mapping |
| `mechanism-bound-value` | Appearance value bound to a mechanism element | The value serves only one framework structure | Keep while the element stays in the spec; delete only when the element is removed, and list the deletion in the version log |
| `motion` | Motion duration | Framework transition values | Keep as `duration-*` / `easing-*` tokens referenced by the spec's transition row |
| `mechanism` | Mechanism | Component class schemes, forced-state classes, plugin `data-*`, scripted component DOM, collapse wiring, framework mapping tables | Remove; replace with anatomy + variant + ARIA |

## Scan summary

| File | Legacy part/modifier classes | Forced-state classes | Framework words | Mechanism fields |
| --- | --- | --- | --- | --- |
| `<path>` | 0 | 0 | 0 | 0 |

## Ledger

Every row needs a category ID (bare, without backquotes), an action and a location after the action. Actions: `keep`, `keep-as-token`, `rewrite`, `delete`, `delete-file`.

| # | Location | Content | Category | Action | Location after action |
| --- | --- | --- | --- | --- | --- |
| 1 | `<path>` § <section> / key `<key>` | <what is there> | brand-value | keep | `<path>` § <section> |
| 2 | `<path>` key `<key>` | <mechanism field> | mechanism | rewrite | `<path>` key `anatomy` |
| 3 | `<path>` | <file only serving the mechanism> | mechanism | delete-file | — (file removed) |

## Version log feed

Rows with action `delete` or `delete-file` that remove something visible, copied into the DESIGN.md version log (§ 10):

- <row # — what was removed — replacement, if any>
