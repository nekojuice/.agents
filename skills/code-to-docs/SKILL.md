---
name: code-to-docs
description: >-
  Exports developer handoff documentation from existing implementation code.
  Orchestrates Multitask or parallel subagents to scan features and produce
  engineering reference docs (boundaries, full DTO/field tables, APIs, validation).
  Not an end-user manual. Use when the user runs /code-to-docs, asks to export
  docs from code, 工程對照文件, 開發者對接文件, or code-to-documentation.
disable-model-invocation: true
metadata:
  author: Cursor Grok 4.5
  version: "1.1"
  last_updated: "2026-07-20T00:00:00"
---

# code-to-docs

Export **developer handoff / engineering reference** docs from **existing code**.  
Not an end-user manual (`doc-user-guide`); **do not** apply end-user manual style.

You are the **orchestrator**: ask scope, present an outline for confirmation, partition, dispatch, merge, and write files.  
**Do not** scan code or author feature body text yourself.

## Hard rules

1. **Truth**: implementation code is authoritative. Do not invent fields, APIs, validation, or calculations; if unknown, write `cannot verify from code` (localize that phrase when `lang` is not English).
2. **Writes**: write docs only after the user **explicitly names an output path** (dir or file) **and** confirms the outline. If path is missing → **ask first**. Do not pick a path; do not change product code.
3. **Model**: Multitask / subagent workers **default to the same model as the orchestrator**. Changing model requires asking the user first and getting approval.
4. **Dedup**: the same feature slice (same `###` target) must not be handled by two workers at once.
5. **Language**: exported doc **prose** defaults to **Traditional Chinese** and follows the user’s language. Keep proper nouns, field identifiers, paths, API names, and type names in their **original** form.

## Goal — cover each feature as completely as practical

- The feature itself (as complete a catalog as practical)
- Behavior boundaries and rules (required fields, defaults, forbidden actions, errors / toasts, collapse, etc.)
- **Data models / DTOs: expand every field and attribute** (never type name only)
- APIs: interface, HTTP / call verb, request / response, validation / guards
- Export or other side effects (write `none` if none)

## 1. Ask first (required)

If any of the following is missing, **ask before** dispatching:

- **Scope**: modules / features / packages (or “all”)
- **code roots**: project roots to scan (may be multiple; frontend and/or backend)
- **Output path**: directory or file names (user-specified)
- **Language**: default Traditional Chinese; may follow the user
- **Optional openspec drift appendix**: allowed by default (see §7); body truth remains code

## 2. Outline confirmation (required before body)

Without writing feature bodies, the orchestrator may do a light read-only inventory (or dispatch a short outline-only task). Present to the user:

1. **File list** to produce (one file per large category — usually top-level menu)
2. Per file: **`#` title, `##` groups, `###` feature list**

**Wait for outline confirmation** before dispatching body workers. If not confirmed → stop at the outline; no files, no body chunks.

### Headings and file split

| Level | Use |
| --- | --- |
| One file | Large category (typically top-level menu) |
| `#` | Category title for that file (one per file) |
| `##` | Feature group; multiple H2s allowed in one file |
| `###` | **One feature** (primary grain) |
| `####` / `#####` | Nesting inside a feature (behavior, models, API, one complex rule, etc.) |

Localize `#` / `##` / `###` titles to `lang` when exporting; structure levels stay as above.

## 3. Feature discovery (suggested, not exclusive)

**Do not assume** every run is a frontend SPA. Choose discovery from the user’s code roots and project shape.

**One suggested approach (frontend / Vue-like demos)**: routes / menus → permission nodes → views → matching services / types / mocks.

For other roots (backend, API, CLI, …) use that stack’s entry points (controllers, route tables, OpenAPI, module dirs, …). State which discovery approach was used in the outline.

Exclusions: unless the user asks, do not treat pure test files as standalone “features”. Mock data may evidence fields / behavior; label the source.

## 4. Partition

| Situation | How to split |
| --- | --- |
| User names a module / series | One task covers related `###`s in that series (still no overlap of the same `###` with another task) |
| Full export | One task per `###`, or a few adjacent features in the same output file (list them explicitly in the dispatch table) |
| Mixed | Series → series cut; remainder → per feature |

