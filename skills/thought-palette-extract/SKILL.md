---
name: thought-palette-extract
description: Analyze a project (or article / plan) and distill its design into scored, categorized elements, then emit an import-ready JSON for the Thought Palette (once-espejo) tool. Use when the user wants to extract a project's core value, architectural health, or any other dimension into a quantifiable overview of libraries (storage), palettes, categories (cat), and scored elements (ele).
---

# Thought Palette Extract

Distill a target (a code project by default, but also an article, plan, or spec) into **elements** — small units of design — grouped into **categories (cat)** and scored, so the user gets a quantifiable, at-a-glance view of the whole. The deliverable is a JSON file that imports directly into the Thought Palette (once-espejo) tool.

You do **not** hand-write the tool's nested JSON. You author a **flat draft** (`draft.json`) and run a bundled **assembler script** that compiles it into the import-ready `import.json`, wiring all cross-references, injecting protected cats, and validating the result. This keeps your reasoning flat and makes the output reliable.

Read [SCHEMA.md](SCHEMA.md) fully before authoring — it defines the flat draft format, the scoring rubric, the color guidance, and the tool's data model and hidden constraints.

## Core mapping

| Concept | Tool object |
|---|---|
| One analysis run, holding **all** elements | a single **library** (`Library` / storage) |
| One extraction direction (core value, architectural health, mixed, …) | one **palette** (盤) |
| A category grouping semantically-close elements | one **cat** (`PaletteCat`) |
| A cat's importance / immediate effect | `cat_factor` / `cat_base` |
| An element's benefit or harm | `ele.val` |

Every palette references elements from the **same** library. Storage is the single source of truth for element text; palettes reference elements by id and add per-palette scores.

## Process

### 1. Understand the target

If the target is a code project, **read documentation first** — `README`, `docs/`, and any `openspec` / `opsx` specs — to grasp intent and structure. If docs are missing or incomplete, read the necessary source code (entry points, models, stores, core modules) until you genuinely understand the whole. Do not score from a shallow skim; a wrong element is worse than a missing one.

Use the `Explore` subagent for broad codebase sweeps when the project is large.

### 2. Ask which directions to extract

Ask the user which extraction direction(s) to use — one palette per direction. Use the question tool if available, otherwise ask in plain text. Allow multiple selections, let the user write their own direction, or discuss to converge on the best fit.

- **Default-selected: Core value** (`kind: value`) — extract the *value itself*, not code tidiness. E.g. for a loyalty-points coupon app: user experience, features, merchant operation, maintainability — *service & usage* value. For a game design doc: art, audio, core loop, UI/UX — *concept & design* value.
- Architectural health & feature completeness (`kind: health`) — an engineering-oriented view: layering cleanliness, over-abstraction, front/back and API integration, dead/deprecated methods left uncleaned, unfinished features. Categorize by architectural layer and major feature; **do not over-fragment**.
- Mixed (`kind: mixed`) — value and engineering in one palette, for small targets or a single overview.
- Future dimensions the user may request: reliability, test coverage, etc. (`kind: custom`).

### 3. Decide output location

Decide where `draft.json` and `import.json` go based on the user's description; if unclear, ask. Reasonable options: a folder inside the target project (e.g. `.thought-palette/`), or the scratchpad (delivering only the final `import.json`).

### 4. Author the flat draft

Write `draft.json` following [SCHEMA.md](SCHEMA.md):

- Write each element's `text` **once** in `elements`, with a stable latin-slug `id` and a neutral `storage_cat` (file by **source / subsystem** — e.g. `frontend`, `backend`, `docs`, `tests`, or a module name — *not* by analytical dimension).
- Under each palette's cats, reference elements by `ele` + `val` only.
- Merge semantically-close elements into the same cat. Aim for **5 / 7 / 9** cats per palette; keep it **under 11** to avoid fatigue, and **never exceed 21**.
- Score with the rubric in [SCHEMA.md](SCHEMA.md): `val` in −5..+5, `factor` default 1, `base` default 0 (avoid negative `base` — let `ele.val` carry the negative sign).
- **Populate each palette's `通用` (common) cat** with cross-cutting elements — ones that evaluate the target as a whole rather than one functional area. The primary content is **documentation health**: one element per existing document type (README, manuals, arch docs, deployment SOP, plans, design mocks), scored positive if well-written, negative if poor or drifted; a missing doc gets **no element**. See section 4 of [SCHEMA.md](SCHEMA.md) for the decision test, per-kind candidates, and the promotion rule. Keep `通用`'s `factor` at 1.
- Assign each cat a `color` per the color guidance in [SCHEMA.md](SCHEMA.md).

### 5. Assemble and validate

Run the bundled assembler, preferring **python first**; if python is unavailable, fall back to **node**, then **PowerShell**:

```sh
python  scripts/assemble.py  <draft.json> [import.json]   # preferred
node    scripts/assemble.mjs <draft.json> [import.json]   # fallback 1
pwsh -File scripts/assemble.ps1 <draft.json> [import.json] # fallback 2
```

The script generates all ids and `index` fields, injects the protected cats (`未分類`, `通用`), writes `import.json` as a directly-importable `Library[]`, and prints a validation report. **Read the report** — resolve any ERROR (orphan `ele` references, cat count over 21, duplicate ids, invalid color) before handing off. Address WARNINGs (cat count over 11, `val` outside −5..+5, negative `base`, unreferenced elements, empty `通用` cat) with judgment — an empty-`通用` warning usually means you skipped cross-cutting elements such as documentation health; go back and add them unless the palette deliberately excludes them.

### 6. Hand off

Tell the user the `import.json` path and a short summary (libraries, palettes, cat counts, notable scores). They import it via the tool's **Import** (overwrite or merge). Because merge keys on names, re-running with stable `library` / palette / cat names lets the user incrementally merge later.
