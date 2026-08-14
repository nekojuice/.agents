---
name: pm-intake-triage
description: >-
  PM intake workflow for classifying and consolidating user questions, customer
  feedback, suspected bugs, design concerns, risks, and initiative ideas. Use
  only within explicit orchestrator-pm mode when one or many incoming items
  must be answered, investigated, grouped by root cause, deferred, rejected, or
  proposed as factory candidates without automatically establishing factory
  work.
disable-model-invocation: true
metadata:
  author: Codex GPT-5.6-Sol
  version: "1.0"
  last_updated: "2026-08-14T13:29:50"
extends: orchestrator-pm, pm-investigation-worker, pm-factory-handoff
---

# PM Intake Triage

Turn mixed incoming reports into answers, bounded investigations, and coherent project-level candidates. Preserve the user's original meaning while reducing duplication and unnecessary factory work.

## Hard rules

- Do not equate one report with one factory candidate.
- Do not establish or start factory work.
- Do not modify product files or canonical status during investigation.
- Preserve the original report, source, and any stated severity.
- Distinguish observed facts from reporter assumptions and PM inference.
- Ask the human when expected behavior is undefined and the answer changes classification.

## Required references

- Read [references/case-classification.md](references/case-classification.md) for item types.
- Read [references/grouping-and-deduplication.md](references/grouping-and-deduplication.md) before merging reports.
- Read [references/triage-outcomes.md](references/triage-outcomes.md) before producing the final disposition.

## Workflow

1. Capture each input as a separate source item.
2. Normalize its question, observed behavior, expected behavior, impact, environment, and available evidence.
3. Answer questions directly when reliable project evidence is sufficient.
4. Group items only when evidence supports a common cause, dependency, or desired outcome. Preserve links to every original source item.
5. Dispatch `pm-investigation-worker` for bounded code, document, or legacy comparison work.
6. Classify each item as answered, investigating, duplicate-or-related, suspected-bug, confirmed-bug, design-concern, initiative, risk, deferred, or rejected.
7. Form factory candidates around coherent outcomes or root causes, not around report count.
8. Present candidate rationale, scope boundary, evidence, confidence, dependencies, and unknowns.
9. Wait for explicit human establishment before invoking `pm-factory-handoff`.

## Output

```text
PM_TRIAGE_RESULT_V1
source_count: <number>
answered:
  - <source id, answer, evidence>
investigating:
  - <source id, question, assigned artifact>
duplicate_or_related:
  - <group, source ids, evidence for grouping>
factory_candidates:
  - <candidate id, outcome, sources, rationale, confidence, unknowns>
deferred:
  - <source id, reason, revisit condition>
rejected:
  - <source id, reason>
human_decisions_needed:
  - <decision or none>
```

Write durable detail into the current manager run and keep the chat rollup short.
