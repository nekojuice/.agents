---
name: doc-general-guide
description: Base and router for the family of docs written for human readers. Decide the document type first and load the child skill that owns it — README, SOP / cheat-sheet / runbook, end-user operation manual, tutorial, OpenAPI docs; this guide directly owns engineering reference manuals and inventory / audit lists. Holds the shared rules each child inherits or explicitly overrides: project understood shallow-to-deep with openspec consulted, verified against real files, command-and-action style by default, name-first headings, no clutter parentheses, no invented terms, single language, placeholder identifiers. Use when creating or revising any document that tells people how to operate or use a project, or when choosing which doc skill applies.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Codex GPT-5, Claude Code Opus 5.5
  version: "1.2"
  last_updated: "2026-10-20T15:44:21"
---

# General Doc Authoring Guide

Every document in this family is written for readers who must **get productive immediately** from a clear structure: engineers, operators, API callers, and application users. Command orientation is the default; child skills whose readers work on screens or read code annotations override it. Avoid long-winded explanation, piling up of in-code objects, and parenthesis clutter.

This guide is the shared foundation for every document written for human readers. Each document type's child skill extends it; where the two conflict, **the child skill wins**, see §6.

## 0. Decide the document type first

| Type | Reader and responsibility | Does NOT belong here | Owning skill |
|---|---|---|---|
| README | Team members and collaborators: environment architecture, why the system is designed this way, overview | Step-by-step operation commands | `doc-readme-guide` |
| SOP / cheat-sheet / runbook | Operators familiar with the environment: shortest operational path, what to do next, what effect it has | Per-parameter explanation, design rationale, complex background | `doc-sop-guide` |
| Engineering reference manual | Engineers: full reference — every command, parameter meaning, combination examples, error table | "Why it is designed this way" architecture prose, which belongs in README | this guide |
| End-user operation manual | People who use the application: getting a task done on its screens | Code, object, or command names | `doc-user-guide` |
| Tutorial | First-time operators, including people taking over an existing system: follow along to finish a deployment, setup, or takeover, mainly in GUI administration tools where available; command-only steps allowed | Inventory data, operations outside the team's responsibility | `doc-tutorial-guide` |
| API documentation, OpenAPI | People who integrate with the API; external audience by default | Processing logic for an external audience, internal component names, operations detail, secrets | `doc-openapi-guide` |
| Inventory / audit list | People doing inventory, audit, or takeover: the inventoried objects and their attributes | Commands, explanatory paragraphs, side notes | this guide, §0.1 |

The types are complementary, not duplicates. Decide the type before you start and load the owning skill; different types link to each other instead of being mixed in one document.

Do not use "operation manual" on its own in this family. A full reference for engineers is an **engineering reference manual**; a screen-operation document for an application's users is an **end-user operation manual**, owned by `doc-user-guide`. A runbook is an SOP-type document.

### 0.1 Inventory and audit lists

An inventory / audit list is a data document: it lists the inventoried objects and their attributes, and is defined separately from tutorials and SOPs.

- The body holds inventory data only — no commands, explanatory paragraphs, or side notes. One leading scope line (§2.6) naming what the list covers is allowed and is not an explanatory paragraph.
- How to obtain or update the data is written in a tutorial or SOP; the list only links to it.
- Inventory data is presented as tables (§2.5).
- The list body may record real identifying values such as hosts, accounts, and paths; secret values are never recorded. Examples in this skill always use placeholders.

## 1. Understand the project: shallow to deep (read openspec if present)

Gather material in order, building understanding layer by layer:

1. **Existing SOP / cheat-sheet** — grab the skeleton: flows, services, environment differences.
2. **openspec (opsx) main spec** — the authoritative semantics and latest context. **Mandatory to read when the project has openspec.**
3. **openspec `changes/` (in-flight)** — separate what is settled from what is still moving; document only the settled state.
4. **Source entry points** (CLI / `__main__` / argparse) — the authoritative source for commands, parameters, defaults.
5. **Config files** (yaml / `.env.example` / compose) — tunable parameters, defaults, ports, profiles.

### Verification rules

