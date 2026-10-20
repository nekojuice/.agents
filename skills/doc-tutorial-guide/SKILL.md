---
name: doc-tutorial-guide
description: Writing or revising a tutorial that a first-time operator follows step by step to finish a deployment, an environment setup, or the takeover of an existing system — mainly clicks in GUI administration tools where available, with equivalent commands as alternatives and command-only steps allowed, location and permission preconditions, a brief "why" beside key steps, and result tables after verification points. Extends doc-general-guide; this guide wins on conflict. Not for SOPs / runbooks for operators who already know the environment (doc-sop-guide), end-user manuals for an application's own screens (doc-user-guide), READMEs (doc-readme-guide), API docs (doc-openapi-guide), or inventory / audit lists (doc-general-guide §0.1). Use when creating or revising a tutorial for engineers, including one for taking over an existing system.
disable-model-invocation: false
metadata:
  author: Claude Code Opus 5.5
  version: "1.0"
  last_updated: "2026-10-20T16:00:57"
extends: doc-general-guide
---

# Tutorial Authoring Guide

A tutorial lets **someone doing it for the first time** finish a deployment, an environment setup, or the takeover of an existing system by following it from top to bottom. Assume the reader does not know the environment: every location, permission, screen, and expected result is written out.

This guide **extends doc-general-guide**. Read that guide for the shared foundations. Where the two conflict, **this guide wins**.

## 0. Scope and boundaries

| Neighbor | Boundary |
|---|---|
| SOP / runbook, `doc-sop-guide` | An SOP gives an operator who knows the environment the shortest path, with no rationale. A tutorial serves a first-time operator and allows a brief "why" per step and result tables. Choose one type per document; link between them when both exist |
| End-user operation manual, `doc-user-guide` | When the objects operated are administration tools and the server environment, and the reader is an engineer or the person taking over, it is a tutorial. Operating the application's own screens is an end-user manual |
| README, `doc-readme-guide` | The architecture overview belongs in README; link to it |
| Inventory / audit list, doc-general-guide §0.1 | Inventory data is never placed inside a tutorial. It is a separate list document; the tutorial links to it where needed |

## 1. Inherited from doc-general-guide

| Inherited rule | Meaning here |
|---|---|
| §1 shallow-to-deep understanding and verification rules | Document only the settled state; flag a defect found while writing and propose a fix |
| §2.5 tables for inventory-type information | Result tables and any service or port overview are tables |
| §2.6 one-line scope statement | Every tutorial opens with one line saying what the reader will have finished |
| §2.7 name only what the reader types or sees | Includes the labels shown on administration tool screens |
| §2.9–2.10 short section openings, minimum concept | Concepts stay next to the step that needs them |
| §2.12 each `>` note at most 2 lines | Applies to the preconditions callout in §4; overflow is handled in Overrides |
| §2.13 no invented terms; §2.14 single language | Unchanged |
| §2.15 an example value appears once | After "the following uses `<X>` as the example", later steps say "replace with the actual location / value" |
| §2.16 placeholders for identifying information; secrets never written | Unchanged |
| §2.17 stay within the team's responsibility | A step owned by another team is one line: "ask `<owning role>` to handle it" |
| §2.18 consistent with settled decisions | No contradicting approach, not even as an alternative or a counterexample |
| §3 name-first headings | Unchanged |
| §4 parentheses discipline | Applies and is stricter here: conditions never trail a step or a result in parentheses, see §5 |
| §2.1 every command in a code block; doc-general-guide §5 code-block comment format | Apply to alternative commands and command-only steps |

### Overrides

| doc-general-guide rule | Here |
|---|---|
| §2.2 numbered steps, each with its own code block | The step unit is a UI action. An equivalent command is an alternative, in a code block right after that step; §5 |
| §2.11 no design rationale by default | A key setting may carry one or two sentences of "why" right next to its step; §6 |
| §2.12 an overlong `>` note is split into steps or moved to README | The preconditions callout may be followed by a short preconditions table; preconditions are never moved to README, §4 |
| §7 completion checklist | Replaced by §8 |

## 2. Understanding and verification

