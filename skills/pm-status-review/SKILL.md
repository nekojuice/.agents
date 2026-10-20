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
  author: Codex GPT-5.6-Sol, Claude Code Opus 4.8, Claude Code Opus 5.5
  version: "1.2"
  last_updated: "2026-10-20T16:00:57"
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
- Read a factory run's `handoff-manager-*.md` read-only. Record how it was processed (adopted, canonical correction, new intake item) in the current manager run. Status and milestone corrections stay in this review. List corrections to the library, backlog, or charter in the review output; the PM drafts them as a manager update in the current run and applies them only after the user checks the draft. Route only new questions or candidates to `pm-intake-triage`; never write back to the factory run or modify the handoff file.

## Required references

- Read [references/reconciliation-checklist.md](references/reconciliation-checklist.md) for evidence discovery.
- Read [references/evidence-ranking.md](references/evidence-ranking.md) before assigning confidence or completion.
- Read [references/status-transitions.md](references/status-transitions.md) before proposing state changes.

## Workflow

1. Read `.manager/_charter.md`, `_status.md`, `_milestones.md`, `_backlog.md`, and `_library/index.md`.
2. Read workspace instructions and discover the actual repositories, specification areas, factory runs, and verification artifacts, including any `handoff-manager-*.md` at a factory run's root. Do not assume a fixed project layout.
3. Define the review scope: whole project, milestone, capability, case, or linked factory run.
4. Compare desired outcomes with observed evidence.
5. Dispatch `pm-investigation-worker` only when evidence gathering is substantial or separable. Give every worker a run-local artifact.
6. Classify each reviewed item as unchanged, progressed, regressed, ambiguous, `completed-pm`, or explicitly `completed-human`.
7. Write a durable review artifact under the manager run when the review is non-trivial.
8. Present proposed status changes, confidence, evidence pointers, and human decisions needed.
9. Update canonical status only when the user asked for the update or confirms the proposed reconciliation. Update `_milestones.md` in the same reconciliation, changing a status only on evidence.

## Baseline crawl

Run this variant when orchestrator-pm first enters PM mode on a workspace that already holds project state and the user has consented to the crawl, including any scope limit. It differs from the workflow above as follows:

- Step 1 confirms that the canonical files were just instantiated from templates. Template placeholders are not evidence.
- The scope is the whole project, within the user's scope limit.
- Dispatch read-only `pm-investigation-worker` assignments by area: code, specifications, change documents, and existing factory runs, including their `handoff-manager-*.md`.
- Record every item's `from` as `unknown`. Assign a stage only from evidence; mark items with insufficient evidence as ambiguous.
- Under the orchestrator-pm entry rule, consent to the crawl counts as the request to write the first `_status.md` and `_milestones.md`.
- The crawl does not settle charter direction; it only informs the charter discussion.
- Write crawl artifacts inside the run. Output `scope: project` and note in the artifact that it is a baseline.

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
manager_corrections: <library, backlog, or charter corrections from handoff files, or none>
artifact: <run-local path or none>
```

Stop after the reconciliation and any requested canonical update. Do not proceed into implementation.
