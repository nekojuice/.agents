---
name: work-effort-eval
description: >-
  Used by the orchestrator of a factory or manager run to record how long the run takes and
  how much load it puts on the agent and the user while the work happens, and to evaluate the
  whole workflow at closing through a separate eval worker that counts signals, grades them
  against fixed anchors, and attributes the load to decisions, methods, the environment, or
  the task itself. Also used to evaluate a run on its own. Workers use it only when dispatched
  as the eval worker. Not for evaluating machine-learning models (ML evals) and not about a
  model's reasoning-effort setting.
disable-model-invocation: false
metadata:
  author: Claude Code Opus 5.5
  version: "1.0"
  last_updated: "2026-11-18T15:40:43"
---

# work-effort-eval

Turn the vague sense of "how hard was this" and "how long did it take" into reference indicators that can be compared across runs. The evaluation covers the whole workflow: decisions, methods, skills, the environment, and the task. Skill quality is one part of it.

The skill has two parts: the orchestrator keeps a light record in `_effort.md` while working, and an eval worker writes `eval-effort.md` at closing. The record is not an audit log. Missing data does not need to be reconstructed precisely.

## Position

- This is an optional evaluation skill. An orchestrator that references it enables it on its own. When the user says not to use it, record that in the state file (`_status.md` for a factory, `_run.md` for a manager) and stop recording.
- Indicators are references, not targets.
- Do not estimate difficulty or duration before the work. Early estimates vary widely, and an estimate that misses gives the user false confidence.

## Unit and start

- The unit of evaluation is one run.
- The skill can also start on its own at any time; the agent that starts it acts as the orchestrator for both parts.
  - Use the current factory or manager run when there is one.
  - Otherwise create a run folder and its state file in the workspace that exists (`.factory` or `.manager`) under that role's naming rules, without entering that role's mode or gates.
  - With neither workspace, keep `_effort.md` and `eval-effort.md` in a folder the user names, and record no baseline.
- When the skill starts mid-run or after the work, mark every signal it could not capture as `not recorded`. Never count a missing signal as zero.

## Three axes

Report the axes separately; never convert one into another. Counts are totals for the whole run.

| Axis | Means | Signals |
| --- | --- | --- |
| Volume | How much work there was | Agent working time, tokens when known, files touched, number of changes. Reference only: much easy work also takes long |
| Agent load | How hard the work was on the agent | Self-fix rounds; review rounds that needed fixes; Check and E2E fix rounds; `needs_input` and stop-for-human events; session handoffs or context compactions; share of clarification items the agent settled itself versus raised to the user. Count E2E `run-error` reruns separately: they reflect tools, not the task |
| User load | How much the user had to carry | User interaction time; exchanges; items in decision lists; recommendations the user overrode; user corrections and things the agent did wrong on its own; process reminders the user had to give; amendment rounds the user started; human E2E items left because the agent could not verify them; information the user supplied that the agent could have looked up (`available, not checked`) |

## Part 1: record while working (orchestrator)

Keep `_effort.md` at the run root and update it in place with an editing tool:

```markdown
# Work effort record

Run: <run path>

## Sessions

| Session start | Orchestrator model, platform, version |
| --- | --- |

## Checkpoints

| Time | Checkpoint | Exchanges since previous |
| --- | --- | --- |

## Events

| Time | Type | Source | Note |
| --- | --- | --- | --- |

## Evaluation

<Filled after closing: eval grades, orchestrator grades, reasons, outlet suggestions>
```

