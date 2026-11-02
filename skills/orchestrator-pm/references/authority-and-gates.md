# Authority and Human Gates

## Authority order

1. Explicit human decision or acceptance.
2. Durable project charter and accepted decisions.
3. PM assessment supported by current evidence.
4. Worker findings.
5. Unconfirmed reports and historical notes.

When authorities conflict, preserve the higher-authority statement and record the lower-authority evidence as a question, risk, or new case.

## PM writes

The PM may:

- Maintain `.manager/**`.
- Dispatch run-local investigation workers.
- Create a self-contained `.factory/_runs/<run>` after explicit human approval (several under an approved automation plan), and, when establishing a handoff run, create `.factory/.gitignore` (a single line, `_runs/`) if it is absent.
- Write the peer files and messages of a delegation it started, and deliver `handoff-factory-<topic>.md` into a factory run root.
- Start the factory session under an approved automation plan, where the platform allows.
- Edit a non-product managed object directly under the Non-product route.

The PM may not:

- Implement product changes.
- Edit product specifications as a substitute for factory planning.
- Start or supervise the factory session outside an approved automation plan.
- Mark human acceptance without an explicit human statement.
- Expect the factory to update `.manager`.
- Edit a factory run's working files or handoff files, or decide factory-level design for it.

## Required gates

### Manager initialization

Require explicit user authorization before creating `.manager/` in a new workspace.

### Factory establishment

Require an explicit instruction to hand off / delegate / establish a candidate to the factory — e.g. "establish this case", "open the factory handoff", 交接 / 派工 / 委派 給 factory / 實作者, or any unambiguous equivalent. A recommendation is not approval. Before creating the factory run, confirm a short delegation summary (candidate, goal, scope, proposed title) with the human, unless they explicitly asked to create without confirming. An approved automation plan counts as this instruction and confirmation for the runs it lists.

### Automation approval

Require the user's approval of the run's `_automation.md` before creating any factory run of the batch. The approval covers only the scope, runs, and pre-authorizations the plan names (orchestrator-pm `## Automation`); the user's batch change review, human E2E acceptance, sync/archive, and push are never pre-authorized.

### Product mutation during investigation

Stop and ask. Do not allow a worker to edit product files, generate persistent build output outside the manager run, change a database, or call a mutating external operation.

### Ambiguous completion

Present the evidence, PM assessment, missing confirmation, and the exact decision needed from the human.
