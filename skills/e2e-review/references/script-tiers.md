# Script Tiers

Scripts accumulate with use, the way project decisions accumulate in manager documents. Three tiers coexist; pick or edit whichever fits the task.

| Tier | What | Typical use | Where |
| --- | --- | --- | --- |
| Ad-hoc | Short script or single driver command written on the spot | New features without scripts, debugging unstable behavior, exploring a screen | Round folder `scratch/`, `peek`, single driver commands |
| Fragment | One stable action or one stable observation | Log in and open a page, set a permission, read a menu, query an audit screen | `.e2e/actions/` (changes state), `.e2e/probes/` (read-only) |
| Scenario | A checklist block or full business flow, with comparisons coded in | A block of acceptance items; later, an application-to-approval flow | `.e2e/scenarios/`, shared pieces in `.e2e/scenarios/lib/` |

Generic, project-independent probes ship with the skill (`scripts/playwright/probes/`): `shot`, `ui-lint`, `contact-sheet`. Fragment lookup order is: explicit path, then `.e2e/`, then the skill.

## Promotion

| From → to | When | How |
| --- | --- | --- |
| Ad-hoc → fragment | The same steps are needed a second time; a step every task needs; a manual check repeated every round | Move it into `.e2e/actions/`, `.e2e/probes/`, or `.e2e/helpers/` |
| Fragment → scenario | A checklist item or flow must be rerun end to end | Write `.e2e/scenarios/<name>.mjs` with comparisons in code |
| Repetition inside scenarios | Two scenarios share a step sequence | Extract it into `.e2e/scenarios/lib/` |
| Project → skill | A fragment or helper turns out to be project-independent | Propose it to the skill owner; do not edit the skill during a task |

Update the script tables in `PROJECT.md` on every promotion, change, or deletion. They are the only script inventory.

## Demotion and repair

- A failing scenario: find the broken fragment and fix it there; do not patch around it in the scenario.
- A fragment unstable after a UI change: return to ad-hoc, re-learn the screen with `peek` and scratch scripts, then fix the fragment.
- Scripts for removed features or screens: delete them and their table rows.

## End-of-task inventory

Before closing a round, review `scratch/`. Promote what qualifies now. Leave the rest in the round folder; next time the same steps come up, look in earlier rounds first.

## Writing fragments

A fragment is one function expression; the driver composes it with injected values.

```js
// One-line purpose; arguments and return value.
async (page, P, H) => {
    await page.goto(`${P.env.baseUrl}/some/path`)
    await H.settle(page)
    return { landed: page.url() }
}
```

| Injected | Content |
| --- | --- |
| `P.env` | `.e2e/config/env.json` |
| `P.config` | Every JSON in `.e2e/config/` by file name, e.g. `P.config.routes` |
| `P.account`, `P.accountKey` | The account for `--account=<key>`; the password stays inside the call and is never logged |
| `P.out` | Absolute round folder path |
| `P.args` | Remaining `--key=value` arguments |
| `H.<name>` | Browser-side helpers: the skill's (`settle`, `uiLint`) plus every file in `.e2e/helpers/` |

Rules:

- Return JSON-serializable values. No `import`, `require`, or `URL` inside fragments; take everything from `P` and `H`.
- Locate elements by role and text, e.g. `getByRole('button', { name: 'Save' })`, not CSS classes.
- Reach pages by URL, not by clicking menus, unless the menu itself is under test.
- Keep login in a few fragments so a login change touches only them.
- Fragments that write must be safe to rerun: check the target state first, skip the write when already done, and say in the return value whether a write happened.
- Close leftover dialogs before clicking persistent controls such as a top bar.
- Call `H.settle(page)` before screenshots or layout checks.
- Take expected values from specs or data; when taken from current code, name the source file in the check note.
- When editing `.js` or `.mjs` files programmatically, use an editor tool for strings with escape sequences; shell heredoc replacements can turn `\n` into real newlines.

## Writing scenarios

A scenario exports one async function and imports nothing from the skill; shared project pieces come from `.e2e/scenarios/lib/` by relative import.

```js
export default async (ctx, opts) => {
    Object.assign(ctx.result.task, { title: '<block>', source: '<checklist text>', requester: '<superior>' })
    const res = await ctx.run('actions/login', { account: 'admin' }, 'login')
    ctx.check('12-1', '<check>', '<expected>', res.value?.user ?? null, res.ok ? res.value.user === 'admin' : null, ['values/login.json'])
    ctx.result.items = [{ id: '12', title: '<item>', checks: ['12-1'], humanWork: '' }]
    await ctx.run('probes/shot', { name: 'final' })
    return ctx.finish('<summary prefix>')
}
```

| `ctx` member | Use |
| --- | --- |
| `run(script, args, saveAs)` | Run a fragment through the driver; returns `{ ok, value, error }` |
| `check(id, title, expected, actual, pass, evidence, note)` | Record a coded check; `pass = null` when a prerequisite failed, attributed to `run-error` automatically |
| `manual(id, title, expected, by, note)` | Record a `not-run` or `visual` check |
| `addWrite(write)` | Record a data write; kept across reruns, duplicates skipped |
| `lint(where, { scope, shot })` | Run the UI lint probe and record findings as automatic UI findings |
| `lastStep()`, `inStep(time, step)`, `toMs(time)` | Match screen or audit timestamps to the step that produced them |
| `valueFile(name)`, `writeValue(name, value)` | Read or write `values/<name>.json` |
| `result` | The round's result object; set `task`, `items`, `limits` here |
| `finish(prefix)` | Compute the overall verdict and summary |

Use `lastStep()` time windows to match records, never "the latest row". Define `result.items` so the report can map checks to checklist items.
