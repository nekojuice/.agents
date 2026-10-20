# Factory Handoff Contract

These files are the cold-start intake for the factory's commanding agent: a fresh session that begins knowing only the project workspace and this factory run.

## Directory

Create a unique `.factory/_runs/<YYYY-MM-DD>-<slug>/`, initializing `.factory/.gitignore` with the single line `_runs/` when it does not exist. Use lowercase English letters, digits, and hyphens. Never overwrite an unrelated run.

This cold-start package is the new factory run's own control files. It does not use the cross-party `handoff-<recipient>-<topic>.md` naming, which applies to handoff files left at a sender run's root.

## Required files

### `_intake.md`

Provide:

- Goal and business or project reason.
- Confirmed context.
- In-scope outcomes.
- Explicit exclusions.
- Constraints and accepted decisions.
- Evidence and relevant project paths.
- Open questions the factory discussion must resolve.
- Expected verification and human checkpoints.
- Optional source: the manager run and candidate id, labeled as an optional clue that the factory never needs to read.

### `_status.md`

Set the handoff state to `await-factory-session`. State that factory has not started and the human must start a separate factory session.

### `_memory.md`

Provide only short shared facts that every later factory worker may need. Do not copy the full intake or PM history.

## Independence test

A fresh session that knows only the project workspace and this factory run must understand:

- Why the work may be needed.
- What is confirmed.
- What is excluded.
- What remains to discuss.
- What the human has and has not approved.

If it must read `.manager` or the PM chat, the handoff is incomplete.

Formal traceability to the manager case is recorded in the manager-side outcome. Any manager reference inside factory-facing files is only a clue.
