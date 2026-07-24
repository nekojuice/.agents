---
name: opsx-propose-guide
description: Authoring discipline for the commanding agent who runs the opsx (OpenSpec) propose flow and packages change tasks for delegation. Use when you are the decision-making hub that, after aligning with the user, produces opsx change task packages to hand off to other models or sessions. Covers change scoping to one cohesive unit of work, series naming with numbering, dependency ordering, cold-start self-containment, disclosing agent-made assumptions allocated per change in a series, laying down a verification skeleton, and a pre-handoff checklist. Works alongside openspec-propose, which handles the mechanical CLI steps.
metadata:
  author: Cursor Grok 4.5
  version: "1.1"
  extends: openspec-propose
---

# opsx-propose-guide

Authoring discipline for the **commanding agent** — the hub that discusses and finalizes decisions with the user, then, when the work should go through the opsx flow, produces the change task packages. Those packages are usually delegated to **other models or sessions** for implementation, enabling parallel collaboration.

Continue to use `openspec-propose` for the mechanical steps (running the CLI, generating `proposal.md` / `design.md` / `tasks.md`). This guide only constrains *how you scope, name, order, and disclose* so that a downstream implementer with **none of this conversation's context** can execute correctly.

## When to use

- You have finished aligning with the user and decided the work will go through opsx.
- You are about to create one or more change task packages that another session will implement.

Apply this guide alongside `openspec-propose`, throughout package creation and again before you hand off.

## 1. Change scoping — one cohesive unit of work

Scope each change as **one cohesive, self-contained unit of work** — sized so it can be reviewed and reverted as a whole. Tasks are the small implementation steps inside the change; the change is the deliverable.

The scoping question is always: **does this change, as a whole, form one coherent unit of work?**

- **Split** when a change mixes unrelated concerns, spans layers that would review better separately, or is too large to reason about as a single unit.
- **Merge / keep together** when a piece is too small to stand alone, or is meaningless without its sibling work.

**Do not write anything about committing into the change documents, and do not perform commits as part of producing the package.** Whether and when to commit is entirely the user's decision and lies outside the scope of the task package. The "unit of work" framing above is only a sizing guide for you — it must never appear in the change as an instruction or action.

## 2. Naming & numbering

Format for ordered or same-series changes:

```
<series>-<NN>-<subtitle>
```

- `series` — the series code: the backbone name shared by the changes that make up one feature line (e.g. `user-api`).
- `NN` — a **two-digit** sequence number (`01`, `02`, …). Two digits keeps ordering stable past nine changes.
- `subtitle` — the specific work of this change (e.g. `fix-auth-bugs`).

Example: `user-api-01-fix-auth-bugs`.

Rules:

- **Number** a change when it belongs to a series or has an ordering relative to siblings.
- **Do not number** a standalone change with no follow-ups — use a plain kebab-case name (e.g. `add-user-auth`).

## 3. Dependency & ordering

Order and dependencies are expressed **in text, inside the change documents** — the implementer must not need to infer them.

- **Within a change:** when tasks form a chained sequence, state the required order explicitly in `tasks.md` (which step must precede which, and why).
- **Across changes:** describe cross-change dependencies in prose at a fixed spot in `proposal.md` (e.g. a `Depends on:` line naming the prerequisite change and stating it must be merged first). Cross-change dependencies are captured as text, not as tooling metadata.

## 4. Assumption disclosure (dual-track — both required)

Boundary conditions and assumptions are decided by **you (the agent) in the moment**, and may be **overridden or changed by the user in the moment**. They are fluid, not final. Every assumption you settled on the user's behalf must be disclosed on **both** of these tracks:

1. **In-document, fixed section** — record the assumptions you decided in a fixed section of `proposal.md` (e.g. `## Assumptions & Decisions Made`), so a cold-start implementer sees them. Frame them as decisions that may still be changed.
2. **In-conversation report** — after building the package, list to the user, as bullet points, exactly which boundary conditions you finalized on their behalf, so they can override any of them on the spot.

Neither track may be skipped. The document keeps the implementer aligned; the conversation report gives the user the chance to change course.

### Per-change allocation (series)

A pre-propose discussion worksheet is **input for allocation**, not content to paste. When packaging one or more changes:

- **Settled only** — write only decisions already closed. Do not put open / TBD / "needs resolution" rows into Assumptions as implementer instructions.
- **This change only** — each package's Assumptions (and its conversation report) include only rows that **this change implements**. Do not paste the full worksheet into any one change.
- **One owner** — map each settled row to the change that owns the work (same series numbering as section 2). Prefer a single owning change; if a later change needs the same decision, **reference** the earlier change instead of duplicating the full text.
- **Deferred** — if a settled-or-open row belongs to a future sibling, name that change (e.g. "deferred to `alert-03`") and omit the detail from this package until that change is proposed.

## 5. Verification skeleton

Lay down, in `tasks.md`, a skeleton of how the change should be verified so the implementer knows what "done" looks like:

- For work that warrants tests, state the **unit-test intent** (test-first): what behavior should be covered.
- For work that only needs checking rather than testing, state **what should be checked**.
- Mark any end-to-end / browser-driven verification as **human-only** — it is for a developer to run by hand, never something the implementing session drives itself.

This is only a skeleton. The final, concrete verification list is produced by the implementing session (it may differ from what was foreseen here) and confirmed with the user then. Do not turn the skeleton into a rigid script.

## 6. Pre-handoff checklist

Because the package will be implemented by a session with **no access to this conversation**, verify each package is self-contained before handoff:

- **Scope** — the change is one coherent unit of work; not too large, not trivially small; and the documents contain no commit instructions or actions.
- **Naming** — series/numbering follows section 2; standalone changes are unnumbered.
- **Ordering** — intra-change task order and cross-change dependencies are stated in text (section 3).
- **Assumptions** — every agent-made boundary for **this** change is in the fixed document section *and* reported to the user (section 4); no full-worksheet paste; no unsettled TBD as instructions; cross-change reuse is by reference.
- **Self-containment** — an implementer with no prior context can act on the package without asking what was meant.
- **Acceptance** — success criteria are concrete enough that the implementer can tell when the change is done.
- **Verification skeleton** — `tasks.md` states unit-test intent or check items, with any E2E marked human-only (section 5).

Do not provide a fill-in-the-blank handoff template. A template invites the downstream session to "copy the homework" and lose focus on the actual task. State what the package must contain; let each package be written to fit its own work.
