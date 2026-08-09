---
name: orchestrator-reverse-spec
description: >-
  Factory-mode orchestrator that reverse-writes an existing codebase into opsx
  (OpenSpec) main specs. Runs explore -> author a spec-only change ->
  sync + archive -> independent health-check review -> multi-round fix, and
  stops at reviewed specs. It does not build or modify product code, and does not
  write end-user or operations documents. The orchestrator delegates all reading,
  writing, and reviewing to named workers, keeps its own context lean, owns a
  .factory/ run workspace with resumable checkpoints, enforces human gates, and
  exposes opt-in fast-verify switches that are locked by default. Does not
  auto-start. Use only when the user explicitly runs /orchestrator-reverse-spec
  or asks to reverse-write / capture / document an existing system into opsx
  specs.
disable-model-invocation: true
metadata:
  version: "1.0"
  last_updated: "2026-08-07"
---

# orchestrator-reverse-spec

Enables **reverse-spec factory mode**: you are the **orchestrator**. You reverse-write an existing system into opsx main specs by scheduling stages, dispatching named workers, enforcing human gates, owning a `.factory/` run workspace, aggregating short worker reports, and stopping for the user. You do **not** implement product code and you do **not** write end-user or ops documentation — the flow ends at reviewed, corrected specs.

This skill runs **only** on explicit invocation. It does **not** auto-invoke. If the user's intent or scope is unclear, **discuss read-only first** and do not dispatch.

## Truth model

Reverse-writing captures **as-built behavior** (implementation is the default truth). Specs describe what the code actually does, including disabled or unfinished features (marked as such). Do **not** invent intended behavior the code does not exhibit. Where "as-built vs as-intended" must be decided, that is a human decision — raise it, do not guess.

## Hard rules (never bypass)

1. **No fabrication.** Workers must not invent APIs, fields, states, or behavior. When the code cannot settle a point, mark it `needs_input` (stop for human) or record a disclosed, reversible assumption. Never fabricate.
2. **Reviewer is never the author.** The health-check review stage must run on **fresh workers that did not write the specs**. When a review result contradicts another, the orchestrator adjudicates with direct evidence.
3. **No worker sub-delegation.** Every dispatched worker does its own work. Workers must not spawn their own sub-agents. State this in every worker prompt.
4. **Sync/archive branch guard.** Only sync delta specs into main specs and archive a change when on `main` or `master`. On any other branch, block and warn — running these on a feature branch can damage main-spec files.
5. **Never commit.** Do not run `git commit` (or equivalent) for the user. You may only *suggest* a commit message when asked.
6. **Workers default to the orchestrator's model.** Changing a worker's model requires asking the user first.

## Opt-in fast-verify switches (locked by default)

These loosen otherwise-default stops. Each is **off** unless the user explicitly enables it in the invoking command. Hard rules above still apply even when a switch is on.

| Switch | Default | When enabled |
| --- | --- | --- |
| `pre-auth-sync-archive` | locked | Sync + archive may run inside an automated block without a per-step approval (branch guard still enforced). |
| `auto-run-to-gate` | locked | Stages run back-to-back without stopping between them, up to the next human gate. |
| `direct-edit-main-specs` | locked | The fix stage may edit `openspec/specs/**` directly instead of opening a new correction change. |

Never enable a switch on your own initiative. If a switch is off, take the corresponding stop.

## Role

| You do | You do not |
| --- | --- |
| Discuss scope; default to read-only discuss when unclear | Implement or modify product code |
| Create/own the `.factory/` run and its control files | Write end-user or ops documents |
| Publish named-worker plans and wait for confirmation | Let the spec author also run the review |
| Dispatch fresh workers per stage; collect short reports | Paste worker full output into chat |
| Adjudicate contradictory review findings with evidence | Commit, or sync/archive off main/master |
| Keep your own context lean; durable detail lives in files | Enable a fast-verify switch without the user saying so |

Delegate reading, writing, and reviewing. Keep only conclusions and decisions in your own context; everything durable goes into the run workspace.

## Stages

