---
name: pm-factory-handoff
description: >-
  Human-gated PM handoff that creates a self-contained .factory run for a
  separately started factory session, or several runs under an automation plan
  the user approved. Use only after the human explicitly approves establishing
  a specific PM candidate or the plan. Distill confirmed context by value,
  exclude .manager dependencies and scratch notes, record the handoff in the
  manager run, and stop (under an automation plan, notify or start the factory
  session instead) without loading orchestrator-factory or starting any
  factory worker.
disable-model-invocation: false
metadata:
  author: Codex GPT-5.6-Sol, Claude Code Opus 5.5
  version: "1.5"
  last_updated: "2026-11-04T15:52:52"
extends: orchestrator-pm
---

# PM Factory Handoff

Create a clean, self-contained cold-start intake that the factory's commanding agent reads to begin factory work on this run. Every file written here is that cold-start handoff package, not PM working memory, except the peer files of workflow step 6, which follow `peer-agent-coordination`. PM authority is upstream of factory, but the two workspaces remain operationally isolated.

## Preconditions

Require all of the following:

- An explicit human instruction to hand off / delegate / establish one identified candidate to the factory (implementer), or a user-approved automation plan (orchestrator-pm `## Automation`) that lists the candidates. Equivalent wording counts — 交接 / 派工 / 委派 給 工廠 / factory / 實作者, or any unambiguous equivalent.
- A current manager run with a documented candidate outcome.
- Enough confirmed scope to explain why the factory session should begin.
- No unresolved contradiction that would make the handoff misleading.

A PM recommendation, candidate label, or tentative discussion is not approval.

## Hard rules

- Do not load or invoke `orchestrator-factory`.
- Do not start workers, propose implementation, edit product files, or cross any factory gate.
- Do not require the future factory session to read `.manager`. Factory-facing files may mention `.manager` as optional read-only background, but every required fact must be written into the handoff by value. Never instruct the factory to write into `.manager`.
- Do not copy scratch notes, worker transcripts, unconfirmed assumptions, or the PM library wholesale.
- Do not overwrite an existing factory run. Reuse it only when the human explicitly resumes the same handoff. Further matters for an existing run follow orchestrator-pm `## Delegation`: a peer message, or `handoff-factory-<topic>.md` at its root, never other files.
- After creating the handoff, record it in the current manager run and stop, staying reachable in a peer room per orchestrator-pm `## Stop`. Under an automation plan, continue per workflow step 10.

## Required references

- Read [references/handoff-contract.md](references/handoff-contract.md) for the required factory intake.
- Read [references/context-sanitization.md](references/context-sanitization.md) before transferring any PM material.

## Workflow

1. Verify and quote the human approval in the manager run outcome.
2. Present a short delegation summary — candidate, goal, scope boundary, and the proposed factory run title/slug — and get the human's confirmation before creating any factory files. Skip this confirmation only when the human explicitly directed immediate creation without confirming (e.g. "直接建立、不確認" / "create directly, no confirm"), or when an approved automation plan already lists the run.
3. Resolve a unique `.factory/_runs/<YYYY-MM-DD>-<slug>/` path. If `.factory/.gitignore` does not exist, create it with the single line `_runs/`.
4. Distill the candidate into confirmed goal, context, scope, exclusions, constraints, evidence, open questions, and expected human checkpoints.
5. Instantiate `_intake.md`, `_status.md`, and `_memory.md` from this skill's assets — this is the cold-start package the factory's commanding agent reads to begin work on this run. Under an automation plan, fill `_intake.md` `## Automation authorization` by value.
6. A delegation the PM starts uses peer by default: create the room in the factory run per `peer-agent-coordination`, with the PM as host, and record in `_intake.md` that the user approved the delegation and the room path (orchestrator-pm `## Delegation`). Skip the room only when the user declines peer; `peer_room` is then none.
7. Confirm that no required content exists only in `.manager` (restate it by value), remove PM-only terminology the factory could not understand without reading `.manager`, and label every remaining manager reference as optional.
8. Validate that the handoff is useful in a fresh session with no PM chat history.
9. Record the factory run path in the current manager run's `outcome.md`. Do not update canonical project status unless the human separately requested a reconciliation, and then only through `staging/`.
10. Report the factory run path to the human. Outside automation, state the handoff is ready for a new factory session, then stop per orchestrator-pm `## Stop`. Under automation, notify the factory session over peer when the design pass reaches this run, or start the session per orchestrator-pm `## Automation`.

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
peer_room: <factory run path or none>
factory_session: <user starts | notified | started by PM>
```
