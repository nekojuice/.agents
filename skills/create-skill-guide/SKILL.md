---
name: create-skill-guide
description: >-
  Frontmatter (YAML header) norms for writing or updating Agent Skills under
  this project. Covers disable-model-invocation, metadata author/version/
  last_updated, and optional extends. Use only when the user runs
  /create-skill-guide or explicitly asks to apply skill header / frontmatter
  conventions when creating or editing a SKILL.md.
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5
  version: "1.0"
  last_updated: "2026-07-23T16:41:54"
---

# create-skill-guide

Norms for the **YAML frontmatter** of a skill `SKILL.md`. Apply when creating or updating a skill **and** the user has invoked this guide (or equivalent). This skill does **not** govern skill body prose, discovery, or tooling beyond the header.

## Required shape

```yaml
---
name: <skill-name>
description: >-
  <what it does and when to use it>
disable-model-invocation: true
metadata:
  author: <Product-or-IDE-or-App> <model>
  version: "1.0"
  last_updated: "YYYY-MM-DDTHH:mm:ss"
---
```

`extends` appears **only when needed** (see below). Do not invent other metadata keys unless the user asks.

## Field rules

### `name` / `description`

- Follow normal skill naming: lowercase, digits, hyphens; description states WHAT and WHEN (third person).

### `disable-model-invocation`

- On **create**: set `true` unless the user explicitly wants automatic / ambient invocation.
- On **update**: if changing this flag, only when the user directs it.

### `metadata` (required block)

Always present when this guide applies to a create or content change.

| Key | Rule |
| --- | --- |
| `author` | If empty or missing → set to **product / IDE / app name + model** (e.g. `Cursor Grok 4.5`, `Claude Code Opus 4.8`). Same model under different hosts must differ. If authors already exist → **append** yourself with `, ` (comma + space); do not remove prior names. |
| `version` | String semver-like. On content change, bump the **minor** segment by 1 (`1.0`→`1.1`, `1.9`→`1.10`). Do **not** bump the major segment unless the user explicitly orders a major bump. |
| `last_updated` | On every create or content change, set to the **current OS local time to the second**: `YYYY-MM-DDTHH:mm:ss`. Obtain via a real OS command (e.g. PowerShell `Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'`, or `date` on Unix). Do not use date-only values or fake midnight (`T00:00:00`). |
| `extends` | Optional. Include **only when** this skill documents a real link to related skill name(s). Comma-separate multiple names. Omit when there is no such link. |

## Create vs update checklist (header only)

**Create**

- [ ] `disable-model-invocation: true` (unless user asked otherwise)
- [ ] `metadata.author` set (host + model)
- [ ] `metadata.version` set (usually `"1.0"`)
- [ ] `metadata.last_updated` from OS, to the second
- [ ] `extends` only if needed

**Update (content changed)**

- [ ] Append `metadata.author` if you are a new co-editor
- [ ] Bump `metadata.version` minor (+1)
- [ ] Refresh `metadata.last_updated` from OS, to the second
- [ ] Add/adjust `extends` only if the relationship changed and still needed
