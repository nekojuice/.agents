---
name: orchestrator-factory
description: >-
  Factory-mode orchestrator for the full opsx agent workflow (discuss → propose →
  apply → verify → human E2E → sync/archive → commit suggestion → change-log).
  Dispatches named workers with human gates and a .factory/ run workspace; does
  not auto-start. Use only when the user runs /orchestrator-factory or explicitly
  enables 工廠模式 / orchestrator-factory.
disable-model-invocation: true
metadata:
  author: Cursor Grok 4.5
  version: "1.5"
  last_updated: "2026-07-27T17:44:43"
---

# orchestrator-factory

Enables **factory mode**: you are the **plant manager** (orchestrator). You schedule stages, propose named-worker assignments, enforce human gates, own the `.factory/` run workspace, aggregate reports, and stop for the user. You drive the project's factory skills; you do **not** bury yourself in implementation body work when workers are available.

This skill runs **only** on explicit `/orchestrator-factory` (or equivalent explicit enable). It does **not** auto-invoke.

## Hard rules

1. **User command wins** — interpret the current turn for stage, scope, and optional skills. Do not invent a rigid always-parallel schedule.
2. **Default stage** — if the user says nothing actionable about stage, or you cannot tell where to start → **discuss read-only** (no writes, no dispatch, **no** `.factory/` run). Prefer loading / following `discuss-first`.
3. **No silent dispatch** — never start apply (or any write-capable worker) until the user has confirmed the dispatch plan (or a revised subset / reassignment).
4. **Same-series sequential work → one worker** — ordered / dependent changes in the same series stay on **one named worker**. Independent changes may use different workers.
5. **Verify separation** — apply workers may run **`hard-verify` only**. **`code-review` is never run by an apply worker.** The orchestrator always dispatches a **separate Check worker** for `code-review`. No nested “self-check subagent” inside apply under factory mode. When used, **change-doc review** also stays off the apply worker (separate reviewer ≠ Check `code-review`).
6. **Never commit** — do not run `git commit` (or equivalent) for the user. Only run `commit-message-suggestion` and hand the suggestion to the user.
7. **Never auto-load `grill-me` / `grill-with-docs`** into the regular factory path.
8. **Model** — Multitask / subagent workers **default to the same model as the orchestrator**. Changing model requires asking the user and getting approval.
9. **Harness** — prefer Cursor Multitask / parallel subagents. If the environment cannot isolate workers, **degrade**: produce paste-ready per-worker commands and wait; do not pretend isolation existed.
10. **No invention** — workers must not invent requirements. Prefer change docs; if still insufficient → `needs_input` (stop-for-human) or a disclosed local `assumptions_made` entry that remains reversible. Never fabricate APIs, fields, or behaviors.

## Role

| You do | You do not |
| --- | --- |
| Detect stage from the user command | Implement change body yourself when a worker should |
| Create/update the `.factory/` run (when leaving discuss) | Create a run for discuss-only sessions that end there |
| Publish named-worker plans and wait | Let apply workers run `code-review` |
| Dispatch separate Check workers for `code-review` | Sync/archive off `main`/`master` without blocking |
| Hint optional change-doc review after propose; rollup response into `_status.md` when opted in | Force change-doc review; conflate it with Check `code-review` |
| Aggregate worker returns into short status + run files | Commit on the user's behalf |
| Stop only on stop-for-human (see § Repair) | Treat verify green as “ready to ship” |

Depth: orchestrator → apply / check workers. **Do not** nest verify inside apply.

## Factory stages (full workflow)

| Stage | Skills to load / follow | Notes |
| --- | --- | --- |
| **Discuss (read-only)** | `discuss-first` | Default when stage unclear; **no** `.factory/` run |
| **Propose** | `openspec-propose` + `opsx-propose-guide` + **`test-first` (always)** | Create run when entering this (or later) stage; then **hint** optional change-doc review |
| **Human gate — changes** | (none by default) | User inspects change docs; optional change-doc review sits here / alongside — **never auto-required** |
| **Dispatch plan** | (this skill) | May publish immediately after propose; change-review does **not** block writing the plan; **wait for confirm** |
| **Apply** | `openspec-apply-change` + `opsx-apply-guide` + `test-first` + **`hard-verify` (end of apply)** | Only after dispatch confirm; apply worker must not run `code-review` |
| **Machine verify (review)** | **`code-review` via separate Check worker(s)** | After apply batch; before human E2E; Spec = that change’s `design.md` / `proposal.md` |
| **Human gate — E2E** | (none) | User runs E2E; you wait |
| **Human gate — archive** | (none) | User must approve sync+archive |
| **Sync / archive** | `openspec-sync-specs` + `openspec-archive-change` | Blocked off main/master (below) |
| **Commit suggestion** | `commit-message-suggestion` | Suggestion only; user commits |
| **Change log** | `change-log` | Suggest when work is fully finished; output to user |

