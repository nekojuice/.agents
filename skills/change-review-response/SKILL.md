---
name: change-review-response
description: >-
  Verdict an experimental OpenSpec change-doc review: read
  change-review-request-NN.md and the cited change package, then write
  matching change-review-response-NN.md with checklist judgments and a next
  action. Use when the user invokes change-review-response (or asks to answer
  that review brief).
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5
  version: "1.0"
  last_updated: "2026-07-27T17:21:16"
  extends: change-review-request
---

# change-review-response

**Verdict** author (reviewer). Read the brief and the change package; write the paired response — **change docs only** unless the request says otherwise. Stay on settled requirements from the brief; keep apply for a later, separate order.

Document shape: read [FORMAT.md](../change-review-request/FORMAT.md) before writing. Pair skill: `change-review-request`.

## Handoff rules

- Same `run_dir`, same `NN`: request `change-review-request-NN.md` ↔ response `change-review-response-NN.md`.
- Request is written first; this skill produces only the response.
- Leave the change package unchanged unless the user separately orders edits.

## Steps

### 1. Read the brief

Open the named `change-review-request-NN.md` (user path, or the latest unmatched request in the active `run_dir`). Take Meta, settled requirements, principles, checklist, and Reference paths as the review scope.

**Done when:** expected response filename, change path, and every checklist row are known.

### 2. Read the change package

Read the Reference paths the brief lists (proposal, design, tasks, named specs, and only the optional paths needed for a checklist row). Prefer evidence from those files over inventing requirements.

**Done when:** each checklist row has enough material for **pass**, **gap**, or **unclear**.

### 3. Write the verdict

Create `run_dir/change-review-response-NN.md` (same `NN` and `run_dir` as the request) using every section in [FORMAT.md](../change-review-request/FORMAT.md): Overall verdict; Checklist results; Gaps and unclear items; Recommended next action.

- Overall verdict: `ready to apply` | `needs doc fix` | `needs user clarify`
- Every request checklist row gets a judgment plus evidence (change file + section)
- Recommended next action: exactly one of `confirm dispatch` | `amend change` | `needs_input`

**Done when:** the response file exists, every checklist item has a judgment, and the next action is explicit.

## Completion

Response exists at the path named by the request; checklist coverage is complete; next action is stated. Stop without starting apply.
