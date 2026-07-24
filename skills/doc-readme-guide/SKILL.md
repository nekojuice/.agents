---
name: doc-readme-guide
description: Writing or revising a README.md for private / small-team repos (private GitLab, private GitHub). README-specialized extension of doc-general-guide. Enforces a fixed block order (title, doc nav, ToC, about, tech stack, getting started, structure, logic, key params), keeps it short and readable, owns the architecture/why that operational docs push here, and omits open-source community blocks. Reader-first plain language with no invented terms and single-language consistency. Language-and-framework agnostic. Use when creating or revising any README.md.
metadata:
  author: Opus 4.8
  version: "1.0"
---

# README Authoring Guide

A README for a private / small-team repo answers **what this is, why it exists, and how it is shaped** — for teammates and collaborators, not the public. It owns the architecture and rationale that operational docs deliberately push here, but it must stay **short and readable**: a README's worst failure is a wall of prose. Write it in plain, common language a teammate understands without reading the code — never invent terms, and do not pad a Chinese doc with English or code identifiers (see §6).

This guide is a **README-specialized extension of doc-general-guide**. Read that guide for the shared foundations; this one overrides and adds where README differs.

## 0. Relationship to doc-general-guide

| Aspect | doc-general-guide | doc-readme-guide (this) |
|---|---|---|
| Responsibility | manual / SOP: how to operate | README: what it is, why, what it looks like |
| Architecture & rationale | forbidden, pushed to README | **owned here**, but kept concise |
| Command-oriented | required | not required; README leads with prose + diagrams + tables |
| Name-first headings | inherited | **inherited** |
| Parentheses discipline | inherited | **inherited** |
| Tables for inventory | inherited | **inherited** (Tech Stack, parameters) |
| Shallow-to-deep understanding + read openspec | inherited | **inherited** (same sourcing & verification) |
| Commands in code blocks | inherited | inherited (Getting Started snippets) |
| "Concise, readability first" | inherited | **reinforced** — brevity is the priority |

Scope: private / internal repos; any language, any framework; applies to new and to revised READMEs.

## 1. Understanding the project (inherited)

Before writing, gather material shallow-to-deep exactly as in doc-general-guide §1:
existing docs → **openspec (opsx) spec/changes if present (mandatory to read)** → source entry points → config files.
Verify every version, path, and structure against the **real files** (`package.json` / `requirements.txt` / `go.mod` / lockfiles / the actual directory tree). Never guess a version or a folder.

## 2. Fixed block order

Blocks appear in this order. The **major block order is fixed**; do not reorder. Optional blocks are omitted entirely when they do not apply (do not leave empty headings).

| # | Block | Required | Purpose | Content rules |
|---|---|---|---|---|
| 1 | Project Title | yes | `# Name` | Title only; no tagline / description line (the About section introduces the project) |
| 2 | Doc Navigation | optional | Quick links to related docs | Only when other docs exist (e.g. a `docs/` folder, SOPs, manuals); compact list or table of verified links |
| 3 | Table of Contents | yes | Section index | Use a **collapsible block** `<details>`; anchor links to each section |
| 4 | About The Project | yes | Introduce the project | A cohesive short introduction (a few flowing sentences); not a mechanical bullet list of features; no implementation mechanics, no code identifiers |
| 5 | Tech Stack | yes | Languages / frameworks / key packages | Language+version, key frameworks+version, a package only when its version matters a lot; table or short list, not the full dependency dump |
| 6 | Getting Started | yes | Shortest path to run | Numbered steps, commands in code blocks; link to an SOP / quickstart for full setup instead of duplicating it |
| 7 | Project Structure | yes | Directory layout | A tree in a code block using `├ │ ─ └`, each line with a short `# comment`; only meaningful folders, terse comments |
| 8 | Project Logic | yes | Flow / sequence | mermaid diagrams (flowchart / sequence); diagram-led, prose as support |
| 9 | Key Parameters | optional | Code / enum mappings | Only when they exist; tables such as status codes or role codes |

## 3. Per-block rules

### Project Title
`# Project name` only. Do **not** add a tagline / description line under the title — the About section below already introduces the project; a line here would duplicate it.

### Doc Navigation
Link only to documents that actually exist; verify the paths. If there is no other doc, omit the whole block.

### Table of Contents
Collapsible, with anchor links:

```markdown
<details>
<summary>目錄 / Contents</summary>

- [About The Project](#about-the-project)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Project Logic](#project-logic)

</details>
```

### About The Project
A cohesive, readable **introduction** to the project — what it is, what problem it solves, and who uses it — written as a few flowing sentences. Do not reduce it to a mechanical bullet list of features, and do not fill it with implementation mechanics, code identifiers, status codes, or invented terms. Keep it to a short paragraph. Design rationale and internals belong in Project Logic / Project Structure where they have context.

### Tech Stack
List only: the language(s) with version, the key external frameworks, and the **external infrastructure the project depends on — databases, message brokers, caches**. Read versions from the real manifest (`package.json` / `requirements.txt` / `go.mod` / lockfile); do not guess.