Gather material in the order of doc-general-guide §1. Verify screen labels, menu paths, status codes, and error messages against the real administration tool screens and the real configuration and source — never invent them.

## 3. Document structure

The document opens with a one-line scope statement. Each operation section keeps this element order:

| Order | Element | Required |
|---|---|---|
| 1 | Name-first section heading | yes |
| 2 | Preconditions callout, §4 | when the section places files, directories, settings, or services, or depends on a condition |
| 3 | Steps, each with its brief "why" when it has one, §5–§6 | yes |
| 4 | Result table after each verification point, §7 | at every verification point |

## 4. Location and permission preconditions

When a section places files, directories, settings, or services, state before its steps where each one goes, which identity needs to read it, and which identity needs to write it. Conditions that limit the section — environment, required state, feature availability — go here too.

Open the section with a callout using the fixed label 操作條件, the same condition-callout label doc-user-guide uses, rendered in the document's language. In a Chinese document:

```
> ⚠ 操作條件：<host> 上有 <path>；<service account> 讀取；<admin account> 寫入。
```

When the items do not fit in the 2-line callout, follow it with a short table with the columns item, location, reader, and writer. Preconditions stay in the tutorial; they are never moved to README.

## 5. Steps

- **UI first, commands as alternatives.** Each step is a click or entry in a GUI administration tool. When an equivalent command exists, put it in a code block right after that step, following doc-general-guide command rules.
- **Command-only steps.** When no GUI can do the step, the command itself is the step, in a code block, following doc-general-guide command rules. The document does not become an SOP because of it.
- **One action per step**, naming each UI element by its exact on-screen label.
- **UI paths**, the same notation as doc-user-guide. Join path nodes with `→`. The starting point, the tool or application name, takes no quotation marks. In a Chinese document, menu nodes after the start use 『』 and button names use 「」:

  ```
  <tool> →『<menu>』→『<submenu>』，按「<button>」
  ```

  A document in another language uses that language's customary quotation marks in the same two roles.
- **No conditions in trailing parentheses.** Never append an environment limit, a required state, feature maturity, or any other condition in parentheses after a step or a result. Move it into the §4 preconditions callout, or write it as its own sentence before the step:

  | Instead of | Write |
  |---|---|
  | `<step> (only when <condition>)` | `When <condition>:` as a lead-in sentence, then `<step>` |
  | `<result> (<state> only)` | A separate sentence: `This result appears only when <state>.` |

## 6. Brief "why"

- A key setting carries one or two sentences of reason, placed right after its step.
- No architecture overview, which belongs in README, and no experimental conclusions.
- Steps that are not key carry no reason.

## 7. Result tables

Every verification point is followed by a result table. It is a standard element of this type, not an optional block at the end.

| What you see | What it means | What to do |
|---|---|---|
| `<status code, error message, or screen state>` | `<meaning>` | `<action>` |

- Render the column headings in the document's language.
- Take every status code, message, and screen state from a real source: the actual screen, logs, or source code.

## 8. Completion checklist

- [ ] The reader is a first-time operator or the person taking over; the document is not an SOP, an end-user manual, or a README, and holds no inventory data, only links to the list.
- [ ] Every section that places files, directories, settings, or services opens with a preconditions callout under the fixed label 操作條件, rendered in the document's language, naming location, reader, and writer, followed by a short table when needed; no preconditions moved to README.
- [ ] Steps are UI actions where a GUI exists; equivalent commands are alternatives in a code block after the step; command-only steps follow doc-general-guide command rules.
- [ ] UI paths follow §5: unquoted start, menu nodes in 『』, button names in 「」; a document in another language uses its customary quotation marks in the same two roles.
- [ ] One action per step; UI elements named by their on-screen labels.
- [ ] No condition trails a step or a result in parentheses.
- [ ] "Why" appears only on key settings, one or two sentences, right next to the step.
- [ ] Every verification point has a result table; codes and messages come from real sources.
- [ ] Inherited rules hold: scope line, example value once, placeholders and no secrets, only in-scope operations, nothing contradicting settled decisions, name-first headings, `>` notes ≤2 lines.
- [ ] Every path, label, menu, and command was verified against real sources; defects found were flagged.