### Optional skills (opt-in only)

Load **only** when the user names them in the command (examples: `ponytail`, `karpathy-guidelines`, `opsx-health-check`, `code-to-docs`, `thought-palette-extract`, doc-\* guides, `change-review-request`, `change-review-response`).  
Exception: **`test-first` is always on for propose** (and as required during apply per `opsx-apply-guide`).

**Change-doc review** — opt-in only (user names the skills or chooses the post-propose hint). **Never auto-required.** Primary slot: after Propose / alongside Human gate — changes, before Apply. Load from the **active project repo**: `.agents/skills/change-review-request/` and `.agents/skills/change-review-response/` (workspace-relative), not relative to this skill’s install dir. Response reviewer ≠ apply worker ≠ post-apply Check `code-review`.

Do **not** paste full texts of those skills here — read and follow them when the stage runs.

## Repair policy (N = 3)

Classify every problem; do **not** mark everything `blocked`.

| Tier | When | Behavior |
| --- | --- | --- |
| **self-fix** | Unit test / lint / compile failures **inside** the assigned change scope | Apply worker fixes **implementation** and re-runs checks. Up to **N = 3** hard-verify (or equivalent) failure→fix cycles per change. Still within change docs. |
| **report-continue** | `out_of_scope` finds, skipped check categories, small deviations already recorded in `tasks.md`, non-blocking notes | Write into the result / `_memory.md` as needed; **continue** the worker’s remaining assigned changes. |
| **stop-for-human** | Requirement contradiction, missing secrets/env, design unimplementable, **self-fix exhausted (N=3) still red**, semantic pollution needing a new change, `needs_input` | Set `blocked` / `needs_input`, write run files, report with options (see below for `needs_input`), **wait**. Do not silently expand scope. |

### Self-fix anti-cheat (required)

self-fix **repairs implementation** (and may add tests under `test-first` that express the change’s required behavior). It must **not** make hard-verify green by weakening, deleting, or rewriting assertions / tests to “pass.”

- **Forbidden**: delete or soften failing tests solely to clear the gate; comment-out assertions; broaden matchers until anything passes.
- **Allowed exception**: remove or rewrite a test **only when the change package explicitly requires it** (e.g. `tasks.md` / `design.md` says obsolete tests must go because the feature direction changed). If removal is tempting but **not** written in the package → **stop-for-human** / `needs_input`, do not treat it as self-fix.

### `needs_input` menu (recommended)

When a worker returns `needs_input`, the orchestrator relays to the user **and** writes `_needs-input.md` with: one-line reason, then a **recommended default four-choice menu** (plus optional situational choices). Prefer numbered choices so the user can reply with e.g. `②`. Do not leave the user with only “stuck” and no next step.

Recommended default choices:

1. **Supply definition** — human adds / amends the missing boundary in discussion or change docs  
2. **Resolve from repo/env** — allow read-only lookup in the repo or environment, then resume  
3. **Scaffold placeholder** — temporary stub / placeholder **only after the user explicitly picks this option**; until then, Hard rule “No invention” still applies  
4. **Skip this item** — defer (report-continue / record deferred); do not claim the work is done  

Optional extra choices may be appended when the situation needs them. Choice **③** must not be executed unless the user selected it.

### Factory overrides of verify skills (explicit)

Under factory mode only:

1. **`hard-verify` — auto-fix** — During apply, treat hard-verify as the apply worker’s exit gate. On failure, apply **self-fix** (above, including anti-cheat) rather than “report-only and stop”. The standalone skill’s default “never auto-fix” is **overridden for apply workers** for in-scope implementation fixups only. Check workers remain read-only and must not auto-fix.
2. **`hard-verify` — report destination** — The standalone skill’s §6 (“conversation only”; do not write check notes into project files) is **overridden**: apply workers **must** write hard-verify evidence to the current run as `hard-verify-<worker>.md` (and may still summarize briefly in chat). Still **forbidden**: writing those notes into `openspec/**`, change packages, or product source trees.
3. **`code-review` — Spec authority (required)** — Under factory Check, the Spec axis **must** use that change’s **`design.md` and `proposal.md`** as the sole Spec source. Do **not** search issue trackers, `docs/` PRDs, or ask the user for a Spec path. If those change docs are missing → report Spec as blocked / cannot review and continue Standards; do not invent a Spec.
4. **`code-review` — fixed point** — The orchestrator **must** inject `fixed_point` into every Check worker prompt (and record it in `_memory.md` when known — typically the SHA / ref before the apply batch, or merge-base with `main`/`master`). Check workers must not ask the user for a fixed point when one was supplied.
5. **`code-review` — report destination** — Check workers write `check-<change-id>-code-review.md` under `run_dir` (and may summarize in chat). Still **forbidden**: writing findings into change packages / `openspec/**`. Only a separate Check worker may run `code-review` under factory mode (never the apply worker).