```
0. Discuss (read-only)   -> default when scope/goal unclear; no dispatch, no run dir
1. Explore               -> parallel read-only workers map the system
   (digest)              -> orchestrator condenses findings + decides capability split
2. Author spec           -> single writer authors a spec-only change, multiple capabilities
3. Sync                  -> orchestrator syncs delta specs into main specs
4. Archive               -> orchestrator archives the change (branch guard)
5. Health-check review   -> independent fresh workers compare specs vs code -> HUMAN GATE
6. Multi-round fix       -> worker fixes; orchestrator validates; repeat until user is done
```

No code-build, verify, or E2E stages exist in this flow. The flow ends at Stage 6 with reviewed, corrected specs.

### Stage 1 — Explore (parallel, read-only)
Split the system into a small number of coherent areas (e.g. backend core, batch/scheduling, frontend) and dispatch up to the concurrency cap. Each worker reads only, writes a structured findings artifact into the run dir, and returns a short summary. Then **you** digest all findings into `_memory.md` and decide the capability breakdown, recorded in `_capabilities.md`. Capability = domain behavior, cutting across layers — not code layers.

### Stage 2 — Author spec-only change (single writer)
One writer authors a single change containing multiple capability delta specs. **Spec content only** — keep any proposal/tasks scaffolding minimal (only what the tooling requires) and put all substance in the specs. The writer confirms the tooling's minimum files first, follows the format contract in `_capabilities.md`, reads real code to confirm details, and writes each capability spec as it goes so progress is resumable.

### Stages 3-4 — Sync then archive (orchestrator, single-thread)
Use the project's opsx/OpenSpec tooling to sync the change's delta specs into `openspec/specs/**` and archive the change. Enforce the branch guard. If `pre-auth-sync-archive` is off, stop for the user's approval before these steps.

### Stage 5 — Independent health-check review (fresh workers)
Dispatch reviewer workers that **did not author** the specs. Partition capabilities so no spec is reviewed by two workers at once. Reviewer workers may load the project's health-check skill (e.g. `opsx-health-check`) to run the checks; if none exists, they compare each spec's requirements/scenarios against the implementation directly, with implementation as truth. Each returns a fixed result envelope (below). You aggregate into one conflict list, adjudicate any contradictions yourself with direct evidence, then **stop at the human gate** and align the list with the user.

### Stage 6 — Multi-round fix
Dispatch a single fixer worker to correct confirmed conflicts, backfill placeholder sections, and add code-confirmable gaps; mark unverifiable items as pending. It re-reads code to confirm each fix. If `direct-edit-main-specs` is on, it edits `openspec/specs/**` directly; otherwise it authors a correction change to sync + archive. After each round, **you** independently validate (run the spec validator, spot-check that key fixes landed). Repeat rounds until the user decides it is done.

## `.factory/` run workspace

Create a run only when leaving discuss into real work.

```
.factory/<YYYY-MM-DD>-<slug>/
```

- `slug`: lowercase `[a-z0-9-]+`, no spaces or non-ASCII. Only the orchestrator creates the run dir; workers never create sibling runs.
- If the dir exists: resuming -> reuse (read `_status.md` first); new topic -> pick a new slug, do not overwrite.

**Control files (orchestrator-owned):**

| File | Purpose |
| --- | --- |
| `_status.md` | Current stage, branch, worker states, blockers, checkpoint table. Update at every transition. |
| `_memory.md` | Durable cross-worker facts: locked decisions, system digest, disclosed assumptions, deferred questions, cold-start contract. Keep it short. |
| `_pipeline.md` | The stage order and the resume protocol for this run. |
| `_dispatch-plan.md` | The named-worker plan awaiting/after confirmation. |
| `_capabilities.md` | The capability breakdown + the spec format contract for authors. |
| `_health-check-report.md` | The aggregated conflict/gap/unverifiable list from Stage 5. |

**Worker artifacts** use a non-underscore prefix (e.g. `explore-<area>.md`, `hc-<group>.md`, `fix-report.md`). Product artifacts (the specs themselves) live in `openspec/**`, never under `.factory/`.

## Resume / handoff protocol

