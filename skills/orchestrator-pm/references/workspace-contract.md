# Manager Workspace Contract

## Root layout

```text
.manager/
|- _charter.md
|- _status.md
|- _backlog.md
|- _library/
|  |- index.md
|  |- facts/
|  `- decisions/
`- <YYYY-MM-DD>-<slug>/
   |- _run.md
   |- notes.md
   |- findings/
   `- outcome.md
```

Use lowercase English letters, digits, and hyphens in run slugs. Keep each full run path unique. Reuse an existing run only when the user is explicitly resuming the same topic.

## Canonical files

### `_charter.md`

Store durable project purpose, target state, constraints, exclusions, PM authority, human authority, and success conditions. Change it only after an explicit project-direction decision.

### `_status.md`

Store the current project projection: current milestone, active cases, known gaps, decisions needed, linked factory runs, and recently accepted outcomes. Update it only through an explicit status reconciliation or direct human request.

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

Store worker artifacts. Give each worker one unique file. Workers may create missing files below this directory but may not write elsewhere.

### `outcome.md`

Store the run conclusion, answered questions, proposed cases, human decisions, promoted facts or decisions, and any created factory handoff.

## Ownership

| Area | Active PM | Investigation worker | Factory session |
| --- | --- | --- | --- |
| `.manager/_*.md` | Read/write | Read only when assigned | No knowledge required |
| `.manager/_library/**` | Read/write | Read only when assigned | No knowledge required |
| Current manager run | Read/write | Write only assigned artifact | No knowledge required |
| Product repositories | Read only | Read only within assignment | Owned by factory workflow |
| `.factory/**` | Create approved handoff only | No access | Owned after human starts factory |

Do not create a callback, event, or reverse dependency from factory to manager.
