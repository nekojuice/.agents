---
name: change-review-response
description: >-
  Verdict an experimental OpenSpec change-doc review: read
  change-review-request-NN.md and the cited change package, then write
  matching change-review-response-NN.md with checklist judgments, categorized
  reviewer concerns, and a next action. Use when the user invokes
  change-review-response (or asks to answer that review brief).
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5, Claude Code Opus 5.5
  version: "1.1"
  last_updated: "2026-10-20T15:44:18"
extends: change-review-request
---

# change-review-response

**Verdict** author (reviewer). Read the brief and the change package; write the paired response.

- The change package is the object under review.
- The brief's settled user requirements are the level 1 basis.
- Keep your own judgment: beyond the checklist, raise concerns by category.
- Keep apply for a later, separate order.

Document shape: read [FORMAT.md](../change-review-request/FORMAT.md) before writing. Pair skill: `change-review-request`.

## Handoff rules

- Same `run_dir`, same `NN`: request `change-review-request-NN.md` ↔ response `change-review-response-NN.md`.
- Request is written first; this skill produces only the response.
- Leave the change package unchanged unless the user separately orders edits.

## Basis and context

Source priority, highest first:

1. Information the user stated or confirmed — the brief's settled requirements, handoff items the user confirmed
2. Management canonical files, main OpenSpec specs, project docs
3. Discussion notes the user has not confirmed
4. The change package itself — a design blueprint that may be wrong or unclear

Keep this list the same in meaning as the master copy in `code-review` step 3.

- Context only calibrates judgment: use it to drop false positives (decided or fixed elsewhere) or confirm a real inconsistency. Never add a requirement that neither the brief nor a higher-level source asks for. Raise concerns; do not rewrite requirements.
- When the change conflicts with a higher-level source, or resolving a problem needs a user decision, record a `change-design-flaw` concern; the verdict is then at least `needs user clarify` and the next action `needs_input`. Do not pick a side. Conflicts between higher-level sources also go to the user. Keep this verdict floor the same in meaning as the master copy, the verdict rules in `change-review-request` FORMAT.
- If a source looks stale or wrong, note it under the concern or in Context consulted; do not edit the source.
- Every source is read-only; never write to one.

## Steps

### 1. Read the brief

Open the named `change-review-request-NN.md` (user path, or the latest unmatched request in the active `run_dir`). Take Meta, settled requirements, principles, checklist, and Reference paths — including Decision context sources — as the review scope.

**Done when:** expected response filename, change path, and every checklist row are known.

### 2. Read the change package

Read the change package paths the brief lists (proposal, design, tasks, named specs, and only the optional paths needed for a checklist row). Prefer evidence from those files over inventing requirements.

When in doubt, consult the brief's decision context sources read-only, highest level first. If they are not enough to judge, you may also consult, read-only, other run records, main OpenSpec specs, project docs, and `.manager/` canonical files; `.manager/_runs/` is a lead only. Record each source you consulted, whether the brief listed it, and which judgment it calibrated.

**Done when:** each checklist row has enough material for **pass** or **gap**, or stays **unclear** only after the context was consulted.

### 3. Write the verdict

Create `run_dir/change-review-response-NN.md` (same `NN` and `run_dir` as the request) using every section in [FORMAT.md](../change-review-request/FORMAT.md): Overall verdict; Checklist results; Gaps and unclear items; Reviewer concerns; Context consulted; Recommended next action.

- Overall verdict: `ready to apply` | `needs doc fix` | `needs user clarify`
- Every request checklist row gets a judgment plus evidence (change file + section, or a context source with its level)
- Reviewer concerns: categorize each per FORMAT's Concern categories as `conforms-but-flawed` (follows the change; fixable without changing intent, including change wording that can simply be amended) or `change-design-flaw` (conflicts with a higher-level source or needs a user decision), with evidence and reasoning. These definitions are shared with FORMAT and the `code-review` finding tags; keep them the same in meaning as the master copy (the `code-review` finding tags).
- Choose the verdict by FORMAT's verdict rules: every row **pass** and no concerns → `ready to apply`; any **gap** or `conforms-but-flawed` concern → `needs doc fix`; any **unclear** row or `change-design-flaw` concern → `needs user clarify`, with next action `needs_input`
- `needs user clarify` items go to the coordinating orchestrator, which resolves what it can from the information sources and escalates only the rest to the user as one consolidated list; do not address the user item by item
- Recommended next action: exactly one of `confirm dispatch` | `amend change` | `needs_input`

**Done when:** the response file exists, every checklist item has a judgment, concerns are categorized (or `none`), and the next action is explicit.

## Completion

Response exists at the path named by the request; checklist coverage is complete; Reviewer concerns and Context consulted are written; next action is stated. Stop without starting apply or editing the change.
