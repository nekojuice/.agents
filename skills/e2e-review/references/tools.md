# Tools

`node <skill>/scripts/e2e.mjs <command>`. Run from the project root (or pass `--project=<root>`); the tool finds `.e2e/` by walking up from the current directory.

## Folders

| Folder | Where |
| --- | --- |
| Project assets | `<project root>/.e2e/` |
| Execution workspace | `<parent>/e2e-review/`, fixed name, self-ignoring |
| Round folder | `<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` |
| Dry-run output | `<round>/dry/<name>/`, one folder per scenario, fragment, recipe step, or `api`: steps, values, exchanges, and result of `--dry` runs; never judged |
| Rehearsal output | `<round>/rehearse/<name>/`: steps and values of `run --rehearse` (web surfaces only); never judged |
| Downloads | `<round>/downloads/` (or the dry folder's), written by `web:probes/download` |
| Driver output (e.g. `.playwright-cli/`) | Inside the execution workspace; the driver runs with that folder as current directory |

Default `<parent>` when none is given: `.e2e/out/` when the project has assets, otherwise the current directory. Dispatched work always passes `--parent` as the orchestrator directs, e.g. `.factory/_runs/<run>`.

Without project assets (a direct, ad-hoc invocation), both built-in surfaces are implicit: `web` at `--url=<base>` and `api` at `--api-url=<base>`. Calls on the implicit api surface carry no login, since there is no `auth.mjs`.

## Commands

| Command | Does |
| --- | --- |
| `check [--out[=<round>]]` | Startup checks: assets, skill version against PROJECT.md, registered surfaces with driver availability and fragment declarations, 1.1 layout warnings, `.e2e/` paths that git ignores although they should be versioned, audit adapter, account keys. `--out` also writes `values/check.json` in the round (the current one when no path is given) |
| `new <short> [--parent] [--prev] [--basis] [--kind=review\|prep\|init]` | Create a round folder, initialize `result.json`, make it the current task |
| `open [--surface=web] [--url]` | Start the browser of a web surface at its `baseUrl`; retries once |
| `run <[surface:]fragment> [--account=<key>] [--save=<name>] [--out=<round>] [--dry\|--rehearse] [--expects=<json>] [--k=v]` | Run a fragment on its surface, log the step, store the value in `values/<name>.json`. `--rehearse` is refused on API surfaces; `scenario`, `step`, and `api` refuse it too |
| `scenario <file> [--out=<round>] [--dry] [--k=v]` | Run a scenario module with a fresh context |
| `api <METHOD> <path> [--surface=api] [--account=<key>] [--body=<json file>] [--dry] [--out]` | One API call on an http surface; always logged, stored in `exchanges/` |
| `step <recipe>#<id> [--out] [--dry]` | Run a script step of a recipe |
| `log start\|end <recipe>#<id> [--evidence=a,b] [--note=<text>] [--fail] [--out]` | Record an agent step of a recipe |
| `peek [--surface=web] [--from=<text>] [--max=<n>]` | Print a condensed snapshot of the current screen; not logged |
| `sheet <round> [--surface=web] [--prefix] [--per]` | Build contact sheets of `shots/` into `review/` |
| `add <round> <field> '<json>'` | Append to `items`, `checks`, `uiFindings`, `writes`, `limits`, `issues`, or `observations`; the entry's shape is checked (see report-spec "result.json") and a wrong shape is refused |
| `amend <round> <check id> '<json>' --reason=<text> --evidence=<paths>` | Correct fields of one recorded check (`verdict`, `actual`, `expected`, `by`, `via`, `note`, `evidence`, `agent`). Reason and evidence are required; evidence paths are relative to the round folder and must exist. The original judgment is kept beside the correction, the check is marked amended, and the report lists both |
| `audit <round> [--users=<keys or ids>] [--actions=<codes>] [--system]` | Fetch audit rows for the formal window into `values/audit.json`, and for the dry-run and rehearsal window into `values/audit-side.json` |
| `report <round>` | Render `report.md`; also updates `result.json`: `verdict` and `stats` from all checks (unchanged when there are none) and `assetsChanged` |
| `close <round> [--users] [--actions] [--system]` | `audit` when any filter is given, then `report`. Without an audit adapter, or when the adapter fails, `close` warns and still renders the report; a failure is also kept as one issue, replaced by a later failure and removed by a successful audit. `audit` alone reports these as errors |
| `init-proposal <round>` | Copy the `.e2e/` skeleton into `<round>/init-proposal/.e2e/` |
| `init-apply <round> --approved-by=<who> [--project=<root>]` | Copy the approved proposal in `<round>` to `<root>/.e2e/`; the current round stays current (its pointer moves into the new `.e2e/state/`) and records the write, or the proposal round when there is no current round; refuses to overwrite |

Commands that take `<round>` fall back to the current task when it is omitted (`run`, `scenario`, `api`, `step`, `log` via `--out`).

### Arguments

- Reserved argument names: `account`, `save`, `out`, `dry`, `rehearse`, `expects`, `recipe` (set by `step`). Fragment arguments must use other names; a recipe step whose `args` uses one (other than `account`) is refused.
- A fragment knows it runs dry from `P.dry`; it needs no argument of its own for that. Scenarios pass the mode on through `ctx.run` automatically.
- A `--k=v` value that is a JSON object or array (`--item='{"sku":"K1","qty":2}'`) arrives as an object, the same type a scenario passes through `ctx.run`; other values stay strings.
- `--expects='[{"action":"<action code>"}]'` declares the audit rows a step produces, for attribution (report-spec "Write traceability").

### Value files

- `values/<name>.json` holds the latest value. Rerunning a step with the same save name keeps the older file as `values/<name>.<n>.json`; the report uses the latest and lists the kept ones.
- Several scenarios may run in one round. Each scenario owns the checks, items, limits, issues, UI findings, and observations it records; rerunning it replaces only its own entries. Entries added with `add` are kept. Writes accumulate across all runs.

## Reruns and corrections

| Situation | Do |
| --- | --- |
| A tool problem stopped a scenario | Fix the tool and rerun the scenario in the same round; its own entries are replaced, other scenarios' and manual entries stay |
| The checking code was wrong but the recorded steps and values are fine, and rerunning would write data again | Do not rerun. Write a scratch script in the round folder (`scratch/`) that reads the round's existing value files and recomputes the check without sending any request, save its output in `values/`, then record the correction with `amend`, citing the script and its output as evidence. One `amend` per corrected check. The superior reviews the corrections |
| One recorded check needs a correction (e.g. after verifying a value by other means) | `amend <round> <check id> '<json>' --reason=<text> --evidence=<paths>`; a later rerun of the scenario replaces the check (the amendment log stays), so amend again if needed |
| On a web surface, you need to try a real interaction that will be cancelled before saving (e.g. open a dialog, then cancel) | `run <fragment> --rehearse`; it operates for real without the dry-run guard, so it must not save anything; it logs under `rehearse/` and never enters the step table or the verdict. API surfaces refuse it (an API call cannot be cancelled, so use `--dry`), and so do `scenario`, `step`, and `api` |

## Sessions and the current task

- The browser session name comes from `E2E_SESSION`, else the surface's `session`, else `e2e`; `open`, `run`, `peek`, and the current-task pointer all follow the same rule.
- `new` records the current round per session in `.e2e/state/current-<session>` (or inside the execution workspace when there are no assets). Later commands without an explicit round use it, so ad-hoc steps are logged to the right round.
- Single browser commands run directly (outside `e2e.mjs`) are not logged; prefer `run` with a scratch script in tasks that write data.
- API calls always go through `e2e.mjs` (`run`, `scenario`, `step`, `api`) so every call is logged. The http driver keeps login sessions in memory for the life of one command; a scenario reuses them across its steps.
- Every formal `run`, `scenario`, `api`, `step`, `log`, and `amend` command is added to `result.reproduce` automatically, redacted like `steps.jsonl`: a `--key` whose name looks secret is masked, and JSON values are masked by key.

## Long runs

Commands that run longer than the shell tool allows (typically a scenario over two minutes) run in the background; wait for them by checking `result.json` or the last line of `steps.jsonl`, not by sleeping in the foreground.

## Windows

- Git Bash rewrites arguments that start with `/` into paths under the Git install (`/items` → `C:/Program Files/Git/items`). `e2e.mjs` undoes that rewrite for its own arguments and for the commands it records, finding the install from `EXEPATH` (set by Git Bash) or the default location; other tools may still need `MSYS_NO_PATHCONV=1`.
- Give the skill path as `C:/Users/...` rather than `/c/Users/...`, and a scratch fragment after a surface prefix as a Windows path (`api:C:/.../scratch/api/x.mjs`); a prefix followed by `/` is not read as a surface.
- The skeleton's `.gitattributes` fixes line endings in `.e2e/`; keep the line endings a file already uses when editing it in a project without one.

## Layers

| Layer | Files | Changes when |
| --- | --- | --- |
| Core (driver-independent) | `scripts/core/`: project lookup, surfaces and driver loading (`drivers.mjs`), round folders and step log (`task.mjs`), audit attribution (`trace.mjs`), value-based redaction (`secrets.mjs`), data manifest, recipes, scenario context, audit, report | Report or workflow rules change |
| Drivers | `scripts/drivers/<driver>/driver.mjs` with its helpers and generic probes; one reference per driver in `references/drivers/<driver>.md` | A driver changes, or a new driver is added |

A driver exports `name`, `extensions` (fragment file types), `available()` (version string or null, for `check`), and `runFragment({ file, P, ctx })` returning `{ ok, value, error }`; it may add `open`, `peek`, and `buildSheets`, which the matching commands use for any surface whose driver offers them. Adding a driver means adding its folder and reference; core does not change.

Core runs on Node.js without third-party packages. The playwright driver needs `playwright-cli` on `PATH`; the http driver needs Node's built-in `fetch`.

## Reading downloaded files

Reading Excel, PDF, or other downloaded files needs a reader the skill does not ship. Install it in the project's own script environment, or in an ignored path such as `.e2e/state/`, as PROJECT.md says; never globally, and never in a versioned `.e2e/` folder (a package folder such as a virtual environment or `node_modules/` would be committed). Small reader scripts of the project may live in `.e2e/tools/`. Record the read values in `values/`.
