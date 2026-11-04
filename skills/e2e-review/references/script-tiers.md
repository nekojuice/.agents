# Script Tiers

Scripts accumulate with use, the way project decisions accumulate in manager documents. Three tiers coexist, plus recipes for flows that still need an agent's hands; pick or edit whichever fits the task.

| Tier | What | Typical use | Where |
| --- | --- | --- | --- |
| Ad-hoc | Short script, single driver command, or single API call written on the spot | New features without scripts, debugging unstable behavior, exploring a screen or an endpoint | Round folder `scratch/<surface>/`, `peek`, `api`, single browser commands |
| Fragment | One stable action or one stable observation on one surface | Log in and open a page, set a permission, read a menu, create a record through the API | `.e2e/surfaces/<surface>/actions/` (changes state), `.e2e/surfaces/<surface>/probes/` (read-only) |
| Scenario | A checklist block or full business flow, every step scripted, comparisons coded in | A block of acceptance items; an application-to-approval flow; API setup followed by screen checks | `.e2e/scenarios/`, shared pieces in `.e2e/scenarios/lib/` |
| Recipe | A solidified flow that still contains agent-operated steps, mixed with script steps; not yet an acceptance basis | Preparing data or state with a tool the scripts cannot drive yet, then handing over to scripts | `.e2e/recipes/`; see [recipes.md](recipes.md) |

Generic, project-independent probes ship with each driver (`scripts/drivers/<driver>/probes/`); the playwright driver has `shot`, `ui-lint`, `contact-sheet`, `download`.

## Surfaces

- A fragment belongs to one surface. Surfaces are registered in `.e2e/config/env.json` under `surfaces`, each with the driver that operates it; see [project-profile.md](project-profile.md).
- Refer to fragments as `<surface>:<path>`, e.g. `web:actions/login`, `api:actions/case-create`. Without a prefix the default surface applies (`env.defaultSurface`, else `web`, else the first registered).
- Lookup order: an explicit file path, then `.e2e/surfaces/<surface>/<path>`, then the skill's `scripts/drivers/<driver>/<path>`.
- Every fragment declares its driver in a comment within its first five lines: `// @driver playwright` or `// @driver http`. A fragment whose declaration does not match its surface's driver refuses to run; `check` counts undeclared and mismatched fragments.
- Scenarios and recipes may cross surfaces, e.g. create data through `api:` and verify it on `web:`.

## Promotion

| From → to | When | How |
| --- | --- | --- |
| Ad-hoc → fragment | The same steps are needed a second time; a step every task needs; a manual check repeated every round | Move it into `.e2e/surfaces/<surface>/actions|probes|helpers/` with a driver declaration |
| Ad-hoc request → template | A request body worked and will be needed again | Save it, redacted, in `.e2e/data/templates/` with its source and date |
| Ad-hoc → recipe | An agent-operated sequence will be repeated but cannot be scripted yet | Write `.e2e/recipes/<name>.md` |
| Recipe → scenario | Every step of the recipe is a script step | Rewrite it as `.e2e/scenarios/<name>.mjs` and delete the recipe |
| Fragment → scenario | A checklist item or flow must be rerun end to end | Write `.e2e/scenarios/<name>.mjs` with comparisons in code |
| Repetition inside scenarios | Two scenarios share a step sequence | Extract it into `.e2e/scenarios/lib/` |
| Project → skill | A fragment or helper turns out to be project-independent | Propose it to the skill owner; do not edit the skill during a task |

Update the script tables in `PROJECT.md` on every promotion, change, or deletion. They are the only script inventory.

## Test data

Test data the review creates through the system's API (or screens) is designed, not improvised.

| Folder | Holds | Rules |
| --- | --- | --- |
| `.e2e/data/templates/` | Request bodies | Recorded from a real screen request (capture it on the web surface) or taken from the project's published API contract; redacted; note the source screen or document and the date |
| `.e2e/data/builders/` | Functions that turn a template plus parameters (dates, codes) into a request | Pure functions; no network calls |
| `.e2e/data/sets/` | Named data sets: which records to build, with which parameters | One file per purpose, e.g. the records a due-date list needs |