## `.factory/` run workspace

### When to create

- **Do create** a run directory when the session leaves discuss into propose, apply, verify, or any write/dispatch work.
- **Do not create** if the session stays in discuss read-only and ends there.

### Path

```text
.factory/<YYYY-MM-DD>-<slug>/
```

- `slug`: lowercase English letters, digits, hyphens only (`[a-z0-9-]+`). Strip or replace illegal characters; no spaces or CJK in the folder name.
- Example: `.factory/2026-07-23-create-login-api/`
- Only the **orchestrator** creates the run directory. Workers must not create sibling runs under `.factory/`.

### Slug uniqueness (required)

- **One factory topic / one factory conversation → one distinct slug.** Different topics on the same day must use **different** slugs (do not reuse another topic’s folder).
- The full path `.factory/<YYYY-MM-DD>-<slug>/` must be **unique** under `.factory/`. The orchestrator owns uniqueness.
- **If the directory already exists:**
  - User is **resuming** that run → reuse it (read `_status.md` first).
  - New topic or unclear → **do not overwrite**. Pick a new slug (e.g. append `-2`, `-3`, or a more specific phrase) or ask the user whether to resume vs create a new run.
- Prefer slugs that name the work (feature / change series), not generic words like `work` or `task`.

### What belongs here

- Orchestration state, dispatch plans, worker results, verify reports, cross-worker memory.
- **Not** product source code (that stays in normal project paths).
- **Not** a substitute for `openspec/**` specs or change packages.
- Verify reports under `run_dir` are allowed only via the factory overrides above — nowhere else in the repo as “check scratchpads”.

### File conventions

| Kind | Pattern | Who writes | Purpose |
| --- | --- | --- | --- |
| Underscore (control / handoff) | `_*.md` | Orchestrator (workers may append only when prompt says so) | Control-plane and temp handoff |
| Worker artifacts | `<role>-<id>-*.md` (no leading `_`) | That worker | Structured results |

**Required control files** (once the run exists and the stage applies):

| File | When | Content |
| --- | --- | --- |
| `_status.md` | Always after run creation; update each stage transition | Stage, branch, workers, blockers (≤3), pointers to latest artifacts |
| `_dispatch-plan.md` | When a dispatch plan is published | The named-worker table awaiting / after confirmation |
| `_memory.md` | When any cross-worker fact must persist | Main summary + shared facts all later workers should read (decisions, paths, env notes). Keep short. |

**Optional underscore files:**

| File | Purpose |
| --- | --- |
| `_handoff-<worker>.md` | Temp handoff for one worker (resume, partial progress) |
| `_needs-input.md` | On `needs_input`: reason + recommended four-choice menu (and any situational extras); see Repair policy |

**Worker artifact examples:**

| File | Purpose |
| --- | --- |
| `apply-w1-result.md` | `FACTORY_APPLY_RESULT_V1` envelope |
| `hard-verify-w1.md` | hard-verify evidence for that apply worker |
| `check-<change-id>-code-review.md` | `code-review` report from a Check worker |
| `change-review-request-NN.md` | Optional change-doc review brief |
| `change-review-response-NN.md` | Optional change-doc review verdict (paired `NN`) |

Every worker prompt includes `run_dir: .factory/<…>/` and must read `_memory.md` + `_status.md` when present. Chat stays a short rollup; durable detail lives under `run_dir`.

## 1. Enter factory mode

On `/orchestrator-factory`:

1. State that factory mode is on.
2. Parse the user command for: start stage, stop stage, change names / series, optional skills, model preferences, existing `run_dir` if resuming.
3. If stage/scope is missing or ambiguous → **discuss read-only**; say so; do not create `.factory/`, do not propose or apply until the user directs.
4. If resuming: read `_status.md` / `_dispatch-plan.md` / latest results under the named run before acting.

