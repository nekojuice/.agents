# Change-review document format

Single source of truth for section headings and pairing. Both `change-review-request` and `change-review-response` follow this file. The concern category names below keep the same meaning as the master copy, the `code-review` finding tags.

## Pairing

| Rule | Value |
| --- | --- |
| Location | Same factory `run_dir` (`.factory/_runs/<date>-<slug>/`) |
| Request file | `change-review-request-NN.md` |
| Response file | `change-review-response-NN.md` |
| `NN` | Two-digit sequence in that `run_dir` (`01`, `02`, …). Request and response share the same `NN`. |

## Request document (`change-review-request-NN.md`)

```markdown
# Change review request NN

## 1. Meta

| Item | Value |
| --- | --- |
| run_dir | `.factory/_runs/<date>-<slug>/` |
| Change id | `<openspec-change-id>` |
| Change path | `openspec/changes/<id>/` |
| Purpose | Judge whether the OpenSpec **change package docs** match settled user requirements (before apply) |
| Expected response | **`change-review-response-NN.md`** (same run_dir; written by reviewer) |

## 2. Settled user requirements

Numbered list of settled requirements the change docs must express. Quote or paraphrase only what the user finalized. This section is a level 1 source and outranks every other source in judgment.

## 3. Design principles for judgment

| Principle | How to use it in review |
| --- | --- |
| … | … |

## 4. Review checklist

Ask the reviewer to mark each row **pass** / **gap** / **unclear** in the response, with brief evidence (file + section).

| # | Focus | Judgment | Evidence / notes |
| --- | --- | --- | --- |
| A | … | | |
| B | … | | |

Also require an overall verdict in the response:
- `ready to apply` / `needs doc fix` / `needs user clarify`

Beyond this checklist, the reviewer may raise concerns of their own; record them by category in the response's **Reviewer concerns** section. If any concern is `change-design-flaw`, the verdict is at least `needs user clarify`.

## 5. Reference paths

### Change package (required reads; object under review)

- `openspec/changes/<id>/proposal.md`
- `openspec/changes/<id>/design.md`
- `openspec/changes/<id>/tasks.md`
- `openspec/changes/<id>/specs/...` (list only the specs that matter)

### Decision context sources (read-only; consult when in doubt)

Group by level, highest first; tag each entry with its level. Write `none` under a level with nothing to list. The change package above is level 4.

- Level 1: information the user stated or confirmed — settled decisions and user-confirmed handoff items in the run (e.g. factory `_memory.md`)
- Level 2: management canonical files (`.manager/` when present), `openspec/specs/...`, project docs
- Level 3: run discussion notes the user has not confirmed

### Optional named by the brief

- Sample docs, `AGENTS.md`, archive / db_schema paths, `_dispatch-plan.md` — only when they ground a checklist item.
```

The paragraph in request §4 that invites concerns beyond the checklist is fixed text; every brief keeps it.

The level list in request §5 (with the change package as level 4) keeps the same meaning as the master copy in `code-review` step 3.

## Response document (`change-review-response-NN.md`)

```markdown
# Change review response NN

## Overall verdict

One of: `ready to apply` | `needs doc fix` | `needs user clarify`

One short paragraph: why.

## Checklist results

Mirror every checklist row from the matching request. Each row gets **pass** / **gap** / **unclear** plus evidence citing change-doc paths and sections, or decision context sources (name the level).

| # | Focus | Judgment | Evidence / notes |
| --- | --- | --- | --- |
| A | … | pass \| gap \| unclear | `design.md` §… — … |

## Gaps and unclear items

For each **gap** or **unclear**: what is missing or ambiguous, with evidence. Skip this section when every row is **pass**.

## Reviewer concerns

One row per concern; write `none` when there are no concerns. A `change-design-flaw` row names the conflicting higher-level source, or explains why the design is judged flawed.

| Category | Concern | Evidence (change file + section) | Reasoning |
| --- | --- | --- | --- |
| `conforms-but-flawed` \| `change-design-flaw` | … | … | … |

## Context consulted

Each decision context source actually consulted, with its level, and which judgment it calibrated. Mark sources the brief did not list as "not in brief". Write `none` when nothing was consulted.

## Recommended next action

Exactly one:
- `confirm dispatch` — docs match; user may proceed toward apply when ready
- `amend change` — name which change files to edit and the minimal fix
- `needs_input` — name the question(s) only the user can answer
```

Verdict rules (master copy; other skills repeating the verdict floor keep the same meaning as this list):

- Every checklist row **pass** and no concerns → `ready to apply`.
- Any **gap** or `conforms-but-flawed` concern, with no **unclear** row and no `change-design-flaw` → `needs doc fix`.
- Any **unclear** row or `change-design-flaw` concern → `needs user clarify`.
- Verdict `needs user clarify` → next action `needs_input`, listing the questions for the user.

`needs user clarify` items go to the coordinating orchestrator, which resolves what it can from the information sources and escalates only the rest to the user as one consolidated list; the reviewer does not address the user item by item.

## Judgment vocabulary

| Term | Meaning |
| --- | --- |
| **pass** | Change docs express the settled requirement clearly and consistently |
| **gap** | Settled requirement missing, contradicted, or under-specified in the change docs, and fixable by amending the change alone |
| **unclear** | Cannot judge even after consulting the change docs and the listed decision context sources |

## Concern categories

| Category | Meaning |
| --- | --- |
| `conforms-but-flawed` | The change docs follow the settled requirements, but have a problem fixable without changing intent — in design, task split, verification steps, internal consistency, or wording the change can simply amend |
| `change-design-flaw` | The change conflicts with a higher-level source, or resolving the problem needs a user decision (for example an overall approach or underlying principle that cannot be fixed without changing intent) |

`violates-change` (the third `code-review` tag: deviates from the change) is carried by checklist **gap** in change-review and never appears under concerns. These definitions are shared with the `code-review` finding tags and `change-review-response`; keep them the same in meaning as the master copy, the `code-review` finding tags.

Gap versus `change-design-flaw`: if the settled requirement is clear and fixing the change alone resolves the problem, judge **gap** (→ `needs doc fix` / `amend change`); likewise, a concern that amending the change alone resolves is `conforms-but-flawed`, not `change-design-flaw`. If resolving it needs a user decision — the settled requirement itself looks unsound, a higher-level source outside the brief conflicts with the change, or higher-level sources conflict with each other — record `change-design-flaw` (→ `needs user clarify` / `needs_input`).
