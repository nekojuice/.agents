---
name: doc-readme-guide
description: Writing or revising a README.md for private / small-team repos (private GitLab, private GitHub). README-specialized extension of doc-general-guide; this guide wins on conflict. Enforces a fixed block order (title, doc nav, ToC, about, tech stack, getting started, structure, logic, key params), keeps it short and readable, owns the architecture/why that operational docs push here, and omits open-source community blocks. Reader-first plain language with no invented terms and single-language consistency. Language-and-framework agnostic. Use when creating or revising any README.md.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Codex GPT-5, Claude Code Opus 5.5
  version: "1.2"
  last_updated: "2026-10-20T15:44:21"
extends: doc-general-guide
---

# README Authoring Guide

A README for a private / small-team repo answers **what this is, why it exists, and how it is shaped** — for teammates and collaborators, not the public. It owns the architecture and rationale that operational docs deliberately push here, but it must stay **short and readable**: a README's worst failure is a wall of prose. Write it in plain, common language a teammate understands without reading the code — never invent terms, and do not pad a Chinese doc with English or code identifiers (see §6).

This guide is a **README-specialized extension of doc-general-guide**. Read that guide for the shared foundations. Where the two conflict, **this guide wins**.

## 0. Relationship to doc-general-guide

| Inherited rule | Meaning in a README |
|---|---|
| §0 type responsibility | README answers what this is, why it exists, and how it is shaped |
| §1 shallow-to-deep understanding and verification rules | Versions, paths, and structure come from the manifest and the real directory tree (§1 below) |
| §3 name-first headings, no status in a heading | Applies to every block and sub-heading |
| §4 parentheses discipline | Applies unchanged to prose, tables, and tree comments |
| §2.5 tables for inventory-type information | Tech Stack, Key Parameters |
| §2.1–2.2 commands in code blocks, numbered multi-step actions | Getting Started snippets |
| §2.13 no invented terms | See §6 |
| §2.14 single language | See §6 |
| §2.15 an example value appears once | Applies to Getting Started and parameter examples |
| §2.16 identifiers as placeholders, anonymous invented names | README boundary in §6 |

### Overrides

| doc-general-guide rule | Here |
|---|---|
| §2.6 open with a one-line scope statement | Not applicable; the title stands alone and About The Project introduces the project, §3 |
| §2.11 no design rationale by default | README owns architecture-level rationale, kept concise |
| §2 command orientation | Not required; README leads with prose, diagrams, and tables |
| §2.9–2.10 concise, minimum concept | Reinforced — brevity is the first priority |
| §7 completion checklist | Replaced by §7 |

Scope: private / internal repos; any language, any framework; applies to new and to revised READMEs.

## 1. Understanding the project (inherited)

Before writing, gather material shallow-to-deep exactly as in doc-general-guide §1:
existing docs → **openspec (opsx) spec/changes if present (mandatory to read)** → source entry points → config files.
Verify every version, path, and structure against the **real files** (`package.json` / `requirements.txt` / `go.mod` / lockfiles / the actual directory tree). Never guess a version or a folder.

## 2. Fixed block order

Blocks appear in this order. The **major block order is fixed**; do not reorder. Optional blocks are omitted entirely when they do not apply (do not leave empty headings).

| # | Block | Required | Purpose | Content rules |
|---|---|---|---|---|
| 1 | Project Title | yes | `# Name` | Title only; no tagline or description line, because About The Project introduces the project |
| 2 | Doc Navigation | optional | Quick links to related docs | Only when other docs exist (e.g. a `docs/` folder, SOPs, manuals); compact list or table of verified links |
| 3 | Table of Contents | yes | Section index | Use a **collapsible block** `<details>`; anchor links to each section |
| 4 | About The Project | yes | Introduce the project | A cohesive short introduction (a few flowing sentences); not a mechanical bullet list of features; no implementation mechanics, no code identifiers |
| 5 | Tech Stack | yes | Languages / frameworks / key packages | Language+version, key frameworks+version, a package only when its version matters a lot; table or short list, not the full dependency dump |
| 6 | Getting Started | yes | Shortest path to run | Numbered steps, commands in code blocks; link to the deployment-related docs for full setup instead of duplicating it, as described in §3 |
| 7 | Project Structure | yes | Directory layout | A tree in a code block using `├ │ ─ └`, each line with a short `# comment`; only meaningful folders, terse comments |
| 8 | Project Logic | yes | Flow / sequence | mermaid diagrams (flowchart / sequence); diagram-led, prose as support |
| 9 | Key Parameters | optional | Code / enum mappings | Only when they exist; tables such as status codes or role codes |

## 3. Per-block rules

### Project Title
`# Project name` only. Do **not** add a tagline / description line under the title — the About section below already introduces the project; a line here would duplicate it.

### Doc Navigation
Link only to documents that actually exist; verify the paths. When the project has API documentation, link to that document or its viewer page here. If there is no other doc, omit the whole block.

### Table of Contents
Collapsible, with anchor links:

```markdown
<details>
<summary>Contents</summary>

- [About The Project](#about-the-project)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Project Logic](#project-logic)

</details>
```

