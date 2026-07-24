---
name: commit-message-suggestion
description: >-
  Suggests git commit messages from staged or unstaged changes, including a
  short single-line form or a subject-plus-bullet body for large opsx batches.
  Use after opsx:archive, when the user asks for a commit message, or before
  committing OpenSpec implementation work.
metadata:
  author: Composer 2.5 Fast, Cursor Grok 4.5
  version: "1.1"
  last_updated: "2026-07-16T15:51:00"
---

# Commit Message Suggestion

Suggest commit message(s) from the working tree. Default: do **not** run
`git add` or `git commit`. If the user verbally asks to stage or commit in the
conversation, follow that request — spoken instruction overrides this skill.

## Workflow

1. Run in parallel: `git status`, `git diff` (+ `--staged` if needed),
   `git log --oneline -10`.
2. Summarize **why**, not which files changed.
3. Set **scope** to the **main project** (not a feature or module). Typical
   pattern: `Project.Service` (e.g. `UBOL.WEB`, `IFRS16.API`). Match casing
   from `git log`.
   - DB-only changes: `db`
   - New or updated agent skill: `skill` with type `feat`
   - Docs: use the main project name as scope
4. Type: `feat`, `fix`, `refactor`, `chore`, `docs`, `perf`, `test`,
   `build`. Add `!` after scope only for breaking changes.
5. Choose output mode (see **Length mode**).
6. Output **one** primary suggestion; at most **two** alternates only when
   intent clearly diverges (e.g. different type or scope).

## Length mode

| Mode | When | Shape |
|------|------|--------|
| Short | Agent judges the change is a single intent, **or** user asks for 簡短 / short | Subject line only |
| With body | Agent judges the change is a large batch (e.g. opsx series kept as one commit for task integrity), **or** user asks for 包含補充大項 / with body bullets | Subject + `-` bullets |

User wording for mode overrides the agent's judgment.

## Format

**Short:**

```
<type>(<scope>): <one-line summary, Chinese preferred>
```

**With body:**

```
<type>(<scope>): <one-line summary, Chinese preferred>

- <one change item>
- <one change item>
```

- Subject: verb-led Chinese (新增、修正、重構、調整、移除…); keep English
  identifiers as-is.
- Parentheses `()` / `（）` are allowed **only** in the Conventional Commits
  `type(scope):` prefix. Forbidden in the subject narrative and in every body
  bullet.
- No sentence-final period: neither `.` nor `。` at the end of the subject or
  any bullet. Dots inside identifiers are fine (e.g. `IFRS16.web`, `v1.0`).
- Each body bullet is **exactly one** sentence-worth of content, then a new
  line. If one line cannot state the change clearly, split or rewrite the
  bullet — do not pack multiple ideas or trail with a period.

## Body content rules

Write **change items** only — what behavior, model, or product surface changed.

**Do not** include:

- OpenSpec process notes (adding/removing capabilities, archiving changes,
  syncing specs, etc.)
- Unit-test process notes (tests added, suite count, all tests passed, etc.)

Those are expected hygiene, not commit change items.

## Examples

**Short:**

```
feat(UBOL.WEB): 新增訂單列表分頁與篩選
fix(IFRS16.API): 修正合約查詢空結果時回傳 500
refactor(db)!: 使用者表主鍵改為 UUID
docs(IFRS16.API): 補充本地開發環境設定步驟
feat(skill): 新增 vue3 開發規範技能
```

**With body** (illustrative shape; omit OpenSpec/test hygiene lines):

```
feat(IFRS16.web): 以節點模型重建前端權限框架

- 清除前端寫死的權限，移除舊 usePermission、v-can、ROLE_PERMISSIONS 與散落各處的 canEdit 閘，UI 先回到無條件顯示
- 建立權限節點模型，節點代號對齊舊系統 S_Authority 的 FormId，並將合約編輯 CM1000 與合約審核 CM5000 拆為兩個獨立節點
- 重建判權限框架，auth store 依帳本角色水合權限表、重寫 usePermission 與 v-can 指令、選單依節點過濾、路由新增節點守衛
```

## Output

```
Suggested commit message:

<message>
```

If offering alternates (at most two):

```
Suggested commit message:

<message>

Alternate:

<message>
```

Do not append a fixed disclaimer. Let the user inspect, copy, or edit the
message themselves unless they ask you to stage or commit.