Dispatch table columns: `file`, `h2`, `features (###)`, `code_roots`. Ensure no two tasks share the same `###`.

## 5. Dispatch — Multitask or multiple subagents

Prefer Cursor **Multitask**; otherwise parallel subagents. The orchestrator **does not** write bodies.

### Worker prompt (must use this shape)

```text
[code-to-docs]
file: <output relative name, e.g. reports.md>
h2: <parent ## title, or empty>
features: <### feature names, comma-separated; usually one>
code_roots: <paths, comma-separated>
lang: zh-Hant
return: CODE_DOC_CHUNK_V1
constraint: read-only on source; do not write files; expand all model fields; no invention
```

Optional: `notes: <user special instruction>`.

### Worker must

- Scan only code in scope; emit markdown body for that scope
- Follow §6 for every feature; **model tables must expand every field**
- Return a full `CODE_DOC_CHUNK_V1` block; not prose-only
- List `touched_paths`

## 6. Per-`###` body structure (worker)

Templates below use **English canonical section titles**. When `lang` is Traditional Chinese (default), localize section titles and prose to that language; keep identifiers unchanged.

```markdown
### <Feature name>

- Entry: route / menu / permission node / functionId (only with evidence)
- Primary implementation paths: views / components / services / controllers …

#### Behavior & boundaries
- Defaults, required inputs, forbidden actions, when queries run, errors / toasts, collapse, etc. (bullets; evidenced)

#### Data models
(Each type gets a ##### heading + full field table; see below)

#### API
| Verb | Interface (service / HTTP path) | Request | Response | Validation / guard |
| --- | --- | --- | --- | --- |
| … | … | … | … | yes / no (where) |

#### Export & other side effects
- … or `none`
```

### Data model tables (required — full field expansion)

For every Filters / Row / Result / DTO / Entity / etc.:

```markdown
##### <TypeName>

| Field | Type | Required / optional | Display label | Source / derivation | Notes |
| --- | --- | --- | --- | --- | --- |
| `fieldName` | `string` | required | UI label or `none (transport only)` | API / user input / calculator function | … |
```

Rules:

- **Forbidden**: “see type `Foo`” without expanding fields
- Has UI mapping → on-screen label; transport-only → `none (transport only)` (localize if needed)
- Formatting / totals / derived values → name the function or calc site; say whether UI or backend computes
- Unknown → `cannot verify from code` (localize if needed)

## 7. Fixed return format (CODE_DOC_CHUNK_V1)

```text
CODE_DOC_CHUNK_V1
file: <reports.md>
h2: <Property & ROU reports>
features: <Property inventory>
status: ok | partial | blocked
summary: <one line>

## markdown
<<<MD
### Property inventory
…
<<<END

## spec_drift
- id: <D-001>
  code: <path>
  spec: <openspec/specs/…> (if compared)
  detail: <short>
or
(none)

## unverifiable
- id: <U-001>
  item: <short>
  reason: <short>
or
(none)

## touched_paths
- <path>
```

Put markdown between `<<<MD` and `<<<END` for easy merge.  
`spec_drift`: only when the user wants the appendix and the worker compared a main spec; **never** treat spec as body truth.

| status | Meaning |
| --- | --- |
| `ok` | Feature body and model tables complete for the scope |
| `partial` | Unverifiable items or missing API / field evidence |
| `blocked` | No implementation entry found; almost nothing to write |

## 8. Aggregate and write (orchestrator)

1. Collect every `CODE_DOC_CHUNK_V1`; detect duplicates via `features` / `touched_paths`; on conflict ask the user — **do not rescan yourself**.
2. Per confirmed outline: each file = `#` + embed each chunk’s `## markdown` under the right `##`.
3. Optional short meta header (time, code roots, scope, language).
4. If any `spec_drift`: appendix per file or a separate file (“differences vs main spec” — reference only).
5. Write to the user-specified path; in chat list written files and worker status summary.

## 9. Stop

Stop after delivery. Re-runs, wider scope, or code changes from the docs are separate tasks.