- **Sessions** — one row per orchestrator session, including one that takes over after a handoff.
- **Checkpoints** — take the time from the OS, local time with offset. Stamp discussion start, convergence, action start, each human gate, each dispatch and each worker return, and closing. Most hosts do not show the agent message timestamps, so checkpoints are the only clock. When the record starts after the discussion began, stamp the discussion start if it is known, otherwise mark it `not recorded`.
- **Events** — record only what the orchestrator alone can see: user corrections, things the agent did wrong without asking, overridden recommendations, process reminders, information the user supplied, session handoffs and context compactions (record one when taking over or resuming), and skill problems. Mark the source skill or role (apply, Check, E2E, reviewer, orchestrator) when it is clear.
- **Skill problems** — when the user's feedback points at a skill, record it per `skill-feedback-notes` as usual and also add an event here. One does not replace the other.
- The main work comes first. Write events when they happen rather than recalling them at closing, since compaction and handoffs lose them, but never interrupt the work to record. Do not copy signals that files already hold; the eval worker counts those.

### Time

- **User interaction time** — inside interactive stretches (discussion, convergence, human gates), count each gap between consecutive checkpoints in full when it is within the idle threshold, default 30 minutes. For a longer gap, count `min(gap, exchanges × threshold)`, using the exchanges recorded for that gap; with no exchanges, count zero.
- **Agent working time** — sum the stretches from dispatch to worker return, the build pass under automation, and the stretches where the orchestrator works on its own without waiting for the user (from action start to the next human gate or interactive checkpoint).

## Part 2: evaluate at closing (eval worker)

Closing always includes the evaluation while the skill is enabled; it needs no gate. Run it before the role handles its skill notes and before the user checks the run's staging drafts, so its findings join the same handoff and the same check.

1. Tell the user that the closing evaluation is about to run.
2. Dispatch a new sub-agent as the eval worker. A fresh worker carries no context from the work, which keeps the grading independent:

   ```text
   [<orchestrator> / eval]
   role: eval
   run_dir: <run path>
   skills: work-effort-eval
   window: <first checkpoint> – <closing>; fixed_point: <from _memory.md when present>
   return: write eval-effort.md at run_dir
   constraint: read-only except eval-effort.md; no dispatch; do not edit _effort.md or other files
   ```

3. Review the result (§ Orchestrator review), write the final grades and outlet suggestions into `_effort.md`, and tell the user the report path and the suggested outlets.

The eval worker does only the following, plus § Anchors, § Attribution, and § Report. It does not keep `_effort.md`, dispatch, or write handoffs.

- Counts the signals files already hold, within the window:
  - factory: `change-review-response-NN.md`; `self_fix_rounds_used` in apply results, summed over changes; `check-*-code-review.md`; amendment rounds, gate events, and Decisions needed in `_status.md`; `## Pending decisions` in `_notes.md`; `e2e-review/` round folders; `_needs-input.md`; items left for the human in `_review-checklist.md`; commit times;
  - manager: reply rounds and the Conflicts and To confirm rows in requirements comparisons; `reviews/_triage*.md`; change decisions; commit times.
- Finds signals the orchestrator did not record when the files show them, and marks the rest `not recorded`.
- Records its own model, platform, and version.

### Report: `eval-effort.md`

- Header: run, date, task type, eval model, platform, and version, and the user's anonymous code or proficiency label when the run records one.
- Counts per axis, each with its source.
- Grades per axis, with the signals that decided them.
- Signals not recorded.
- Attribution: each hotspot, its layer, its evidence, and the suggested outlet.
- Difficulty profile, when the task itself is hard.

## Anchors

Grade each anchored signal low, medium, or high from the run totals. An axis takes the highest grade among its signals and names the deciding signal. Signals without an anchor row are reported as counts only and are not graded. Signals not recorded are listed and left out of the grade.

