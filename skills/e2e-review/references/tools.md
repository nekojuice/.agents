# Tools

`node <skill>/scripts/e2e.mjs <command>`. Run from the project root (or pass `--project=<root>`); the tool finds `.e2e/` by walking up from the current directory.

## Folders

| Folder | Where |
| --- | --- |
| Project assets | `<project root>/.e2e/` |
| Execution workspace | `<parent>/e2e-review/`, fixed name, self-ignoring |
| Round folder | `<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` |
| Dry-run output | `<round>/dry/`: steps, values, exchanges, and result of `--dry` runs; never in the report |
| Driver output (e.g. `.playwright-cli/`) | Inside the execution workspace; the driver runs with that folder as current directory |

Default `<parent>` when none is given: `.e2e/out/` when the project has assets, otherwise the current directory. Dispatched work always passes `--parent` as the orchestrator directs, e.g. `.factory/_runs/<run>`.

Without project assets (a direct, ad-hoc invocation), both built-in surfaces are implicit: `web` at `--url=<base>` and `api` at `--api-url=<base>`. Calls on the implicit api surface carry no login, since there is no `auth.mjs`.

## Commands

| Command | Does |
| --- | --- |
| `check` | Startup checks: assets, skill version against PROJECT.md, registered surfaces with driver availability and fragment declarations, 1.1 layout warnings, audit adapter, account keys |
| `new <short> [--parent] [--prev] [--basis] [--kind=review\|prep\|init]` | Create a round folder, initialize `result.json`, make it the current task |
| `open [--surface=web] [--url]` | Start the browser of a web surface at its `baseUrl`; retries once |
| `run <[surface:]fragment> [--account=<key>] [--save=<name>] [--out=<round>] [--dry] [--k=v]` | Run a fragment on its surface, log the step, store the value in `values/<name>.json` |
| `scenario <file> [--out=<round>] [--dry] [--k=v]` | Run a scenario module with a fresh context |
| `api <METHOD> <path> [--surface=api] [--account=<key>] [--body=<json file>] [--dry] [--out]` | One API call on an http surface; always logged, stored in `exchanges/` |
| `step <recipe>#<id> [--out] [--dry]` | Run a script step of a recipe |
| `log start\|end <recipe>#<id> [--evidence=a,b] [--note=<text>] [--fail] [--out]` | Record an agent step of a recipe |
| `peek [--surface=web] [--from=<text>] [--max=<n>]` | Print a condensed snapshot of the current screen; not logged |
| `sheet <round> [--surface=web] [--prefix] [--per]` | Build contact sheets of `shots/` into `review/` |
| `add <round> <field> '<json>'` | Append to `items`, `checks`, `uiFindings`, `writes`, `limits`, `issues`, or `observations` |
| `audit <round> --users=<keys or ids>` | Fetch audit rows for the task window into `values/audit.json` |
| `report <round>` | Render `report.md` |
| `close <round> [--users]` | `audit` when users are given, then `report` |
| `init-proposal <round>` | Copy the `.e2e/` skeleton into `<round>/init-proposal/.e2e/` |
| `init-apply <round> --approved-by=<who> [--project=<root>]` | Copy an approved proposal to `<root>/.e2e/`; refuses to overwrite |

Commands that take `<round>` fall back to the current task when it is omitted (`run`, `scenario`, `api`, `step`, `log` via `--out`).

Reserved argument names for `run`: `account`, `save`, `out`, `dry`. Fragment arguments must use other names.

## Sessions and the current task

- The browser session name comes from `E2E_SESSION`, else the surface's `session`, else `e2e`; `open`, `run`, `peek`, and the current-task pointer all follow the same rule.
- `new` records the current round per session in `.e2e/state/current-<session>` (or inside the execution workspace when there are no assets). Later commands without an explicit round use it, so ad-hoc steps are logged to the right round.
- Single browser commands run directly (outside `e2e.mjs`) are not logged; prefer `run` with a scratch script in tasks that write data.
- API calls always go through `e2e.mjs` (`run`, `scenario`, `step`, `api`) so every call is logged. The http driver keeps login sessions in memory for the life of one command; a scenario reuses them across its steps.

## Long runs

Commands that run longer than the shell tool allows (typically a scenario over two minutes) run in the background; wait for them by checking `result.json` or the last line of `steps.jsonl`, not by sleeping in the foreground.

## Windows

- Git Bash rewrites arguments that start with `/` into paths under the Git install (`/items` → `C:/Program Files/Git/items`). `e2e.mjs` undoes that rewrite for its own arguments, finding the install from `EXEPATH` (set by Git Bash) or the default location; other tools may still need `MSYS_NO_PATHCONV=1`.
- Give the skill path as `C:/Users/...` rather than `/c/Users/...`.
- Keep the line endings a file already uses when editing `PROJECT.md` and scripts.

## Layers

| Layer | Files | Changes when |
| --- | --- | --- |
| Core (driver-independent) | `scripts/core/`: project lookup, surfaces and driver loading (`drivers.mjs`), round folders and step log (`task.mjs`), value-based redaction (`secrets.mjs`), data manifest, recipes, scenario context, audit, report | Report or workflow rules change |
| Drivers | `scripts/drivers/<driver>/driver.mjs` with its helpers and generic probes; one reference per driver in `references/drivers/<driver>.md` | A driver changes, or a new driver is added |

A driver exports `name`, `extensions` (fragment file types), `available()` (version string or null, for `check`), and `runFragment({ file, P, ctx })` returning `{ ok, value, error }`; it may add `open`, `peek`, and `buildSheets`, which the matching commands use for any surface whose driver offers them. Adding a driver means adding its folder and reference; core does not change.

Core runs on Node.js without third-party packages. The playwright driver needs `playwright-cli` on `PATH`; the http driver needs Node's built-in `fetch`.
