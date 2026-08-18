# Reconciliation Checklist

Use only sources that exist in the current workspace. Discover conventions from workspace instructions instead of assuming a fixed layout.

## Desired state

- Project charter and accepted decisions.
- Milestone and feature-progress ledger (`_milestones.md`).
- Current milestone outcome and known exclusions.
- Active case outcomes and expected behavior.
- Accepted specifications or other authoritative project documents.

## Delivery evidence

- Existing `.factory` run status and artifacts.
- Current specification or change state, when the project uses one.
- Repository history, implementation paths, and configuration.
- Existing test, build, review, verification, deployment, or E2E evidence.
- Explicit human acceptance supplied in the workspace or conversation.

## Integrity checks

- Status claims with no evidence pointer.
- Completed items whose implementation or verification is missing.
- Implemented behavior absent from the desired state.
- Factory runs that are created, active, stalled, or finished but not reflected in PM status.
- Human-accepted outcomes with later regression evidence.
- Duplicate, obsolete, or contradictory active cases.
- Gaps discovered in legacy or reference systems that have not been accepted, rejected, or deferred.

## Output discipline

Report the inspected source, observation, inference, confidence, and proposed state separately. Do not hide uncertainty in a polished status summary.
