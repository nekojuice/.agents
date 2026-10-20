---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match the spec under review — issue, PRD, or change — judged against basis sources in priority order?). Runs both reviews as parallel sub-agents by default (merged when the change is small, sequential when the host has no sub-agents) and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
disable-model-invocation: false
metadata:
  author: Codex GPT-5, Claude Code Opus 5.5
  version: "1.1"
  last_updated: "2026-10-20T15:44:18"
---

Two-axis review of the diff between the working tree (committed, uncommitted, and untracked changes) and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the spec under review (issue / PRD / change)? That spec is one object of the review, not the sole source of truth: judge it against the basis sources from step 3, in priority order.

By default both axes run as **parallel sub-agents** so they don't pollute each other's context (step 5 covers merged and sequential runs), then this skill aggregates their findings.

Fetching from an issue tracker is needed only when step 2 resolves the spec from issue references in commits; skip it when the caller already named the spec under review. Follow the fetch method the repo's docs describe; if they describe none, ask the user for the issue contents or a path.

## Finding tags

Every finding carries exactly one tag. "Change" in a tag name means the spec under review — in an OpenSpec workflow, the change package.

| Tag | Meaning | Axis |
| --- | --- | --- |
| `violates-change` | The code deviates from the spec under review — breaks or omits something it explicitly requires | Spec only |
| `conforms-but-flawed` | The code follows the spec under review, but has a problem fixable without changing the spec's intent — a standards breach, smell, logic defect, or risk, including where the spec is silent, and including spec wording that can simply be amended (unclear or internally inconsistent; note "amend change") | Standards, Spec |
| `change-design-flaw` | The spec under review conflicts with a higher-priority basis source, or resolving the problem needs a user decision | Spec only |

These names and definitions are shared with the concern categories in the change-review format (`change-review-request/FORMAT.md`) and with `change-review-response`. This table is the master copy; those copies keep the same meaning as it.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

A caller may instead supply a snapshot ref taken before a fix (for example from `git stash create`) or the fix's file list; either serves as the fixed point for a re-check. With a file list, diff from the original fixed point but limit the review to those paths. A snapshot ref does not capture untracked files, and a file list still includes earlier uncommitted work in those files; when the caller also supplies a re-check scope (the findings fixed and the files or hunks touched), review only that scope.

Capture the diff commands once, so the review covers uncommitted work as well as commits:

- Tracked changes: `git diff <base>` against the working tree, where `<base>` is `git merge-base <fixed-point> HEAD` for a branch-like fixed point, or the snapshot ref itself. When the caller supplied a file list, append `-- <paths>`.
- Untracked files: `git ls-files --others --exclude-standard` (filtered to the file list when one was supplied); the sub-agents read these files in full as new files.
- Commits: `git log <fixed-point>..HEAD --oneline` — may be empty when all work is uncommitted.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and that the tracked diff or the untracked list is non-empty. A bad ref or empty change set should fail here — not inside two parallel sub-agents.

### 2. Identify the spec under review

If the caller already named the spec under review, use it — do not search or ask the user. Otherwise look for it, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.) — fetch them as described above.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. An `openspec/changes/<id>/` package matching the branch name or change id.
5. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** review will skip and report "no spec available".

### 3. Identify the basis sources

Basis sources are what the Spec axis judges the code — and the spec under review — against. Priority, highest first:

1. Information the user stated or confirmed — the user's statements in this conversation, and handoff items or decision records written after the user confirmed them.
2. Canonical and other valid references — management canonical files (under `.manager/` when it exists), main OpenSpec specs (`openspec/specs/`), project docs.
3. Discussion notes the user has not confirmed (for example, run notes).
4. The spec under review itself — a design blueprint that may contain generated or self-decided content, and may be wrong or unclear.

This four-level list is the master copy; other skills repeat it and keep their copies the same in meaning as this master copy.

**Getting them.** When the caller supplies a basis-source list, use that list. When used standalone without one, probe read-only for: the user's statements in this conversation, `openspec/specs/`, project docs and README, and `.manager/` canonical files when present. `.manager/_runs/` is a lead only, never a basis. If nothing is found, review against the spec alone and note "basis: spec only" in the report. Do not ask the user just to find basis sources.

**Using them.**

- All basis sources are read-only; never write to them.
- When in doubt, consult them before judging.
- Context calibrates judgement — drop false positives already decided or fixed elsewhere, confirm a real violation. Never use it to demand something neither the spec under review nor a higher-priority source asks for.
- When the spec under review conflicts with a higher-priority source, tag `change-design-flaw`, cite both sides, and leave the decision to the user. Do not pick a side or rewrite the requirement.
- If a basis source itself looks stale or wrong, note it in the report; do not edit it.

### 4. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 5. Run both reviews

**Execution mode.**

- **parallel** (default) — send a single message with two `Agent` tool calls, using the `general-purpose` subagent for both.
- **merged** — when the change is small, one agent may run both axes.
- **sequential** — when the host does not support sub-agents, run both axes yourself: finish the Standards report before starting Spec.

In merged and sequential runs, each axis still gets its own section; do not merge or rerank findings. Open the report with the execution mode and the reason.

**Standards sub-agent prompt** — include:

- The full diff commands from step 1 (tracked diff and untracked-file list) and the commit list.
- The list of standards-source files you found in step 4, **plus the smell baseline from step 4** pasted in full — the sub-agent has no other access to it.
- The basis-source list from step 3, with priority levels.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Tag every standards breach or smell `conforms-but-flawed`; never use `violates-change` — judgments against the spec under review belong to the Spec axis. Under 400 words."

**Spec sub-agent prompt** — include:

- The diff commands from step 1 (tracked diff and untracked-file list) and the commit list.
- The path or fetched contents of the spec under review.
- The basis-source list from step 3, with priority levels, and the usage rules from step 3 pasted in full.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong — tag (a)–(c) `violates-change`; (d) behaviour that matches the spec but has a logic defect or risk — tag `conforms-but-flawed`; (e) places where the spec itself conflicts with a higher-priority basis source or needs a user decision — tag `change-design-flaw` and cite both sides; spec wording that is unclear or inconsistent but can be amended without changing intent — tag `conforms-but-flawed` and note 'amend change'. Quote the spec line for each finding; when citing a basis source, name it and its priority level. List the basis sources you actually consulted. Under 400 words; the consulted-sources list does not count toward the limit."

If the spec is missing, skip the Spec review and note this in the final report.

### 6. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned, keeping every finding's tag. Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, the count of each tag per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent. Tags do not create a cross-axis ranking either.

Close with **Basis sources consulted**: each source and its priority level, or `none`. This list and the execution-mode note do not count toward the per-axis word limit.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other. Finding tags are a property within an axis and do not change that separation; `violates-change` and `change-design-flaw` belong to the Spec axis because they judge against the spec under review, not how the code is written.
