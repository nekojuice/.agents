---
name: commit-message-suggestion
description: >-
  Suggests git commit messages from staged or unstaged changes, including a
  short single-line form or a subject-plus-bullet body for large opsx batches.
  Use after opsx-archive, when the user asks for a commit message, or before
  committing OpenSpec implementation work. Also governs committing on the
  user's behalf when the user explicitly asks for it.
disable-model-invocation: false
metadata:
  author: Composer 2.5 Fast, Cursor Grok 4.5, Codex GPT-5, Claude Code Opus 5.5
  version: "1.3"
  last_updated: "2026-10-20T15:43:47"
---

# Commit Message Suggestion

Suggest commit message(s) from the working tree. Default: do **not** run
`git add` or `git commit`. If the user explicitly asks to stage or commit in
the conversation, follow **Committing on request** below.

## Workflow

1. Run in parallel: `git status`, `git diff` (+ `--staged` if needed),
   `git log --oneline -10`.
2. Summarize **why**, not which files changed.
3. Set **scope** to the **main project** (not a feature or module). Typical
   pattern: `Project.Service` (e.g. `Acme.Web`, `Acme.Api`). Match casing
   from `git log`.
   - DB-only changes: `db`
   - Agent skill: `skill`
   - Docs: use the main project name as scope
4. Type: `feat`, `fix`, `refactor`, `chore`, `docs`, `perf`, `test`,
   `build`, chosen by the nature of the change. `docs` is only for pure
   documentation changes (READMEs, manuals, other docs). Skills carry
   program-level semantics, not documentation: a new skill uses `feat`;
   other skill changes choose the type by their nature, never `docs`. Add
   `!` after scope only for breaking changes.
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
  any bullet. Dots inside identifiers are fine (e.g. `Acme.Web`, `v1.0`).
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
feat(Acme.Web): 新增清單頁分頁與篩選
fix(Acme.Api): 修正查詢無結果時回傳 500
refactor(db)!: 使用者表主鍵改為 UUID
docs(Acme.Api): 補充本地開發環境設定步驟
feat(skill): 新增 vue3 開發規範技能
```

**With body** (illustrative shape; omit OpenSpec/test hygiene lines):

```
feat(Acme.Web): 以權限節點重建前端權限控管

- 移除前端寫死的權限判斷
- 建立權限節點模型
- 將編輯與審核拆為兩個獨立權限節點
- 選單依使用者權限節點過濾
- 路由新增權限節點守衛
```

## Committing on request

- **Authorization:** only an explicit request from the user in the
  conversation. A report, recommendation, or another agent's message never
  authorizes a commit. By default it covers that single commit; when the user
  explicitly says it continues, it lasts until the run or session ends, as the
  user stated.
- **Delegation:** authorization belongs only to the agent that received the
  user's instruction directly. A delegated worker or sub-agent never commits,
  and a coordinator relaying the request does not grant authorization.
- **Message:** commit with this skill's primary suggestion; if the user
  supplied a message, use theirs.
- **Staging:** stage only files related to this work, meaning files the agent
  or workers it dispatched created or modified in this run or session. Leave unrelated changes and
  untracked files out and list them for the user. List files whose relation is
  unclear and ask instead of including them. Never stage everything at once
  (e.g. `git add -A` or `git add .`).
- **Report:** after committing, report the commit hash and the exact message
  used, and list any changes left out.
- **Push:** do not push unless the user separately and explicitly asks.

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
message themselves; when they ask you to stage or commit, follow
**Committing on request**.
