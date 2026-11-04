# Recipes

A recipe is a solidified flow that still contains steps an agent operates by hand, for example through an MCP tool the scripts cannot call, mixed with script steps. It sits beside scenarios: a scenario is all script steps and reruns unattended; a recipe is replayed by an agent following the file.

Recipes may cross surfaces and may switch between agent and script steps as often as the flow needs, e.g. prepare data through the API, operate a tool by hand for a while, then hand the rest to a script.

**Recipes are not yet an acceptance basis.** Use them to prepare data or state and to grow scripts. A check whose judgment rests on an agent step is marked (`opts.agent` in `ctx.check`); its checklist item stays `needs-human` even when the check passes, and the report lists such checks under the conclusion.

## File format

`.e2e/recipes/<name>.md`: Markdown with a YAML front matter and one fenced `yaml` block per step. The template is `assets/recipe.template.md`.

````markdown
---
purpose: prepare orders whose due date falls inside the reminder window
preconditions: api surface reachable; clerk and approver accounts exist
surfaces:
  - api
  - web
writes: two approved orders with E2E codes
---

# Due orders

### 1. Create an order due today

```yaml
id: 1
surface: api
kind: script
run: actions/order-create
args: {account: clerk, set: due-orders, row: today}
save: order-today
expect: status 201 and an id
```

### 2. Check the order on screen

```yaml
id: 2
surface: web
kind: agent
do: |
  Open the order detail of the new id on the web surface.
  Read the due date shown in the header.
expect: the due date equals today
evidence:
  - shots/order-today.png
```
````

| Field | Steps | Meaning |
| --- | --- | --- |
| `id` | all | Unique within the recipe (`0` is allowed); used in commands and the step log |
| `surface` | all | The surface the step operates; required |
| `kind` | all | `script` or `agent` |
| `run` | script | Fragment path on the step's surface; a `<surface>:` prefix is allowed but must match `surface` |
| `args` | script | Fragment arguments as a map (flow map `{a: 1}` or JSON); `account` names the account; other reserved names (`save`, `out`, `dry`, `rehearse`, `expects`, `recipe`) are refused |
| `save` | script | Value file name; default `<recipe>-<id>` |
| `expects` | script | Audit rows the step produces, a map or a list of maps such as `[{action: <code>}]`; used for attribution like `--expects` |
| `do` | agent | What the agent operates and how, specific enough to replay; may be a `|` block |
| `expect` | all | What must be true after the step |
| `evidence` | agent | Value files or screenshots the agent must leave |

The YAML is read as a subset: `key: value` scalars, `|` and `>` block scalars for top-level keys, one level of nested maps or `- item` lists, and single-line flow maps or lists (`{a: 1, b: x}`, `[a, b]`) or JSON. Anything else fails with a message naming the line.

## Running

| Step kind | Command | Logged as |
| --- | --- | --- |
| script | `step <recipe>#<id> [--dry]` | A normal step of the fragment, with `recipe=<recipe>#<id>` in its arguments |
| agent | `log start <recipe>#<id>`, operate, `log end <recipe>#<id> [--evidence=a,b] [--note=…] [--fail]` | A step of kind `agent` with its evidence and note, placed on the timeline by its start time |

Both land in the round's `steps.jsonl`, so audit attribution, the report's step table, and write traceability work as for scripts. Script steps, `run`, or `api` commands you run between `log start` and `log end` are shown nested under the agent step; audit rows go to the nested step that produced them, and rows of the agent's own operation after a nested step ended go to the agent step. Record writes an agent step made with `add <round> writes '<json>'`.

## Growing a recipe

1. Start ad-hoc. When the sequence will be repeated, write it down as a recipe, mostly agent steps.
2. Each time a stretch of agent steps becomes stable, script it: put the fragment in its surface, and change the step to `kind: script`.
3. When every step is a script step, rewrite the recipe as a scenario and delete the recipe file.
4. Keep the recipes table in `PROJECT.md` current, including how many agent steps remain.