When the README uses another language, the summary label, link text, and anchors all follow that language's block headings.

### About The Project
A cohesive, readable **introduction** to the project — what it is, what problem it solves, and who uses it — written as a few flowing sentences. Do not reduce it to a mechanical bullet list of features, and do not fill it with implementation mechanics, code identifiers, status codes, or invented terms. Keep it to a short paragraph. Design rationale and internals belong in Project Logic / Project Structure where they have context.

### Tech Stack
List only: the language(s) with version, the key external frameworks, and the **external infrastructure the project depends on — databases, message brokers, caches**. Read versions from the real manifest (`package.json` / `requirements.txt` / `go.mod` / lockfile); do not guess.

Use a coarse `Type` (Language / Framework / Datastore / Broker); do **not** split by fine-grained function. **The database is mandatory** when the project uses one.

```markdown
| Type | Name | Version |
|---|---|---|
| Language | Python | 3.9 |
| Datastore | SQL Server | 2019 |
| Broker | RabbitMQ | 3.x |
| Datastore | Redis | 5.x |
| Framework | FastAPI | 0.115 |
```

Exclude: the project's own / vendored packages (not third-party tech), and ubiquitous low-level libraries nobody chooses a project by (e.g. polars, pyarrow). List a third-party package only when its version materially affects usage. Never reproduce the full dependency list.

### Getting Started
- **If deployment-related docs exist**: this block is a **pointer only** — link to the external file(s). List a tutorial first when one exists; an SOP may be listed alongside. Do **not** distinguish environments here and do **not** excerpt any command snippet; a partial excerpt is incomplete and goes stale.
- **If no SOP / doc exists**: write the steps here with the **production environment as the main axis** and dev / test as secondary (for a library / CLI tool, lead with the most common install / usage instead). Numbered steps, each command in a code block.

Example, used only when there is no SOP to link:

````markdown
1. Clone the repository.

   ```bash
   git clone <repo-url>
   ```

2. Enter the project folder.

   ```bash
   cd <project>
   ```

3. Install the dependencies.

   ```bash
   <install command>
   ```
````

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

## 4. Revising an existing README

When **revising** an existing README: keep the valuable content, refit it into the fixed block order, and do not break existing anchors.

## 5. Blocks to omit

**Open-source / community sections** — they are never used in private repos and only add weight:

- License, Contributing, Code of Conduct
- Status / build / coverage badges
- Contributors, sponsors, community / support channels

**Per-endpoint API descriptions** — endpoints, parameters, responses, and error codes belong in the API documentation (`doc-openapi-guide`). The README only links to it from Doc Navigation.

## 6. Wording and language

**Plain, common terms — never invent terminology** (doc-general-guide §2.13). Write for a reader who has not read the code.

**Single language** (doc-general-guide §2.14). README specifics:

- In a Chinese README, do not pad prose with English terms or with program object / class / module / diagram-node names where plain Chinese works. Keep foreign-language tokens only for: genuine proper nouns (e.g. Redis, MSSQL, Python), real commands, and identifiers inside code blocks.
- The fixed block headings are a fixed design; render each heading in the README's chosen language, one consistent set — do not mix languages within one README.

**Identifiers** (doc-general-guide §2.16). In Getting Started, Project Structure comments, Project Logic diagram nodes, and Key Parameters, demonstration examples, example values, and identifiers — accounts, hosts, internal URLs, people, organizations — are written as `<placeholder>` or anonymous invented names. The project's own name, tool names, and verified project facts such as its own directories, tech stack, and versions are written as they are. Never write secret values.

## 7. Completion checklist

- [ ] Major blocks follow the fixed order; optional blocks are omitted, not left empty.
- [ ] Title is the name only; no tagline / description line under it.
- [ ] Table of Contents is collapsible with working anchors.
- [ ] Table of Contents summary label, link text, and anchors are in one language and match the block headings.
- [ ] About The Project is a cohesive short introduction; not a mechanical feature bullet list; no implementation mechanics or code identifiers.
- [ ] Plain, common terms only; no invented / self-defined terminology.
- [ ] Single language throughout; no unnecessary English or program object / class / node names in a Chinese doc; headings in the chosen language, not bilingual.
- [ ] Tech Stack lists language + key external frameworks + external infra (database mandatory); excludes own / vendored packages and trivial low-level libs; versions verified against the real manifest.
- [ ] Getting Started links to deployment-related docs when they exist, tutorial first (no command excerpts); otherwise production-first.
- [ ] Project Structure tree uses `├ │ ─ └` with terse one-phrase comments; not every file expanded.
- [ ] Project Logic uses mermaid (default `TD`), one idea per diagram, with human-readable labels and prose.
- [ ] No License / Contributing / badges / community blocks.
- [ ] No per-endpoint API descriptions; API documentation appears only as a link.
- [ ] Demonstration examples and identifiers use placeholders or anonymous invented names; project facts are written as they are.
- [ ] Inherited doc-general-guide rules are followed (§0 Inherited table).
- [ ] Every version, path, and structure verified against real files.
