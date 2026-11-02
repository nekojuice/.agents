# Non-product Route

Steps for editing a non-product managed object directly. Default steps run unless their skip condition applies. Record each stage change in the run; canonical status changes go through `staging/` (section 7).

## 1. Requirements comparison (default)

- Decompose the request; `explain` may be used. Compare it with the managed object's current content and with any decomposition the library keeps. List conflicts and design suggestions, and restate the request.
- Write `requirements-comparison.md` at the run root from [../assets/requirements-comparison.template.md](../assets/requirements-comparison.template.md). Number every item; the conflict and design tables carry a user column.
- Supporting evidence from other workspaces is optional and goes to `findings/`; project content stays in the run.
- May skip: a small edit to a single target with a clear request.

## 2. Settle with the user

- Record each round of the user's replies as a dated reply section. Never rewrite an earlier answer.
- Write change decisions only after every open item is settled.

## 3. Change decisions

- One document per target under `changes/`, from [../assets/change-decision.template.md](../assets/change-decision.template.md).
- `changes/_index.md` lists batches, dependencies, a manager-impact summary, and any question that comes up while writing the decisions.

## 4. Edit

- Edit after the user reviews the change decisions and instructs the edit. Follow the managed object's own authoring rules, such as version and timestamp updates.
- The item enters `in-delivery`.

## 5. Review (default)

- Dispatch reviewers that follow `code-review`, grouped by target and run in parallel where possible. Basis order: the user's settled answers, then library decisions, then the change decisions. The fixed point is the state before the edit.
- Triage every finding into `reviews/_triage.md` from [../assets/review-triage.template.md](../assets/review-triage.template.md): adopt, adopt in part, or reject with the basis for a false positive. Reviewers lack context, so never adopt a finding unchecked.
- Discuss findings that need the user before fixing. Re-check only what the fix touched, until no new findings remain.
- A low-severity wording fix within a settled direction may skip the re-check; record it in the triage.
- A necessary edit outside the original scope gets an added change decision. Annotate a superseded design in the older change decision instead of rewriting it.
- May skip: the user declines review, or the edit only changes wording.

## 6. User review

The user reviews the edit through git diff, or an equivalent before/after diff when the managed object is not version-controlled. The item enters `verifying`.

## 7. Manager impact

- Draft every canonical update into `staging/`: the change decisions' manager impact, and status and milestone proposals through `pm-status-review`. When the library keeps a decomposition of the managed object, re-decompose the edited parts from the new text and include it.
- The user checks the draft once; then apply it.

## 8. Commit and close

- Commit only when the user asks: the managed object and canonical manager files in separate commits unless the user says otherwise. Never push unless asked.
- Close the run per run-lifecycle, or split off a topic into a new run.
