# Plan — P1 extract (`<brand>` raw snapshot)

> TEMPLATE: Copy into the run as `_plan.md` (factory plan route) or `plan-p1.md` (single session). Write it in the project's language. Replace every `<…>`; delete `> TEMPLATE:` lines. § 1, 2, 4, 5, 6, 7, 8, 9 are the factory plan-route required items (goal, scope and what is left out, deliverables and paths, allowed writes, worker assignments, verification method, human checkpoints, hand-on); keep them all.
> TEMPLATE: Paths are relative to the run directory (`<run>/`) or the product root (`<product>/`); never write absolute paths into the produced skill.

- Run: `<run>`
- Phase: P1 extract
- Stage: `plan` → `execute` → `done`, kept on the run state file's Stage line (`_status.md` under a factory) together with the resume point, written on every stop.
- Plan review: `change-review-request-<NN>.md` / `change-review-response-<NN>.md`

## 1. Goal

Extract the design language of `<target-frontend>` faithfully and traceably, and package it as a raw snapshot brand skill `<brand>` v1.0: values as the source renders them, every value traceable to a source line or a render measurement. The deliverable is a visual design specification; CSS analysis is only the means of reading values.

## 2. Scope and what is left out

In scope:

- Frontends: `<target-frontend>` (pages: <list or "all reachable">).
- Component groups and assets the user named: <list>.

Left out:

- <frontends excluded, e.g. a back-office area with its own look>.
- Advertising images, third-party widgets, server-generated images.
- Rebuilding, merging or renaming values (P2); framework migration (P3).
- Anything the user gave only as an example, not as a target.

## 3. Entry condition and inputs

| Input | Path | Notes |
| --- | --- | --- |
| Product source (read-only) | `<product>/` | templates, components, style sheets |
| Local dev server for render checks | `<command>` | started by the orchestrator; local only |
| Reference format (optional) | `<path>` | structure only, never content |
| User decisions | `_memory.md` | invocation (explicit), keep original values, delivery location |

## 4. Deliverables and paths

| # | Deliverable | Path | Producer |
| --- | --- | --- | --- |
| DL1 | Stack profiles and source map | `<run>/findings/01-stack.md` + `.json` | research worker A |
| DL2 | Component and asset inventory | `<run>/findings/02-components.json`, `03-assets.md` | research worker A |
| DL3 | Content and layout survey (real copy, page anatomy, container, grid, alignment) | `<run>/findings/04-content-layout.md` | research worker B |
| DL4 | CSS rule index and contrast script with self-test | `<run>/findings/index/`, `<run>/tools/` | research worker B |
| DL5 | Per-component resolved values (`source`, `resolved`, `confidence`) | `<run>/findings/05-component-values-*.md` | research workers A, B |
| DL6 | Render check of `runtime-dependent` and `unresolved` values | `<run>/findings/07-render-check.md` | research worker C |
| DL7 | Token candidates (coexisting values kept, suggested main value with reason, residue list) | `<run>/findings/06-token-candidates.md` + `.json` | research worker C |
| DL8 | Packaged skill in the layered schema (`origin: source`; research fields stay in DL5–DL7): `tokens.json`, `tokens.css`, `tokens.dtcg.json`, `tailwind/`, `components/component-tokens.json`, `data/`, `assets/`, `scripts/` (copies) | `<run>/staging/<brand>/` | packaging worker |
| DL9 | `DESIGN.md`, `SKILL.md`, `agents/openai.yaml`, component specs, preview | `<run>/staging/<brand>/` | packaging worker |
| DL10 | Verification and cold-start reports | `<run>/verify/` | verifier, cold-start trial |

Order: DL1–DL4 → DL5 → DL6 (before DL7 when many values are `runtime-dependent`) → DL7 → DL8 → DL9 → DL10.

## 5. Allowed writes