Use a coarse `Type` (Language / Framework / Datastore / Broker); do **not** split by fine-grained function. **The database is mandatory** when the project uses one.

```markdown
| Type | Name | Version |
|---|---|---|
| Language | Python | 3.9 |
| Database | SQL Server | 2019 |
| Broker | RabbitMQ | 3.x |
| Cache | Redis | 5.x |
| Framework | FastAPI | 0.115 |
```

Exclude: the project's own / vendored packages (not third-party tech), and ubiquitous low-level libraries nobody chooses a project by (e.g. polars, pyarrow). List a third-party package only when its version materially affects usage. Never reproduce the full dependency list.

### Getting Started
- **If a setup SOP / deployment doc exists**: this block is a **pointer only** — link to the external file(s). Do **not** distinguish environments here and do **not** excerpt any command snippet; a partial excerpt is incomplete and goes stale.
- **If no SOP / doc exists**: write the steps here with the **production environment as the main axis** and dev / test as secondary (for a library / CLI tool, lead with the most common install / usage instead). Numbered steps, each command in a code block.

```bash
# only when there is no SOP to link — minimal steps live here
git clone <repo-url> && cd <project>
<install command>
```

### Project Structure
A tree in a code block; only meaningful folders, one short comment per line:

```text
project/
├── src/            # application source
├── configs/        # declarative config, secrets via ${VAR}
├── tests/          # unit tests
└── docs/           # SOPs, manuals, ADRs
```

Do not expand every file; stop at the level that conveys responsibility. Keep comments to one short phrase.

### Project Logic
mermaid diagrams, default to `TD` to avoid horizontal squeezing. One diagram per idea; split complex flows into several diagrams rather than one dense graph. The framing prose and the node labels must be human-readable per §6: plain common words, no invented terms, no telegraphic label-only meaning, and no unnecessary code identifiers.

### Key Parameters
One table per parameter set; map `value → meaning`, no parenthesis-stuffed lines:

```markdown
| Code | Meaning |
|---|---|
| 0 | created |
| 1 | modified |
| 2 | deleted |
```

## 4. Inherited rules from doc-general-guide

- **Name-first headings**; no status/condition in a heading (use a callout on the first body line).
- **Parentheses discipline**: cut redundant supplements and cross-references; keep only short units, notation, literal strings, and diagram labels.
- **Tables for inventory-type information** (tech stack, parameters, structure-adjacent reference).
- **Commands in fenced code blocks**; numbered multi-step actions.
- **Verify against real files**; document only the settled state.
- When **revising** an existing README: keep the valuable content, refit it into the fixed block order, and do not break existing anchors.

## 5. Omit these (clutter for private repos)

Do not add open-source / community sections — they are never used here and only add weight:

- License, Contributing, Code of Conduct
- Status / build / coverage badges
- Contributors, sponsors, community / support channels

## 6. Wording and language

**Plain, common terms — never invent terminology.**

- Describe the project in plain, widely-used, industry-standard words. Do **not** coin or invent terms, and do not define your own vocabulary. If no standard term fits, describe the idea in a plain sentence instead of minting a label.
- Avoid telegraphic jargon strings and code-identifier soup; write for a reader who has not read the code.

**Single language — no unnecessary code-switching.**

- Write the README in a **single language**, matching what the user asks for (e.g. Chinese-primary or English-primary). **Not bilingual.**
- In a Chinese README, do not pad prose with English terms or with program object / class / module / diagram-node names where plain Chinese works. Keep foreign-language tokens only for: genuine proper nouns (e.g. Redis, MSSQL, Python), real commands, and identifiers inside code blocks.
- The fixed block headings are a fixed design; render each heading in the README's chosen language, one consistent set — do not mix languages within one README.

## 7. Completion checklist

- [ ] Major blocks follow the fixed order; optional blocks are omitted, not left empty.
- [ ] Title is the name only; no tagline / description line under it.
- [ ] Table of Contents is collapsible with working anchors.
- [ ] About The Project is a cohesive short introduction; not a mechanical feature bullet list; no implementation mechanics or code identifiers.
- [ ] Plain, common terms only; no invented / self-defined terminology.
- [ ] Single language throughout; no unnecessary English or program object / class / node names in a Chinese doc; headings in the chosen language, not bilingual.
- [ ] Tech Stack lists language + key external frameworks + external infra (database mandatory); excludes own / vendored packages and trivial low-level libs; versions verified against the real manifest.
- [ ] Getting Started links to the SOP when one exists (no command excerpts); otherwise production-first.
- [ ] Project Structure tree uses `├ │ ─ └` with terse one-phrase comments; not every file expanded.
- [ ] Project Logic uses mermaid (default `TD`), one idea per diagram, with human-readable labels and prose.
- [ ] No License / Contributing / badges / community blocks.
- [ ] Name-first headings, parentheses discipline, tables, and code blocks follow doc-general-guide.
- [ ] Every version, path, and structure verified against real files.
