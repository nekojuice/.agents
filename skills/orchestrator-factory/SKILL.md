---
name: orchestrator-factory
description: >-
  Factory-mode orchestrator for the full opsx agent workflow (discuss → propose →
  apply → verify → agent E2E review → human E2E → sync/archive → commit
  suggestion → change-log).
  Dispatches named workers with human gates and a .factory/ run workspace. Use
  when the user requests 工廠模式 / factory mode or equivalent wording, or when
  a fresh session is assigned an existing .factory run whose status is
  await-factory-session. Under an automation plan a manager approved with the
  user, one factory session works through several runs in sequence.
  Non-project implementation work may use a tailored factory route without
  forcing opsx.
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5, Codex GPT-5, Claude Code Opus 5.5
  version: "1.10"
  last_updated: "2026-11-03T17:21:42"
---

# orchestrator-factory

Enables **factory mode**: you are the **plant manager** (orchestrator). You schedule stages, propose named-worker assignments, enforce human gates, own the `.factory/` run workspace, aggregate reports, and stop for the user. You drive the project's factory skills; you do **not** bury yourself in implementation body work when workers are available.

## Activation

Enter factory mode through either route:

1. **User intent** — the user runs `/orchestrator-factory`, says 工廠模式 / factory mode, asks to hand work to the factory, or uses unambiguous equivalent wording.
2. **Cold-start handoff** — a fresh session is assigned a specific existing `.factory/_runs/<run>/` and its `_status.md` says `Stage: await-factory-session` and `Factory started: no`. A running factory session the manager moves to another run of an automation plan enters that run the same way, whatever its stage.

For a cold-start handoff, announce factory mode, reuse that run, and read `_status.md`, `_intake.md`, and `_memory.md` before choosing a stage. When moving from another run, carry over nothing that run did not record. Do not require the user to repeat an enable command. Skill activation does **not** authorize dispatch, apply, E2E acceptance, sync, or archive; every existing human gate still applies, except as § Automation sets for a run with an automation authorization.

Do **not** activate merely because `.factory/` exists, because an old/completed run is present, because factory or PM is mentioned in explanation, or because the user makes an ordinary implementation request without factory intent or a named cold-start handoff.

## Hard rules

1. **User command wins** — interpret the current turn for stage, scope, and optional skills. Do not invent a rigid always-parallel schedule. This includes lifting a default such as rule 6, but only through the user's explicit request in the conversation or an automation authorization recorded in the run (see rule 6).
2. **Default stage** — if the user says nothing actionable about stage, or you cannot tell where to start → **discuss read-only** (no writes, no dispatch, **no** `.factory/` run). Prefer loading / following `discuss-first`.
3. **No silent dispatch** — never start apply (or any write-capable worker) until the user has confirmed the dispatch plan (or a revised subset / reassignment), except as § Automation allows.
4. **Same-series sequential work → one worker** — ordered / dependent changes in the same series stay on **one named worker**. Independent changes may use different workers.
5. **Verify separation** — apply workers may run **`hard-verify` only**. **`code-review` is never run by an apply worker.** The orchestrator always dispatches a **separate Check worker** for `code-review`, unless the user leaves Check out at dispatch confirmation. No nested “self-check subagent” inside apply under factory mode. When used, **change-doc review** also stays off the apply worker (separate reviewer ≠ Check `code-review`). **`e2e-review` runs only in a separate E2E worker** (§ 5b); neither apply workers nor the orchestrator operate the system under test.
6. **No commit by default** — run `commit-message-suggestion` and hand the suggestion to the user. The orchestrator commits on the user's behalf only under that skill's `## Committing on request`: the user's explicit request in the conversation, or the commit rule of the run's automation authorization (§ Automation). Record a continuing authorization's scope and expiry in `_memory.md` under `## User decisions` when a run exists. Never infer authorization; never push unless the user separately asks. **Workers never commit.**
7. **Never auto-load `grill-me` / `grill-with-docs`** into the regular factory path.
8. **Model** — workers **default to the same model as the orchestrator**. Changing model requires asking the user and getting approval.
9. **Harness** — prefer parallel workers or subagents. If the environment cannot isolate workers, **degrade**: produce paste-ready per-worker commands and wait; do not pretend isolation existed.
10. **No invention** — workers must not invent requirements. When information is insufficient, consult sources read-only in the order of § Information sources. If the change conflicts with a higher-priority source, do not pick one yourself → `needs_input`. If still insufficient → `needs_input` (stop-for-human) or a disclosed local `assumptions_made` entry that remains reversible. Never fabricate APIs, fields, or behaviors.
11. **Workflow fits the work** — use the opsx path for durable project implementation. For work that is not project implementation, do not force OpenSpec artifacts or opsx stages; select a smaller factory route with explicit deliverables, worker boundaries, verification, and human gates.
12. **No project edits outside write stages** — while discussing, assisting with deployment, or drafting documents, the orchestrator does not modify project files, configuration files, or entry-point code. When code needs to change, explain why and ask whether to open a propose. Exception: an edit the user verbally authorizes — with a run, record the authorization in `_memory.md` under `## User decisions`; without a run, restate the authorized scope in the conversation. A non-project route follows the allowed writes it declared. The Agent E2E review stage is a write stage for the project's `.e2e/` folder only (§ 5b).
13. **`.manager` is read-only** — when the workspace has `.manager/`, the orchestrator and workers may read all of it read-only and must never write to it. Treat `.manager/_runs/` as leads only. `.manager` is never a required input; handoffs into the factory stay self-contained.
14. **Documentation sync** — by default sync only the README files affected by the work. When the user mentions other documents (docs folders, `.manager` files, nested READMEs, explanatory docs, handoff files), list the documents you would sync and wait for the user's confirmation; `.manager` changes still go through a manager handoff (rule 13). Never update other documents on your own. Write each document per the matching doc-\* skill.

