---
name: doc-general-guide
description: Writing or revising operational docs for human readers—operation manuals, SOPs / cheat-sheets, runbooks (how to operate / deploy / set up / recover). Enforces a command-and-action style: name-first headings, no clutter parentheses, verified against real files, project understood shallow-to-deep with openspec consulted. Standalone—does not require doc-sop-guide. Use when creating or revising any "how to operate / use this project" document for engineers.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Codex GPT-5
  version: "1.1"
  last_updated: "2026-08-20T14:36:57"
---

# General Doc Authoring Guide

Operational docs are written for engineers and collaborators who must **get productive immediately** from a clear structure. Avoid long-winded explanation, piling up of in-code objects, and parenthesis clutter.

This guide is standalone — it does not require doc-sop-guide.

## 0. Decide the document type first

| Type | Responsibility | Does NOT belong here |
|---|---|---|
| README | Environment architecture, why the system is designed this way, overview | Step-by-step operation commands |
| SOP / cheat-sheet | Shortest operational path: what to do next, what effect it has | Per-parameter explanation, complex background |
| Operation manual | Full reference: every command, parameter meaning, combination examples, error table | "Why it is designed this way" architecture prose (belongs in README) |

The three are complementary, not duplicates. Decide which one you are writing before you start.

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

1. **Every command goes in a fenced code block.** Never inline a command in prose.
2. **Multi-step actions = numbered steps**, each with its own code block. No "first X → then Y" prose flow.
3. **Manual edits** (no single command) are written as a prose sentence, not a fake command.
4. **Give the real setup command**, not a vague gesture: write `cp .env.example .env.<env>` then "fill in:", not "(prepared from the template)".
5. **Use tables for inventory-type information**: services, ports, parameters, error mappings.
6. **Lead with a one-line scope statement**, optionally followed by a service/endpoint table, so the reader knows what this brings up.
7. **Only name objects the operator types or sees**: CLI flags, file paths, config keys, env vars, container names, log/error strings. Do not make internal classes / functions / modules the subject of explanation. E.g. "`resolver` resolves the panel…" / "locate via `StageError.output`" → "resolves to the matching panel month by anchor…" / "locate from the tail of the failure output".
8. **A manual** may include parameter-meaning tables and combination examples; **an SOP** forbids that kind of explanation.
9. **Section opening prose is at most 2 lines** (scope / orientation only); put no long narrative between the heading and the first command or table.
10. **Keep only the minimum concept needed to read the commands**, placed right next to the commands or tables; link to README for deeper concepts instead of restating, and do not write concept-only sections.
11. **No design rationale, no experimental conclusions.** "Why it is designed this way" belongs in README; "X measured better than Y" belongs in experiment notes. A manual answers only: what it does, how to invoke it, what effect it has.
12. **Each `>` note is at most 2 lines**, stating behavior / effect / precondition only — no stacked rationale; if it grows beyond that, split into steps or move it to README.

## 3. Headings and naming

1. **Name first.** When there is a Chinese/English name or component, put the name first and the object node after.
   - `inference.app (main inference loop)` → `main inference loop inference.app`
2. **No status/condition in the heading.** To mark a status, use a callout on the first line of the body.
   - `tailwriter (ingest service, real only)` → `ingest service tailwriter` + body `> real mode only.`
3. **Heading names the real scope**; drop empty qualifiers (e.g. "(operational version)"). Keep meaningful environment/audience scope ("experiment machine", "prod").
4. **Scope already fixed globally** is not restated inside the body.

## 4. Parentheses

Principle: **if it adds no semantic value, cut it; keep only short units or notations.**

| Category | Handling | Example |
|---|---|---|
| Redundant supplement / explanation | Forbidden; use punctuation or rephrase | `data/ root (read-only mount for direct raw read)` → `data/ root, read-only mount for direct raw read` |
| Cross-reference | No parens; join with a comma | `restart main loop (same as §5.2 step 2)` → `restart main loop, same as §5.2 step 2` |
| Supplement inside a heading | Forbidden; move to callout / body | see 3.2 |
| Short, meaningful unit / type | Allowed | `(sec)`, `(datetime2)` |
| Math interval / composite-key notation | Allowed (notation, not supplement) | `[T − 24h, T)`, `(txn_id, model_id)` |
| Literal program string / error message | Keep verbatim, including its parentheses | `real mode missing required secret (provide MSSQL_* in .env)` |
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
# stop all containers, keep containers and state, restart later via §5.5
docker compose --env-file ../.env.<env> --profile monitoring --profile metrics stop
```

## 6. Relationship to doc-sop-guide

This guide already contains every rule it needs; doc-sop-guide does **not** need to be loaded alongside it. Provenance of the rules:

- **Adopted**: commands in code blocks, numbered multi-step blocks, manual edits as prose, real setup commands, tables for inventories, verify against real files, flag defects.
- **Adapted**: a manual uses sections instead of split files; a manual allows parameter tables / combination notes (an SOP stays terse); code comments allow a one-line step note above the command; one-line architecture hints are permitted.
- **Added** (not covered by doc-sop-guide): name-first headings; the parentheses rules; the namable-object boundary (§2.7); concept minimization and the ban on design rationale / experimental conclusions (§2.10–2.11); the 2-line cap on `>` notes (§2.12); one-line scenario comments per example (§5); openspec `changes/` as the settled-state criterion.

## 7. Completion checklist

- [ ] Document type is clear; it does not encroach on README / SOP responsibilities.
- [ ] Material gathered via SOP → openspec spec/changes → source/config, basing only on settled state.
- [ ] Every command is in a code block; no inline commands.
- [ ] Multi-step actions are numbered, each with its own code block.
- [ ] Section openings are ≤2 lines; no design rationale or experimental conclusions; concepts kept to the minimum and linked to README.
- [ ] Each `>` note is ≤2 lines, stating only behavior / effect / precondition.
- [ ] Only objects the operator types or sees are named; no internal class / function / module as the subject.
- [ ] Headings are name-first with no status parentheses; status is marked via a callout.
- [ ] No redundant or cross-reference parentheses; only units, notation, literal strings, and diagrams remain.
- [ ] Code comments follow §5; end-of-line expected output is minimized; every example carries a one-line scenario comment.
- [ ] Every referenced command / script / path was verified against real files.
- [ ] Any defect found was flagged, not documented as if it worked.
