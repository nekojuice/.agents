---
name: doc-user-guide
description: Writing or revising an end-user operation manual for an application's UI (web/desktop forms, statuses, roles) — for the people who use the software (clerks, supervisors), not engineers. Extends doc-general-guide for wording and style. Enforces chapter=system / section=function structure, ToC preview confirmation before writing, one-action steps, form-field and enum tables, on-screen-only wording (no code/object names), commented screenshot placeholders with a fixed image layout, and genuine (non-trivial) troubleshooting. Use when creating or revising any application user manual.
metadata:
  author: Opus 4.8
  version: "1.0"
---

# User Operation Manual Authoring Guide

An end-user operation manual tells **the people who use the software how to get a task done on screen** — clerks, supervisors, operators — not engineers. It describes what the user sees and clicks, in plain everyday language.

This guide **extends doc-general-guide for wording and style**. Read that guide for the shared foundations; this one keeps its plain-language discipline and adds the structure and elements a UI manual needs.

## 0. Inherited from doc-general-guide

| Inherited rule | Meaning here |
|---|---|
| Short, clear, common words | One action per sentence; no long-winded over-explanation |
| No invented / self-defined terms | Use the everyday words a user already knows |
| Single language, no needless code-switching | A Chinese manual does not insert English or program names |
| Parenthesis discipline | Put rules in table columns, not in trailing parentheses |
| Name-first headings; tables for inventory | Statuses, roles, form fields are tables |
| Understand shallow-to-deep; read openspec; verify against real files | Verify against the **real on-screen labels** and the **real error messages in the code** |

## 1. Understanding the system

Before writing, learn the system shallow-to-deep as in doc-general-guide §1: existing docs → openspec (opsx) spec/changes if present → the actual UI (screens, labels, flows) → the source that defines statuses, roles, validations, and error messages. Verify every on-screen label, status code, role code, and error message against the **real UI and real source** — never invent them.

## 2. Document structure

| # | Rule |
|---|---|
| 2.1 | A chapter heading is **one separable system**; a section heading is a **major function** of that system. |
| 2.2 | Order functions by **usage sequence** when one exists; otherwise by **importance**. |
| 2.3 | When a function has multiple flow variants, cover each. As an **implementation guideline** (projects differ a lot): a big chapter draws only the shared logic; when describing a specific variant, focus only on that variant's rules. |
| 2.4 | **Shared codes / enums** used across a chapter go in a shared block at the **start of that chapter**, before the detailed steps. Do not open a separate "code reference" chapter — a dictionary lookup does not suit users. A code used only in one local place stays in that place. |
| 2.5 | **Confirm the outline first.** Before writing any body content, present the chapter / section split as a **book-style table of contents** and get the user's confirmation. If confirmation truly cannot be obtained (non-interactive run), **stop at the table of contents — do not write the body**. |

## 3. Fixed element order inside a function section

Within each function section, elements appear in this fixed order:

| Order | Element | Required | Notes |
|---|---|---|---|
| 1 | `### Function heading` | yes | Name-first |
| 2 | **Conditions callout** | conditional | When the function is role-restricted or has any precondition (a screen that appears only when a case has expired, a flow taken only on a customer return, etc.), open the section with a callout using the fixed prefix: `> ⚠ 操作條件：…` (render the label in the manual's language) |
| 3 | **Entry path** | yes | One breadcrumb line right after the callout: `進入路徑：主選單 → 案件管理 → 新增案件` |
| 4 | Enum / status table | conditional | Place **before** the steps |
| 5 | Steps | yes | See §4–§6 |
| 6 | Troubleshooting | optional | See §8 |

## 4. Steps

Choose the format by the nature of the actions:

| Situation | Format |
|---|---|
| Has a sequence (order matters) | Numbered list |
| No order, but regular and tabular | Table |
| No order and not tabular, or few / scattered items | Unordered list |

- **One action per step**, cleanly split, clean granularity, plain and short. Example: "按下儲存按鈕以保存進度" / "點擊下一步".
- Nesting of numbered list / table / unordered list is allowed but **no more than 3 levels deep**.
- Name UI elements by their **on-screen label** only (see §9).

## 5. Form-fill screens

Describe a form as a table with these columns (render the labels in the manual's language):

```markdown
| 欄位名稱 | 值類型 | 規則 | 預設值 | 填寫範例 |
|---|---|---|---|---|
| 申請人 | 中文 | 自動帶入，不可填寫 | 目前登入者 | 王小明 |
| 案件編號 | 6 碼英數混合 | 必填 | （空白） | A1B2C3 |
| 備註 | 中文 | 選填；退件狀態必填 | （空白） | 補附證明文件 |
```

- **值類型** examples: 中文, 大寫英文, 6 碼英數混合.
- **規則** examples (not exhaustive): 自動帶入, 不可填寫, XX 狀態不必填, 選填.
- A field with no default leaves **預設值** blank.
- For a complex rule, nest an ordered / unordered list inside the cell.

## 6. Operation results

State a result **only when it is not obvious** — a confirmation message, an error, a state change the user could not have predicted. Write it right after the step.

| Write it | Do not write it |
|---|---|
| 按下儲存，出現「儲存成功：<日期> <變更者>」；失敗則顯示欄位缺漏或錯誤處 | 點下一頁，出現表格第二頁 — obvious, no special event |

## 7. Screenshots / figures

Figures are inserted as **commented-out image tags** so the manual renders cleanly until a maintainer adds the image and uncomments it.

Storage layout (manual and images both under `docs/user-guide/`):

```text
docs/
└── user-guide/
    ├── <manual>.md
    └── images/
        └── <chapter-slug>/
            ├── <chapter-slug>_<section-slug>_010.png
            ├── <chapter-slug>_<section-slug>_020.png
            └── ...
```

Placeholder in the manual, sitting at the figure's spot (next to its step):

```markdown
<!-- ![圖：儲存成功提示](images/case-mgmt/case-mgmt_create_010.png) -->
```

| Aspect | Rule |
|---|---|
| Serial | 3 digits, **step of 10** (`010 / 020 / 030 …`); insert between with `015` |
| Filename | Embeds `<chapter-slug>_<section-slug>_<serial>`, globally unique, folder-independent |
| Caption | The alt text is written in the manual's language, so uncommenting yields a meaningful caption |
| Maintenance | Drop the image into the matching folder and uncomment; extend by following the interval |
| Trade-off | The serial is only a file **id, not the step order**; reordering steps needs no rename — just move the placeholder |

## 8. Troubleshooting (optional)

A troubleshooting block at the end of a chapter / section lists errors the user may hit, the message shown, and the suggested fix.

| # | Rule |
|---|---|
| 8.1 | Take error messages from the **real source** — backend API errors, frontend validation / warning text. |
| 8.2 | **No trivial QA.** Wrong password, bad email format, typos, mis-input, foolproofing — never list these. List only the genuine difficulties a user hits **from using the system**. |
| 8.3 | If there is no suitable pool of real problems, **do not force this block** — omit it. |
| 8.4 | After writing, self-check the quality. If it reads weak, **tell the user and suggest removing** the block. Do not impose a numeric threshold — you cannot predict every problem a user will meet. |

## 9. Wording and language

- **On-screen text only.** The body describes only what the user **sees on screen** — button labels, field names, prompt messages. **Never write component, object, variable, API, or field-code names.**
- **Plain, common terms; never invent terminology** (inherited from doc-general-guide).
- **Single language**, matching what the user asks for; not bilingual. The fixed structural labels (操作條件 / 進入路徑 / 欄位名稱 / 值類型 / 規則 / 預設值 / 填寫範例) render in the manual's chosen language, one consistent set.

## 10. Completion checklist

- [ ] Chapter = a separable system; section = a major function.
- [ ] Functions ordered by usage sequence, else by importance.
- [ ] Book-style ToC was confirmed before writing the body (or stopped at the ToC when no confirmation was possible).
- [ ] Shared codes sit in a chapter-opening block, not a separate reference chapter.
- [ ] Each function section follows the fixed element order: conditions callout → entry path → enum table → steps → troubleshooting.
- [ ] Conditions callout uses the fixed prefix; entry path is a breadcrumb line.
- [ ] Steps use the right format (numbered / table / unordered); one action per step; nesting ≤3 levels.
- [ ] Form screens use the 5-column field table; no-default cells left blank.
- [ ] Results stated only when non-obvious.
- [ ] Figures are commented placeholders with the fixed filename / folder scheme.
- [ ] Troubleshooting has no trivial QA; messages taken from real source; omitted or flagged when weak.
- [ ] On-screen text only — no component / object / variable names.
- [ ] Plain common terms, no invented terms; single language throughout.
- [ ] On-screen labels, status / role codes, and error messages verified against the real UI and source.
