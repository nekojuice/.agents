---
name: doc-sop-guide
description: Writing or editing SOP / runbook / cheat-sheet docs for operators who already know the environment (setup, deploy, restart, recover) — the shortest command path. Extends doc-general-guide; this guide wins on conflict. Enforces an action-and-command style—commands in code blocks, one expected result per command, no prose rationale (an SOP rule), verified against real files. Not for tutorials for first-time operators (use doc-tutorial-guide), end-user application manuals (use doc-user-guide), or standalone inventory / audit lists (follow doc-general-guide). Use when creating or revising an SOP, runbook, or cheat-sheet.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Codex GPT-5, Claude Code Opus 5.5
  version: "1.2"
  last_updated: "2026-10-20T13:33:25"
extends: doc-general-guide
---

# SOP Authoring Guide

An SOP is a **procedure**, not an explanation. The reader wants to know **what command to run** and **what action to take**, in order, and how to confirm it worked. Not explaining *why* the system is designed the way it is is a rule of the SOP type, not of every operational document: architecture-level rationale belongs in README, and a first-time operator who needs a reason per step gets a tutorial, not an SOP with a "why" exception.

If a sentence does not tell the operator to *do* something or to *check* a result, it probably does not belong in an SOP.

This guide **extends doc-general-guide**. Read that guide for the shared foundations. Where the two conflict, **this guide wins**.

## Scope and boundaries

| Type | Reader | Shape | Owner |
|---|---|---|---|
| SOP / runbook / cheat-sheet | An operator who already knows the environment | Shortest path; command-oriented; each command paired with one expected result; no rationale | This guide |
| Tutorial | A first-time operator | Mostly UI steps; short reasons and result-comparison tables allowed | `doc-tutorial-guide` |

- The two are distinguished by document type. Do not mix them in one document; link between them when needed.
- A standalone inventory / audit list is not an SOP; it follows doc-general-guide §0.1. Service, port, or endpoint tables inside an SOP serve only that SOP's steps.

## Inherited from doc-general-guide

| Inherited rule | Meaning in an SOP |
|---|---|
| §1 shallow-to-deep material gathering, openspec mandatory when present; verification rules 1–5 | Apply doc-general-guide §1 verification rules in full; Process below adds only SOP cases. Document only the settled state |
| §2.5 tables for inventory-type information | Services, ports, endpoints, URLs |
| §2.6 one-line scope statement | Opens the SOP, optionally with a service / endpoint table |
| §2.7 name only objects the operator types or sees | Commands, flags, paths, config keys, container names, log strings |
| §3 name-first headings, no status in a heading | Applies to every step heading |
| §4 parentheses discipline | Applies unchanged to prose and notes |
| §2.13 no invented terms | Plain, widely used words in step text and notes |
| §2.14 single language | One language per SOP; commands and identifiers stay verbatim |
| §2.15 an example value appears once | After "using `<env>` as the example", do not rewrite the value later; write "replace with the actual value" |
| §2.16 identifiers as placeholders, anonymous invented names | Accounts, hosts, internal URLs, people, organizations as `<placeholder>`; no secrets |
| §2.17 only operations within the owning team's responsibility | An out-of-scope step is one line: "ask `<owning role>` to handle it" |
| §2.18 consistent with settled decisions | No approach that contradicts the main spec or decision records, not even as an alternative or counter-example |

### Overrides

| doc-general-guide rule | Here |
|---|---|
| §2.11 design rationale by document type | An SOP never contains rationale |
| §2.12 `>` notes at most 2 lines | At most 1 line (Hard rule 4) |
| §5 a one-line step comment above the command | Comments mark only an expected output or a target (Hard rule 3) |
| §2.8 an engineering reference manual may carry parameter-meaning tables | An SOP carries no parameter explanation |
| §2.8 an engineering reference manual is divided into sections, not split files | An SOP splits by environment or audience into self-contained files, see Structure |
| §7 completion checklist | Replaced by the checklist below |

## Hard rules

1. **Every command goes in a fenced code block**, same as doc-general-guide §2.1.
   - Bad: `- **Restart**: \`docker compose up -d\`; it warms up and resumes.`
   - Good: a `## Restart` heading, the command in a ```code block```, then one short line of result.

