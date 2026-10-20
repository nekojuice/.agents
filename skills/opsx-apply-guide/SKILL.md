---
name: opsx-apply-guide
description: Implementation discipline for the session applying an opsx (OpenSpec) change. Use when you are working through the tasks of a change package during the opsx apply flow. Covers ticking the checklist as each task is done and reconciling it per section, test-first with unit tests as the bar, test-change discipline (anti-cheat) including amendment rounds, treating end-to-end verification as human-only, producing a developer verification list, reporting completion honestly, surfacing out-of-scope discoveries, and recording deviations. Works alongside openspec-apply-change (mechanical steps) and the test-first skill.
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5, Codex GPT-5, Claude Code Opus 5.5
  version: "1.2"
  last_updated: "2026-10-20T15:52:52"
extends: openspec-apply-change, test-first
---

# opsx-apply-guide

Implementation discipline for the session that **applies** an opsx change — the one working through the tasks a commanding agent packaged and handed off. This session usually has **none of the proposing conversation's context**, so it must rely on the change documents and follow them faithfully.

Continue to use `openspec-apply-change` for the mechanical steps and the `test-first` skill for the testing workflow. This guide only adds the working discipline that those do not cover.

## When to use

- You are implementing the tasks of an opsx change package.
- Applies throughout implementation and again as you close out the change.

## 1. Keep the checklist current

`tasks.md` is grouped under headings (`## 1. …`, `## 2. …`). Each such heading group is a **section**.

- **Tick each task as soon as it is done** — change `- [ ]` to `- [x]` when you finish it, matching `openspec-apply-change`.
- **When a section is complete, go back and reconcile the checklist**: confirm every tick reflects finished work and nothing in that section was silently skipped.
- Never leave a whole change's checklist to the very end, and never finish work without the checklist reflecting reality.

## 2. Test-first, unit tests are the bar

- Implement **test-first** (per the `test-first` skill): write the failing unit test first, then the code to pass it.
- **A passing unit-test suite is the bar for "done."** You do not need any higher tier of automated testing to consider implementation complete.
- Keep unit tests focused on real behavior and logic. Do not pad coverage with tests of trivial or framework-provided behavior.

## Test changes (anti-cheat)

Applies to **every** apply session — standalone or delegated, including when you are repairing a failed hard check (build, test, lint).

Fix the **implementation**. You may add tests under `test-first` that express behavior the change requires. You must **not** make a check green by weakening, deleting, or rewriting assertions or tests.

- **Forbidden**: deleting or loosening a failing test to clear a gate; commenting out assertions; broadening matchers until any result passes.
- **Allowed exception**: remove or rewrite a test **only when the change package explicitly requires it** (e.g. `tasks.md` / `design.md` states that obsolete tests must go because the behavior changed). In an amendment round, the boundary is the superseded behavior (see Amendment rounds).
- If changing a test is tempting but the package does **not** require it, **stop and report** — to the delegator when delegated (in factory mode, `needs_input` / stop-for-human), otherwise to the user. Do not treat it as an ordinary fix.

## Amendment rounds

An amendment round revises a change after apply and before archive. When to amend an existing change versus open a new one, and which human gates apply, are defined in `orchestrator-factory` `### Amendment rounds`; how an amendment is annotated in the change documents is in `opsx-propose-guide` (Amendments). This section covers only the implementing side.

- **Tick and reconcile** the appended tasks per section 1. Keep the amendment annotation intact.
- **Superseded behavior is the boundary.** Only tests that directly assert the behavior the amendment names as superseded may be rewritten or deleted. Every other test stays under Test changes (anti-cheat). If tests would need to change but the amendment names no superseded behavior, stop and report.
- **Rewritten tests stay test-first** (section 2): the rewritten test must first fail for the right reason, then change the code.
- **Record the mapping in `tasks.md`**: each rewritten or deleted test, the old behavior it covered, and the amendment item it belongs to.
- **Large-scale amendments**: an amendment is large-scale when it replaces most of a feature's behavior, or when the old tests can no longer map one-to-one onto the new behavior. When the amendment is marked large-scale — by the orchestrator in factory mode, otherwise by the commanding agent that wrote it — list every rewritten or deleted test with its old behavior one by one, so the reviewer (in factory mode, the Check worker) can verify each. If it is unmarked but meets that criterion, list them the same way; over-record rather than under-record.
- This mapping is separate from deviations (section 7).