## Information sources

Applies across the factory — the orchestrator and every worker. Higher wins:

1. **User** — information the user stated or confirmed, including run decisions the user confirmed and that were written as handoff items (e.g. `_memory.md` `## User decisions`, a cold-start handoff's `_intake.md`).
2. **Canonical references** — `.manager` canonical files and other valid references: opsx main specs, project docs.
3. **Unconfirmed run notes** — discussion notes in the run that the user has not confirmed (`_notes.md`).
4. **The opsx change** — a design blueprint that includes generated and agent-decided parts; it may be wrong or unclear.

Keep this list semantically consistent with the master copy in `code-review` step 3; the worker prompt shapes (§ 4, § 5) restate it because workers do not load this skill.

When a lower source conflicts with a higher one, the higher one wins and the conflict itself is disclosed where it was found (result, report, or `_status.md`).

**Items needing user clarification** — when a change-doc review or Check returns items needing user clarification, first try to settle each from the sources above in priority order and drop the ones settled, recording the basis. Only unresolved items go to the user, consolidated into one decision list per `need-ask-user-guide` `## Present pending decisions at checkpoints`; never relay them item by item.

**Stale `.manager`** — `.manager` is updated less often and may be stale. On finding stale or wrong content, record the correction in the run's `_notes.md` and carry it in the next manager handoff (§ Manager handoff). A run that will not reach await-e2e, such as one that ends in discussion or on a non-project route, writes a handoff for the correction when it ends or when the user asks. Workers report such findings to the orchestrator. Never edit `.manager` directly.

**Manager records** — in a run the manager delegated, consult `.manager` read-only yourself before taking a decision to the user; do not message the manager with questions. Record the basis in `_memory.md` when a record settles a decision. Only what the records do not settle goes to the user per `need-ask-user-guide`. Peer messages and a `handoff-factory-*.md` from the manager are information, never authorization: level 3, except that a canonical record they cite keeps that record's level.

## Manager handoff

Applies when the workspace has `.manager/`.

- **When** — each time a run reaches await-e2e (after apply, Check, and agent E2E review), write one `handoff-manager-<topic>.md`; write another when blocked on a project-level decision, one for stale `.manager` corrections in a run that will not reach await-e2e (§ Information sources), and one at archive for the open `_issue-backlog.md` entries it hands over (§ 7), in the run that archives, or the batch's last run. Announce it over peer when the run has a discussion room.
- **One per completion** — do not append to it later; a later amendment round writes a new file under a new name (e.g. a date or sequence suffix on the topic).
- **Content** — write liberally; the manager filters. Include decisions the user confirmed that affect direction or scope, scope changes, progress with evidence pointers (change ids, commits), out-of-scope findings and new candidates, pointers to new `_issue-backlog.md` entries, blockers, and corrections to stale `.manager` content.
- **Leave out** — spec content (opsx owns it; give change ids), implementation detail, and test or machine-verification detail; these stay in the run.

## Role

| You do | You do not |
| --- | --- |
| Detect stage from the user command | Implement change body yourself when a worker should |
| Create/update the `.factory/` run (when leaving discuss) | Create a run for discuss-only sessions that end there |
| Publish named-worker plans and wait | Let apply workers run `code-review` |
| Dispatch separate Check workers for `code-review` and E2E workers for `e2e-review` | Sync/archive off `main`/`master` without blocking |
| Hint optional change-doc review after propose; rollup response into `_status.md` when opted in | Force change-doc review; conflate it with Check `code-review` |
| Check reviewer and E2E reports against § Information sources and their evidence before aggregating | Relay or adopt reviewer findings, recommendations, or E2E statuses without checking them; operate the system under test yourself |
| Aggregate worker returns into short status + run files | Modify project files while discussing, assisting with deployment, or drafting documents (rule 12) |
| Maintain `.factory/_review-queue.md` and `.factory/_issue-backlog.md` | Treat verify green or an E2E report as “ready to ship” |
| Commit on the user's behalf only as rule 6 allows | Commit without that authorization; let workers commit |
| Stop at every human gate, on stop-for-human, and after delivering the current stage's artifact (§ 6, § 10) | Stop the whole factory for report-continue items |

Depth: orchestrator → apply / check / E2E workers. **Do not** nest verify inside apply. A Check worker may run `code-review`'s two axes in parallel, merged, or sequentially (`code-review` step 5) and reports the mode it used. An E2E worker may dispatch sub-workers as `e2e-review` allows; only it operates the system under test.

## Workflow selection

Choose the route before creating new artifacts or dispatching workers:

- **Project implementation** — durable changes to product behavior, source code, project configuration, data/schema, or a feature/fix intended to become part of the project. Use the full opsx workflow below unless the user explicitly sets another approved process.
- **Non-project implementation** — research, analysis, inventory, planning, documentation-only work, audits, or another deliverable that does not implement a durable project change. Do not require an OpenSpec change package. Build a task-specific route using only relevant skills and workers.

A non-project route must still state its deliverable, allowed writes, named-worker assignments when dispatching, verification method, and required human checkpoints. Reuse the factory run controls where useful, but do not invent empty propose/apply/sync/archive stages merely to resemble opsx. If the classification is ambiguous and changes the workflow materially, discuss read-only and ask the user.

## Factory stages (opsx project implementation workflow)

| Stage | Skills to load / follow | Notes |
| --- | --- | --- |
| **Discuss (read-only)** | `discuss-first` | Default when stage unclear; **no** `.factory/` run |
| **Propose** | `openspec-propose` + `opsx-propose-guide` + **`test-first` (always)** | Create run when entering this (or later) stage; then **hint** optional change-doc review |
| **Human gate — changes** | (none by default) | User inspects change docs; optional change-doc review sits here / alongside — **never auto-required** outside § Automation |
| **Dispatch plan** | (this skill) | May publish immediately after propose; change-review does **not** block writing the plan; **wait for confirm** |
| **Apply** | `openspec-apply-change` + `opsx-apply-guide` + `test-first` + **`hard-verify` (end of apply)** | Only after dispatch confirm; apply worker must not run `code-review` |
| **Machine verify (review)** | **`code-review` via separate Check worker(s)** | After apply batch; before agent E2E review; the change is the review target, judged against § Information sources |
| **Agent E2E review** | **`e2e-review` via separate E2E worker(s)** | Default; after Check, before human E2E; iterates with fixes (§ 5b) |
| **Human gate — E2E** | (none) | Present the checklist revised after agent E2E review and update `.factory/_review-queue.md`; user runs E2E on what remains; you wait |
| **Human gate — archive** | (none) | User must approve sync+archive |
| **Sync / archive** | `openspec-sync-specs` + `openspec-archive-change` | Blocked off main/master (below) |
| **Commit suggestion** | `commit-message-suggestion` | Suggestion by default; commit on the user's behalf only as rule 6 allows |
| **Change log** | `change-log` | Suggest when work is fully finished; output to user |

### Optional skills (opt-in only)

Load **only** when the user names them in the command (examples: `ponytail`, `karpathy-guidelines`, `opsx-health-check`, `code-to-docs`, `thought-palette-extract`, doc-\* guides, `change-review-request`, `change-review-response`).  
Exception: **`test-first` is always on for propose** (and as required during apply per `opsx-apply-guide`).

**Change-doc review** — opt-in only (user names the skills or chooses the post-propose hint). **Never auto-required**, except that § Automation always runs it. Primary slot: after Propose / alongside Human gate — changes, before Apply. Response reviewer ≠ apply worker ≠ post-apply Check `code-review`.

**Multi-agent collaboration** — `peer-agent-coordination` exists for peer sessions sharing a run directory. It is costly: do not enable it on your own; enable it when the user mentions it or a collaborative discussion with the user calls for it (see its `## 1. When to enable`), never because of run structure, another skill's reference, or worker count. When the run's `_intake.md` records the user's approval of the manager's delegation and a peer room, it is enabled; use that room. It is distinct from assigning one worker several tasks or several workers one task (§ 3 Assignment rules), which is ordinary subagent dispatch.

Do **not** paste full texts of those skills here — read and follow them when the stage runs.

## Repair policy (N = 3)

Classify every problem; do **not** mark everything `blocked`.

| Tier | When | Behavior |
| --- | --- | --- |
| **self-fix** | Unit test / lint / compile failures **inside** the assigned change scope | Apply worker fixes **implementation** and re-runs checks. Up to **N = 3** hard-verify (or equivalent) failure→fix cycles per change. Still within change docs. Test changes follow `opsx-apply-guide` anti-cheat. |
| **report-continue** | `out_of_scope` finds, skipped check categories, small deviations already recorded in `tasks.md`, non-blocking notes | Write into the result / `_memory.md` as needed; **continue** the worker’s remaining assigned changes. |
| **stop-for-human** | Requirement contradiction, missing secrets/env, design unimplementable, **self-fix exhausted (N=3) still red**, semantic pollution needing a new change, `needs_input` | Set `blocked` / `needs_input`, write run files, report with options (see below for `needs_input`), **wait**. Do not silently expand scope. |

E2E results are classified by the orchestrator, not by tier: a confirmed `product-fail` goes to a fix round; `run-error` and `needs-human` items are either re-dispatched or handed to the human checklist (§ 5b). Agent operation of the system is not fully reliable, so a `run-error` is never treated as a product failure.

### Self-fix anti-cheat (required)

self-fix **repairs implementation** and must follow `opsx-apply-guide` `## Test changes (anti-cheat)`, the single source for which test changes are allowed. Assertion changes during an amendment round follow `opsx-apply-guide` `## Amendment rounds` (flow and gates: § Amendment rounds).

### `needs_input` menu (recommended)

Before relaying a worker's `needs_input`, check the records the task designates — confirmed run decisions, `.manager`, project docs. If they already answer it, resume from that record and disclose the basis instead of asking the user again (criteria per `need-ask-user-guide`).

Otherwise the orchestrator relays to the user **and** writes `_needs-input.md` with: one-line reason, then a **recommended default four-choice menu** (plus optional situational choices). Prefer numbered choices so the user can reply with e.g. `②`. Do not leave the user with only “stuck” and no next step.

Recommended default choices:

1. **Supply definition** — human adds / amends the missing boundary in discussion or change docs  
2. **Resolve from repo/env** — allow read-only lookup in the repo or environment, then resume  
3. **Scaffold placeholder** — temporary stub / placeholder **only after the user explicitly picks this option**; until then, Hard rule “No invention” still applies  
4. **Skip this item** — defer (report-continue / record deferred); do not claim the work is done  

Optional extra choices may be appended when the situation needs them. Choice **③** must not be executed unless the user selected it.

### Factory overrides of verify skills (explicit)

Under factory mode only:

1. **`hard-verify` — auto-fix** — During apply, treat hard-verify as the apply worker’s exit gate. On failure, apply **self-fix** (above; anti-cheat per `opsx-apply-guide`) rather than “report-only and stop”. The standalone skill’s default “never auto-fix” is **overridden for apply workers** for in-scope implementation fixups only. Check workers remain read-only and must not auto-fix.
2. **`hard-verify` — report destination** — The standalone skill’s §6 (“conversation only”; do not write check notes into project files) is **overridden**: apply workers **must** write hard-verify evidence to the current run as `hard-verify-<worker>.md` (and may still summarize briefly in chat). Still **forbidden**: writing those notes into `openspec/**`, change packages, or product source trees.
3. **`code-review` — Spec basis (required)** — Under factory Check, the change is the review target. Judge it against § Information sources: user decisions, confirmed run handoff items, `.manager`, opsx main specs, project docs. When the change conflicts with a higher-priority source, classify the finding as `change-design-flaw` for the user to decide. Do **not** ask the user for a Spec path, and do **not** search external sources outside § Information sources (e.g. issue trackers). If the change docs are missing → report Spec as blocked / cannot review and continue Standards; do not invent a Spec.
4. **`code-review` — fixed point** — The orchestrator **must** inject `fixed_point` into every Check worker prompt (and record it in `_memory.md` when known — typically the SHA / ref before the apply batch, or merge-base with `main`/`master`; since workers do not commit, it is a working-tree base and the diff covers uncommitted and untracked files; re-checks use § Re-check after fixes). Check workers must not ask the user for a fixed point when one was supplied.
5. **`code-review` — report destination** — Check workers write `check-<change-id>-code-review.md` under `run_dir` (and may summarize in chat). Still **forbidden**: writing findings into change packages / `openspec/**`. Only a separate Check worker may run `code-review` under factory mode (never the apply worker).
6. **`hard-verify` — trigger** — The standalone skill's “run only when the user explicitly invokes it” is **overridden**: the user's dispatch confirmation authorizes each apply worker to run hard-verify before finishing each change (or the batch it owns). Check workers do not run hard-verify.
7. **`code-review` — finding categories** — Every finding in a Check report carries the category marker defined by `code-review`: `violates-change`, `conforms-but-flawed`, or `change-design-flaw`; `violates-change` and `change-design-flaw` occur on the Spec axis only.
8. **`e2e-review` — trigger and placement** — The user's dispatch confirmation (or the run's automation authorization) authorizes the E2E workers it lists. The report parent is always `run_dir`; the worker creates `run_dir/e2e-review/`.
9. **`e2e-review` — project assets** — Changes the E2E worker makes to the project's `.e2e/` belong to the run's change set; the orchestrator commits them only as rule 6 allows. Creating `.e2e/` for the first time needs the user's approval (§ 5b).

