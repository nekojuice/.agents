---
name: create-skill-guide
description: >-
  Cross-host authoring norms for creating or updating Agent Skills under this
  project. Covers Claude SKILL.md frontmatter, Codex agents/openai.yaml,
  inverse invocation policies, metadata author/version/last_updated, and
  optional extends. Use whenever an agent creates or updates a project skill,
  or when the user explicitly runs /create-skill-guide.
disable-model-invocation: false
metadata:
  author: Cursor Grok 4.5, Codex GPT-5
  version: "1.1"
  last_updated: "2026-08-20T15:05:36"
---

# create-skill-guide

Cross-host norms for a skill's Claude-facing `SKILL.md` frontmatter and Codex-facing `agents/openai.yaml`. Apply automatically whenever creating or updating a skill in this project; explicit `/create-skill-guide` invocation also works. This skill does **not** govern skill body prose or unrelated tooling.

## Required paired shape

Every project skill must store an explicit invocation choice for both hosts. Do not rely on either host's omitted/default value.

`SKILL.md`:

```yaml
---
name: <skill-name>
description: >-
  <what it does and when to use it>
disable-model-invocation: <true-or-false>
metadata:
  author: <Product-or-IDE-or-App> <model>
  version: "1.0"
  last_updated: "YYYY-MM-DDTHH:mm:ss"
---
```

`agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: <true-or-false>
```

Preserve existing `interface` and `dependencies` blocks in `agents/openai.yaml`. Add only the fields the skill actually needs; the invocation policy itself must always be present and explicit.

`extends` appears **only when needed** (see below). Do not invent other metadata keys unless the user asks.

## Field rules

### `name` / `description`

- Follow normal skill naming: lowercase, digits, hyphens; description states WHAT and WHEN (third person).

### Invocation policy — Claude and Codex are inverse

| Intended behavior | Claude `SKILL.md` | Codex `agents/openai.yaml` |
| --- | --- | --- |
| Agent may invoke automatically | `disable-model-invocation: false` | `allow_implicit_invocation: true` |
| User must invoke explicitly | `disable-model-invocation: true` | `allow_implicit_invocation: false` |

Never copy the same boolean across hosts. After any invocation-policy edit, verify that the two explicit values are opposites.

#### Decide with the user

- **New skill:** inspect the skill's nature, recommend automatic or explicit-only invocation with one short reason, and ask the user which behavior they want. Do not ask again when the user already stated the choice.
- **Existing skill:** preserve the current paired decision during ordinary content edits. Ask only when either property is missing, the pair conflicts, the requested change affects activation behavior, or the user asks to reconsider it.
- When a repository policy or an explicit user decision already supplies the answer, follow it and do not ask a redundant question.

#### Recommendation criteria

Recommend **explicit-only** when the skill changes session-wide persona/output behavior, has unusually broad orchestration or write authority, can create disruptive or very large output, or represents a costly/special workflow without a safe discriminating trigger.

Recommend **automatic invocation** when the skill is a narrow and safely applicable discipline, framework/domain guidance, ordinary diagnostic/documentation help, or a worker/helper that another workflow must be able to select. Its `description` must state precise positive triggers and meaningful exclusions.

Authority alone is not an absolute rule. A powerful skill may allow automatic invocation when it has a reliable contextual entry condition and preserves internal authorization gates. `orchestrator-factory`, for example, can activate from an approved cold-start factory handoff while still requiring its dispatch and human gates.

### Codex `agents/openai.yaml`

- Store the file at `<skill>/agents/openai.yaml`, not in `SKILL.md` and not at the repository root.
- `policy.allow_implicit_invocation` controls automatic Codex selection. `false` still permits explicit `$skill-name` invocation.
- Preserve unrelated `interface` and `dependencies` values when updating an existing file.
- Use quoted strings for UI/dependency string values; keep YAML keys and booleans unquoted.

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

- [ ] Recommend an invocation mode and ask the user unless already decided
- [ ] Claude `disable-model-invocation` explicitly set
- [ ] Codex `policy.allow_implicit_invocation` explicitly set to the inverse value
- [ ] `metadata.author` set (host + model)
- [ ] `metadata.version` set (usually `"1.0"`)
- [ ] `metadata.last_updated` from OS, to the second
- [ ] `extends` only if needed

**Update (content changed)**

- [ ] Preserve the existing invocation decision unless this change affects it
- [ ] Ask when either host property is missing/conflicting or activation is being reconsidered
- [ ] Verify Claude and Codex values are both explicit and inverse
- [ ] Append `metadata.author` if you are a new co-editor
- [ ] Bump `metadata.version` minor (+1)
- [ ] Refresh `metadata.last_updated` from OS, to the second
- [ ] Add/adjust `extends` only if the relationship changed and still needed
