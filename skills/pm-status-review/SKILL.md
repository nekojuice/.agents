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
  version: "1.3"
  last_updated: "2026-11-02T12:17:40"
extends: orchestrator-pm, pm-investigation-worker
---

# PM Status Review

Reconcile the durable PM projection with current evidence. Treat this as a pull-based review started by the human or by a factory's peer notice, not as background monitoring.

## Contract

- Run inside explicit PM mode or with an explicit user request for PM status reconciliation.
- Read project state and delivery evidence outside `.manager`; never mutate it.
- Write detailed review evidence only inside the supplied manager run.
- Let the active PM session draft canonical updates into the run's `staging/` after synthesis and apply them only after the user checks the draft.
- Never infer human acceptance. Record it only from an explicit human statement.
- Never run a command that creates persistent output outside the manager run without human approval.
- Read a factory run's `handoff-manager-*.md` read-only, on the human's instruction or a peer notice. Record how it was processed (adopted, canonical correction, new intake item) in the current manager run. Draft every resulting correction — status, milestones, library, backlog, charter — into `staging/`. Route only new questions or candidates to `pm-intake-triage`; never write back to the factory run or modify the handoff file.
- The factory may write more than the manager needs; filter instead of adopting wholesale. Keep decisions that affect direction or scope, progress with evidence, new candidates and out-of-scope findings, blockers, and corrections to stale `.manager` content. Record spec content only as opsx change ids; drop implementation detail.

## Required references

- Read [references/reconciliation-checklist.md](references/reconciliation-checklist.md) for evidence discovery.
- Read [references/evidence-ranking.md](references/evidence-ranking.md) before assigning confidence or completion.
- Read [references/status-transitions.md](references/status-transitions.md) before proposing state changes.

## Workflow

1. Read `.manager/_charter.md`, `_status.md`, `_milestones.md`, `_backlog.md`, and `_library/index.md`.
2. Read workspace instructions and discover the actual repositories, specification areas, factory runs, and verification artifacts, including any `handoff-manager-*.md` at a factory run's root. Do not assume a fixed project layout. Do not assume a factory reported everything: when a factory run has no handoff or an incomplete one, use its `_status.md` and git history as evidence.
3. Define the review scope: whole project, milestone, capability, case, or linked factory run.
4. Compare desired outcomes with observed evidence.
5. Dispatch `pm-investigation-worker` only when evidence gathering is substantial or separable. Give every worker a run-local artifact.
6. Classify each reviewed item as unchanged, progressed, regressed, ambiguous, `completed-pm`, or explicitly `completed-human`.
7. Write a durable review artifact under the manager run when the review is non-trivial.
8. Present proposed status changes, confidence, evidence pointers, and human decisions needed.
9. Draft the `_status.md` and `_milestones.md` updates into `staging/`, changing a milestone status only on evidence, and apply them only after the user checks the draft, including reconciliations the user requested.

## Baseline crawl

Run this variant when orchestrator-pm first enters PM mode on a workspace that already holds project state and the user has consented to the crawl, including any scope limit. It differs from the workflow above as follows:

- Step 1 confirms that the canonical files were just instantiated from templates. Template placeholders are not evidence.
- The scope is the whole project, within the user's scope limit.
- Dispatch read-only `pm-investigation-worker` assignments by area: code, specifications, change documents, and existing factory runs, including their `handoff-manager-*.md`.
- Record every item's `from` as `unknown`. Assign a stage only from evidence; mark items with insufficient evidence as ambiguous.
- Under the orchestrator-pm entry rule, consent to the crawl counts as the request to produce the first `_status.md` and `_milestones.md`; draft them into `staging/` and write them after the user checks the draft.
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
staging: <run-local path or none>
```

Stop after the reconciliation and its `staging/` draft, or after applying the draft once the user has checked it. Do not proceed into implementation.
