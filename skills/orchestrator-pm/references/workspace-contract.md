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
      |- findings/
      |- changes/                          (optional; Non-product route)
      |- handoff-<recipient>-<topic>.md    (optional; cross-party handoff)
      `- outcome.md
```

Use lowercase English letters, digits, and hyphens in run slugs. Keep each full run path unique. Reuse an existing run only when the user is explicitly resuming the same topic.

Canonical files (`_charter`, `_status`, `_milestones`, `_backlog`, `_library/**`) are meant to be tracked by the workspace repository. Runs are working memory: keep them under `_runs/`, which is git-ignored through `.manager/.gitignore` (a single line, `_runs/`). This requires no parent directory to ignore `.manager/` itself; a nested ignore cannot re-include an already-ignored parent.

## Canonical files

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

Store purpose, current position, confirmed inputs, pending questions, worker inventory, and the next action. Make this the first file a replacement PM session reads.

### `notes.md`

Store scratch notes. Never treat notes as canonical truth.

### `findings/`

Store worker artifacts by default. Give each worker one or more unique paths; the PM may assign other unique paths inside the run when dispatching. Workers write only the assigned paths and may create their missing parent directories inside the run.

### `changes/`

Store change-decision documents for the Non-product route, named `<NN>-<target>.md`, one per edit target. Use this directory only on that route.

### `outcome.md`

Store the run conclusion, answered questions, proposed cases, human decisions, promoted facts or decisions, and any created factory handoff.

## Cross-party handoff files

- Place a cross-party handoff file at the sender's run root, named `handoff-<recipient>-<topic>.md` with lowercase letters, digits, and hyphens.
- Start the file with three header lines: `Source run:`, `Recipient:`, and `Date:`.
- The recipient records its processing in its own run and never writes back to the sender's run.
- Process a factory's `handoff-manager-<topic>.md` under these rules; apply the same rules when the PM sends one.
- The cold-start `.factory` package created by `pm-factory-handoff` is not a cross-party handoff file and keeps its own control files.

## Ownership

| Area | Active PM | Investigation worker | Factory session |
| --- | --- | --- | --- |
| `.manager/_*.md` | Read/write | Read only when assigned | Read only, optional |
| `.manager/_library/**` | Read/write | Read only when assigned | Read only, optional |
| Manager runs (`_runs/**`) | Read/write | Write only assigned artifact paths in its run | Read only, optional; clues only |
| Product repositories | Read only | Read only within assignment | Owned by factory workflow |
| Non-product managed object | Write under the Non-product route | Read only within assignment | Not involved |
| `.factory/**` | Read only for status review and handoff files; create approved handoff only, plus `.factory/.gitignore` when absent | No access | Owned after human starts factory |

Do not create a callback, event, or reverse dependency from factory to manager. The only return channel is a `handoff-manager-<topic>.md` at a factory run root, which the PM pulls when the human instructs.
