# Manager Run Lifecycle

## Create

Create a manager run when work needs durable notes, multiple evidence sources, workers, or a later-session continuation. Do not create a run for a short read-only answer that leaves no durable project effect.

1. Choose `.manager/_runs/<YYYY-MM-DD>-<slug>/`.
2. Confirm the path is unique.
3. Instantiate `_run.md`, `notes.md`, and `outcome.md` from the supplied assets.
4. Create `findings/` before dispatching workers.
5. On the Non-product route, create `changes/` before editing the managed object.
6. Record the starting objective and source inputs in `_run.md`.

## Work

- Update `_run.md` after a material decision, worker batch, or context boundary.
- Keep worker details at their assigned run paths (default `findings/`) and point to them from `_run.md`.
- Keep chat as a concise rollup.
- Treat assumptions as pending until confirmed.

## Replace the PM session

A replacement PM session must:

1. Read manager root state.
2. Read the named run's `_run.md`.
3. Read only the findings and references named by `_run.md`, and `_automation.md` when the run has one.
4. State the recovered objective, current position, and next action before continuing.

Do not rely on the previous chat transcript or on a persistent agent identity. In a peer room the PM hosts, replace the old PM `canonical_id` in the roster and note the change in `_communication-notes.md`.

## Conclude

1. Write `outcome.md` with answers, case decisions, unresolved items, and human approvals.
2. Promote only confirmed facts, decisions, backlog entries, or status changes, drafted in `staging/` and applied after the user checks them; status and milestone proposals come from `pm-status-review` into the same `staging/`. On the Non-product route, see that route's section 7. Record every cross-party handoff file processed in this run in `outcome.md`.
3. Mark `_run.md` as concluded and point to `outcome.md`.
4. Keep the run as audit history; do not treat its scratch notes as current truth.

## Split off a topic

When a topic should continue in its own run, create the new run and write its `inputs/handoff.md`: background, current state, suggested direction, and dependencies on the source run. Record the split in the source run's `outcome.md`.