| Who | May write | Must not write |
| --- | --- | --- |
| Research workers | their own files under `<run>/findings/`, scripts under `<run>/tools/` | product source, staging, other workers' files |
| Packaging worker | `<run>/staging/<brand>/` | product source, research files, final skill location |
| Verifier, cold-start trial | `<run>/verify/` | anything they verify |
| Orchestrator | `_plan.md`, `_status.md`, `_memory.md`, `used_by` entries the packaging worker returns (appended to the token candidates), swap into `<skill-location>/<brand>/` once the swap preconditions pass | product source |

No network from scripts; tool downloads only after user approval, installed inside the run.

## 6. Worker assignments

| Worker | Brief (from `worker-briefs.md`) | Deliverables | Depends on |
| --- | --- | --- | --- |
| research-a | Research | DL1, DL2, DL5 (part) | — |
| research-b | Research | DL3, DL4, DL5 (part) | — |
| research-c | Research | DL6, DL7 | DL1–DL5 |
| packaging | Packaging (one worker for the dependent series DL8 → DL9) | DL8 → DL9 | DL7 |
| verifier | Independent verifier | DL10 (V1) | DL9 |
| cold-start | Cold-start trial | DL10 (V2) | DL9 |

Fix loop owner: the packaging worker (mapping and tokens first, then specs and preview, then handbook).

## 7. Verification method

Mechanical (scripts, all PASS before the gate):

- Research scripts pass their self-tests before use.
- Every resolved value carries `source`, `resolved`, `confidence`; every inventory row has `path:line`.
- Package check: `check_package.py --stage data --allow-orphans` passes (unreferenced residue primitives are reported, not failed); generated files equal regeneration (`build_tokens.py --check`, `build_tailwind.py --check`, `build_contrast.py --check`, `build_preview.py --check`); mapping covers every brand variant; invocation policies inverse.
- Handbook and spec hex/px values ⊂ `tokens.json` ∪ `component-tokens.json`; backticked token names exist.
- Neutrality scan of the skill's generic parts with the run's forbid list: 0 hits.

Independent (V1): full diff of tokens against candidates (only planned transformations); tokens traced back to source and side-by-side visual checks as `references/verification.md` sets them (sample sizes, all when fewer; components and widths: <list>; without a live site: <frozen evidence>); all contrast recomputed; group layout and alignment checked.

Cold start (V2): a fresh agent with only the skill folder builds one full page; report reading order, basis per region, guesses.

Acceptance:

- Values equal source or render measurement; contrast recorded as is, no recoloring.
- Hard rules H1–H5 are not gated in P1 (nothing is merged yet); record the data P2 needs to check them.
- Unreachable pages and unverifiable values are listed in Known Gaps.

## 8. Human checkpoints

1. Plan → independent review → plan stop (SKILL.md, Gates, step 3). The plan lists the verifier and the cold-start trial as work for the user to authorize (role, write scope, evidence).
2. Research done → **user reviews the token candidates summary** (main values, residue, gaps).
3. Package built → V1 + V2 → fix loop until clean.
4. Orchestrator swaps the staging package into place (rollback written in this plan first; for a first build it is emptying `<skill-location>/<brand>/`) → **user reviews and accepts**, or the rollback restores the previous state.
5. Before P2, after its plan is confirmed: freeze the accepted v1.0. Commit and annotated tag only when the user asks (`orchestrator-factory` hard rule 6; `commit-message-suggestion` `## Committing on request`).

Agent-derived verification routes that cannot be completed are recorded as Known Gaps, not turned into user questions; when the evidence is needed for a required verification, the worker returns it to the orchestrator as a blocker.

## 9. Hand-on

- P2 takes the frozen baseline (tag export or hashed copy, read-only), the token candidates, the inventory and the contrast data as inputs.
- Confirmed user decisions go to `_memory.md` `## User decisions`.

## 10. Decisions and revision notes

| # | Decision | Reason | Reversible by |
| --- | --- | --- | --- |
| 1 | <agent-made decision> | <reason> | <how> |

Revision notes: <date — what changed in this plan and why>.