## `.factory/` run workspace

### When to create

- **Do create** a run directory when the session leaves discuss into propose, apply, verify, or any write/dispatch work.
- **Do not create** if the session stays in discuss read-only and ends there.
- **Initialize `.factory/`** when creating the first run: if `.factory/.gitignore` does not exist, create it with the single line `_runs/`. Runs are working space for discussion and orchestration and get too noisy to track; converged results live in opsx changes and specs.

### Path

```text
.factory/
├── .gitignore            # single line: _runs/
├── _review-queue.md
├── _issue-backlog.md
└── _runs/
    └── <YYYY-MM-DD>-<slug>/
```

- `slug`: lowercase English letters, digits, hyphens only (`[a-z0-9-]+`). Strip or replace illegal characters; no spaces or CJK in the folder name.
- Example: `.factory/_runs/2026-07-23-create-login-api/`
- Only the **orchestrator** creates the run directory. Workers must not create sibling runs under `.factory/_runs/`.
- The `.factory/` root holds only `.gitignore`, `_review-queue.md`, `_issue-backlog.md`, and `_runs/`. Workers never write the two root files; the orchestrator writes them, and the manager may update them when needed.

### Slug uniqueness (required)

- **One factory topic → one distinct slug.** Different topics on the same day must use **different** slugs (do not reuse another topic’s folder). One factory session may work through several runs in sequence under an automation plan.
- The full path `.factory/_runs/<YYYY-MM-DD>-<slug>/` must be **unique** under `.factory/_runs/`. The orchestrator owns uniqueness.
- **If the directory already exists:**
  - User is **resuming** that run → reuse it (read `_status.md` first).
  - New topic or unclear → **do not overwrite**. Pick a new slug (e.g. append `-2`, `-3`, or a more specific phrase) or ask the user whether to resume vs create a new run.
