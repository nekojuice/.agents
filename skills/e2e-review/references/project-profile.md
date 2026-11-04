# Project Profile

Each project keeps its review knowledge in `<project root>/.e2e/`. The skill stays project-free; the project folder accumulates environment facts, accounts, scripts, test data designs, and pitfalls.

## Layout

```
<project root>/.e2e/
├── PROJECT.md                     # read first on every task
├── config/
│   ├── env.json                   # surfaces, dataScope, repos, project query endpoints
│   ├── <name>.json                # any other project config, injected as P.config.<name>
│   ├── accounts.local.json        # account keys → { userId, password, note }; local only
│   └── accounts.local.example.json
├── surfaces/
│   └── <surface>/                 # one folder per registered surface, e.g. web, api
│       ├── actions/               # fragments that change state
│       ├── probes/                # read-only fragments
│       └── helpers/               # helpers injected as H.<name>; api: auth.mjs logs in
├── data/
│   ├── templates/                 # request bodies recorded from real screen requests
│   ├── builders/                  # template + parameters → request
│   └── sets/                      # named data sets
├── scenarios/                     # solidified scenarios, may cross surfaces
│   └── lib/                       # pieces shared by scenarios
├── recipes/                       # flows with agent-operated steps (references/recipes.md)
├── audit/fetch.mjs                # audit adapter
├── tools/                         # project tools used by scripts, e.g. file readers
├── state/                         # current-task pointers, data-<env>.json registry (ignored)
├── out/                           # default report parent for direct user runs (ignored)
└── .gitignore                     # config/accounts.local.json, state/, out/
```

| Path | Version control |
| --- | --- |
| PROJECT.md, config (except accounts.local.json), surfaces, data, scenarios, recipes, audit, tools | Committed by the superior; the worker never commits |
| config/accounts.local.json | Never, unless the user explicitly allows it for a closed internal test environment |
| state/ (including `data-<env>.json`), out/ | Never |
| Any `e2e-review/` execution workspace | Never; the folder carries its own `.gitignore` with `*` |

Execution artifacts (reports, screenshots, values, exchanges, manifests, scratch scripts, step logs) never enter `.e2e/`. Only promoted scripts, templates, data designs, and project facts do.

## Surfaces

`config/env.json` registers every surface the review operates:

```json
{
  "dataScope": "<test data scope>",
  "repos": { "web": "../<web repo>", "api": "../<api repo>" },
  "surfaces": {
    "web": { "driver": "playwright", "baseUrl": "http://localhost:5173/app", "browser": "msedge", "session": "app" },
    "api": { "driver": "http", "baseUrl": "http://localhost:8080/api" }
  }
}
```

| Driver | Fields |
| --- | --- |
| `playwright` | `baseUrl`, `browser`, `session` (browser session name; `E2E_SESSION` overrides), `dryAllow` (URL fragments allowed to write during a dry run, e.g. login) |
| `http` | `baseUrl`; login through `surfaces/<surface>/helpers/auth.mjs` |

Optional top-level `name` names the environment (used in `state/data-<env>.json`; falls back to `dataScope`).

- Surface names carry meaning for the project (`web`, `api`, `admin-console`); a project with two web systems registers two surfaces.
- Register only the surfaces the project has. A project without screens has no web surface; a project without an API has no api surface.
- Adding a surface: add its entry to `env.json`, create `surfaces/<name>/`, and confirm the skill ships its driver (`check` reports it). A driver the skill does not ship is a proposal to the skill owner, not a project change.
- `env.defaultSurface` names the surface used when a fragment reference has no prefix; otherwise `web`, else the first registered.

## PROJECT.md

Keep these sections current; the template is in `assets/e2e-skeleton/PROJECT.md`.

| Section | Content |
| --- | --- |
| Verified skill version | `Verified skill version: <x.y>`; the skill version the assets were last checked against |
| System under test | Site, checklist source, where routes, permissions, and API endpoints are defined, how to read the tested version |
| Surfaces | Each surface: driver, base URL, how login works, what it is used for |
| Operating limits | Test environment only, browser, writable data, untouchable data, external services, pending confirmations |
| Accounts | Key, user, role, purpose; never passwords |
| Audit trail | Source, adapter, action codes |
| Test data | Templates with their recorded source and date, builders, sets, how to read `state/data-<env>.json` (`<env>` is `env.json` `name`, else `dataScope`), the test-data naming prefix |
| Scripts | Tables per surface for actions and probes; scenarios; recipes with the number of agent steps left |
| Known pitfalls | Behavior that looks wrong but is by design, flaky spots, workarounds |