- What a round actually creates or changes is recorded in the round's `data/manifest.json`. API write calls are recorded automatically; fragments add record ids with `api.record`, scenarios with `ctx.addWrite`. Every call adds an event, so intermediate states (created, submitted, approved, a setting changed and restored) stay visible; `latest` gives the last state per record.
- Records that later rounds will reuse are registered in `.e2e/state/data-<env>.json` (not committed), where `<env>` is `env.json` `name`, else `dataScope`. Read it before creating data; reuse instead of duplicating.
- Test data rules (identifiable test data, new records instead of changing existing ones, the exception for system-wide settings): SKILL.md "Boundaries". Here: name created records with the project's test prefix from PROJECT.md, record ids in the manifest, and register reusable records in the environment registry.

## Demotion and repair

- A failing scenario: find the broken fragment and fix it there; do not patch around it in the scenario.
- A fragment unstable after a UI or API change: return to ad-hoc, re-learn the screen with `peek` or the endpoint with `api`, then fix the fragment.
- Scripts for removed features or screens: delete them and their table rows.

## End-of-task inventory

Before closing a round, review `scratch/`. Promote what qualifies now. Leave the rest in the round folder; next time the same steps come up, look in earlier rounds first.

## Writing fragments

Rules for every driver:

- Return JSON-serializable values.
- Fragments that write must be safe to rerun: check the target state first, skip the write when already done, and say in the return value whether a write happened.
- Fragments that write honor `P.dry`: build the request or fill the form, but do not send or save; return what would have been sent. As a safety net the http driver sends nothing in a dry run, and the playwright driver blocks write requests (see the driver references); a fragment must not rely on that net alone. A web fragment that skips a request itself reports it with `H.reportBlocked('<method> <path>')`, so it appears with the step's blocked requests.
- Read the dry-run flag from `P.dry`; do not add an argument of your own for it (`dry` is reserved).
- Take expected values from specs or data; when taken from current code, name the source file in the check note.
- Keep login in one place per surface so a login change touches only it.
- Edit `.js`, `.mjs`, and `.py` files with an editor tool. Shell or script string replacements corrupt escape sequences such as `\n` and regex backslashes.
- Never pass passwords or tokens as arguments; take them from `P.account` inside the call. An API fragment that needs another account's credentials (e.g. the old and new password of a change request) takes them from `H.account('<key>')`; never read `accounts.local.json` yourself.

### Web fragments (`playwright`)

A web fragment is one function expression; the driver composes it with injected values and runs it in the browser.

```js
// @driver playwright
// One-line purpose; arguments and return value.
async (page, P, H) => {
    await page.goto(`${P.surfaceConfig.baseUrl}/some/path`)
    await H.settle(page)
    return { landed: page.url() }
}
```

- No `import`, `require`, or `URL` inside web fragments; take everything from `P` and `H`.
- Locate elements by role and text, e.g. `getByRole('button', { name: 'Save' })`, not CSS classes.
- Reach pages by URL, not by clicking menus, unless the menu itself is under test.
- Close leftover dialogs before clicking persistent controls such as a top bar.
- Call `H.settle(page)` before screenshots or layout checks. Give waits an explicit timeout.

### API fragments (`http`)

An API fragment is an ES module run inside Node; see [drivers/http.md](drivers/http.md) for the client.

```js
// @driver http
// Create one record from a template; returns the status and the new id.
import build from '../../../data/builders/order.mjs'

export default async (api, P, H) => {
    const res = await api.post('/orders', { body: build(P.args) })
    if (res.status === 201) api.record({ type: 'order', id: res.body.id, state: 'created' })
    return { status: res.status, id: res.body?.id ?? null, dry: P.dry }
}
```

Ad-hoc API scripts in `scratch/api/` are run with the surface prefix, e.g. `run api:<round>/scratch/api/try-create.mjs`; without it the default surface (usually web) applies and the driver declaration does not match.

### Injected values

| Injected | Content |
| --- | --- |
| `P.env` | `.e2e/config/env.json` |
| `P.surface`, `P.surfaceConfig` | The surface name and its entry in `env.surfaces` |
| `P.config` | Every JSON in `.e2e/config/` by file name, e.g. `P.config.routes` |
| `P.account`, `P.accountKey` | The account for `--account=<key>`; the password stays inside the call and is never logged |
| `P.out` | Absolute folder the step writes to: the round folder, `<round>/dry/<name>/` in a dry run, or `<round>/rehearse/<name>/` in a rehearsal |
| `P.args` | Remaining `--key=value` arguments; JSON objects and arrays arrive as objects |
| `P.dry` | True in a dry run |
| `H.<name>` | Helpers: the driver's own plus every file in `.e2e/surfaces/<surface>/helpers/` (browser-side for web, Node modules for api) |
| `H.account(key)` | API fragments only: a copy of another account's entry; its secret fields are redacted wherever they appear, and the account is listed in the report. `account` is a reserved helper name: a project helper of that name is ignored (`check` warns) |
| `H.reportBlocked(what)` | Web fragments only: add a request the fragment skipped to the step's blocked requests |

