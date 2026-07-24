---
name: opsx-health-check
description: >-
  Periodic OpenSpec main-spec health check against the current demo/implementation
  codebase. Orchestrates Multitask or parallel subagents to find conflicts, gaps,
  unverifiable items, and internal spec issues; reports only (no code/doc edits
  unless the user names an export path). Use when the user runs /opsx-health-check,
  asks for opsx/spec health, drift check, 總健檢, or 規格健康度.
disable-model-invocation: true
metadata:
  author: Cursor Grok 4.5
  version: "1.1"
  last_updated: "2026-07-20T00:00:00"
---

# opsx-health-check

**Periodic / full health check**: verify that `openspec/specs/**` (main specs) still correctly describe the current implementation.  
Not a post-task acceptance check.

You are the **orchestrator**: ask scope, partition, dispatch workers, aggregate the report.  
**Do not** read specs or judge implementation health yourself.

## Hard rules

1. **Read-only**: do not create, modify, delete, or stage any source or docs. Sole exception: write **one** report file when the user **explicitly names an export path**.
2. **Spec scope**: only `openspec/specs/**`. Do not scan `openspec/changes/**` or archive.
3. **Truth**: bidirectional compare; **implementation is the default truth**. Conflicts go into the report for humans; do not auto-fix specs or code.
4. **Model**: Multitask / subagent workers **default to the same model as the orchestrator**. Changing model requires asking the user first and getting approval.
5. **Dedup**: the same `spec.md` must not be handled by two workers at once.

## Checks (every worker)

1. **behavior** — Requirement / Scenario vs actual code behavior  
2. **types-api** — types, fields, API signatures  
3. **routes-nav-perm** — routes, menus, `functionId`, permission nodes  
4. **stale-tbd** — stale wording, wrong change references, Purpose / content TBD  
5. **cross-spec** — contradictions with other main specs already in scope (do not read out-of-scope specs just for cross-checks unless the orchestrator put them in the same task)

## 1. Ask scope first (required)

If scope is missing, **ask before** dispatching. Confirm at least:

- Which capabilities / series (or “all main specs”)
- **code roots** in the workspace (frontend / backend / multi-package paths)
- Report language (default: **Traditional Chinese**; follow the user’s language)
- File export (default: no; if yes, path must come from the user)

## 2. Partition

| Situation | How to split |
| --- | --- |
| User names a module / series (e.g. `report-*`) | **B**: one (or few) tasks covering that series’ main specs + matching code |
| No series; full scan | **A**: one task per `openspec/specs/<capability>/spec.md` |
| Mixed | Series → B; remaining capabilities → A |

Before dispatch, publish a task table (`scope` ↔ `code_roots`) and ensure no two tasks share the same `spec.md`.

## 3. Dispatch — Multitask or multiple subagents

Prefer Cursor **Multitask** (parallel background); otherwise launch parallel subagents.  
The orchestrator **does not** perform the check.

### Worker prompt (must use this shape)

Keep each task short; do not paste long chat history or a full repo tour.

```text
[opsx-health-check]
scope: <spec path or series glob, e.g. openspec/specs/report-*>
code_roots: <project paths, comma-separated>
truth: implementation-default
checks: behavior, types-api, routes-nav-perm, stale-tbd, cross-spec
return: OPSX_HC_RESULT_V1
constraint: read-only; do not edit any files; do not check specs outside scope
```

Optional one-liner: `notes: <user special instruction>` — keep it brief.

### Worker must

- Read only main specs in `scope` and implementation under `code_roots` (including mock / types when relevant)
- Return a full `OPSX_HC_RESULT_V1` block (below); no prose-only report
- Use `(none)` under empty sections
- List `touched_specs` (spec paths actually read)

## 4. Fixed return format (OPSX_HC_RESULT_V1)

```text
OPSX_HC_RESULT_V1
scope: <same as dispatch>
status: ok | partial | blocked
summary: <one line>

## conflicts
- id: <C-001>
  spec: <path>#<requirement or scenario>
  code: <path>:<line or symbol>
  spec_says: <short>
  code_says: <short>
  note: <optional>

## gaps
- id: <G-001>
  code: <path>
  missing_in_spec: <short>

## unverifiable
- id: <U-001>
  item: <short>
  reason: <short>

## spec_internal
- id: <I-001>
  specs: <path[, path]>
  issue: stale | tbd | contradiction
  detail: <short>

## touched_specs
- <path>
```

| Section | Meaning |
| --- | --- |
| `conflicts` | Spec and code disagree (state implementation as default truth) |
| `gaps` | Behavior / API / route exists in code but not in main spec |
| `unverifiable` | Cannot judge from available files |
| `spec_internal` | Stale, TBD, or contradiction between specs |
| `status: ok` | Scope finished; not blocked |
| `status: partial` | Ran, but unverifiable items or some code missing in range |
| `status: blocked` | Spec / code_roots missing; almost nothing checkable |

## 5. Aggregate (orchestrator)

1. Collect every `OPSX_HC_RESULT_V1`; ignore worker prose outside the envelope.
2. Use `touched_specs` to detect duplicate coverage; if two results touch the same spec, flag it and let the user choose — **do not re-check yourself**.
3. Merge items; make ids globally unique (scope prefix allowed, e.g. `report-data-model/C-001`).
4. Deliver the **final report** in chat (language follows the user; default Traditional Chinese).

### Final report structure

Localize headings/prose to the report language. Canonical sections:

```markdown
# Opsx health check report

- Time / workspace: …
- Scope: …
- Code roots: …
- Worker count / status summary: …

## Conflicts (implementation ≠ spec)
…

## Gaps (in code, missing from spec)
…

## Unverifiable
…

## Spec-internal issues
…

## Verdict
(One line: healthy / drift / largely stale; do not claim “ready to merge / ship”)
```

Empty sections: write “none” (or the localized equivalent).

## 6. Optional file export

Only when the user gives a path (e.g. `docs/opsx-health-2026-07-20.md`), write that same report there.  
Do not pick a path yourself; do not write under `openspec/`.

## 7. Stop

Stop after delivering the report unless the user asks to narrow, re-run, export, or fix separately (fixes are out of scope for this skill).
