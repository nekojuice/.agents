# Change-review document format

Single source of truth for section headings and pairing. Both `change-review-request` and `change-review-response` follow this file.

## Pairing

| Rule | Value |
| --- | --- |
| Location | Same factory `run_dir` (`.factory/<date>-<slug>/`) |
| Request file | `change-review-request-NN.md` |
| Response file | `change-review-response-NN.md` |
| `NN` | Two-digit sequence in that `run_dir` (`01`, `02`, …). Request and response share the same `NN`. |

## Request document (`change-review-request-NN.md`)

```markdown
# Change review request NN

## 1. Meta

| Item | Value |
| --- | --- |
| run_dir | `.factory/<date>-<slug>/` |
| Change id | `<openspec-change-id>` |
| Change path | `openspec/changes/<id>/` |
| Purpose | Judge whether the OpenSpec **change package docs** match settled user requirements (before apply) |
| Expected response | **`change-review-response-NN.md`** (same run_dir; written by reviewer) |

## 2. Settled user requirements

Numbered list of settled requirements the change docs must express. Quote or paraphrase only what the user finalized.

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

## 5. Reference paths

### Change package (required reads)

- `openspec/changes/<id>/proposal.md`
- `openspec/changes/<id>/design.md`
- `openspec/changes/<id>/tasks.md`
- `openspec/changes/<id>/specs/...` (list only the specs that matter)

### Optional named by the brief

- Sample docs, `AGENTS.md`, archive / db_schema paths, factory `_memory.md` / `_dispatch-plan.md` — only when they ground a checklist item.
```

## Response document (`change-review-response-NN.md`)

```markdown
# Change review response NN

## Overall verdict

One of: `ready to apply` | `needs doc fix` | `needs user clarify`

One short paragraph: why.

## Checklist results

Mirror every checklist row from the matching request. Each row gets **pass** / **gap** / **unclear** plus evidence citing change-doc paths and sections.

| # | Focus | Judgment | Evidence / notes |
| --- | --- | --- | --- |
| A | … | pass \| gap \| unclear | `design.md` §… — … |

## Gaps and unclear items

For each **gap** or **unclear**: what is missing or ambiguous, with evidence. Skip this section when every row is **pass**.

## Recommended next action

Exactly one:
- `confirm dispatch` — docs match; user may proceed toward apply when ready
- `amend change` — name which change files to edit and the minimal fix
- `needs_input` — name the question(s) only the user can answer
```

## Judgment vocabulary

| Term | Meaning |
| --- | --- |
| **pass** | Change docs express the settled requirement clearly and consistently |
| **gap** | Settled requirement missing, contradicted, or under-specified in the change docs |
| **unclear** | Cannot judge from cited docs alone (ambiguous wording or missing cross-link) |
