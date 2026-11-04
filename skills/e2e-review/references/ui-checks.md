# UI Checks

Beyond the checklist, judge whether the UI behaves unreasonably. Findings go to the report's UI findings section and never affect verdicts.

These checks apply to web surfaces. Rounds that only use API surfaces skip them; obviously wrong API behavior outside the checklist (wrong status codes, leaked fields) goes under observations.

## Categories

| Type | Look for |
| --- | --- |
| `operation` | Clicks with no effect, unnecessary steps, results that contradict the control's label, no feedback after an action |
| `layout` | Overlap, truncated text, headers squeezed into many lines, misalignment, unexpected scrollbars |
| `wording` | Menu label differs from page title, one concept named differently across screens, misleading names |
| `display` | Raw timestamps, the same data formatted differently across screens, read-only fields that look editable, odd empty values |
| `error` | Console errors, failed API calls, unclear error messages |

## Method

1. Run the automatic lint first: `ctx.lint(where, { scope })` in scenarios, or `run web:probes/ui-lint --scope=<selector> --shot=<name>`.
2. Review visually what lint cannot catch: take viewport screenshots, scan a contact sheet (`sheet <round> --prefix=<prefix>`), then open originals or scroll where something looks off.
3. A visual check you find yourself repeating every round becomes a lint rule.

## Automatic rules

Generic rules ship with the skill in `scripts/drivers/playwright/helpers/uiLint.js`:

| Rule | Detects |
| --- | --- |
| `iso-datetime` | Timestamps shown in raw ISO format |
| `clipped-text` | Text clipped by its container |
| `stacked-header` | Table header text occupying three or more lines |
| `readonly-counter` | Read-only field still showing a character counter |
| `overflow-x` | Horizontal page scrollbar (whole-page scope only) |

Project-specific rules, such as those tied to a component library's class names, go in `.e2e/surfaces/<web surface>/helpers/uiLintExtra.js`: a function `async (page, scope) => findings` returning the same shape `{ type, rule, what, samples }`. The `ui-lint` probe merges both.

## Adding or changing a rule

- Run it on at least one page known to have the problem and one known not to, before using it in scenarios.
- Before validating, confirm the logged-in account can see those pages; the browser keeps the account the previous scenario left logged in.
- Measure what the content actually looks like, such as how many lines text occupies, not container sizes; spanning cells and auto-grown rows make container measurements misfire.
- Call `H.settle(page)` first. Messages captured during an entry animation look clipped.

## Writing findings

- Attach evidence: a screenshot first, the read value for wording issues. If no evidence was kept at the time, mark the finding for human review.
- State the phenomenon and where it occurs. No causes, no fixes.
- Do not comment on test data content.
- Skip behavior PROJECT.md lists as by design.