2. **Multi-step actions = numbered steps, each with its own command block**, same as doc-general-guide §2.2. Never put a "first X → then Y" flow inside a code-block comment either.
   - Bad (inside a code block): `# first cp exporter.yml.example → fill the connection string, then --profile exporter up -d`
   - Good: step 1 with the `cp` command in a block, a prose line for the manual edit, step 2 with the `up` command in a block.

3. **Code-block comments annotate the command only — never describe behavior or rationale.** Allowed: expected output (`# PONG`), a target (`# → <data-dir>`). Not allowed: outcome/behavior text, multi-action instructions, explanations.
   - Move any behavior note to a single `>` line *after* the block.

4. **Notes are at most one `>` line, and precise.** Cut vague phrases. Replace fuzzy wording with a concrete statement.
   - Bad: "should be fine", "mostly idempotent", "fully in sync".
   - Good: "resumes after the last checkpoint; a record whose `record_id` was already imported is skipped".

5. **Manual edits are prose, not fake commands**, same as doc-general-guide §2.3. "Edit `x.yml` to fill the connection string" is a sentence after the `cp` command, not a comment pretending to be a step.

6. **Give the real setup command, not a vague gesture**, same as doc-general-guide §2.4.

7. **No redundant scope qualifiers**, same as doc-general-guide §3.4. A production SOP does not need "(only staging and prod have the reporting database)".

8. **Titles name the real scope; drop empty qualifiers**, same as doc-general-guide §3.3. An environment or audience such as Staging or Prod is meaningful and belongs in the title or the file split.

## Structure

- **Split by environment/audience when the flows diverge a lot.** If staging and production differ in services, data source, and output target, write two self-contained files (e.g. `SOP_setup_staging.md`, `SOP_setup_prod.md`) rather than one doc full of "if prod… / if staging…" branches. Some duplication of shared steps is fine — each file must stand alone.

- **Order steps in execution order.** What the operator does first comes first. Pre-deploy actions on the dev machine (run tests, publish/ship) precede on-target setup. Use sub-steps (`0a`, `0b`) when something legitimately precedes the "prerequisites" section.

- **Each section: command → expected result / verification.** Pair actions with a check the operator can eyeball.
  ```bash
  docker exec app-cache redis-cli ping     # PONG
  ```

- **Use compact tables for inventories** — services started, endpoints, UIs/URLs, ports. A table beats paragraphs for reference lookups.

## Process (before writing)

Apply doc-general-guide §1 verification rules 1–5 before writing. Cases that come up often in an SOP:

- Read the actual compose, env, config, and script files the steps use.
- A referenced `start_worker.sh` that lives in another project, or a whitelist that omits a needed directory, makes the SOP wrong.
- A publish step that would ship a broken tree is flagged with a proposed fix, not documented.

## Examples

**Inline command + vague outcome → heading, code block, precise note.**

Bad (one bullet): `**Restart**: `docker compose --profile worker up -d`; warm up + checkpoint resume, nothing lost.`

Good:

> A `### Restart` heading, then the command alone in a `bash` code block, then one line: "Warms up, then resumes after the last checkpoint; a record whose `record_id` was already imported is skipped."

**Prose flow inside a comment → numbered steps.**

Bad (a comment line inside the code block): `# exporter: first cp exporter.yml.example → exporter.yml fill the connection string, then --profile exporter up -d`

Good:

> Step 1 — "Copy the exporter template, then edit the copy to fill the connection string; the copy is gitignored:" with `cp …example …exporter.yml` in its own block. Step 2 — "Start the exporter:" with `docker compose --profile exporter up -d` in its own block.

## Completion checklist

Before finishing an SOP, confirm:

- [ ] The document is an SOP, not a tutorial or an inventory list.
- [ ] Every command is in a code block; no command appears inline in prose.
- [ ] Multi-step actions are numbered, each with its own command block; no "first → then" prose flow.
- [ ] No behavior/rationale text sits inside code-block comments; notes are single `>` lines and precise.
- [ ] No redundant scope qualifiers; title names the real scope, no empty "(… version)".
- [ ] Setup steps include the actual `cp`/create commands; manual edits are prose, not fake commands.
- [ ] Steps are in execution order (pre-deploy before on-target).
- [ ] Every referenced command/script/path was verified to exist against current files.
- [ ] Diverging environments are split into self-contained files where appropriate.
- [ ] Any defect found while writing was flagged, not documented as if it worked.
- [ ] Inherited doc-general-guide rules are followed: parentheses, identifiers, example values, responsibility scope, no invented terms, single language.
