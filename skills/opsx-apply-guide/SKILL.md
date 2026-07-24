---
name: opsx-apply-guide
description: Implementation discipline for the session applying an opsx (OpenSpec) change. Use when you are working through the tasks of a change package during the opsx apply flow. Covers keeping the checklist updated per section, test-first with unit tests as the bar, treating end-to-end verification as human-only, producing a developer verification list, reporting completion honestly, surfacing out-of-scope discoveries, and recording deviations. Works alongside openspec-apply-change (mechanical steps) and the test-first skill.
metadata:
  author: Cursor Grok 4.5
  version: "1.0"
  extends: openspec-apply-change, test-first
---

# opsx-apply-guide

Implementation discipline for the session that **applies** an opsx change — the one working through the tasks a commanding agent packaged and handed off. This session usually has **none of the proposing conversation's context**, so it must rely on the change documents and follow them faithfully.

Continue to use `openspec-apply-change` for the mechanical steps and the `test-first` skill for the testing workflow. This guide only adds the working discipline that those do not cover.

## When to use

- You are implementing the tasks of an opsx change package.
- Applies throughout implementation and again as you close out the change.

## 1. Keep the checklist updated per section

`tasks.md` is grouped under headings (`## 1. …`, `## 2. …`). Each such heading group is a **section**.

- You do **not** have to tick every small task the instant you finish it.
- But **when a section is complete, go back and reconcile the checklist**: tick the tasks you actually finished and confirm nothing in that section was silently skipped.
- Never leave a whole change's checklist to the very end, and never finish work without the checklist reflecting reality.

## 2. Test-first, unit tests are the bar

- Implement **test-first** (per the `test-first` skill): write the failing unit test first, then the code to pass it.
- **A passing unit-test suite is the bar for "done."** You do not need any higher tier of automated testing to consider implementation complete.
- Keep unit tests focused on real behavior and logic. Do not pad coverage with tests of trivial or framework-provided behavior.

## 3. End-to-end verification is human-only

Within the opsx apply flow, **do not drive browsers or UI automation tools (Playwright, built-in browser-operation tools, etc.) to perform end-to-end verification.** Agent-driven UI clicking is slow and its precision and edge-case coverage fall far short of a developer doing it by hand. Treat E2E as a **human-only** activity: instead of running it, write the E2E steps out for the developer (see section 4).

This restriction is scoped to opsx apply verification only. It does **not** govern the user's own separate, deliberate use of browser tools outside this flow — do not police that.

## 4. Developer verification list (dual-track — both required)

When you finish the change, produce the list of things a developer should verify. Because the real implementation can differ from what the proposal foresaw, **you (the applying session) own the final list** that the user confirms.

- If the work had tests, list what the developer should test — including any **E2E steps to run by hand** (section 3).
- If the work needs no testing, only checking, list **what should be checked** instead.
- Deliver this list on **both** tracks:
  1. **Task-tail fixed section** — append it to a fixed section at the end of `tasks.md` (e.g. `## Developer verification`).
  2. **In-conversation reminder** — also state it directly to the user in your reply, so they can confirm or adjust it on the spot.

Neither track may be skipped.

## 5. Report completion honestly

- Do **not** tick a task or a section, or claim a change is done, while its unit tests fail or any task in it is unfinished.
- If tests fail or a step was skipped, say so plainly and include the actual failing output. A tick means "verified," not "I think I did it."

## 6. Surface out-of-scope discoveries

If, while implementing, you find something the change package does not cover (a related bug, a needed refactor, a missing decision), **surface it to the user rather than silently expanding scope.** Report what you found and let the user decide; do not fold unrequested work into the change.

## 7. Record deviations

If the implementation ends up differing from what the task package described, **note the actual approach and the reason in `tasks.md`**, so the documents do not contradict what was built and a later reader understands why.
