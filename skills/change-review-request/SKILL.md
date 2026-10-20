---
name: change-review-request
description: >-
  Brief an experimental OpenSpec change-doc review: write
  change-review-request-NN.md under the factory run_dir so a reviewer can
  judge whether the change package matches settled requirements before apply.
  Use when the user invokes change-review-request (or asks to author that
  review brief).
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5, Claude Code Opus 5.5
  version: "1.1"
  last_updated: "2026-10-20T15:44:18"
extends: change-review-response
---

# change-review-request

**Brief** author (orchestrator / requester). Produce a review brief that hands a peer the change package and a checklist — **not** a product-code review, and **not** apply.

Document shape: read [FORMAT.md](FORMAT.md) before writing. Pair skill: `change-review-response`.

## Handoff rules

- Same `run_dir`, same `NN`: request `change-review-request-NN.md` ↔ response `change-review-response-NN.md`.
- Write the request first. Leave the response file for the reviewer; create it in this turn only when the user explicitly asks.
- Reviewer edits the change package only when the user separately orders those edits.

## Steps

### 1. Resolve targets

Identify:

- Factory `run_dir`: `.factory/_runs/<date>-<slug>/` (current run; create only if the user already directed a factory run there)
- Change package: `openspec/changes/<id>/` (proposal, design, tasks, relevant specs)
- Decision context sources related to this change, by source priority (highest first):
  1. Information the user stated or confirmed, including handoff items and decisions in the run written after the user confirmed them
  2. Management canonical files (under `.manager/` when it exists; read-only), main OpenSpec specs, project docs
  3. Discussion notes in the run that the user has not confirmed

  The change package itself is level 4 — the object under review. Keep this list the same in meaning as the master copy in `code-review` step 3. `.manager/_runs/` is a lead only. List these sources whether or not they ground a checklist item.
- Optional paths the brief must name: sample docs, `AGENTS.md`, archive / schema — only when they ground checklist items

**Done when:** `run_dir` and change id/path are known, and decision context sources are listed or confirmed absent.

### 2. Choose `NN`

List existing `change-review-request-*.md` in `run_dir`. Use the next two-digit number (`01` if none).

**Done when:** filename `change-review-request-NN.md` is fixed and unused.

### 3. Write the brief

Create `run_dir/change-review-request-NN.md` using every section in [FORMAT.md](FORMAT.md) (Meta; Settled user requirements; Design principles for judgment; Review checklist; Reference paths — change package, decision context sources, optional paths).

Meta must set **Expected response** to `change-review-response-NN.md` (same `NN`). Checklist rows must be answerable as **pass** / **gap** / **unclear** from the change docs alone, consulting the listed decision context sources when in doubt. Keep FORMAT's fixed invitation for reviewer concerns in §4; do not remove it.

**Done when:** the file exists at that path, cites the change package, and names the expected response filename.

## Completion

Brief exists at `run_dir/change-review-request-NN.md` and points the reviewer at the change package plus `change-review-response-NN.md`. Stop — do not write the response unless the user asks.