| Axis | Signal | Low | Medium | High |
| --- | --- | --- | --- | --- |
| Volume | Agent working time | < 1 h | 1–4 h | > 4 h |
| Agent load | Review rounds needing fixes | 0 | 1 | ≥ 2 |
| Agent load | Self-fix, Check, and E2E fix rounds | 0 | 1–2 | ≥ 3 |
| Agent load | `needs_input` and stop-for-human | 0 | 1 | ≥ 2 |
| Agent load | Handoffs or compactions | 0 | 1 | ≥ 2 |
| User load | User interaction time | < 30 min | 30 min–2 h | > 2 h |
| User load | Corrections and wrong acts | 0 | 1–2 | ≥ 3 |
| User load | Overridden recommendations | 0 | 1 | ≥ 2 |
| User load | Process reminders | 0 | 1 | ≥ 2 |
| User load | Decision-list items | 0–2 | 3–5 | ≥ 6 |
| User load | User-started amendment rounds | 0 | 1 | ≥ 2 |
| User load | Human E2E items left | 0–2 | 3–5 | ≥ 6 |
| User load | Available, not checked | 0 | 1 | ≥ 2 |

## Attribution

Attribute load events, not the run as a whole.

1. Find the hotspots: the stages, gates, or kinds of question where the load concentrates.
2. Trace each hotspot up to the decision, rule, or condition that produced it.
3. Assign a layer:
   - Load from tools or the environment (E2E `run-error`, missing secrets, permissions, tool failures) → **environment layer**.
   - Otherwise ask the counterfactual: would this load have disappeared if a different decision or route had been taken earlier? Yes → **decision layer** (the manager's scope, split, order, or premise) or **method layer** (the skill's route, stages and gates, or verification method). No under any reasonable route → **inherent difficulty**.
4. Check `available, not checked` against the sources: run notes, `.manager`, project docs, specs, and external docs. Available at the time → **agent behavior**, or the method layer when the skill does not require checking. Not available → **documentation gap**.
5. For inherent difficulty, give a profile: uncertainty, feedback-loop length, difficulty of verification, domain knowledge, resources.
6. Tag the run with a task type so baselines can be compared later.

A single run only supports a hypothesis. A pattern across runs supports changing a skill or a decision.

## Outlets

The evaluation changes nothing itself; it suggests where each finding goes, and that outlet's own gates decide.

| Layer | Outlet |
| --- | --- |
| Method layer (skill) | `skill-feedback-notes` |
| Decision layer or wrong premise in documents | Manager handoff; revision of the manager's decision documents |
| Documentation gap | Manager handoff and document revision; a gap in a skill goes to `skill-feedback-notes` |
| Agent behavior | The report and the baseline only; when it recurs across runs, `skill-feedback-notes` |
| Environment and tools | Issue backlog |
| Inherent difficulty | Baseline for that task type; no fix |

After the review, write method-layer findings and calibration items as entries in the run's skill notes, so they leave with the same closing handoff.

## Orchestrator review

As with other reviews, the orchestrator checks the eval worker's report and may ignore, reject, or change a finding, but respects the evaluation in most cases. When it changes a grade, keep both in `_effort.md`: the eval grade, the orchestrator grade, and a one-line reason.

## Hand back to the manager

- **Factory with `.manager` present** — write one more handoff, `handoff-manager-<topic>-effort.md`, carrying the evaluation summary and the report path. The factory never writes `.manager` itself. Without `.manager`, the evaluation ends with the report.
- **Factory under automation** — at the batch's closing, evaluate each run of the batch: one `eval-effort.md` and one evaluation handoff per run.
- **Manager** — draft `staging/_effort-ledger.md` as the full ledger with this run's row added, from `orchestrator-pm`'s `assets/effort-ledger.template.md` when the ledger does not exist yet; apply it after the user checks the draft. A factory's evaluation handoff is drafted into the ledger the same way.
- Work outside this framework records no baseline.
- When the evaluation crosses into the skill repository, generalize it as `skill-feedback-notes` does: project content stays in runs. Compare users only through an anonymous code or a proficiency label, never an identity.

## Calibration

The anchors, the idle threshold, and the evaluation instructions are themselves calibration targets, like the prompt of an LLM-as-a-judge. The orchestrator's grade changes and the user's corrections of an evaluation are the calibration material; hand them back through `skill-feedback-notes`.