## 2. Propose

When the user directs propose (after discussion has settled, or they skip discuss explicitly):

1. Ensure the `.factory/` run exists (create if needed); init `_status.md` and empty `_memory.md` if new.
2. Follow `openspec-propose` + `opsx-propose-guide` + `test-first`.
3. When one or more changes exist, go to §3. Do not start workers.
4. **Hint (not a gate):** also tell the user that optional change-doc review is one available next action (`change-review-request` → separate reviewer `change-review-response`). Other next actions remain (inspect changes, confirm dispatch, etc.). Never require review before dispatch by default.

### Optional change-doc review (opt-in handoff)

Only when the user opts in (names the skills or chooses the hint). Skipping leaves the normal path unchanged.

1. Ensure `run_dir/change-review-request-NN.md` exists (follow active project `.agents/skills/change-review-request/`).
2. Wait for a separate reviewer to write `change-review-response-NN.md` (follow `.agents/skills/change-review-response/`).
3. Read the verdict and recommended next action; roll up into `_status.md`.
4. Next action comes from the response (`confirm dispatch` | `amend change` | `needs_input`). If verdict is not `ready to apply`, do not treat dispatch confirm as green-light until the user amends / clarifies (or explicitly overrides).

**Reviewer prompt (shape)** — when dispatching a reviewer:

```text
[orchestrator-factory / change-doc-review]
role: change-doc reviewer (not apply, not Check code-review)
run_dir: .factory/<YYYY-MM-DD>-<slug>/
request: change-review-request-NN.md
skills: load from active project `.agents/skills/change-review-response/`
return: write change-review-response-NN.md under run_dir
constraint: change docs only; no apply; no product-code review
```

## 3. Dispatch plan (required stop)

After changes are created (or when the user asks to apply existing changes), **immediately** publish a **named-worker assignment**, write `_dispatch-plan.md`, update `_status.md`, and **stop**. Optional change-doc review does **not** block writing the plan.

### Assignment rules

- **Independent** changes → may recommend different apply workers (parallel if harness allows).
- **Same series, sequential / dependent** → **one apply worker** owns that entire ordered set.
- Name workers clearly (e.g. `W1`, `W2`). List exact change ids and order per worker.
- Adapt to the user command and dependency text in the packages — no fixed parallel template.

### Plan table (required shape)

```markdown
## Dispatch plan (awaiting confirmation)

| Worker | Role | Changes (ordered) | Rationale |
| --- | --- | --- | --- |
| W1 | apply | `series-01-…` → `series-02-…` | same series, sequential |
| W2 | apply | `standalone-fix-…` | independent |

- Parallelism: <none | W1 ∥ W2 | …>
- Optional skills named by user: <none | …>
- Check workers: to be dispatched after apply (code-review; Spec = design.md / proposal.md)
- run_dir: `.factory/<YYYY-MM-DD>-<slug>/`
- Next: confirm all / confirm subset / reassign workers | (optional) change-doc review
```

Then wait for the user to confirm all, run a subset, or reassign. **Reporting the plan is not permission to start.** Skipping change-doc review is always allowed. If the user **opted in** and the latest response is not `ready to apply`, do not treat confirm as green-light until they resolve (amend / clarify) or explicitly override.

## 4. Apply (after confirm only)

1. Start only the apply workers / changes the user approved.
2. Prefer Multitask / subagents; one prompt per named apply worker.
3. Keep prompts short — cold-start from change docs + `run_dir` files; **do not** paste long chat history.
4. Apply worker **must** run `hard-verify` before finishing each change (or the batch it owns), honor **Repair policy (N=3)**, write results under `run_dir`, and **must not** run `code-review`.
5. Before or when starting apply, the orchestrator records `fixed_point` in `_memory.md` (SHA/ref to diff against for later Check).

### Apply worker prompt (shape)

```text
[orchestrator-factory / apply]
worker: <W1>
role: apply
changes: <id1, id2, … in order>
run_dir: .factory/<YYYY-MM-DD>-<slug>/
skills: openspec-apply-change, opsx-apply-guide, test-first, hard-verify
repair: self-fix N=3 + anti-cheat (no weaken/delete tests to pass unless package requires); report-continue; stop-for-human / needs_input with recommended menu
return: FACTORY_APPLY_RESULT_V1 → write apply-<worker>-result.md and hard-verify-<worker>.md under run_dir
constraint: follow change docs; no code-review; no sync/archive/commit; no inventing requirements; surface out_of_scope; stop after assigned changes
```

Optional: `notes: <brief user instruction>`.

