# Verification

Every phase ends with independent verification and a cold-start trial before the swap (SKILL.md, Gates). Verifiers never edit the package; they write their own scripts and do not trust a worker's self-report. Mechanical checks and visual checks are both required: full diffs, hashes and recomputed contrast can all pass while a visual check still finds a rule the research missed.

## Contents

- [Roles](#roles)
- [Independent verification](#independent-verification)
- [Cold-start trial](#cold-start-trial)
- [Box-size comparison](#box-size-comparison)
- [Fix loop](#fix-loop)
- [Report classes](#report-classes)

## Roles

| Role | Who | Writes |
| --- | --- | --- |
| Builder | The series worker that built the package (one worker keeps the whole series) | Staging only |
| Independent verifier | A different worker | Its own scripts and report in the run |
| Cold-start tester | A fresh worker that has read nothing but the package | One mock page and a reading log |

Briefs: `assets/worker-briefs.md`.

Under a factory, the verifier and the cold-start tester are workers the user authorizes at Converge: the plan lists each role, its write scope and the evidence it returns. Without that authorization, follow the factory plan route rather than dispatching them. Standalone, run each in a fresh session or sub-agent that receives only the inputs its brief names.

## Evidence by phase

| Phase | Package check | Hard rules | Comparison evidence |
| --- | --- | --- | --- |
| P1 | `check_package.py --stage data --allow-orphans` and `build_preview.py --check` | Not compared (nothing is merged yet); record what P2 will compare: contrast pairs with opacity, control heights, type order per variant and width | Source lines and render measurements |
| P2, P3 | `check_package.py --stage full` with the approved Tailwind CLI | H1–H5 recomputed from the data against the frozen previous deliverable | The frozen baseline |

## Independent verification

Mechanical, full coverage:

| Check | Method |
| --- | --- |
| Transform fidelity | Full diff of `tokens.json` against its input (candidates, or the consolidation file); only transformations the plan lists are allowed |
| Values ⊂ JSON | Every hex and px in md files occurs in `tokens.json` or the component map |
| Generated CSS | Generated styles match the component map entry by entry |
| Staleness | Every generated artifact equals a fresh regeneration (`--check` on every build script); counts in manuals point to data files |
| Idempotence | Run each generator twice; compare hashes |
| Assets | Hashes equal the original files |
| Links | Every relative link resolves |
| Excluded scope | Excluded variants are absent from the preview |
| Gaps | Each original gap id appears exactly once, in `gaps` or `excluded` |
| Paths | No absolute paths in the package |
| Neutrality | Forbid-list scan of the package and of this run's notes meant for the skill: 0 hits |
| Hard rules | P2 and P3: re-run H1–H5 from the data, not from the builder's `checks`. P1: confirm the recorded baselines exist |
| Phase 3 | Theme in sync, utilities exist, whitelist, mechanism scan 0, residue ledger rows realized |

Back to source, sampled:

- At least 30 tokens, at least 3 per family (all of them when the package has fewer); open the cited `path:line` or measurement and confirm the value.
- Recompute every contrast pair.

Visual:

- Pick the components (5 by default, all when there are fewer) and the widths the plan sets; screenshot the live site and the preview side by side. Without a live site (a source-only P1, or entering P2 or P3 with an equivalent package), use the frozen evidence the plan names (the previous preview, render-check captures in the run); when none exists, stop for the user with that gap.
- Look at whole groups, not only single components: alignment of a row of controls, centering versus start alignment, column widths.
- Sample computed styles in the preview against the render-check measurements.
- Preview health: images load, no console errors, `scrollWidth` not greater than the viewport (measure with script, not by screenshot).

## Cold-start trial

Tests whether a reader can produce on-brand screens from the package alone.

1. Give a fresh worker only the package folder and one task: build a full-page mock from a blank HTML file (a page type the source has).
2. The tester reports: the order in which it read files, the basis for each block it built (file and section), every point where it had to guess.
3. The orchestrator compares the mock with a live screenshot of the same page type, or with the frozen evidence the plan names. A different page type allows comparing frame and components only, not content or column widths; say so in the report.
4. Every guess is a package gap: missing section, unnamed file in the reading order, value only in prose. Feed it to the fix loop.

Typical guesses to look for: container gutters beyond max width, gap between two buttons side by side, gap between groups, reset needed outside the source framework, fallback for unbundled fonts, full-page skeleton order.

## Box-size comparison

For Phase 3, and for any change that should not move pixels.

1. Build old and new previews with the same DOM.
2. Measure `getBoundingClientRect` of every element in both, at the same widths.
3. Compare with `scripts/verify/boxdiff.py`: the browser path and the widths are arguments (`jobs --widths`, for example a phone width plus each `tokens.json` breakpoint value and the width just below it). `diff --jobs` checks the results against the jobs manifest first: a missing side, a fragment on one side only, an empty measurement, differing cards or a stale result file fail the comparison.
4. Explain every difference. Exclude reset effects first (list padding, button padding, table border collapse); what remains must be justified one by one or fixed.

The element listing is for review. Control heights are judged separately: H4 holds in the browser when each new control box height differs from the original by less than 4px.

## Fix loop

Problems found by verification or by any downstream worker always go back to the source of truth, in this fixed order:

1. Component map and tokens (one worker).
2. Specs and preview regenerated (in parallel).
3. DESIGN.md synchronized.
4. Full package check.
5. Independent re-verification.

Never patch a generated file or the preview to hide a map problem. Repeat until the verifier passes; each round is triggered by a report.

## Report classes

| Class | Meaning | Next |
| --- | --- | --- |
| `product-fail` | The package is wrong: value, link, anchor, rule, missing section | Fix loop |
| `run-error` | The check itself failed: script bug, wrong path, tool limit, environment | Fix the check, rerun; do not count against the package |
| `needs-human` | Requires a judgment the run cannot make (design intent, scope, a rule conflict) | Stop at the gate with the evidence |

Each finding carries evidence: file and line, the value seen, the value expected, and a screenshot path for visual findings.
