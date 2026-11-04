---
name: e2e-review
description: >-
  Worker rules for agent E2E / interaction review: operate the system under test through its
  screens or its API (each a registered surface) against a checklist, prepare test data through
  the system's own API instead of writing to the database, judge each item with value evidence and screenshots, record UI
  findings and write traceability, and hand an evidence-backed report to the superior (the factory
  orchestrator in automated flows, the user when invoked directly). Scripts grow in three tiers
  (ad-hoc, stable fragments, solidified scenarios) plus recipes for flows with agent-operated
  steps, all kept in the project's .e2e/ folder. Use when dispatched as the E2E / interaction
  reviewer before human acceptance, or when the user asks for an agent E2E or API integration check
  of screens and workflows. Not for unit tests, code review, or production environments.
disable-model-invocation: false
metadata:
  author: Claude Code Opus 5.5
  version: "1.3"
  last_updated: "2026-11-04T17:55:29"
extends: playwright-cli
---

# E2E Review

Verify implemented behavior by actually operating the system under test, through its screens or its API, then report what was verified, what was not, and the evidence. This is the last agent self-check before human acceptance; it never replaces human acceptance.

The skill holds no project information. Everything project-specific lives in the project's `.e2e/` folder, starting with `.e2e/PROJECT.md`.

Each part of the system the review operates is a **surface**, registered in `.e2e/config/env.json` with the driver that operates it. The skill ships two drivers: `playwright` for web screens and `http` for APIs. A project registers only the surfaces it has; adding one is described in [references/project-profile.md](references/project-profile.md).

## Role and superior

You are the review worker. You operate, judge, collect evidence, and report. You do not accept items on anyone's behalf, and you do not edit your superior's checklists or control files.

| Invoked by | Superior | Report location | Return |
| --- | --- | --- | --- |
| An orchestrator dispatch, e.g. factory | The dispatching orchestrator | The parent folder the dispatch names, e.g. a factory run | The return block in "Return" |
| The user directly | The user | A path the user names, else see [references/tools.md](references/tools.md) | Report link, overall verdict, items needing a decision or human check |

Questions go to the superior: missing input, write permission, missing accounts, environment down. Do not decide them yourself, and do not go around an orchestrator to ask the user.

## Required input

Return `needs-input` to the superior when any required item is missing. Return `blocked` when the environment or a driver is unavailable (site down, tool missing) and the remaining items cannot be operated; say which items and why in `notes`.

| Item | Required | Notes |
| --- | --- | --- |
| Checklist items | Yes | Number and original text of each item; the report is organized by these items. When the checklist has no numbers, the superior sets the numbering rule in the dispatch; do not invent one |
| Report parent folder | Dispatch: yes | The worker creates the fixed-name `e2e-review/` folder under it |
| Test-data write (`data_write`) | Yes | Test data that may be created or changed; `none` when not granted. The project's `.e2e/` folder and the round folder are always writable |
| Round kind (`round_kind`) | Optional | `review` (default), `prep`, or `init`; passed to `new --kind` |
| Accounts | When not in PROJECT.md | Which account keys to use and their roles; without PROJECT.md, use only the keys the superior names for E2E |
| Environment | When not in PROJECT.md | Site, version, data scope |
| Previous round | For iterations | Path of the previous round folder |
| Round basis | Optional | The fix this round verifies, e.g. a commit or change name |
| Init apply (`init_apply`) | After an approved init proposal | Round folder of the approved proposal and who approved it; run `init-apply <round> --approved-by=<who>` in this round |

## Boundaries