## 3. End-to-end verification is human-only

Within the opsx apply flow, **do not drive browsers or UI automation tools (Playwright, built-in browser-operation tools, etc.) to perform end-to-end verification.** Agent-driven UI clicking is slow and its precision and edge-case coverage fall far short of a developer doing it by hand. Treat E2E as a **human-only** activity: instead of running it, write the E2E steps out for the developer (see section 4).

This restriction is scoped to opsx apply verification only. It does **not** govern the user's own separate, deliberate use of browser tools outside this flow — do not police that.

## 4. Developer verification list (dual-track — both required)

When you finish the change, produce the list of things a developer should verify. Because the real implementation can differ from what the proposal foresaw, **you (the applying session) own the final list** that the user confirms.

- If the work had tests, list what the developer should test — including any **E2E steps to run by hand** (section 3).
- If the work needs no testing, only checking, list **what should be checked** instead.

**Abstraction level** — this is the canonical rule; `opsx-propose-guide` and coordinating workflows reference it:

- Each item is a **feature or business flow**: e.g. "on a given screen, confirm a given feature works" or "run one complete business flow and confirm nothing is off."
- **Group screen checks by screen**: everything to look at on one screen sits in one item or one place.
- Do not list individual controls, message text, or internal implementation.
- List only items that **need human judgment**. Leave out what unit tests or hard checks already cover, and simple logic checks (`need-ask-user-guide`, `## Present pending decisions at checkpoints`).
- Placeholder contrast — it shows the level only, not a template:
  - Too fine: "Click `<control>`; message `<text>` appears."
  - Right level: "On `<screen>`, complete one `<flow>` and confirm the result."
- **Safety boundary** — the same as in `opsx-propose-guide` section 5: no step may run a command that prints secret values; to check that a secret exists, list only the file name. No step may call a paid external service. If verification genuinely needs a real paid service, mark it human-only and note the cost and side effects.

Deliver this list on **both** tracks:

1. **Task-tail fixed section** — append it to a fixed section at the end of `tasks.md` (e.g. `## Developer verification`).
2. **In-conversation reminder** — also state it directly to the user in your reply, so they can confirm or adjust it on the spot. When a coordinator delegated this work, put the list in your returned result instead; the delegator presents it to the user.

Neither track may be skipped. Each change keeps its own list. Consolidating lists across changes or runs belongs to the coordinating workflow, not this skill.

## 5. Report completion honestly

- Do **not** tick a task or a section, or claim a change is done, while its unit tests fail or any task in it is unfinished.
- If tests fail or a step was skipped, say so plainly and include the actual failing output. A tick means "verified," not "I think I did it."

## 6. Surface out-of-scope discoveries

If, while implementing, you find something the change package does not cover (a related bug, a needed refactor, a missing decision), **surface it to the user rather than silently expanding scope.** Report what you found and let the user decide; do not fold unrequested work into the change.

This includes documentation: update no documentation outside the change's tasks. README and other document sync follow the coordinating workflow's documentation-sync rule, such as `orchestrator-factory` hard rule 14: README by default; other documents only after the user confirms a listed set.

## 7. Record deviations

If the implementation ends up differing from what the task package described, **note the actual approach and the reason in `tasks.md`**, so the documents do not contradict what was built and a later reader understands why.

Test mappings from an amendment round are not deviations; they live in the amendment-round record (see Amendment rounds) and are not repeated here.
