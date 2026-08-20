---
name: change-log
description: Generates a user-facing change log in Traditional Chinese from recent work. Use after finishing an opsx change, when the user asks for a change log / release notes / update summary, or wants to summarize what changed for end users.
disable-model-invocation: false
metadata:
  author: Opus 4.8, Codex GPT-5
  version: "1.1"
  last_updated: "2026-08-20T14:36:57"
---

# Change Log

Produce a concise, plain-language change log in **Traditional Chinese (繁體中文)**, grouped by audience-relevant sections. The reader is usually **non-technical**, so describe changes in friendly, everyday language — not implementation detail.

The change log output is **always Traditional Chinese**, regardless of this skill's language.

## Step 1 — Ask for the audience (required, do this first)

Before writing anything, ask the user which audience the change log targets, using the question tool:

- **一般向** (default): for general users. Use plain, approachable wording and **filter out non-user-facing changes** (pure refactors, tests, dependency bumps, internal type changes, build/CI tweaks).
- **工程向**: for the engineering team. Technical changes may be kept and technical vocabulary is allowed.

## Step 2 — Determine what changed (source priority)

Pick the source in this order; do not ask if one clearly applies:

1. **Just finished an opsx change** → derive the changes from the opsx flow and the implementation context of this session.
2. **User specified content or a range** → use what they described in the conversation context.
3. **Otherwise** → fall back to the git working tree (`git status`, `git diff`).

## Step 3 — Classify into sections

- Choose the single most fitting classification dimension for this batch — by **feature area**, by **page/screen**, or similar. Judge from the changes themselves; do not ask.
- Each section is an `###` heading.
- Each change is a `-` bullet. Keep every bullet short.
- For **一般向**, drop anything the user cannot perceive. For **工程向**, keep technical items.

## Step 4 — Output

**Absolute simplicity. No preamble, no intro sentence, no closing remarks.**

- Start with a top-level `#` heading that is the date, e.g. `# 2026/07/07 change log`. Use the current date (or a version/date the user provided).
- Immediately after the title, go straight into `###` section headings and their bullets. Nothing between them.
- Default: print the change log **directly in the chat**.
- Only when the user asks for a file: write to `CHANGELOG-<date>.md` (e.g. `CHANGELOG-2026-07-07.md`) in the working directory, creating a new file.

## Format

```markdown
# 2026/07/07 change log

### <區塊標題（依功能或頁面分類）>

- <平易近人、簡潔的更動描述>
- <平易近人、簡潔的更動描述>

### <另一個區塊標題>

- <更動描述>
```

## Example (一般向)

```markdown
# 2026/07/07 change log

### 資產合約清單

- 新增依租約日期篩選，日期範圍有交集的合約都會顯示
- 篩選條件可用標籤快速移除

### 合約明細頁

- 修約版本改用面板呈現，切換版本更直覺
- 基本資訊區塊欄位排版調整，資料更好閱讀
```
