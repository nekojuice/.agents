---
name: doc-sop-guide
description: Writing or editing SOP / runbook / operational deployment docs (setup, deploy, restart, recover). Enforces an action-and-command style—commands in code blocks, no prose rationale, verified against real files. Use when creating or revising any "how to operate / deploy / set up" document.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Codex GPT-5
  version: "1.1"
  last_updated: "2026-08-20T14:36:57"
---

# SOP Authoring Guide

An SOP is a **procedure**, not an explanation. The reader wants to know **what command to run** and **what action to take**, in order, and how to confirm it worked. It is not a place to explain *why* the system is designed the way it is.

If a sentence does not tell the operator to *do* something or to *check* a result, it probably does not belong in an SOP.

## Hard rules

1. **Every command goes in a fenced code block.** Never inline a command in prose.
   - Bad: `- **Restart**: \`docker compose up -d\`; it warms up and resumes.`
   - Good: a `## Restart` heading, the command in a ```code block```, then one short line of result.

2. **Multi-step actions = numbered steps, each with its own command block.** Never compress a procedure into a "first X → then Y" prose flow, and never put that flow inside a code-block comment.
   - Bad (inside a code block): `# first cp template.yml → fill DSN, then --profile mssql up -d`
   - Good: step 1 with the `cp` command in a block, a prose line for the manual edit, step 2 with the `up` command in a block.

3. **Code-block comments annotate the command only — never describe behavior or rationale.** Allowed: expected output (`# PONG`), a target (`# → /srv/.../data`). Not allowed: outcome/behavior text, multi-action instructions, explanations.
   - Move any behavior note to a single `>` line *after* the block.

4. **Notes are at most one `>` line, and precise.** Cut vague phrases. Replace fuzzy wording with a concrete statement.
   - Bad: "no gaps no dups", "score under-estimates velocity", "bit-level identical".
   - Good: "resumes after the checkpoint; already-landed rows (same model_id) are not re-scored".

5. **Manual edits (no single command) are prose, not fake commands.** "Edit `x.yml` to fill the DSN" is a sentence after the `cp` command, not a comment pretending to be a step.

6. **Give the real setup command, not a vague gesture.** Write `cp .env.example .env.<env>` then "fill:"; do not write "(prepared from the template)".

7. **No redundant scope qualifiers.** If the whole document is already scoped (one environment, one audience), do not restate that scope inside it. A production SOP does not need "(only test/prod has MSSQL)".

8. **Titles name the real scope; drop empty qualifiers.** "(operational version)" is redundant — the whole doc is operational. But the environment/audience ("Experiment machine", "Prod") *is* meaningful and belongs in the title or split.

## Structure

- **Split by environment/audience when the flows diverge a lot.** If experiment vs production differ in services, data source, and result sink, write two self-contained files (e.g. `SOP_setup_experiment.md`, `SOP_setup_prod.md`) rather than one doc full of "if real… / if experiment…" branches. Some duplication of shared steps is fine — each file must stand alone.

- **Order steps in execution order.** What the operator does first comes first. Pre-deploy actions on the dev machine (run tests, publish/ship) precede on-target setup. Use sub-steps (`0a`, `0b`) when something legitimately precedes the "prerequisites" section.

- **Each section: command → expected result / verification.** Pair actions with a check the operator can eyeball.
  ```bash
  docker exec ml-redis redis-cli ping     # PONG
  ```

- **Use compact tables for inventories** — services started, endpoints, UIs/URLs, ports. A table beats paragraphs for reference lookups.

- **Lead with a one-line scope statement and (if useful) a service/endpoint table**, so the reader knows what this run brings up before the steps.

## Process (before writing)

1. **Verify against the real files, not memory or code comments.** Read the actual compose / env / config / scripts. Code comments and prior docs may be stale; confirm the present behavior.
2. **When changes are in flight (concurrent edits), confirm the settled state.** Check `git status`/task progress to separate landed state from work still moving, and base the doc on what is settled.
3. **Never document a script, path, flag, or command you have not confirmed exists.** A referenced `start_x.sh` that lives in another project, or a whitelist that omits a needed dir, makes the SOP wrong.
4. **Flag real defects you find while writing instead of documenting something broken.** If the publish step would ship a broken tree, or a referenced command does not exist, surface it and propose the fix — do not paper over it.

## Examples

**Inline command + vague outcome → heading, code block, precise note.**

Bad (one bullet): `**Restart**: `docker compose --profile real up -d`; warm up + checkpoint resume, no gaps no dups.`

Good:

> A `### Restart` heading, then the command alone in a `bash` code block, then one line: "Warms up, then resumes after the checkpoint; already-landed rows (same model_id) are not re-scored."

**Prose flow inside a comment → numbered steps.**

Bad (a comment line inside the code block): `# MSSQL metrics: first cp sql_exporter.yml.example → sql_exporter.yml fill DSN, then --profile mssql up -d`

Good:

> Step 1 — "Copy the DSN template, then edit it to fill the MSSQL DSN (gitignored):" with `cp …example …sql_exporter.yml` in its own block. Step 2 — "Start the exporter:" with `docker compose --profile mssql up -d` in its own block.

## Completion checklist

Before finishing an SOP, confirm:

- [ ] Every command is in a code block; no command appears inline in prose.
- [ ] Multi-step actions are numbered, each with its own command block; no "first → then" prose flow.
- [ ] No behavior/rationale text sits inside code-block comments; notes are single `>` lines and precise.
- [ ] No redundant scope qualifiers; title names the real scope, no empty "(… version)".
- [ ] Setup steps include the actual `cp`/create commands; manual edits are prose, not fake commands.
- [ ] Steps are in execution order (pre-deploy before on-target).
- [ ] Every referenced command/script/path was verified to exist against current files.
- [ ] Diverging environments are split into self-contained files where appropriate.
- [ ] Any defect found while writing was flagged, not documented as if it worked.
