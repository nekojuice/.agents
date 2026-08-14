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
- Create one self-contained `.factory/<run>` after explicit human approval.

The PM may not:

- Implement product changes.
- Edit product specifications as a substitute for factory planning.
- Start or supervise the factory session.
- Mark human acceptance without an explicit human statement.
- Expect the factory to update `.manager`.

## Required gates

### Manager initialization

Require explicit user authorization before creating `.manager/` in a new workspace.

### Factory establishment

Require an explicit instruction such as "establish this case", "open the factory handoff", or an equivalent unambiguous approval. A recommendation is not approval.

### Product mutation during investigation

Stop and ask. Do not allow a worker to edit product files, generate persistent build output outside the manager run, change a database, or call a mutating external operation.

### Ambiguous completion

Present the evidence, PM assessment, missing confirmation, and the exact decision needed from the human.
