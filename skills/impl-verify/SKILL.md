---
name: impl-verify
description: >-
  Verifies implementation against user requirement boundaries after opsx apply
  and before archive (派工執行→收尾歸檔). Checks design.md / proposal.md via code
  review and optional light playwright-cli UI peek. Use when the user runs
  /impl-verify, asks to verify a change against requirements, or wants an
  implementation check / 實作檢查 / 驗收檢查. Not a security or optimization review.
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5
  version: "1.0"
  last_updated: "2026-07-20T00:00:00"
  extends: opsx-apply-guide, playwright-cli
---

# impl-verify

Post-implementation **requirement-boundary** check. Sits between **apply** (派工執行) and **archive** (收尾歸檔).

`metadata.extends` documents relationship only. This skill runs **only** when the user explicitly invokes it (e.g. `/impl-verify`). It does **not** auto-run at the end of apply.

This is **outside** the opsx apply flow. During apply, `opsx-apply-guide` still forbids agent-driven E2E. Here, limited playwright-cli is allowed only for a light UI peek (see §4).

## Goal

Answer: **does the implementation match the user's requirement boundaries?**

- In scope: boundaries and intent from `design.md` and `proposal.md`
- Out of scope: security audits, performance/optimization, code-style taste, speculative refactors

**Human remains final acceptance.** This skill assists; it does not green-light archive.

## 1. Identify the change and evidence

1. Resolve which opsx change (user name, or sole active change; if ambiguous, ask).
2. Read that change's **`design.md`** and **`proposal.md`** — these are the authority for boundaries.
3. Detect whether there are **changed files** for this work (`git status` / `git diff`, scoped to the change when possible).
   - **No changed files** → report that there is nothing to verify; do **not** launch a check subagent; stop.
   - **Has changed files** → continue.

Do **not** treat conversation memory as the sole source of truth. Do **not** write findings into change docs (see §5).

## 2. Who is checking — isolation rules

| Invoker | How to check |
| --- | --- |
| **Separate checker session** (not the session that implemented) | Check directly in this session. |
| **Implementing session** (same agent/session that built the change) | **Must** launch a **subagent** to perform the actual check. Never self-certify. |

### Subagent constraints (when used)

- **Read-only**: must not edit, create, delete, or stage files.
- Returns a structured report (pass / fail / unclear items, evidence).
- The implementing session **must critically evaluate** the subagent's corrections and suggestions — they may be wrong. Do not apply fixes automatically.
- Whether to fix is decided by the **human** or the **implementing session** after that judgment — not by the subagent.

## 3. What to verify

From `design.md` / `proposal.md`, extract concrete boundaries (accepted behavior, explicit non-goals, named constraints). For each relevant boundary:

1. Map it to code (and UI, if applicable).
2. Mark **met** / **not met** / **cannot verify** with brief evidence (file paths, quote of the boundary).
3. Prefer honest **cannot verify** over guessing.

Logic and behavior boundaries are checked primarily by **reading code** against those docs — not by long UI scripts.

## 4. Frontend UI peek (optional)

Only when the change includes user-visible UI **and** a preview is reachable.

Follow the `playwright-cli` skill for commands. Keep the peek **minimal**.

### Allowed

- Open the app / necessary login / navigate to the **target route**
- Snapshot and/or **1–2 screenshots**
- Compare against **visible** UI boundaries from `design.md` / `proposal.md`

### Forbidden

- Multi-step form filling
- Cross-page workflows
- Permission-matrix exhaustion
- Data-writing operations

### Environment

- Assume the **dev server is already running**.
- If it is not: report **「無法做畫面檢查」** and continue with code-only checks.
- Do **not** start the server (`npm run` / similar) unless the user explicitly allows it.

## 5. Report to the user only

Deliver the result **in the conversation** (agent context). Structure:

1. **Change** checked
2. **Authority docs** used (`design.md`, `proposal.md`)
3. **Boundary results** (met / not met / cannot verify)
4. **UI peek** (skipped / done / blocked — with reason)
5. **Suggested fixes** (advisory only; flagged as unverified if from a subagent)
6. Reminder: **human final acceptance** before archive

### Do not

- Write check notes, handoff logs, or intermediate findings into the change package
- Treat change files as a scratch pad — they record **final outcomes** later in the finish/archive path, not this skill's working notes
- Claim the change is ready to archive solely because this check ran

## 6. After the report

Stop after reporting unless the user asks to fix or re-check. If the implementing session triggered via subagent, state which subagent findings you **accept** or **reject** and why (briefly).