- Prefer slugs that name the work (feature / change series), not generic words like `work` or `task`.

### What belongs here

- Orchestration state, dispatch plans, worker results, verify reports, cross-worker memory.
- **Not** product source code (that stays in normal project paths).
- **Not** a substitute for `openspec/**` specs or change packages.
- Verify reports under `run_dir` are allowed only via the factory overrides above — nowhere else in the repo as “check scratchpads”.

### Cross-run review queue

`.factory/_review-queue.md` summarizes, across runs, what the user still checks at final acceptance. It is built from the runs' `_review-checklist.md` and written at a higher level of abstraction than they are, so the user is not buried in small items.

- Group items by feature or business flow; everything to check on one screen sits in one place. Each item links back to its source run; when the same feature changes again, merge into the existing item.
- An item that agent E2E review verified and the orchestrator checked is ticked, with the report path as its source pointer; evidence stays in the run.
- End state: only what a human alone can handle remains unticked. Exclude what automated tests, hard-verify, or checked agent E2E results already cover, and simple logic checks (`need-ask-user-guide`).
- Under an automation plan, consolidate the runs' checklists here once, when the batch ends.
- Clearing is part of archive (§ 7): ticked items move back to the run that owns them. Items not finished, or needing long observation, stay only when the user decides, and are then committed; otherwise the queue is empty once the work is done.

### Cross-run issue backlog

`.factory/_issue-backlog.md` is a holding area for problems not yet handled: out-of-scope findings such as a broken layout, implementation failures that agent E2E review found, and suspected errors. Anything may go in; the user reviews it to open the next change or run.

