---
name: design-system-extraction
description: >-
  Reverse-engineers a brand's design specification from an existing frontend's code and delivers
  it as a design-system skill for people and agents: extracts faithful, traceable values, rebuilds
  them into layered tokens and function-based components, and optionally moves the web layer to a
  utility-first CSS framework without changing values. Use when the user asks to extract, reverse,
  rebuild, or migrate a brand design system from existing frontend code, typically under a
  factory plan route. Not for designing a new brand from scratch, implementing product features,
  or restyling a single component.
disable-model-invocation: true
metadata:
  author: Claude Code Opus 5.5
  version: "1.0"
  last_updated: "2026-11-17T17:59:56"
---

# design-system-extraction

A domain skill: it says **what to do and how to check it** for each step of turning an existing frontend into a design-system skill. It does not orchestrate. Under `orchestrator-factory`, load it on the plan route; the factory owns the run, dispatch, and gates. Without a factory, one session follows the same order and stops at the same gates.

The deliverable is an **art and design specification**. CSS analysis is only the means of getting values; it never becomes the content of the deliverable.

## Phases

Enter at any phase, provided its inputs exist (the previous phase's deliverable or an equivalent).

| Phase | Goal | Input | Deliverable | Acceptance | Reference |
| --- | --- | --- | --- | --- | --- |
| P1 Extract | Faithful, traceable snapshot of the brand as built | `<target frontend>` source, read-only; optionally a running local instance | Research notes with per-value source (they stay in the run); a raw brand skill in the layered package schema with every entry `origin: source` (tokens, mapping file, DESIGN.md, component specs, offline preview) | Generated files equal regeneration (`--check`); package check passes (`data` with `--allow-orphans`); independent verification; cold-start trial | `references/phase-1-extract.md`, `references/authoring.md` |
| P2 Rebuild | Cross-project design system | Frozen P1 deliverable | Layered tokens (primitive → semantic → component), function-based components (variant / size / state), pattern registry, lineage table, project-neutral examples | H1–H5 hold against P1; package check passes (`data`, then `full`); independent verification; cold-start trial | `references/phase-2-rebuild.md`, `references/authoring.md` |
| P3 Migrate | Utility-first web layer, values unchanged | A frozen package not yet in utility notation | Theme generated from tokens, component specs in utility notation, preview compiled offline, residue ledger with every item resolved | H1–H5 and box-size comparison against P2; residue scan clean; cold-start trial | `references/phase-3-migrate.md`, `references/tailwind-notation.md` |

A new project runs P1 → P2; P2 delivers in Tailwind notation (Iron rules 6). P3 is only for an existing package whose web layer is not yet in utility notation.

## Iron rules

1. **Project neutrality.** The reusable parts of the deliverable, and every note written to improve this skill, contain no company, brand, product, or project content from the source. Use placeholders. Project data stays in the run.
2. **Values stay original.** Do not "improve" a value. A failing contrast ratio is recorded as a fact, in neutral wording; do not change colors or add states the source lacks on your own.
3. **Do not carry degraded structure.** An element or interaction mechanism whose form is clearly a later patch or a regression of the design is not a specification. Replace its structure with the established pattern (for interactive widgets, a WAI-ARIA APG pattern), keep its values, and record the replacement in the version log.
4. **Local only.** Do not publish design data. Scripts never use the network. A tool that must be downloaded needs the user's approval first and is installed inside the run (`references/run-operations.md`).
5. **An example is not a target.** An example the user gives to illustrate a situation ("such as X", "like X") is not a target; only what the user names as a target is in scope. When it is unclear whether something is an example or a target, put it on the open list instead of promoting it (`discuss-first`).
6. **Tokens are the single source of values.** Tailwind notation is the shared language for expressing styles, including for non-CSS media (slides, print); conversions follow `references/tailwind-notation.md`.
7. **Faithful first, then rebuild.** P1 never merges or renames for elegance; P2 never invents values. Every P2 value traces back to P1 through the lineage table.

## Hard rules

Every phase after P1 re-checks these against the frozen previous deliverable. A failure stops the phase.

| Rule | Check |
| --- | --- |
| H1 | No contrast regression for any recorded text/background pair |
| H2 | Surfaces that were distinguishable stay distinguishable |
| H3 | Font-size order is preserved within each role and within each variant at each width |
| H4 | Control box heights differ by less than 4px at every checked width |
| H5 | No orphan primitive: every primitive is used by a semantic token or a documented direct reference |

Also: every generated file equals a fresh regeneration (stale-output check), and every number in a manual is a subset of the data files.

## Gates

Each phase runs the same loop. Under a factory, map it onto the plan route; stop for the user where marked.

1. Write the phase plan from `assets/plan-phase-<n>.md` into the run.
2. Independent plan review; amend and re-review.
3. **Plan stop.** Under a factory, the factory plan route's stop rules apply; at Converge, recommend that the user ask to see the plan first, since this domain needs plan, independent review and user confirmation. Without a factory, stop for the user to confirm the plan.
4. After the plan is confirmed and before construction, for P2 or P3: freeze the previous deliverable and export a read-only baseline: a tag export, or a hashed copy when there is no tag (`references/run-operations.md`). The commit and tag happen only when the user asks (`orchestrator-factory` hard rule 6; `commit-message-suggestion` `## Committing on request`).
5. One worker builds the dependent series in the run's `staging/`.
6. A separate worker verifies; another runs the cold-start trial (`references/verification.md`). At Converge, list both in the plan as work for the user to authorize (role, write scope, evidence); standalone, run each in a fresh context given only its brief's inputs.
7. Fix loop in the fixed order: mapping file and tokens → specs and preview → manual → full check → re-verification.
8. Swap staging into place after the preconditions pass, with the rollback ready: a verified hashed copy of the target folder taken just before the swap (empty for a first P1 build).
9. **Stop:** the user reviews the preview and the diff and accepts, or the rollback restores the previous version. Commit only when the user asks.

Every time work stops, write the resume point into the run state file's Stage line (`_status.md` under a factory).

## Working with a factory

- The plan skeleton fills the factory's `_plan.md`; worker briefs come from `assets/worker-briefs.md`.
- A dependent series stays with one worker; verification and the cold-start trial use different workers.
- The forbid list is generated by the orchestrator before construction and stays in the run (`assets/forbid-list.template.txt`).
- Classify verification results as product-fail, run-error, or needs-human; only a confirmed product-fail goes to a fix round.

## Reading order

Read only what the current step needs.

| Step | Reference | Scripts | Assets |
| --- | --- | --- | --- |
| Scope and plan | this file | — | `plan-phase-1.md`, `worker-briefs.md` |
| Style sources, inventory, layout survey | `phase-1-extract.md` | `extract/stack_scan.py`, `extract/framework_structure.py`, `extract/markup_scan.py`, `extract/asset_scan.py` | — |
| Rule index, per-component values, contrast | `phase-1-extract.md` | `extract/css_index.py`, `extract/batch_query.py`, `extract/profile_diff.py`, `extract/sheet_residue.py`, `extract/contrast.py`, `extract/selftest.py` | — |
| Render check, token synthesis, packaging | `phase-1-extract.md` | `package/build_tokens.py`, `package/build_tailwind.py`, `package/build_contrast.py`, `package/check_package.py` | `deliverable-skeleton/` |
| Manual, component specs, preview | `authoring.md` | `package/build_preview.py` | `deliverable-skeleton/` |
| Rebuild | `phase-2-rebuild.md` | `rebuild/colormetrics.py`, `rebuild/rationalize.py`, `rebuild/selftest.py`, `package/build_tokens.py`, `package/build_contrast.py`, `package/check_package.py` | `plan-phase-2.md` |
| Migrate | `phase-3-migrate.md`, `tailwind-notation.md` | `package/build_tailwind.py`, `migrate/residue_scan.py`, `migrate/residue_ledger_check.py`, `migrate/theme_name_diff.py` | `plan-phase-3.md`, `residue-ledger.template.md` |
| Verify | `verification.md` | `verify/boxdiff.py`, `package/check_package.py` | `worker-briefs.md` |
| Freeze, swap, tools, environment | `run-operations.md` | — | `forbid-list.template.txt` |

`scripts/README.md` lists every script's arguments.
