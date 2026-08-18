# Factory Handoff Contract

These files are the cold-start intake for the factory's commanding agent: a fresh session that begins knowing only the project workspace and this factory run.

## Directory

Create a unique `.factory/<YYYY-MM-DD>-<slug>/`. Use lowercase English letters, digits, and hyphens. Never overwrite an unrelated run.

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

### `_status.md`

Set the handoff state to `await-factory-session`. State that factory has not started and the human must start a separate factory session. Do not identify the upstream producer.

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

Factory-facing files must not mention `.manager`, a manager run path, or PM-origin metadata. Traceability to the manager case belongs only in the manager-side outcome.
