# Tools

`node <skill>/scripts/e2e.mjs <command>`. Run from the project root (or pass `--project=<root>`); the tool finds `.e2e/` by walking up from the current directory.

## Folders

| Folder | Where |
| --- | --- |
| Project assets | `<project root>/.e2e/` |
| Execution workspace | `<parent>/e2e-review/`, fixed name, self-ignoring |
| Round folder | `<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/` |
| Driver output (e.g. `.playwright-cli/`) | Inside the execution workspace; the driver runs with that folder as current directory |

Default `<parent>` when none is given: `.e2e/out/` when the project has assets, otherwise the current directory. Dispatched work always passes `--parent` as the orchestrator directs, e.g. `.factory/_runs/<run>`.

## Commands

| Command | Does |
| --- | --- |
| `check` | Startup checks: assets, skill version against PROJECT.md, driver version, audit adapter, account keys |
| `new <short> [--parent] [--prev] [--basis]` | Create a round folder, initialize `result.json`, make it the current task |
| `open [--url]` | Start the browser with `env.browser` at `env.baseUrl`; retries once |
| `run <fragment> [--account=<key>] [--save=<name>] [--out=<round>] [--k=v]` | Run a fragment, log the step, store the value in `values/<name>.json` |
| `scenario <file> [--out=<round>] [--k=v]` | Run a scenario module with a fresh context |
| `peek [--from=<text>] [--max=<n>]` | Print a condensed snapshot of the current screen; not logged |
| `sheet <round> [--prefix] [--per]` | Build contact sheets of `shots/` into `review/` |
| `add <round> <field> '<json>'` | Append to `items`, `checks`, `uiFindings`, `writes`, `limits`, `issues`, or `observations` |
| `audit <round> --users=<keys or ids>` | Fetch audit rows for the task window into `values/audit.json` |
| `report <round>` | Render `report.md` |
| `close <round> [--users]` | `audit` when users are given, then `report` |
| `init-proposal <round>` | Copy the `.e2e/` skeleton into `<round>/init-proposal/.e2e/` |
| `init-apply <round> --approved-by=<who> [--project=<root>]` | Copy an approved proposal to `<root>/.e2e/`; refuses to overwrite |

Commands that take `<round>` fall back to the current task when it is omitted (`run`, `scenario` via `--out`).

## Sessions and the current task

- The browser session name comes from `E2E_SESSION`, else `env.session`, else `e2e`.
- `new` records the current round per session in `.e2e/state/current-<session>` (or inside the execution workspace when there are no assets). Later commands without an explicit round use it, so ad-hoc steps are logged to the right round.
- Single driver commands run directly (outside `e2e.mjs`) are not logged; prefer `run` with a scratch script in tasks that write data.

## Layers

| Layer | Files | Changes when |
| --- | --- | --- |
| Core (driver-independent) | `scripts/core/`: project lookup, round folders and step log, scenario context, audit, report | Report or workflow rules change |
| Driver | `scripts/playwright/`: browser launch, fragment execution, browser-side helpers, generic probes | The driver changes; a new driver gets its own sibling folder and `references/drivers/<driver>.md` |

Core runs on Node.js without third-party packages. The Playwright driver needs `playwright-cli` on `PATH`.