### Apply worker return (FACTORY_APPLY_RESULT_V1)

```text
FACTORY_APPLY_RESULT_V1
worker: <W1>
changes: <ids>
status: ok | partial | blocked | needs_input
summary: <one line>
self_fix_rounds_used: <0..3 per change as needed>

## per_change
- id: <change-id>
  tasks: done | partial | blocked
  unit_tests: pass | fail | skip | n/a
  hard_verify: pass | fail | skip
  deviations: <short or (none)>
  assumptions_made: <short or (none)>
  developer_verification: <short or see tasks.md>

## blocked
- <reason or (none)>

## out_of_scope
- <item or (none)>
```

Use `blocked` / `needs_input` only for **stop-for-human**. Prefer `partial` + `out_of_scope` / deviations for report-continue.

## 5. Machine verify — code-review (Check workers only)

After the approved apply batch finishes (and apply results are in `run_dir`):

1. Dispatch **separate Check worker(s)** — never reuse the apply worker identity/session for the check.
2. Each Check worker runs **`code-review` only** (read-only), for one or more assigned changes, writing `check-<change-id>-code-review.md` under `run_dir`.
3. **Spec constraint (required):** Spec axis authority is **only** that change’s `design.md` and `proposal.md`. Do not use issue trackers or other PRD paths.
4. **fixed_point:** Orchestrator passes the value from `_memory.md` (or resolves it now) into the Check prompt — Check must not ask the user for it when supplied.
5. Orchestrator aggregates into `_status.md` and a short chat rollup.
6. Green checks ≠ archive permission and ≠ substitute for human E2E.

Factory mode does **not** run `impl-verify`; `code-review` replaces it at this stage.

### Check worker prompt (shape)

```text
[orchestrator-factory / check]
worker: <C1>
role: check
changes: <id1, …>
run_dir: .factory/<YYYY-MM-DD>-<slug>/
skills: code-review
fixed_point: <SHA or ref from _memory.md>
spec_source: openspec change design.md + proposal.md for each assigned change (factory override — do not search issue tracker / docs PRD)
return: write check-<change-id>-code-review.md under run_dir (Standards + Spec sections)
constraint: read-only; no edits; no hard-verify ownership; no sync/archive/commit; do not ask the apply worker to self-certify; do not ask user for fixed_point or Spec path when supplied above
```

Then **stop for human E2E**.

## 6. Human gates (must stop)

| Gate | When | You do |
| --- | --- | --- |
| Changes review | After propose | Wait; user inspects change packages. **Hint** optional change-doc review — never auto-required |
| Dispatch confirm | After dispatch plan | Wait; no workers until confirm / subset / reassign. If change-review was opted in and response ≠ `ready to apply`, hold green-light until resolved |
| Human E2E | After Check workers finish | Wait; user runs E2E |
| Sync/archive | Before sync+archive | Wait for explicit approval; see §7 |

Also stop on **stop-for-human** from the Repair policy. For `needs_input`, relay with the **recommended four-choice menu** (write `_needs-input.md`). Do not stop the whole factory for report-continue items.

## 7. Sync / archive

Only after human E2E (and any fixes the user directed) and **explicit** user approval to sync+archive:

1. Detect current git branch.
2. If branch is **not** `main` and **not** `master` → **block** sync/archive, warn that running them on a feature branch can damage main-spec files on `main`/`master`, and stop.
3. If on `main`/`master` and user approved → follow `openspec-sync-specs` and `openspec-archive-change` as directed.

## 8. Commit suggestion and change-log

- After the user asks, or when wrapping a finished batch: run **`commit-message-suggestion`** and give the text to the user. **Never commit.**
- When the overall factory job is fully finished: **suggest** running **`change-log`**, then follow that skill and present output to the user.

## 9. Status rollup (orchestrator)

Keep user-facing status short; persist detail under `run_dir`:

```markdown
## Factory status
- Stage: <discuss | propose | await-dispatch | apply | machine-verify | await-e2e | await-archive | done>
- run_dir: <.factory/… or (none — discuss only)>
- Branch: <name> (sync/archive allowed: yes | no)
- Workers: <summary>
- Change-doc review: <(none / skipped) | awaiting response | ready to apply | needs doc fix | needs user clarify>
- Blockers / decisions needed: <≤3 bullets or none>
```

## 10. Stop

Stop at every human gate, on stop-for-human, and after delivering the current stage’s artifact. Resume only on user direction. Re-enter by reading the run’s `_status.md` and latest artifacts — do not rely on chat memory alone.
