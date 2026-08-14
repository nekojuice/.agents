---
name: pm-factory-handoff
description: >-
  Human-gated PM handoff that creates a self-contained .factory run for a
  separately started factory session. Use only after the human explicitly
  approves establishing a specific PM candidate. Distill confirmed context by
  value, exclude .manager dependencies and scratch notes, record the handoff in
  the manager run, and stop without loading orchestrator-factory or starting
  any factory worker.
disable-model-invocation: true
metadata:
  author: Codex GPT-5.6-Sol
  version: "1.0"
  last_updated: "2026-08-14T13:29:50"
extends: orchestrator-pm
---

# PM Factory Handoff

Create a clean implementation intake for a future factory session. PM authority is upstream of factory, but the two workspaces remain operationally isolated.

## Preconditions

Require all of the following:

- An explicit human instruction to establish one identified candidate.
- A current manager run with a documented candidate outcome.
- Enough confirmed scope to explain why the factory session should begin.
- No unresolved contradiction that would make the handoff misleading.

A PM recommendation, candidate label, or tentative discussion is not approval.

## Hard rules

- Do not load or invoke `orchestrator-factory`.
- Do not start workers, propose implementation, edit product files, or cross any factory gate.
- Do not require the future factory session to read `.manager`.
- Do not mention `.manager`, manager run paths, or PM-origin metadata inside factory-facing files.
- Do not copy scratch notes, worker transcripts, unconfirmed assumptions, or the PM library wholesale.
- Do not overwrite an existing factory run. Reuse it only when the human explicitly resumes the same handoff.
- After creating the handoff, record it in the current manager run and stop.

## Required references

- Read [references/handoff-contract.md](references/handoff-contract.md) for the required factory intake.
- Read [references/context-sanitization.md](references/context-sanitization.md) before transferring any PM material.

## Workflow

1. Verify and quote the human approval in the manager run outcome.
2. Resolve a unique `.factory/<YYYY-MM-DD>-<slug>/` path.
3. Distill the candidate into confirmed goal, context, scope, exclusions, constraints, evidence, open questions, and expected human checkpoints.
4. Instantiate `_intake.md`, `_status.md`, and `_memory.md` from this skill's assets.
5. Remove manager paths, PM-origin metadata, and PM-only terminology from every factory-facing file.
6. Validate that the handoff is useful in a fresh session with no PM chat history.
7. Record the factory run path in the current manager run's `outcome.md`. Do not update canonical project status unless the human separately requested a reconciliation.
8. Tell the human that the handoff is ready for a new factory session, then stop.

## Output

```text
PM_FACTORY_HANDOFF_V1
candidate: <PM candidate id>
factory_run: <.factory path>
approval: <human statement and date>
files:
  - _intake.md
  - _status.md
  - _memory.md
manager_outcome: <path>
factory_started: false
```