1. Verify against the **real files**, not memory or code comments (comments may be stale).
2. When changes are in flight, use `git status` and openspec `changes/` to separate landed from moving state; document only what is settled.
3. Never document a script / path / flag / command you have not confirmed exists.
4. If you find a defect while writing (a command that does not exist, a publish step that ships a broken tree), **flag it and propose a fix** — do not paper over it.
5. When an existing doc is poor quality, treat it as a **negative example**, not a source of meaning; re-derive material from source and spec.

## 2. Writing style — hard rules

These rules are the default for every type; the child skill that owns a type may override one explicitly, for example a type built around UI steps does not use commands as the step unit.

1. **Every command goes in a fenced code block.** Never inline a command in prose.
2. **Multi-step actions = numbered steps**, each with its own code block. No "first X → then Y" prose flow.
3. **Manual edits** (no single command) are written as a prose sentence, not a fake command.
4. **Give the real setup command**, not a vague gesture: write `cp .env.example .env.<env>` then "fill in:", not "(prepared from the template)".
5. **Use tables for inventory-type information**: services, ports, parameters, error mappings.
6. **Lead with a one-line scope statement**, optionally followed by a service/endpoint table, so the reader knows what this brings up.
7. **Only name objects the operator types or sees**: CLI flags, file paths, config keys, env vars, container names, log/error strings. Do not make internal classes / functions / modules the subject of explanation. E.g. "`OrderMatcher` matches each order…" / "locate via `ImportError.detail`" → "matches each order to its invoice by order number…" / "locate from the tail of the failure output".
8. **An engineering reference manual** may include parameter-meaning tables and combination examples; **an SOP** forbids that kind of explanation. An engineering reference manual is one document divided into sections, not split into separate files.
9. **Section opening prose is at most 2 lines** (scope / orientation only); put no long narrative between the heading and the first command or table.
10. **Keep only the minimum concept needed to read the commands**, placed right next to the commands or tables; link to README for deeper concepts instead of restating, and do not write concept-only sections.
11. **Design rationale follows the document type; experimental conclusions are never written.** By default no type writes "why it is designed this way". README owns architecture-level rationale (`doc-readme-guide`); a tutorial allows one or two sentences of "why" right next to a key step (`doc-tutorial-guide`); other child skills may override this explicitly. "X measured better than Y" belongs in experiment notes for every type. An engineering reference manual answers only: what it does, how to invoke it, what effect it has.
12. **Each `>` note is at most 2 lines**, stating behavior / effect / precondition only — no stacked rationale; if it grows beyond that, split into steps or move it to README.
13. **No invented terms.** Use plain, widely used, industry-standard words; do not coin terms or define your own vocabulary. If no standard term fits, describe the idea in a plain sentence. Avoid telegraphic jargon strings and code-identifier soup.
14. **Single language.** Write in one language, matching what the user asks for; not bilingual. Keep foreign-language tokens only for proper nouns, real commands, and identifiers inside code blocks. Fixed structural labels render in the chosen language, one consistent set.
15. **An example value appears once.** After "the following uses `<X>` as the example", do not rewrite the same example value later; where the reader must substitute, write "replace with the actual location / value".
16. **Identifying information uses placeholders.** Accounts, hosts, internal URLs, person names, and organization names are written as `<placeholder>`; where a demonstration needs a concrete name, use an anonymous invented one. Names of tools and of the project being documented are exempt. Secret values are never written. Inventory list bodies follow §0.1.
17. **Stay within the team's responsibility.** Write only operations the team responsible for the document performs; a step owned by someone else is one line: "ask `<owning role>` to handle it".
18. **Consistent with settled decisions.** Never write an approach that contradicts a settled decision in the main spec or decision records — not as an alternative, a "not recommended" note, or a counterexample.

## 3. Headings and naming

1. **Name first.** When there is a Chinese/English name or component, put the name first and the object node after.
   - `reports.app (report generator)` → `report generator reports.app`
2. **No status/condition in the heading.** To mark a status, use a callout on the first line of the body.
   - `syncagent (sync service, production only)` → `sync service syncagent` + body `> production mode only.`