- One entry per problem: status (open, change opened, won't fix), symptom, and evidence path.
- Clearing is part of archive (§ 7): entries still open move to the manager through a manager handoff, then the backlog is emptied; they stay in the factory and are committed only when the user asks. Without `.manager`, the user decides where they go.

Leave both root files out of run commits unless the user asks to keep them.

### File conventions

| Kind | Pattern | Who writes | Purpose |
| --- | --- | --- | --- |
| Underscore (control / handoff) | `_*.md` | Orchestrator (workers may append only when prompt says so); peer files follow `peer-agent-coordination` | Control-plane and factory-internal temp handoff |
| Worker artifacts | `<role>-<id>-*.md` (no leading `_`) | That worker | Structured results |
| Cross-party handoff | `handoff-<recipient>-<topic>.md` in this run's root | Orchestrator, or the manager delivering `handoff-factory-<topic>.md` | Handoff between this run and a party outside it (e.g. `manager`) |

Handoff files between the manager and a factory always live at the factory run root: the factory's `handoff-manager-<topic>.md` in its own run, and the manager's `handoff-factory-<topic>.md` in the receiving factory run. Names use lowercase letters, digits, and hyphens only. The file starts with three header lines: `Source run:`, `Recipient:`, `Date:`. The recipient never edits the file and records its processing in its own run.

**Required control files** (once the run exists and the stage applies):

| File | When | Content |
| --- | --- | --- |
| `_status.md` | Always after run creation; update each stage transition | Stage, branch, workers, Blockers / Decisions needed / Reminders, amendment rounds, gate events, pointers to latest artifacts |
| `_dispatch-plan.md` | When a dispatch plan is published | The named-worker table awaiting / after confirmation |
| `_memory.md` | When any cross-worker fact must persist | Main summary + shared facts all later workers should read (decisions, paths, env notes); user-confirmed decisions under `## User decisions`. Keep short. |
| `_intake.md` | Written by the PM handoff; the factory never rewrites it | Confirmed context, the delegation record, and any `## Automation authorization` |
| `_review-checklist.md` | After Check (input to agent E2E review); revised before await-e2e | This run's checklist at the level `opsx-apply-guide` §4 sets; after agent E2E review, each item's result and report pointer, with what remains for the human. Ticks stay permanently |

**Optional underscore files:**

| File | Purpose |
| --- | --- |
| `_handoff-<worker>.md` | Factory-internal temp handoff for one worker (resume, partial progress); not a cross-party handoff |
| `_needs-input.md` | On `needs_input`: reason + recommended four-choice menu (and any situational extras); see Repair policy |
| `_notes.md` | Discussion notes not yet confirmed by the user, and corrections to stale `.manager` content (§ Information sources level 3) |

**Control-file writes** — update `_status.md`, `_memory.md`, `_dispatch-plan.md`, `_review-checklist.md`, `_review-queue.md`, and `_issue-backlog.md` in place with an editing tool. When an append is genuinely needed, first check that the same content is not already there. Never blind-append with shell redirection.

**Worker artifact examples:**

| File | Purpose |
| --- | --- |
| `apply-w1-result.md` | `FACTORY_APPLY_RESULT_V1` envelope |
| `hard-verify-w1.md` | hard-verify evidence for that apply worker |
| `check-<change-id>-code-review.md` | `code-review` report from a Check worker |
| `e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` | One agent E2E round per folder (report, result, evidence), per `e2e-review` |
| `change-review-request-NN.md` | Optional change-doc review brief |
| `change-review-response-NN.md` | Optional change-doc review verdict (paired `NN`) |

Every worker prompt includes `run_dir: .factory/_runs/<…>/` and must read `_memory.md` + `_status.md` when present. Workers judge by § Information sources and may read `.manager` read-only. By default a worker works only in its current run. A named worker may be reused across runs: the prompt restates the new run's `run_dir`, constraints, and control files to read, and declares that unrecorded context from the earlier run does not carry over. Chat stays a short rollup; durable detail lives under `run_dir`.

## 1. Enter factory mode

On either activation route:

1. State that factory mode is on.
2. Determine whether this is explicit user intent, a cold-start handoff, or a resume; identify the exact `run_dir` when supplied.
3. Read the named run's `_status.md` and relevant intake, memory, dispatch, or latest result files before acting. A cold-start handoff reads `_intake.md` and `_memory.md` first. When needed, consult `.manager` read-only per § Information sources; its absence never blocks entering factory mode.
4. Classify the work as project implementation or non-project implementation and select the matching route.
5. Parse the request for start/stop stage or deliverable, scope, optional skills, model preferences, and verification needs.
6. If stage, deliverable, scope, or workflow classification is missing or ambiguous → **discuss read-only**; say so; do not create another run, propose, apply, or dispatch until resolved.

## 2. Propose

When the user directs propose (after discussion has settled, or they skip discuss explicitly):

1. Ensure the `.factory/` run exists (create if needed); init `_status.md` and empty `_memory.md` if new.
2. Follow `openspec-propose` + `opsx-propose-guide` + `test-first`.
3. Set the run's checklist level (`broad` or `focused`) per `opsx-apply-guide` §4 and record it in `_memory.md`.
4. When one or more changes exist, go to §3. Do not start workers.
5. **Hint (not a gate):** also tell the user that optional change-doc review is one available next action (`change-review-request` → separate reviewer `change-review-response`). Other next actions remain (inspect changes, confirm dispatch, etc.). Never require review before dispatch by default.

### Optional change-doc review (opt-in handoff)

Only when the user opts in (names the skills or chooses the hint). Skipping leaves the normal path unchanged.

1. Ensure `run_dir/change-review-request-NN.md` exists (follow `change-review-request`).
2. Wait for a separate reviewer to write `change-review-response-NN.md` (follow `change-review-response`).
3. Read the verdict and recommended next action, then check the response against § Information sources: mark each finding adopted, excluded as a false positive (with the basis), or in conflict with a higher-priority source. Items needing user clarification follow § Information sources. Roll up into `_status.md`.
4. The next action is the orchestrator's checked recommendation (`confirm dispatch` | `amend change` | `needs_input`), not the response copied over. Any `change-design-flaw` in the response makes the verdict at least `needs user clarify`. If the verdict is not `ready to apply`, do not treat dispatch confirm as green-light until the user amends / clarifies (or explicitly overrides).

**Reviewer prompt (shape)** — when dispatching a reviewer:

```text
[orchestrator-factory / change-doc-review]
role: change-doc reviewer (not apply, not Check code-review)
run_dir: .factory/_runs/<YYYY-MM-DD>-<slug>/
request: change-review-request-NN.md
skills: change-review-response
return: write change-review-response-NN.md under run_dir
constraint: review target = change docs; when in doubt, read-only lookup of the decision-context sources the request lists (confirmed run handoff items, .manager, opsx main specs, docs); when those are insufficient, other sources read-only, marked "not in brief" in Context consulted; no apply; no product-code review
```

## 3. Dispatch plan (required stop)

After changes are created (or when the user asks to apply existing changes), **immediately** publish a **named-worker assignment**, write `_dispatch-plan.md`, update `_status.md`, and **stop**. Optional change-doc review does **not** block writing the plan.

### Assignment rules

- **Independent** changes → may recommend different apply workers (parallel if harness allows).
- **Same series, sequential / dependent** → **one apply worker** owns that entire ordered set.
- Name workers clearly (e.g. `W1`, `W2`). List exact change ids and order per worker.
- Adapt to the user command and dependency text in the packages — no fixed parallel template.
- The user may direct one worker to take several tasks or several workers to share one task (rule 1 overrides rule 4's default).
- A named worker from a previous run may be reused; note its source run under `Reused workers` in the plan.

### Plan table (required shape)

```markdown
## Dispatch plan (awaiting confirmation)

| Worker | Role | Changes (ordered) | Rationale |
| --- | --- | --- | --- |
| W1 | apply | `series-01-…` → `series-02-…` | same series, sequential |
| W2 | apply | `standalone-fix-…` | independent |

- Parallelism: <none | W1 ∥ W2 | …>
- Optional skills named by user: <none | …>
- Check workers: to be dispatched after apply (code-review; judged against § Information sources)
- E2E workers: to be dispatched after Check (e2e-review; write permission: <read-only | scope>)
- Reviewers left out by the user: <none | Check | E2E>, with the reason
- Reused workers: <none | W1 ← <source run>>
- run_dir: `.factory/_runs/<YYYY-MM-DD>-<slug>/`
- Next: confirm all / confirm subset / reassign workers | (optional) change-doc review
```

Then wait for the user to confirm all, run a subset, or reassign. **Reporting the plan is not permission to start.** Skipping change-doc review is always allowed. If the user **opted in** and the latest response is not `ready to apply`, do not treat confirm as green-light until they resolve (amend / clarify) or explicitly override.

## 4. Apply (after confirm only)

1. Start only the apply workers / changes the user approved.
2. Prefer parallel workers or subagents; one prompt per named apply worker.
3. Keep prompts short — cold-start from change docs + `run_dir` files; **do not** paste long chat history.
4. Apply worker **must** run `hard-verify` before finishing each change (or the batch it owns), honor **Repair policy (N=3)**, write results under `run_dir`, and **must not** run `code-review`.
5. Before or when starting apply, the orchestrator records `fixed_point` in `_memory.md` (SHA/ref to diff against for later Check).

### Apply worker prompt (shape)

```text
[orchestrator-factory / apply]
worker: <W1>
role: apply
changes: <id1, id2, … in order>
run_dir: .factory/_runs/<YYYY-MM-DD>-<slug>/
skills: openspec-apply-change, opsx-apply-guide, test-first, hard-verify
repair: self-fix N=3; anti-cheat per opsx-apply-guide; report-continue; stop-for-human / needs_input with recommended menu
sources: when information is insufficient, consult read-only in this order, higher wins — 1 user-confirmed (_memory.md ## User decisions, _intake.md, confirmed handoff items) > 2 .manager canonical, opsx main specs, project docs > 3 _notes.md (unconfirmed) > 4 the change; on a conflict with a higher source → needs_input; .manager read-only
verification_level: <broad | focused, from _memory.md; per opsx-apply-guide §4>
reuse: <only for a reused worker — this run_dir replaces the earlier run; unrecorded context from <source run> does not carry over>
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
  developer_verification: <items needing human judgment at the verification_level, per opsx-apply-guide §4; exclude what tests or hard-verify cover; or see tasks.md>

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
3. **Review basis (required):** the change is the review target, judged against § Information sources (override 3); every finding carries a category marker (override 7). Do not search issue trackers.
4. **fixed_point:** Orchestrator passes the value from `_memory.md` (or resolves it now) into the Check prompt — Check must not ask the user for it when supplied.
5. Before aggregating, check every finding against § Information sources: mark it adopted, excluded as a false positive (with the basis), or in conflict with a higher-priority source; items needing user clarification follow § Information sources. Do not relay or adopt the reviewer's report or recommendations unchecked. Then aggregate into `_status.md` and a short chat rollup.
6. Green checks ≠ archive permission and ≠ substitute for human E2E. The same holds for an agent E2E report.

Factory mode does **not** run `impl-verify`; `code-review` replaces it at this stage.

### Check worker prompt (shape)

```text
[orchestrator-factory / check]
worker: <C1>
role: check
changes: <id1, …>
run_dir: .factory/_runs/<YYYY-MM-DD>-<slug>/
skills: code-review
fixed_point: <SHA, ref, or snapshot ref from _memory.md; may be a working-tree base — workers do not commit, so the diff includes uncommitted and untracked files per code-review step 1>
recheck_scope: <optional, re-checks only: the findings the fix addresses and the files or hunks it touches; review only these>
review_basis: each assigned change is the review target; judge it against these basis sources in priority order, higher wins — 1 user-confirmed (_memory.md ## User decisions, _intake.md, confirmed handoff items) > 2 .manager canonical, opsx main specs, project docs > 3 _notes.md (unconfirmed) > 4 the change; do not search issue trackers
amendment: <optional; large-scale amendment only — verify every rewritten or deleted test listed in tasks.md against the behavior it supersedes, per opsx-apply-guide ## Amendment rounds>
return: write check-<change-id>-code-review.md under run_dir (Standards + Spec sections; state the execution mode)
constraint: read-only; may read the listed sources including .manager; tag each finding violates-change | conforms-but-flawed | change-design-flaw; no edits; no hard-verify ownership; no sync/archive/commit; do not ask the apply worker to self-certify; do not ask the user for a Spec path, or for fixed_point when supplied above
```

After the Check findings are handled (fixed and re-checked), or after apply when the user left Check out, write the run's full `_review-checklist.md` from the changes' developer verification lists (`opsx-apply-guide` §4) and go to § 5b, or **stop for human E2E** when the user left agent E2E review out at dispatch confirmation (small runs such as a single debug fix); record the skip in `_status.md`. The user may likewise leave out Check.

### Re-check after fixes

- Before a fix starts, the orchestrator records the re-check `fixed_point` in `_memory.md`: a snapshot ref of the working tree taken before the fix (e.g. `git stash create`; fall back to `HEAD` when the tree is clean), or the list of files the fix touches when no snapshot is possible. Workers do not commit, so a committed ref before the fix usually does not exist.
- Also record the fix scope: the findings the fix addresses and the files, or hunks, it touches. Untracked files are not captured by a snapshot ref, and a file list alone also pulls in earlier uncommitted work in those files, so the scope is what narrows the re-check.
- A re-check after a fix covers only that fix: dispatch a Check worker with that `fixed_point` and the fix scope in `recheck_scope:`.
- It may be skipped when the fix only touches documentation, only adjusts test data, or the user says no re-check is needed. Record the skip and its reason in `_status.md`.

## 5b. Agent E2E review (E2E workers only)

The last agent self-check before human E2E. Neither apply workers nor the orchestrator operate the system under test.

1. Dispatch a separate E2E worker with the full `_review-checklist.md` and the inputs `e2e-review` requires (shape below). Write permission comes from the user's dispatch confirmation or the automation authorization; without it the worker is read-only. Only one E2E worker operates a given environment at a time.
2. Check the returned `E2E_REVIEW_RESULT_V1` against its report and evidence before using it. Mark each item trusted, not trusted, or to rerun; never drop a human item because a worker says it passed.
3. A trusted `product-fail` goes to a fix round; re-check the fix as in § Re-check after fixes, then dispatch the next E2E round with `--prev` and the fix as its basis.
4. For `run-error` and `needs-human`, decide whether to send the worker back to operate again or to hand the item to the human. Tool reliability is limited, so allow reruns; stop when the item clearly cannot be done by the agent. For `verified-with-limits`, tick only what was verified and keep the limit as a human item.
5. A `needs-input` return is handled like `needs_input` in the Repair policy. A `blocked` return (environment or driver unavailable) hands the remaining items to the human, or stops for the user when the run cannot continue without them.
6. Out-of-scope findings and implementation failures not fixed in this run go to `.factory/_issue-backlog.md`.
7. Revise `_review-checklist.md`: tick trusted items with the report path; keep key items and those untested, failed, inconclusive, or that the agent could not run. Then update `.factory/_review-queue.md` (under § Automation, consolidate at the end of the batch instead) and go to the Human E2E gate.

**`.e2e/` assets** — the E2E stage may write the project's `.e2e/` folder within `e2e-review`'s boundaries; this is not a product edit and needs no propose. List the worker's writes in the run and check them against the granted permission; a write beyond it is a blocker. When the return says `init_needed: yes`, present the proposal at the next human gate; only after the user approves, tell the next E2E dispatch to apply it.

### E2E worker prompt (shape)

```text
[orchestrator-factory / e2e]
worker: <E1>
role: e2e
run_dir: .factory/_runs/<YYYY-MM-DD>-<slug>/
skills: e2e-review
checklist: <item numbers and original text from _review-checklist.md>
report_parent: run_dir
write_permission: <read-only | test data the user allowed>
accounts / environment: <only when .e2e/PROJECT.md does not cover them>
previous_round: <round folder, or none>
round_basis: <the fix this round verifies: commit or change id>
init_apply: <only after the user approved an init proposal: its round folder and who approved it, for --approved-by>
return: E2E_REVIEW_RESULT_V1
constraint: follow e2e-review boundaries; write only .e2e/ and run_dir/e2e-review/; no product edits; no commit; questions go to the orchestrator
```

## 6. Human gates (must stop)

| Gate | When | You do |
| --- | --- | --- |
| Changes review | After propose | Wait; user inspects change packages. **Hint** optional change-doc review — never auto-required. Under § Automation, held once for the whole batch |
| Dispatch confirm | After dispatch plan | Wait; no workers until confirm / subset / reassign. If change-review was opted in and response ≠ `ready to apply`, hold green-light until resolved. Under § Automation, the batch change review stands in |
| Human E2E | After agent E2E review (or Check, when E2E was left out) | Write the manager handoff (§ Manager handoff), present the `_review-checklist.md` (revised after agent E2E review, or the full list when E2E was left out), update `.factory/_review-queue.md` outside § Automation, then wait; user runs E2E on what remains. Tick items the user reports passed (§ Cross-run review queue). Under an automation plan, follow § Automation instead |
| Sync/archive | Before sync+archive | Wait for explicit approval; see §7 |

Also stop on **stop-for-human** from the Repair policy. For `needs_input`, relay with the **recommended four-choice menu** (write `_needs-input.md`). Do not stop the whole factory for report-continue items.

### Amendment rounds

Applies to requirement changes or E2E findings (agent or human) after apply and before archive.

- **Amend or open new** — amend the existing change when intent and scope stay the same; open a new change for a new capability or a changed meaning.
- **Docs and tests** — how the amendment is annotated in the change docs follows `opsx-propose-guide` `## Amendments`; which existing assertions may change follows `opsx-apply-guide` `## Amendment rounds`. Record the round in `_status.md`; Stage keeps its existing values.
- **Gate** — an amendment the user requests directly skips the Changes review gate but is recorded in the run (`_memory.md` `## User decisions`). An amendment the orchestrator initiates returns to Changes review.
- **Dispatch** — dispatch confirmation still applies (rule 3). A user-requested amendment that names the worker to carry it out counts as that confirmation.
- **Large-scale amendments** — the orchestrator marks the amendment as large-scale and hands it to a worker; the Check worker then verifies each test change the worker lists against `opsx-apply-guide` `## Amendment rounds` (Check prompt `amendment:` line).

## Automation

Applies when the run's `_intake.md` carries an automation authorization the user approved through the manager. For such a run, this section wins where the rest of this skill differs.

The manager moves this session between the batch's runs over peer. Check the manager records first (§ Information sources).

1. **Design pass** (Stage `design`) — in each run, discuss and propose, then always run change-doc review. Do not stop for questions: record each decision the records do not settle in the run's `_notes.md` under `## Pending decisions`, disclose the assumption the change makes per `opsx-propose-guide`, and keep going. On `needs doc fix`, amend the change and review again; after two rounds that still need fixes, record the remaining items as pending decisions. On `needs user clarify`, record the unsettled items the same way. A later run's propose treats earlier changes of the batch as prerequisites, stated with `Depends on:` per `opsx-propose-guide` §3.
2. **Batch change review** (Stage `await-batch-review`) — once every run has its changes, present all changes and every run's pending decisions in one checkpoint, as one decision list per `need-ask-user-guide`, and wait. This is the Changes review gate for the whole batch. The user confirms all runs or a subset; amendments the user directs here need no further review.
3. **Build pass** — dispatch each confirmed run in dependency order; the batch review stands in for its Dispatch confirm gate. After Check, fix the adopted findings and re-check, then run agent E2E review (§ 5b). On reaching await-e2e, with the revised `_review-checklist.md`, commit as the authorization says (default one commit), then write the manager handoff with the commit hash and report over peer.
4. **Stop** a run in the build pass on `needs_input` or stop-for-human, self-fix exhausted, a Check finding that needs the user, or an out-of-scope finding that needs a new change. Report to the manager; only runs that depend on it wait.
5. **End of batch** — when the manager reports the batch done, consolidate the runs' checklists into `_review-queue.md`; the Human E2E and Sync/archive gates then apply as usual. Never push without the user's separate explicit request.

## 7. Sync / archive

Only after human E2E (and any fixes the user directed) and **explicit** user approval to sync+archive:

1. Detect current git branch.
2. If branch is **not** `main` and **not** `master` → **block** sync/archive, warn that running them on a feature branch can damage main-spec files on `main`/`master`, and stop.
3. If on `main`/`master` and user approved → follow `openspec-sync-specs` and `openspec-archive-change` as directed.
4. Clear the cross-run files as part of archive: move this work's ticked `_review-queue.md` items back to the runs that own them, and hand open `_issue-backlog.md` entries to the manager (§ Cross-run issue backlog). Keep and commit either file's entries only when the user asks.

If manual verification items remain unchecked, the user's verbal confirmation is enough to archive; record the confirmation and its time in `_status.md`. Never tick an item as human-verified for the user or claim the user verified it; agent-verified ticks carry their report path.

## 8. Commit suggestion and change-log

- After the user asks, or when wrapping a finished batch: run **`commit-message-suggestion`** and give the text to the user. Commit on the user's behalf only as rule 6 allows.
- When the overall factory job is fully finished: **suggest** running **`change-log`**, then follow that skill and present output to the user.

## 9. Status rollup (orchestrator)

Keep user-facing status short; persist detail under `run_dir`:

```markdown
## Factory status
- Stage: <discuss | await-factory-session | propose | design | await-batch-review | await-dispatch | apply | machine-verify | agent-e2e | await-e2e | await-archive | done>
- run_dir: <.factory/_runs/… or (none — discuss only)>
- Branch: <name> (sync/archive allowed: yes | no)
- Workers: <summary>
- Change-doc review: <(none / skipped) | awaiting response | ready to apply | needs doc fix | needs user clarify>
- Blockers: <≤3 bullets or none; recorded decisions that still block are always listed, with a pointer to their record, and do not count toward the cap>
- Decisions needed: <blocking decisions not yet recorded, or none>
- Reminders: <non-blocking reminders or none>
```

`Decisions needed` lists only decisions that block the flow and are not already recorded. A decision that is recorded but still unanswered and still blocks the flow goes under `Blockers` with a pointer to its record, not under `Reminders`. Before sending, check the records the task designates (`.manager`, docs, run). Selection criteria follow `need-ask-user-guide` `## Present pending decisions at checkpoints`.

## 10. Stop

Stop at every human gate, on stop-for-human, and after delivering the current stage’s artifact. Resume only on user direction, or on the manager's run assignment under § Automation. Re-enter by reading the run’s `_status.md` and latest artifacts — do not rely on chat memory alone.

### Replacing the orchestrator session

An exception, for when large work exhausts a session. The outgoing session, if it still can, writes unrecorded progress into `_status.md` and `_memory.md`. The incoming session reads the control files and latest artifacts, states the stage it recovered, then continues. The user is present for a replacement; in a peer room, update the roster as the user directs. Only authorization recorded in `_memory.md` or `_intake.md` carries over.
