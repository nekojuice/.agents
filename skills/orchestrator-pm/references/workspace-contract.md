# Manager Workspace Contract

## Root layout

```text
.manager/
|- .gitignore
|- _charter.md
|- _status.md
|- _milestones.md
|- _backlog.md
|- _library/
|  |- index.md
|  |- facts/
|  `- decisions/
`- _runs/
   `- <YYYY-MM-DD>-<slug>/
      |- _run.md
      |- notes.md
      |- inputs/                           (optional; original request or handoff)
      |- findings/
      |- staging/                          (optional; drafts of canonical updates)
      |- requirements-comparison.md        (optional; Non-product route)
      |- changes/                          (optional; Non-product route)
      |- reviews/                          (optional; review reports and triage)
      |- handoff-factory-<topic>.md        (optional; draft before delivery)
      |- _automation.md                    (optional; automation plan)
      `- outcome.md
```

Use lowercase English letters, digits, and hyphens in run slugs. Keep each full run path unique. Reuse an existing run only when the user is explicitly resuming the same topic.

Canonical files (`_charter`, `_status`, `_milestones`, `_backlog`, `_library/**`) are meant to be tracked by the workspace repository. Runs are working memory: keep them under `_runs/`, which is git-ignored through `.manager/.gitignore` (a single line, `_runs/`). This requires no parent directory to ignore `.manager/` itself; a nested ignore cannot re-include an already-ignored parent.

## Canonical files

Every change to these files is drafted in a run's `staging/` first and applied after the user checks the draft. Only the initialization in Enter PM mode creates them directly.

### `_charter.md`

Store durable project purpose, target state, constraints, exclusions, PM authority, human authority, and success conditions. Change it only after an explicit project-direction decision.

### `_status.md`

Store the current project projection: current milestone, active cases, known gaps, decisions needed, linked factory runs, and recently accepted outcomes. Update it only through an explicit status reconciliation or direct human request.

### `_milestones.md`

Store the durable milestone and feature-progress ledger: the milestone ledger, a feature-progress matrix across delivery axes, and an in-progress layer for work items not yet complete. It is the persistent progress map, distinct from `_status.md`'s point-in-time snapshot. Update it only during status reconciliation, and change a status only on evidence.

### `_backlog.md`

Store uncommitted questions, suspected bugs, ideas, risks, and candidate outcomes. A backlog entry is not approval to implement.

### `_library/**`

Store durable facts and decisions with provenance. `index.md` is the routing index; read detailed entries only when relevant.

## Run-local files

### `_run.md`

Store route, purpose, current position, confirmed inputs, pending questions, worker inventory, and the next action, plus any departure from this skill that the user allowed (Deviations). Make this the first file a replacement PM session reads.

### `notes.md`

Store scratch notes. Never treat notes as canonical truth.

### `inputs/`

Store the original request, a handoff from another run, or source material the user supplied.

### `findings/`

Store worker artifacts by default. Give each worker one or more unique paths; the PM may assign other unique paths inside the run when dispatching. Workers write only the assigned paths and may create their missing parent directories inside the run.

### `changes/`

Store change-decision documents for the Non-product route, named `<NN>-<target>.md`, one per edit target, with `_index.md` for batches, dependencies, and pending confirmations. Use this directory only on that route. The route's requirements comparison sits at the run root as `requirements-comparison.md`.

### `reviews/`

Store review reports and the PM's triage (`_triage.md`) for the Non-product route.

### `staging/`

Store drafts of canonical updates: an `_index.md` review index listing each change with its basis, and draft files mirroring the canonical paths they would replace. Apply a draft only after the user checks it.

### `_automation.md`

Store an automation plan from `assets/automation.template.md`: scope, factory runs with order and dependencies, the two-pass flow, commit rule, stop conditions, report points, and the user's quoted approval.

### `outcome.md`

Store the run conclusion, answered questions, proposed cases, human decisions, promoted facts or decisions, and any created factory handoff.

## Cross-party handoff files

- Handoff files between the manager and a factory always live at the factory run root: the factory's `handoff-manager-<topic>.md` in its own run, and the manager's `handoff-factory-<topic>.md` in the receiving factory run. A draft the PM discusses with the user before delivering stays at the manager run root under the same name. Use lowercase letters, digits, and hyphens.
- Start the file with three header lines: `Source run:`, `Recipient:`, and `Date:`.
- The recipient never edits the file; it records its processing in its own run.
- The cold-start `.factory` package created by `pm-factory-handoff` is not a cross-party handoff file and keeps its own control files.

## Ownership

| Area | Active PM | Investigation worker | Factory session |
| --- | --- | --- | --- |
| `.manager/_*.md` | Read/write | Read only when assigned | Read only, optional |
| `.manager/_library/**` | Read/write | Read only when assigned | Read only, optional |
| Manager runs (`_runs/**`) | Read/write | Write only assigned artifact paths in its run | Read only, optional; clues only |
| Product repositories | Read only | Read only within assignment | Owned by factory workflow |
| Non-product managed object | Write under the Non-product route | Read only within assignment | Not involved |
| `.factory/**` | Read only for status review and handoff files; create approved handoff runs, plus `.factory/.gitignore` when absent; peer files of a delegation it started; delivered `handoff-factory-<topic>.md`; `_review-queue.md` and `_issue-backlog.md` when needed, including deleting entries it picks up; read `archive/`, never write it | No access | Owned after the factory session starts |

The factory returns to the manager only through `handoff-manager-<topic>.md` at its run root, optionally announced over peer. The PM reads it on the human's instruction or a peer notice, and drafts canonical updates into `staging/`.