3. **Heading names the real scope**; drop empty qualifiers (e.g. "(operational version)"). Keep meaningful environment/audience scope ("staging machine", "prod").
4. **Scope already fixed globally** is not restated inside the body.

## 4. Parentheses

Principle: **if it adds no semantic value, cut it; keep only short units or notations.**

| Category | Handling | Example |
|---|---|---|
| Redundant supplement / explanation | Forbidden; use punctuation or rephrase | `uploads/ root (read-only mount for the import job)` → `uploads/ root, read-only mount for the import job` |
| Cross-reference | No parens; join with a comma | `restart the worker (same as §5.2 step 2)` → `restart the worker, same as §5.2 step 2` |
| Supplement inside a heading | Forbidden; move to callout / body | see 3.2 |
| Short, meaningful unit / type | Allowed | `(sec)`, `(datetime2)` |
| Math interval / composite-key notation | Allowed (notation, not supplement) | `[T − 24h, T)`, `(order_id, line_no)` |
| Literal program string / error message | Keep verbatim, including its parentheses | `missing required setting (provide DB_* in .env)` |
| Diagram node labels (mermaid, etc.) | Treat as whole material; do not edit individually | — |

## 5. Code-block comment format

```
# step or short note
command    # expected output value, if any — avoid where possible
```

- Comment **above** the command (`#`): a step or short note, ideally one line. When a section has multiple examples, every code block leads with this line stating what that example does.
- Comment **at end of line** (`#`): an expected output value (e.g. `PONG`) or a target; **avoid where possible**, add only when confirming the result helps.
- **Never** write behavior / rationale / multi-action flow / warnings / preconditions in a comment; move behavior notes to a single `>` line after the code block, and write warnings and preconditions as prose.

Good example:

```
# stop all containers
docker compose --env-file ../.env.<env> --profile <profile> stop
```

> Containers and their state are kept; restart them via §5.5.

## 6. Child skills

Each child skill inherits every rule in this guide; where they conflict, the child skill wins. Each child marks its differences with Inherited and Overrides tables; a rule that does not fit the child's type is listed in Overrides as not applicable.

| Skill | Document type | Relationship to this guide |
|---|---|---|
| `doc-readme-guide` | README | Extends it; adds the fixed block order and owns architecture-level rationale |
| `doc-sop-guide` | SOP / cheat-sheet / runbook | Extends it; keeps procedures terse and command-only |
| `doc-user-guide` | End-user operation manual | Extends it for wording and style; replaces commands with on-screen steps |
| `doc-openapi-guide` | API documentation, OpenAPI | Extends it; text lives in code annotations, with audience-based exposure control |
| `doc-tutorial-guide` | Tutorial | Extends it; UI steps first, a brief "why" beside key steps, result tables |

## 7. Completion checklist

- [ ] Document type was decided via §0 and the owning child skill is loaded; the document does not encroach on other types' responsibilities.
- [ ] Material gathered via SOP → openspec spec/changes → source/config, basing only on settled state.
- [ ] Every command is in a code block; no inline commands.
- [ ] Multi-step actions are numbered, each with its own code block.
- [ ] Section openings are ≤2 lines; design rationale follows §2.11 for this type; no experimental conclusions; concepts kept to the minimum and linked to README.
- [ ] Each `>` note is ≤2 lines, stating only behavior / effect / precondition.
- [ ] Only objects the operator types or sees are named; no internal class / function / module as the subject.
- [ ] Headings are name-first with no status parentheses; status is marked via a callout.
- [ ] No redundant or cross-reference parentheses; only units, notation, literal strings, and diagrams remain.
- [ ] Code comments follow §5; end-of-line expected output is minimized; every example carries a one-line scenario comment.
- [ ] No invented terms; one language throughout (§2.13–2.14).
- [ ] Each example value appears once (§2.15).
- [ ] Identifying information uses placeholders or anonymous invented names; no secret values (§2.16).
- [ ] Only operations within the team's responsibility; no approach contradicting a settled decision (§2.17–2.18).
- [ ] An inventory / audit list holds inventory data only (§0.1), when writing one.
- [ ] Every referenced command / script / path was verified against real files.
- [ ] Any defect found was flagged, not documented as if it worked.
