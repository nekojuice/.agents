# Project Profile

Each project keeps its review knowledge in `<project root>/.e2e/`. The skill stays project-free; the project folder accumulates environment facts, accounts, scripts, and pitfalls.

## Layout

```
<project root>/.e2e/
├── PROJECT.md                     # read first on every task
├── config/
│   ├── env.json                   # baseUrl, dataScope, browser, session, repos, project query endpoints
│   ├── <name>.json                # any other project config, injected as P.config.<name>
│   ├── accounts.local.json        # account keys → { userId, password, note }; local only
│   └── accounts.local.example.json
├── actions/                       # fragments that change state
├── probes/                        # read-only fragments
├── scenarios/                     # solidified scenarios
│   └── lib/                       # pieces shared by scenarios
├── helpers/                       # project browser-side helpers, e.g. uiLintExtra.js
├── audit/fetch.mjs                # audit adapter
├── state/                         # current-task pointers per session (ignored)
├── out/                           # default report parent for direct user runs (ignored)
└── .gitignore                     # config/accounts.local.json, state/, out/
```

| Path | Version control |
| --- | --- |
| PROJECT.md, config (except accounts.local.json), actions, probes, scenarios, helpers, audit | Committed by the superior; the worker never commits |
| config/accounts.local.json | Never, unless the user explicitly allows it for a closed internal test environment |
| state/, out/ | Never |
| Any `e2e-review/` execution workspace | Never; the folder carries its own `.gitignore` with `*` |

Execution artifacts (reports, screenshots, values, scratch scripts, step logs) never enter `.e2e/`. Only promoted scripts and project facts do.

## PROJECT.md

Keep these sections current; the template is in `assets/e2e-skeleton/PROJECT.md`.

| Section | Content |
| --- | --- |
| Verified skill version | `Verified skill version: <x.y>`; the skill version the assets were last checked against |
| System under test | Site, checklist source, where routes and permissions are defined, how to read the tested version |
| Operating limits | Test environment only, browser, writable data, untouchable data, external services, pending confirmations |
| Accounts | Key, user, role, purpose; never passwords |
| Audit trail | Source, adapter, action codes |
| Scripts | Tables of actions, probes, scenarios, scenario lib pieces |
| Known pitfalls | Behavior that looks wrong but is by design, flaky spots, workarounds |

Write project knowledge learned during a task (new pitfalls, new scripts) back into PROJECT.md. Generic lessons go to the skill owner instead.

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

## Initialization

Initialize only when an orchestrator dispatches the review in a standardized project and `.e2e/` is missing. Direct user invocations never initialize; they work ad-hoc in the execution workspace.

1. Run the review ad-hoc in the execution workspace; initialization does not block the review.
2. `init-proposal <round>` copies the skeleton into `<round>/init-proposal/.e2e/` with the current skill version filled in.
3. Fill the proposal from a read-only survey: site URL, where routes and permissions are defined, the audit source, candidate test accounts. Leave writable data scope, passwords, and anything uncertain as pending confirmation. Never put passwords in the proposal.
4. List ad-hoc scripts from this round worth promoting.
5. Report that the project is not initialized, with the proposal path, in the conclusion and issues; set `init_needed` in the return block.
6. The superior approves, asking the user when it needs to. The worker does not ask the user directly.
7. On the next dispatch or explicit instruction: `init-apply <round> --approved-by=<who>` copies the proposal to `<project root>/.e2e/` (never overwrites), then move in approved promotions. The apply is recorded under writes. Committing is the superior's decision.
