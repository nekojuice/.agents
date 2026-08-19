---
name: pm-status-review
description: >-
  Evidence-based project status reconciliation for the orchestrator-pm control
  plane. Use when PM mode is explicitly active and the user asks what is
  complete, what is missing, whether a milestone is done, whether bugs or gaps
  remain, or to refresh .manager/_status.md after factory or human work. It may
  coordinate read-only investigation workers but never edits product code or
  starts factory work.
disable-model-invocation: false
metadata:
  author: Codex GPT-5.6-Sol, Claude Code Opus 4.8
  version: "1.1"
  last_updated: "2026-08-18T16:01:37"
extends: orchestrator-pm, pm-investigation-worker
---

# PM Status Review

Reconcile the durable PM projection with current evidence. Treat this as a pull-based review initiated by the human, not as background monitoring.

## Contract

- Run inside explicit PM mode or with an explicit user request for PM status reconciliation.
- Read project state and delivery evidence outside `.manager`; never mutate it.
- Write detailed review evidence only inside the supplied manager run.
- Let the active PM session update canonical `.manager/_status.md` after synthesis.
- Never infer human acceptance. Record it only from an explicit human statement.
- Never run a command that creates persistent output outside the manager run without human approval.

## Required references

- Read [references/reconciliation-checklist.md](references/reconciliation-checklist.md) for evidence discovery.
- Read [references/evidence-ranking.md](references/evidence-ranking.md) before assigning confidence or completion.
- Read [references/status-transitions.md](references/status-transitions.md) before proposing state changes.

## Workflow

1. Read `.manager/_charter.md`, `_status.md`, `_milestones.md`, `_backlog.md`, and `_library/index.md`.
2. Read workspace instructions and discover the actual repositories, specification areas, factory runs, and verification artifacts. Do not assume a fixed project layout.
3. Define the review scope: whole project, milestone, capability, case, or linked factory run.
4. Compare desired outcomes with observed evidence.
5. Dispatch `pm-investigation-worker` only when evidence gathering is substantial or separable. Give every worker a run-local artifact.
6. Classify each reviewed item as unchanged, progressed, regressed, ambiguous, `completed-pm`, or explicitly `completed-human`.
7. Write a durable review artifact under the manager run when the review is non-trivial.
8. Present proposed status changes, confidence, evidence pointers, and human decisions needed.
9. Update canonical status only when the user asked for the update or confirms the proposed reconciliation. Update `_milestones.md` in the same reconciliation, changing a status only on evidence.

## Output

```text
PM_STATUS_REVIEW_V1
scope: <project | milestone | capability | case | factory-run>
reviewed_at: <timestamp>
changes:
  - item: <id or name>
    from: <prior stage or unknown>
    to: <proposed stage>
    confidence: <low | medium | high>
    evidence: <paths or human statement>
gaps: <items or none>
regressions: <items or none>
ambiguous: <items or none>
human_decisions_needed: <items or none>
artifact: <run-local path or none>
```

Stop after the reconciliation and any requested canonical update. Do not proceed into implementation.