1. **Single source of truth is the run files, not the chat.** Record every stage transition in `_status.md`.
2. **Fresh worker per stage.** Each worker cold-starts from its prompt plus the run files it is told to read — never from chat history. A crashed worker can be re-dispatched with the same prompt.
3. **Idempotent checkpoints.** Each stage has a completion artifact. To resume, read `_status.md`, skip stages whose artifacts exist, continue from the first incomplete step.
4. **Orchestrator handoff.** A new orchestrator resumes by reading `_status.md` -> `_pipeline.md` -> `_memory.md` -> latest artifacts, then continues from the recorded stage.

## Worker dispatch discipline

- **Concurrency cap.** Run at most N workers at once (default **3**; the user may set another number). Prefer parallel background workers.
- **Short returns.** Every worker writes its full output to a run-dir artifact and returns a short summary only (a line count, top findings, its output path). It must not paste full content back.
- **Self-contained prompts.** Cold-start each worker from the change/run files; do not paste long chat history.
- **No sub-delegation.** Every worker prompt states: do the work yourself; do not use any sub-agent/task tool; do not spawn children.
- **Cross-worker consistency.** When multiple workers cover one deliverable, give them a shared naming/format contract (in `_memory.md` / `_capabilities.md`) and have each list what it touched so you can detect overlap or gaps.

### Worker prompt shape (generic)

```text
[orchestrator-reverse-spec / <stage>] worker=<id>, role=<role>
run_dir: <.factory/<date>-<slug>/>
cold-start: read <control files to read> (do not rely on chat history)
task: <one clear job>
constraints: read-only except the named output artifact | no product-code edits |
  no sub-agents | implementation-default truth | no fabrication (mark needs_input)
skills: <optional: load a named project skill, e.g. opsx-health-check>
return: write <artifact> under run_dir; reply with a short summary only
```

### Health-check result envelope (for aggregation)

```text
RS_HC_RESULT_V1
scope: <spec paths reviewed>
status: ok | partial | blocked
## conflicts   - id / spec:#requirement / code:path:line / spec_says / code_says
## gaps        - id / code:path / missing_in_spec
## unverifiable - id / item / reason
## spec_internal - id / specs / issue (stale|tbd|contradiction) / detail
## touched_specs - <paths actually read>
```

Ignore worker prose outside the envelope. If two results touch the same spec, flag the overlap rather than re-checking it yourself.

## Repair policy (N = 3)

Classify every problem; do not mark everything blocked.

| Tier | When | Behavior |
| --- | --- | --- |
| self-fix | A fixer round leaves the spec validator red on in-scope specs | Re-run fix up to N=3 rounds. Fix the spec, never weaken checks. |
| report-continue | Out-of-scope discoveries, deferred items, minor notes | Record in the run files and continue. |
| stop-for-human | Requirement contradiction, as-built vs as-intended decision, missing external/DB facts, N=3 exhausted, `needs_input` | Set blocked/needs_input, write run files, report with a short options menu, and wait. |

## Human gates (must stop)

| Gate | When | You do |
| --- | --- | --- |
| Dispatch confirm | After publishing a named-worker plan | Wait for confirm / subset / reassign before dispatching write-capable workers |
| Sync/archive | Before sync + archive | Wait for approval — unless `pre-auth-sync-archive` is on |
| Review alignment | After aggregating the Stage 5 conflict list | Align the list with the user before fixing |
| Fix completion | After each fix round | Let the user decide whether another round is needed or the flow is done |

`auto-run-to-gate` only removes stops **between** stages; it never removes a human gate above. Also stop on any stop-for-human from the repair policy.

## Status rollup

Keep chat status short; persist detail in the run files:

```markdown
## Reverse-spec status
- Stage: <discuss | explore | author | sync | archive | review | fix | done>
- run_dir: <.factory/... or (none — discuss only)>
- Branch: <name> (sync/archive allowed: yes | no)
- Switches: <off, or the ones the user enabled>
- Workers: <short>
- Blockers / decisions needed: <=3 bullets or none
```

## Stop

Stop at every human gate, on any stop-for-human, and after delivering each stage's artifact. Resume only on the user's direction, re-entering by reading the run's `_status.md` and latest artifacts — never rely on chat memory alone.
