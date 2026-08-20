---
name: test-first
description: >-
  Test-first red→green loop in vertical slices at confirmed seams. Use when
  implementing or fixing with unit tests before production code, or when another
  skill needs test-first discipline.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Cursor Grok 4.5, Codex GPT-5
  version: "1.2"
  last_updated: "2026-08-20T14:36:57"
---

# Test-First

Unit-only **test-first**: one **seam**, one failing test (**red**), minimal code (**green**), repeat as **tracer bullets**. Refactoring is outside this loop.

## Hard rules

1. **Red before green** — Production code only after a new or updated unit test has failed for the right reason (missing behavior or failing assertion — not setup/compile noise).
2. **Vertical slices** — One seam, one test, one minimal implementation per cycle. No horizontal bulk of tests-then-code.
3. **Unit scope** — Behavior through the public seam. Integration/E2E does not replace this step.
4. **Opt-out** — Skip only when the user explicitly opts out for this task; state that you are opting out and why.

## Loop

### 1. Lock the seam

Name the public boundary under test (the **seam**). Mirror existing test layout when the project already has patterns.

**Done when:** the seam for this slice is written down (change docs, task notes, or working plan). No test at an unlocked seam.

### 2. Red — one failing test

Add one unit test that specifies the next behavior. Run it; confirm **red** for the right reason.

**Done when:** that test fails as expected.

### 3. Green — minimal production code

Write only enough production code to pass that test. Scope stays inside what the test requires.

**Done when:** that test is **green**.

Repeat 1–3 for the next **tracer bullet**. Do not park refactoring inside the loop.

## Tests worth keeping

A good test reads like a spec of observable behavior and survives refactors of internals.

**Reject:**

- **Implementation-coupled** — private methods, internal collaborators, or side channels; breaks when structure changes but behavior does not.
- **Tautological** — expected value recomputed the same way as the code; use an independent known literal or worked example.
- **Horizontal slicing** — all tests first, then all implementation.

**Mock** only at system boundaries (external I/O, time, randomness) — not your own internals.

## Done

- [ ] Each slice went **red** then **green** at a locked **seam** (or explicit opt-out).
- [ ] Delivery is vertical slices — not implementation-coupled, tautological, or horizontal bulk.
