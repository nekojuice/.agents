# Plan — P3 migrate (`<brand>` web layer to utility CSS)

> TEMPLATE: Copy into the run as `_plan.md` (factory plan route) or `plan-p3.md` (single session). Write it in the project's language. Replace every `<…>`; delete `> TEMPLATE:` lines. § 1, 2, 4, 5, 6, 7, 8, 9 are the factory plan-route required items (goal, scope and what is left out, deliverables and paths, allowed writes, worker assignments, verification method, human checkpoints, hand-on); keep them all.

- Run: `<run>`
- Phase: P3 migrate
- Stage: `plan` → `execute` → `done`, kept on the run state file's Stage line (`_status.md` under a factory) together with the resume point, written on every stop.
- Plan review: `change-review-request-<NN>.md` / `change-review-response-<NN>.md`

## 1. Goal

Express the web layer of `<brand>` in utility CSS (Tailwind v4) so the styles move to any frontend framework, with token values unchanged. Legacy framework mechanisms (component class schemes, forced-state classes, plugin attributes, scripted component DOM) are inventoried and removed; specs become parts + appearance + states + example markup.

## 2. Scope and what is left out

In scope:

- Theme generated from tokens; entry CSS; base layer; component specs; preview fragments; handbook usage section; package checker rules.
- Residue inventory of values, tokens and mapping fields, not only class strings.

Left out:

- Any token value change. A required change goes back to P2 as a decision.
- Mappings for anything the user did not name as a target; only the framework the user named.
- Brand prefix on every class (an option only for non-utility targets).

## 3. Entry condition and inputs

| Input | Path | Notes |
| --- | --- | --- |
| Frozen layered skill | `<run>/baseline/` | unpacked export of tag `<tag>`, or a hashed copy when there is no tag; blob SHAs checked against the tag or `<run>/baseline.sha1` |
| Forbid list | `<run>/forbid-list.txt` | run only |
| Tailwind CLI | `<run>/tools/<tool-dir>/` | approved by the user; pinned version at least two weeks old; installed with prefix and cache inside the run, install scripts off; cache removed after install |

## 4. Deliverables and paths

| # | Deliverable | Path | Producer |
| --- | --- | --- | --- |
| DL1 | Residue ledger (location, content, category, action, location after action) | `<run>/findings/residue-ledger.md` | construction worker |
| DL2 | `tailwind/theme.css` (generated), `tailwind/index.css` | `<run>/staging/<brand>/tailwind/` | construction worker |
| DL3 | `base.css` trimmed to brand-only rules on top of Preflight | `<run>/staging/<brand>/` | construction worker |
| DL4 | Mapping with semantic fields (anatomy, state → variant) replacing mechanism fields | `<run>/staging/<brand>/components/component-tokens.json` | construction worker |
| DL5 | Component specs rewritten (Tailwind example non-normative) | `<run>/staging/<brand>/components/` | construction worker |
| DL6 | Preview fragments in utility markup (same DOM as before), static states via marker attributes; compiled preview CSS | `<run>/staging/<brand>/preview/` | construction worker |
| DL7 | `DESIGN.md` § 7 (entry, layers, allowed arbitrary values, same-name/different-value list, reset, font fallback) and version log | `<run>/staging/<brand>/DESIGN.md` | construction worker |
| DL8 | `scripts/` copied again from this skill's `scripts/package/`, unchanged; a rule the checker lacks or gets wrong is reported as a finding for this skill, not patched in the copy | `<run>/staging/<brand>/scripts/` | construction worker |
| DL9 | Box-size diff old vs new preview; verification and cold-start reports | `<run>/verify/` | verifier, cold-start trial |

Order: DL1 → DL2 → DL3 → DL4 → DL5 ∥ DL6 → DL7 → DL8 → DL9.

## 5. Allowed writes

| Who | May write | Must not write |
| --- | --- | --- |
| Construction worker | `<run>/findings/residue-ledger.md`, `<run>/staging/<brand>/`, the alias hand-off file `<run>/findings/alias-handoff.md` | `tokens.json` values, baseline, forbid list, product source (unless this plan names an authorized path for the aliases), git |
| Verifier, cold-start trial | `<run>/verify/` | anything they verify |
| Orchestrator | plan, status, memory, tool install (after approval), swap once the swap preconditions pass | staging content |

## 6. Worker assignments

| Worker | Brief (from `worker-briefs.md`) | Deliverables | Depends on |
| --- | --- | --- | --- |
| construction | Construction (one worker for the whole dependent series; spec and notation rules checked with the copied checker, disagreements reported) | DL1–DL8 | baseline, CLI |
| verifier | Independent verifier | DL9 (V1, box diff) | DL8 |
| cold-start | Cold-start trial | DL9 (V2) | DL8 |

## 7. Verification method

Values unchanged (gate):

- `tokens.css` and `tokens.dtcg.json` regenerated are byte-identical to the baseline (only description text and version may differ).
- H1–H5 still hold (no token changed, so they must reproduce P2's results exactly).
- **H4 by measurement**: old and new preview with the same DOM, element-by-element bounding boxes; every difference explained (Preflight differences excluded first: list padding, button padding, table border collapse).

Mechanical (all PASS):

- Theme regenerated byte-identical; breakpoint literals equal `tokens.json`.
- Every class in specs and preview exists as a selector in the compiled CSS (CSS escaping handled).
- Theme-type utilities defined in the theme; arbitrary values free of colors and unregistered lengths; spacing on allowed steps.
- Legacy class schemes and forced-state classes: 0 hits in specs and preview (preview frame classes excepted).
- Residue ledger check: every row has category, action, location after action; locations exist; deleted files are gone.
- Neutrality scan 0 hits; generated files equal regeneration.

Independent (V1): spot-check ledger actions; visual check at the widths this plan sets, including group layout, against the source or the frozen evidence this plan names (`references/verification.md`). Cold start (V2): fresh agent, skill folder only, one full page in Tailwind in a project not on the source framework (exercises reset and font fallback).

## 8. Human checkpoints

1. Plan → independent review → plan stop (SKILL.md, Gates, step 3). The plan lists the verifier and the cold-start trial as work for the user to authorize (role, write scope, evidence).
2. After the plan is confirmed, before construction: freeze the P2 deliverable and export `<run>/baseline/` (commit and annotated tag only when the user asks: `orchestrator-factory` hard rule 6; `commit-message-suggestion` `## Committing on request`); tool download approved by the user.
3. Residue ledger → **user reviews deletions** when it removes visible elements; otherwise continue and report.
4. Build → V1 + V2 → fix loop.
5. Orchestrator swaps into place (rollback commands in this plan first) → **user reviews and accepts**, or the rollback restores the previous version.

## 9. Hand-on

- The accepted skill is the delivered brand skill; projects copy the folder.
- The run's ledger, box diff and tool folder stay in the run; tool folder removed or ignored by version control.
- Confirmed user decisions go to `_memory.md` `## User decisions`.

## 10. Decisions and revision notes

| # | Decision | Reason | Reversible by |
| --- | --- | --- | --- |
| 1 | <decision> | <reason> | <how> |

Revision notes: <date — what changed and why>.
