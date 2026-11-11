---
name: skill-feedback-notes
description: >-
  Records skill feedback notes during factory, manager, or helper work (and in a worker the
  orchestrator authorized) whenever the work involves changing a skill, making a skill, or
  tracking a skill's quality; handles the notes at closing by handing them to the manager that
  revises skills, and records a comparison of a new skill version against the old one when a
  session holds both. Use when that work involves such intent, whether stated or implied. Not
  for ordinary work that merely uses a skill without any such intent.
disable-model-invocation: false
metadata:
  author: Claude Code Opus 5.5
  version: "1.0"
  last_updated: "2026-11-11T10:02:59"
---

# skill-feedback-notes

Corrections a user gives while a skill is in use are the raw material for improving that skill. Keep them in one notes file, hand them to whoever revises the skill at closing, and record how a revised version behaves when a session can compare it with the old one.

## When to record

Start when the work involves changing a skill, making a skill, or tracking a skill's quality, whether the user says so or the task is about it. Create the notes file when the first item worth recording appears. Keep one notes file per run or workspace.

## Where

- **Factory** — `run_dir/_skill-notes.md`.
- **Manager** — `skill-notes.md` at the run root.
- **Helper** — `skill-notes.md` in its own workspace, next to its context file. When hosted in another role's run, use that run's notes file unless the contract says otherwise.
- **Worker** — record only when the orchestrator's assignment authorizes it. Put the entries in the return; the orchestrator writes them into its notes file.

## What to record

One entry per item:

- the situation;
- what the agent did;
- what the user wanted;
- the user's own words;
- the reason, only when the user gave one;
- the skill involved and its version.

Prefer the user's corrections, problems that recur, and principles the user states. Leave out ordinary progress. Aim for the important items, but do not hold back an entry for being minor; whoever revises the skill filters the noise.

## At closing

When the notes file has entries, closing must handle it, alongside the role's other closing items:

- **Hand off (default)** — write `handoff-skill-<topic>.md` at the run or workspace root, carrying the entries. It starts with three header lines: `Source run:`, `Recipient:` (the manager of the skill repository), `Date:`. Write liberally; the recipient filters. Names use lowercase letters, digits, and hyphens. Write it once per closing and never append to it; later entries go in a new handoff. Tell the user its path: the user carries it to the skill repository's manager.
- **Defer or discard** — only when the user says so. Record the choice in the state file: `_status.md` for a factory, `_run.md` for a manager, the context file for a helper. List deferred notes as reminders at later checkpoints, not as new decisions.

A manager run that is itself revising skills uses its notes directly as input to the Non-product route's requirements comparison and writes no handoff.

## Receiving a handoff

The manager of the skill repository stores the handoff in its run's `inputs/` and starts the Non-product route from the requirements comparison. Generalizing the notes happens there: project content stays in runs and never reaches a skill or the manager's canonical files.

For a complex revision, the session holding the full context may, on the user's instruction, enter the skill repository in manager mode and run the Non-product route itself.

## Verification

Verification is optional. Run it only when a session holds the memory or context of both the old and the new version of a skill and is comparing them:

1. Re-read the new version of the skill; do not rely on the copy loaded earlier.
2. Compare how the work goes under the new version with the old.
3. Record the result as an entry: improved, not improved, or side effects.

When the user reports during the work that a revision did or did not help, record that as an entry too. Verification entries go through the same closing.
