# Playwright Driver

Driver name `playwright`, for web surfaces. It operates the browser through `playwright-cli`; see the `playwright-cli` skill for the raw command set. All driver calls go through `scripts/drivers/playwright/driver.mjs`.

## Surface entry

```json
"web": { "driver": "playwright", "baseUrl": "http://localhost:5173/app", "browser": "msedge", "session": "app", "dryAllow": ["/auth/login"] }
```

`dryAllow` lists URL fragments whose write requests may pass during a dry run, typically the login endpoint; see "Dry runs".

Fragments live in `.e2e/surfaces/<surface>/` as `.js` files with `// @driver playwright` within their first five lines, and are referenced as `<surface>:<path>`, e.g. `web:actions/login`.

## How fragments run

`run` composes the fragment with the injected `P` and `H` into one `async page => {}` function, writes it to a temporary file inside the execution workspace, runs `playwright-cli run-code --filename=<file>`, and deletes the file. The temporary file is the only place a password exists outside `accounts.local.json`, and only for the duration of the call; files left by a killed run are deleted before the next call.

Constraints of `run-code`:

- The code is a single function expression; no `import` or `require`, and `URL` is unavailable. Fragments take everything from `P` and `H`.
- Return values come back as JSON; keep them small and serializable.
- There is no timeout around the call itself. A wait that never resolves blocks the command until it is stopped from outside, and the step is not logged. Give every wait and locator action an explicit `timeout`.

## Dry runs

With `--dry`, the composed function first routes every request through a guard: `POST`, `PUT`, `PATCH`, and `DELETE` requests are aborted unless their URL contains a `dryAllow` entry, and the guard is removed when the fragment ends. The fragment's value is returned unchanged; the aborted requests are recorded in the step's `blockedWrites` under `dry/steps.jsonl`. A fragment that ignores `P.dry` therefore cannot save, but it may fail where it expected a save to succeed; read such failures as expected in a rehearsal.

## Browser-side helpers

| Helper | Purpose |
| --- | --- |
| `H.settle(page)` | Wait for network idle and running CSS animations before screenshots or layout checks |
| `H.uiLint(page, scope)` | Generic UI lint rules; see [../ui-checks.md](../ui-checks.md) |
| `.e2e/surfaces/<surface>/helpers/<name>.js` | Project helpers, injected as `H.<name>`; `uiLintExtra` is merged by the `ui-lint` probe |

## Generic probes

| Probe | Args | Returns |
| --- | --- | --- |
| `web:probes/shot` | `--name`, `--full=1` | Viewport screenshot (full page when asked) |
| `web:probes/ui-lint` | `--scope`, `--shot` | Lint findings from generic and project rules |
| `web:probes/contact-sheet` | called by `sheet` | Screenshots of the contact-sheet pages |

Use the project's web surface name in place of `web` when it differs.

## Known pitfalls

- The first browser launch occasionally fails; `open` retries once.
- `playwright-cli` writes snapshots and console logs to `<cwd>/.playwright-cli/`. The tool sets the current directory to the execution workspace so these stay out of the project.
- Full-page screenshots of fixed layouts repeat the top bar and side menu mid-image. Judge layout from viewport screenshots.
- A screenshot taken right after a message appears catches the entry animation and looks clipped. Settle first.
- Leftover dialogs block persistent controls such as top-bar buttons. Close them before clicking.
- Reading text from an element that does not exist waits for the full action timeout without an error; check `count()` first or pass a short timeout.
- The browser keeps the last logged-in account between scenarios. Log in explicitly before checks that depend on permissions.
- Audit rows usually land about one second after the step that caused them; report attribution allows 1.5 s after a step ends.
- A dev server serves the working tree; uncommitted changes are part of the tested version, and `new` records the uncommitted file count.
- Capturing a request template: intercept the screen's request with `page.on('request')` or `page.waitForRequest` in a scratch fragment, save the body to `values/`, then redact it into `.e2e/data/templates/`.