## Writing scenarios

A scenario exports one async function and imports nothing from the skill; shared project pieces come from `.e2e/scenarios/lib/` by relative import.

```js
export default async (ctx, opts) => {
    Object.assign(ctx.result.task, { title: '<block>', source: '<checklist text>', requester: '<superior>' })
    const made = await ctx.run('api:actions/order-create', { account: 'clerk', code: 'E2E-01' }, 'order', { expects: [{ action: '<action code>' }] })
    const res = await ctx.run('web:probes/order-detail', { account: 'approver', id: made.value?.id }, 'detail')
    ctx.check('12-1', '<check>', '<expected>', res.value?.title ?? null, res.ok ? res.value.title === '<expected>' : null, ['values/detail.json'], '', { via: 'web' })
    ctx.result.items = [{ id: '12', title: '<item>', checks: ['12-1'], humanWork: '' }]
    await ctx.run('web:probes/shot', { name: 'final' })
    return ctx.finish('<summary>')
}
```

| `ctx` member | Use |
| --- | --- |
| `run(ref, args, saveAs, opts)` | Run a fragment through its surface's driver; returns `{ ok, value, error, step }` where `step` has `startedAt`, `endedAt`, `surface`. In a formal run, after a write step (`actions/`) failed, later write steps are skipped and return `{ ok: false, skipped: true }` with a `step` marked `skipped`; `opts.always: true` runs a step anyway (restoring a changed setting must). `opts.expects`: the audit rows the step produces, `[{ object, action }]`, for attribution |
| `check(id, title, expected, actual, pass, evidence, note, opts)` | Record a coded check; `pass = null` when a prerequisite failed, attributed to `run-error` automatically, as is `pass = false` after a skipped write step unless the check is clearly unrelated to it (report-spec "Reruns and corrections"). `opts.via`: `web`, `api`, `db`; `opts.by` overrides the source (e.g. `value` for a read value awaiting the superior's decision); `opts.agent`: the judgment rests on an agent step |
| `manual(id, title, expected, by, note, evidence, opts)` | Record a `not-run` or `visual` check |
| `addWrite(write)` | Record a data write (`what`, `where`, `how`); kept across reruns, duplicates skipped, times converted to local, mirrored into `data/manifest.json`. Missing fields are recorded as `—` with an issue |
| `finding(f)` | Record a UI finding from the scenario; replaced on rerun |
| `lint(where, { scope, shot })` | Run the web UI lint probe and record findings as automatic UI findings |
| `ownerStep(time, row)` | The step a screen or audit timestamp belongs to, by the same rule the report uses; pass the audit row to use step `expects` |
| `same(a, b)` | Deep equality that ignores object key order (arrays keep order); compare objects with it, never as JSON strings |
| `lastStep()`, `inStep(time, step)`, `toMs(time)`, `toLocal(time)` | Lower-level time helpers |
| `valueFile(name)`, `writeValue(name, value)` | Read or write `values/<name>.json` (redacted; an older file of the same name is kept). A dry run uses its own folder |
| `name`, `dry` | The scenario name (its file name; its side folders use the same name with spaces and file-system characters replaced); true with `--dry` (results go to `<round>/dry/<name>/`) |
| `result` | This scenario's view of the round: set `task`, `items`, `limits` here. It starts without entries of its own; entries of other scenarios and manual additions are kept when it saves |
| `finish(summary)` | Compute this scenario's verdict; the round's verdict follows all checks, and the report renders the counts |

Use `ownerStep` or `step` time windows to match records, never "the latest row". Define `result.items` so the report can map checks to checklist items; item titles need not repeat the id. A scenario that writes runs once with `--dry` first, then once for real; save the values its checks rest on, so a wrong check can later be recomputed from them by a scratch script and corrected with `amend`.
