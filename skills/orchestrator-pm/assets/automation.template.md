# Automation Plan

Status: proposed | approved | design | change-review | build | ended

## Approval

- <User's quoted approval and date; empty until approved>

## Scope

- <Backlog item or case the batch covers>

## Factory runs

| Order | Factory run | Goal | Depends on |
| --- | --- | --- | --- |
| 1 | `.factory/_runs/<YYYY-MM-DD>-<slug>/` | <goal> | none |

## Flow

- Design pass: every run goes through discussion, propose, and change-doc review; unsettled decisions are listed per run.
- Batch change review: the user reviews all changes and each run's pending decisions in one gate.
- Build pass: confirmed runs are dispatched in dependency order without a separate dispatch confirmation.

## Commit

- <One commit per factory run (default) | other rule the user set | none>
- Never push without the user's separate explicit authorization.

## Stop conditions

- <Conditions beyond the factory's own stop rules, or none>

## Report points

- Each factory run reaching await-e2e: manager handoff, drafted into `staging/`.
- <Other point, or none>

## End of batch

- Factory consolidates `.factory/_review-backlog.md`; the user runs E2E once; sync/archive follows.