Write project knowledge learned during a task (new pitfalls, new scripts, new templates) back into PROJECT.md. Generic lessons go to the skill owner instead.

## Audit adapter

`.e2e/audit/fetch.mjs` is a persistent script and part of the script chain. The skill calls it for the task's time window and handles step attribution and rendering.

```js
// Read-only access only.
export default async ({ from, to, users, env, config }) => [
    { time: '2026-11-03T14:21:05.197', user: 'U01', action: '01 login', target: 'index', detail: '', source: '127.0.0.1' }
]
```

- `from`, `to`: local timestamps of the first step start and the last step end.
- `users`: user ids resolved from the account keys passed to `--users` (literal ids pass through).
- `time` must be local time in `yyyy-MM-ddTHH:mm:ss[.fff]`.
- `action` should combine the code and a readable label.
- A project without an audit trail deletes the adapter; reports then show the step timeline without audit rows.

## Versioning

- The skill's `metadata.version` is the compatibility marker.
- `PROJECT.md` records the version the assets were verified with; every `result.json` records the skill version that produced it.
- On mismatch, work continues and the mismatch goes under issues. The superior decides whether to update the assets; after checking them, update the PROJECT.md line.

## Migrating from 1.1

Skill 1.2 reads fragments only from `surfaces/<surface>/`; `check` warns when it finds the 1.1 layout. Migrate once, in one change:

1. Move `.e2e/actions/`, `.e2e/probes/`, `.e2e/helpers/` into `.e2e/surfaces/web/`.
2. Add `// @driver playwright` as the first line of every moved fragment in `actions/` and `probes/`; helpers need no declaration.
3. Move the web fields of `config/env.json` (`baseUrl`, `browser`, `session`) into `surfaces.web` with `"driver": "playwright"`; add `surfaces.api` when the project will use its API.
4. In scenarios and their `lib/`, change fragment references from `actions/…` and `probes/…` to `web:actions/…` and `web:probes/…`; generic probes become `web:probes/shot`, `web:probes/ui-lint`.
5. Create `data/`, `recipes/`, and, for an api surface, `surfaces/api/{actions,probes,helpers}/` with `helpers/auth.mjs`.
6. Update PROJECT.md: Surfaces and Test data sections, script tables per surface, and `Verified skill version: 1.2`.
7. Run `check` (no warnings, no mismatched fragments). Then rehearse one existing scenario with `--dry` to confirm the references resolve: set `dryAllow` to the login endpoint first, since 1.1 fragments do not read `P.dry`; the driver blocks their other writes, so failures after a blocked save are expected in the rehearsal.

## Initialization

Initialize only when an orchestrator dispatches the review in a standardized project and `.e2e/` is missing. Direct user invocations never initialize; they work ad-hoc in the execution workspace.

1. Run the review ad-hoc in the execution workspace; initialization does not block the review.
2. `init-proposal <round>` copies the skeleton into `<round>/init-proposal/.e2e/` with the current skill version filled in.
3. Fill the proposal from a read-only survey: which surfaces exist (screens, API), their base URLs and login, where routes, permissions, and endpoints are defined, the audit source, candidate test accounts. Remove the surfaces the project does not have. Leave writable data scope, passwords, and anything uncertain as pending confirmation. Never put passwords in the proposal.
4. List ad-hoc scripts from this round worth promoting.
5. Report that the project is not initialized, with the proposal path, in the conclusion and issues; set `init_needed` in the return block.
6. The superior approves, asking the user when it needs to. The worker does not ask the user directly.
7. On the next dispatch or explicit instruction: `init-apply <round> --approved-by=<who>` copies the proposal to `<project root>/.e2e/` (never overwrites), then move in approved promotions. The apply is recorded under writes. Committing is the superior's decision.
