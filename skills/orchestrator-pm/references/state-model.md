# PM State Model

## Work item types

Use one of these types and keep the original user language in the description:

- `question`: can be answered without product change.
- `suspected-bug`: reported behavior is not yet confirmed as a defect.
- `confirmed-bug`: evidence shows behavior violates an accepted expectation.
- `design-concern`: current behavior works as designed but the design is harmful or inadequate.
- `initiative`: a desired project outcome or capability direction.
- `risk`: a condition that may harm delivery or operation.

## Work item stages

Use the smallest stage that truthfully represents the evidence:

```text
inbox
-> investigating
-> answered | candidate | deferred | rejected
candidate
-> approved-for-factory
-> handed-off
-> in-delivery
-> verifying
-> completed-pm | completed-human
```

Not every item follows every stage. A question may move directly from `investigating` to `answered`. A rejected or deferred item must keep its reason.

## Required fields

Every active item should have:

- Stable PM identifier.
- Type.
- Desired outcome or question.
- Current stage.
- Evidence summary and source pointers.
- Confidence: `low`, `medium`, or `high`.
- Related items.
- Related factory run, when known.
- Next human checkpoint or next investigation action.

## Milestones

Treat milestones as outcome groups, not task containers. Track:

- Intended outcome.
- Included active items or capabilities.
- Known exclusions.
- Current evidence.
- PM completion assessment.
- Human acceptance, when supplied.

Do not infer percentage completion when the set of undiscovered work may still change.

## Progress ledger

Maintain milestones and feature progress in canonical `_milestones.md`, carrying three layers: the milestone ledger, a feature-progress matrix across delivery axes, and an in-progress layer for work items not yet complete.

Ledger display statuses project the work-item stages above; they are not a second vocabulary:

| Glyph | Meaning | Stage source |
| --- | --- | --- |
| ✅ | done | `completed-pm` or `completed-human` |
| 🟡 | in progress | `investigating`, `approved-for-factory`, `handed-off`, `in-delivery`, or `verifying` |
| ⬜ | not started | `inbox` or `candidate` |
| ⚠️ | transitional | any stage, flagged as a usable stand-in pending the proper solution |

Change a ledger status only on evidence, during status reconciliation. Prefer these evidence-backed states over invented completion percentages.
