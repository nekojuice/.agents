# Factory Intake

## Goal

<Human-approved outcome>

## Why now

<Project reason and affected cases>

## Confirmed context

- <Confirmed fact or decision>

## In scope

- <Outcome boundary>

## Explicit exclusions

- <Not part of this handoff>

## Constraints

- <Constraint>

## Evidence and project paths

- `<path>` - <relevance>

## Open questions for factory discussion

- <Question or none>

## Verification intent

- <Observable result>

## Source (optional)

- <Manager run and candidate id; optional clue only, never required reading>

## Human checkpoints

- Review factory discussion and proposed changes before dispatch.
- Perform human E2E before final acceptance.

## Delegation (when the PM started this delegation)

- User approval: <user's statement and date>
- Peer room: <this run directory, or none if the user declined peer>

## Automation authorization (only under an approved automation plan)

- Approval: <user's quoted approval and date>
- Batch: <this run's order among the batch's runs>; the user reviews all changes of the batch in one gate before building
- Dispatch: after that review, confirmed runs are dispatched in order without a separate confirmation, including Check and agent E2E review
- E2E write permission: <read-only | test data the user allows>; reviewers left out: <none | Check | E2E>
- Commit: <one commit when this run reaches await-e2e | other rule | none>; never push
- Depends on: <earlier runs in the batch, or none>
- Stop conditions: <beyond the factory's own, or none>
- Human E2E and sync/archive: after the whole batch
