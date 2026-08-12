---
name: explain
description: >-
  Parse a target — a passage, document, email, code, design text, or even a
  skill — into a concise summary plus an organized breakdown of its elements
  and conditions. Use when the user wants something explained, dissected, or
  laid out as itemized elements, requirements, and boundary conditions.
disable-model-invocation: true
metadata:
  author: Claude Code Opus 4.8
  version: "1.0"
  last_updated: "2026-08-12T09:51:21"
---

# explain

Break a target down into a short summary and an organized view of its parts. A target can be a passage, a document, an email, a piece of code, a design text, or a skill.

Understand before you output. For code or a skill, read it until you genuinely grasp it — a wrong element is worse than a missing one. Do not narrate this step; it does not become a long process.

By default, **output the parsed result only — do not open a discussion.** Enter discussion only when this skill is combined with another skill, or when the user explicitly asks to discuss.

Deliver the result inline. Write to a file only when the user says so; do not ask.

## Output structure

Three segments. The last is optional.

1. **Summary** — a concise summary, introduction, or explanation of the target. If the target carries steps or an order, describe them here.
2. **Elements** — the target's elements as a list or table: design elements, and logic / requirement / boundary conditions. Group lightly (see below); describe them, do not score them.
3. **Other** (optional) — conditions that do not fit the Elements grouping, plus any conflicts, self-inconsistencies, or gaps you found.

## Choosing list vs table

- Use a **table** when the entries share uniform attributes, or when the content involves a comparison or contrast.
- Use a **list** otherwise — heterogeneous or narrative content.

## Grouping

Group elements lightly, only enough to aid reading. Do not over-fragment or add structure that burdens the reader; when the elements are few, a flat list is fine.