- Never touch a production environment. Work only in the test environment PROJECT.md names.
- Do not call paid external services or external websites unless the user approves the scope.
- Do not modify the product's code, configuration, or specifications. Write only to the project's `.e2e/` folder and the execution workspace (`e2e-review/`).
- Do not commit or push. Commits of `.e2e/` are the superior's decision.
- Write test data only within the granted permission (`data_write`). Login, logout, page-open, and query audit entries are expected side effects; list them in the report.
- Use the accounts created for E2E, each by its role; when a check needs an administrator role, the dispatch or PROJECT.md says which E2E account to use. Existing accounts (people's own and existing administrator accounts) are not yours to use unless PROJECT.md lists them as protected accounts, with what they may be used for and the checks around them. Without PROJECT.md, use only the account keys the superior names for E2E, and ask before using any administrator account.
- Records a check needs changed (a field, a flag, an assignment) are created as dedicated test data through the API and changed there; never alter existing records to stage a check. A setting that exists once for the whole system and cannot be created anew may be changed only when `data_write` names it: save its original value first, restore it in a step run with `{ always: true }`, and record both the change and the restore as writes.
- Test data the round leaves in the test environment is expected, but it must be identifiable by round and worker: the project's naming prefix, the dedicated accounts, the round's `data/manifest.json`, and `.e2e/state/data-<env>.json`.
- Passwords live only in `.e2e/config/accounts.local.json`, which is never committed unless the user explicitly allows it, e.g. for a closed internal test environment. Every artifact records account keys only, never passwords: reports, `result.json`, `steps.jsonl`, `exchanges/`, values, screenshots, scratch scripts, init proposals, and anything you return. Tokens and session cookies are treated like passwords.
- API calls go only to surfaces PROJECT.md registers for the test environment. Build requests from templates recorded from real screen requests, or from the project's published API contract (controllers, OpenAPI, or API docs PROJECT.md names); never call endpoints outside both, such as undocumented internal or admin endpoints. Prepare test data through the API rather than writing to the database, so the backend writes every related table.
- Anything that writes (fragments, scenarios, recipe steps, ad-hoc API calls) supports a dry run (`--dry`) that builds the request or fills the form without sending it. On web surfaces the driver also blocks write requests during a dry run. Dry-run first; run the real write once. A dry run needs no test-data permission. Logging in and out during a dry run is normal; never clear the browser session (cookies, storage, profile) in place of a logout.
- One worker operates the system under test per environment at a time, across all surfaces. Sub-workers you dispatch never operate it; see "Internal delegation".

## Startup

Run on every invocation; create things only when missing.

1. Read `.e2e/PROJECT.md` when the project has one.
2. Run `node <skill>/scripts/e2e.mjs check`: project assets, skill version against the version PROJECT.md was verified with, registered surfaces and their drivers, layout warnings, audit adapter, account keys.
3. A version mismatch or layout warning does not stop the work; record it under issues.
4. Driver or environment unavailable: report to the superior. Do not install tools or start services.
5. Confirm the required input, then create the round folder with `new` (see "Workflow"); `check --out` then keeps the startup check in the round.

### When the project has no `.e2e/`

| Situation | Action |
| --- | --- |
| Dispatched by an orchestrator in a standardized project (a fixed agent workflow with folders such as `.factory/`) | Init handoff below |
| Invoked directly by the user | No init. Work ad-hoc in the execution workspace only |

Init handoff, always with superior approval:

1. Do the review anyway, ad-hoc, in the execution workspace.
2. Write a proposal with `init-proposal <round>`, then fill `init-proposal/.e2e/PROJECT.md` from a read-only survey of the project. Keep only the surfaces the project has. Mark anything you cannot confirm (writable data, accounts, audit source) as pending. List ad-hoc scripts worth promoting.
3. State in the report conclusion and issues that the project is not initialized, with the proposal path.
4. After the superior approves, on the next dispatch or explicit instruction: create that round with `new` (kind `init` when dispatched so), then run `init-apply <proposal round> --approved-by=<who>` and move the approved promotions in. The current round stays current and records the creation of `.e2e/` under writes. `init-apply` never overwrites.

Details: [references/project-profile.md](references/project-profile.md).

## Workflow

Commands are `node <skill>/scripts/e2e.mjs <command>`, run from the project root. Full reference: [references/tools.md](references/tools.md).

1. `new <short> --parent=<report parent> [--prev=<previous round>] [--basis=<fix>] [--kind=review|prep|init]` creates `<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` and makes it current. Use `prep` for rounds that only prepare data.
2. `open --surface=web` starts the browser when a web surface is involved; API surfaces need no open.
3. Run the matching scenario with `scenario scenarios/<name>`, or compose fragments with `run <surface>:<fragment> --account=<key> --save=<name>`. Flows with agent-operated steps follow a recipe: `step <recipe>#<id>` runs a script step, `log start|end <recipe>#<id>` records an agent step; see [references/recipes.md](references/recipes.md).
4. Fill gaps ad-hoc: `peek --from=<text>` to explore a screen, `api <METHOD> <path>` for one logged API call, a `scratch/` script run through `run`, or single browser commands (not logged; avoid in write tasks). On a web surface, try an interaction you will cancel before saving with `run --rehearse`, which stays out of the formal steps; it operates for real and must not save anything, and API surfaces refuse it.
5. Check the UI beyond the checklist on web surfaces; see [references/ui-checks.md](references/ui-checks.md). Use `sheet` for many screenshots.
6. `run web:probes/shot --name=final` when a web surface was used.
7. Record what scenarios did not: `add <round> <field> '<json>'` for UI findings, issues, limits, observations, writes, items.
8. Review `scratch/` for promotion, including request templates and recipe drafts; see [references/script-tiers.md](references/script-tiers.md).
9. `close <round> --users=<account keys>` fetches audit rows for the task window and renders `report.md`.
10. Return to the superior.

## Judgment

Full rules and the result format: [references/report-spec.md](references/report-spec.md).

- Every pass or fail needs evidence; value evidence beats screenshots. No evidence means inconclusive.
- Check sources: `script`, `value`, `visual`, `not-run`, `run-error`. Visual-only, not-run, and run-error checks are always inconclusive.
- Record how each check was verified (`via`: web, api, db). A screen behavior verified only through the API is a limit, not a full pass of a screen item.
- Recipes are not yet an acceptance basis. Mark checks whose judgment rests on an agent-operated recipe step (`agent`); their items stay `needs-human` even when the check passes.
- Report failures as they are. Never loosen a check to make it pass.
- Tell product failures from tool failures. Fix the tool and rerun in the same round folder, keeping both runs in the report; if it cannot be fixed, the check is inconclusive with source `run-error`. When only the checking code was wrong and rerunning would write data again, write a scratch script in the round folder (`scratch/`) that reads the round's existing value files and recomputes the check without sending any request, save its output in `values/`, then record the correction with `amend`, citing the script and its output as evidence; the original judgment stays beside the correction and the superior reviews it. See [references/tools.md](references/tools.md).
- Record your own assumptions, substitute methods, and coverage gaps under issues; record passed checks verified under restricted conditions under limits.
- `prep` and `init` rounds without checks give no pass verdict; their return carries `verdict: inconclusive`, no items, and the round kind in `notes`. When they record checks, they are judged like `review` rounds and the return names the round kind in `notes`.
- The report suggests a status per checklist item. The superior decides what counts as done.

## Iterations

- Each round gets a new round folder with `--prev` pointing to the previous one; the report compares item statuses.
- Reruns caused by tool problems stay in the same round folder.
- Items verified in an earlier round are re-verified when this round's fix may affect them; the superior decides about unaffected items.

## Return

Return this block to an orchestrator. For the user, give the same facts in prose.

```text
E2E_REVIEW_RESULT_V1
status: done | needs-input | blocked
round_folder: <absolute path>
report: <round_folder>/report.md
verdict: pass | fail | inconclusive
items:
  - <id>: <verified | verified-with-limits | needs-human | run-error | product-fail> — <one line>
init_needed: no | yes (<proposal path>)
writes: <none | short list; data/manifest.json holds the full record>
assets_changed: <none | versioned .e2e/ files added or changed this round, paths relative to .e2e/>
notes: <blockers, version mismatch, questions for the superior>
```

`assets_changed` lists versioned files only: `new` records the `.e2e/` git state, and `report` or `close` compares against it into `result.assetsChanged` and the report's `.e2e/` changes section; copy that list. Files deleted in the round are marked "(deleted)"; renamed ones are listed as "<old path> → <new path>". In a round that starts before `.e2e/` exists (an init round in a git project), every file of the new `.e2e/` is listed. Local-only files (`config/accounts.local.json`, `state/`, `out/`) are never listed. Without git the report says it cannot compare; list the changes yourself.

A `needs-human` item that rests on an agent step says so in its line (e.g. "agent step: …"); rerunning the round does not change it, so the superior hands it to a person.

## Internal delegation

You may dispatch sub-workers for parallel preparation. Only you operate the system under test, run scripts, and write test data.

Sub-workers may: derive expected values from specs, changes, and code; run read-only database queries; draft fragments, scenarios, recipes, and request templates from snapshots or recorded requests you give them; review screenshots and value files for UI finding candidates; draft issue and observation text.

You trial their code before it enters `.e2e/`, and you check the evidence before their findings enter the report.

## References

| File | Read when |
| --- | --- |
| [references/report-spec.md](references/report-spec.md) | Judging checks, writing the result, reading the report format |
| [references/script-tiers.md](references/script-tiers.md) | Writing, promoting, or repairing scripts and test data |
| [references/recipes.md](references/recipes.md) | Writing or running flows with agent-operated steps |
| [references/ui-checks.md](references/ui-checks.md) | Checking the UI beyond the checklist on web surfaces |
| [references/project-profile.md](references/project-profile.md) | Reading or creating `.e2e/`, surfaces, the audit adapter, versioning |
| [references/tools.md](references/tools.md) | Command reference, folders, sessions |
| [references/drivers/playwright.md](references/drivers/playwright.md) | Operating web surfaces through playwright-cli |
| [references/drivers/http.md](references/drivers/http.md) | Operating API surfaces |
