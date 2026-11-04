# Playwright Driver

Driver name `playwright`, for web surfaces. It operates the browser through `playwright-cli`; see the `playwright-cli` skill for the raw command set. All driver calls go through `scripts/drivers/playwright/driver.mjs`.

## Surface entry

```json
"web": { "driver": "playwright", "baseUrl": "http://localhost:5173/app", "browser": "msedge", "session": "app", "dryAllow": ["/auth/login", "/auth/logout"], "dryBlock": ["/reports/export"] }
```

`dryAllow` lists URL path fragments whose write requests must pass during a dry run: at least login and logout, also read-only queries sent as POST. `dryBlock` lists path fragments blocked during a dry run whatever the method, for requests with side effects such as a GET export that writes an audit row. See "Dry runs".

Fragments live in `.e2e/surfaces/<surface>/` as `.js` files with `// @driver playwright` within their first five lines, and are referenced as `<surface>:<path>`, e.g. `web:actions/login`.

## How fragments run

`run` composes the fragment with the injected `P` and `H` into one `async page => {}` function, writes it to a temporary file inside the execution workspace, runs `playwright-cli run-code --filename=<file>`, and deletes the file. The temporary file is the only place a password exists outside `accounts.local.json`, and only for the duration of the call; files left by a killed run are deleted before the next call.

Constraints of `run-code`:

- The code is a single function expression; no `import` or `require`, and `URL` is unavailable. Fragments take everything from `P` and `H`.
- Return values come back as JSON; keep them small and serializable.
- There is no timeout around the call itself. A wait that never resolves blocks the command until it is stopped from outside, and the step is not logged. Give every wait and locator action an explicit `timeout`.

## Dry runs

With `--dry`, the composed function first routes every request through a guard, matching on the URL path without query string or fragment: any request whose path contains a `dryBlock` entry is aborted; `POST`, `PUT`, `PATCH`, and `DELETE` requests are aborted unless their path contains a `dryAllow` entry. The guard is removed when the fragment ends. The fragment's value is returned unchanged; the aborted requests are recorded in the step's `blockedWrites` under `dry/<name>/steps.jsonl`, together with requests the fragment skipped itself and reported with `H.reportBlocked`. A fragment that ignores `P.dry` therefore cannot save, but it may fail where it expected a save to succeed; read such failures as expected in a dry run.

Logging in and out during a dry run is normal; allow both in `dryAllow`. Never clear the browser session (cookies, storage, or the profile) in place of a logout.

## Rehearsals

`run <fragment> --rehearse` operates for real, without the guard, for an interaction that will be cancelled before anything is saved (open a dialog, read it, cancel). It must not save anything: a save during a rehearsal is a real write that never reaches the round's writes. Only web surfaces accept it. It logs under `rehearse/<name>/` and never enters the step table or the verdict; its audit rows are listed with the dry-run rows.

## Browser-side helpers

| Helper | Purpose |
| --- | --- |
| `H.settle(page)` | Wait for network idle and running CSS animations before screenshots or layout checks |
| `H.uiLint(page, scope)` | Generic UI lint rules; see [../ui-checks.md](../ui-checks.md) |
| `H.reportBlocked(what)` | Add a request the fragment skipped itself (honoring `P.dry`) to the step's blocked requests |
| `.e2e/surfaces/<surface>/helpers/<name>.js` | Project helpers, injected as `H.<name>`; `uiLintExtra` is merged by the `ui-lint` probe |

## Generic probes

| Probe | Args | Returns |
| --- | --- | --- |
| `web:probes/shot` | `--name`, `--full=1` | Viewport screenshot (full page when asked) |
| `web:probes/ui-lint` | `--scope`, `--shot` | Lint findings from generic and project rules |
| `web:probes/contact-sheet` | called by `sheet` | Screenshots of the contact-sheet pages |
| `web:probes/download` | `--button=<name>` or `--link=<text>`, `--name`, `--timeout` | Clicks the control, saves the download to `downloads/`; returns the file, suggested name, and URL. Read its content with a project tool (tools.md "Reading downloaded files"); add the download path to `dryBlock` if fetching it writes an audit row |

Use the project's web surface name in place of `web` when it differs.

## Known pitfalls

- The first browser launch occasionally fails; `open` retries once.
- A `beforeunload` dialog (a page with unsaved input being left) interrupts the fragment. The driver accepts it, so the session is not trapped on that page, and fails the step; the unsaved input on that page is lost, nothing is saved. Other dialogs left open fail the step with a message; handle them with `playwright-cli -s=<session> dialog-accept` or `dialog-dismiss`, or register a dialog handler in the fragment.
- `playwright-cli` writes snapshots and console logs to `<cwd>/.playwright-cli/`. The tool sets the current directory to the execution workspace so these stay out of the project.
- Full-page screenshots of fixed layouts repeat the top bar and side menu mid-image. Judge layout from viewport screenshots.
- A screenshot taken right after a message appears catches the entry animation and looks clipped. Settle first.
- Leftover dialogs block persistent controls such as top-bar buttons. Close them before clicking.
- Reading text from an element that does not exist waits for the full action timeout without an error; check `count()` first or pass a short timeout.
- The browser keeps the last logged-in account between scenarios. Log in explicitly before checks that depend on permissions.
- Audit rows usually land about one second after the step that caused them; report attribution allows 1.5 s after a step ends. Rows stored with whole-second times can be ambiguous between short steps; declare `--expects` (or `opts.expects`) on such steps.
- A dev server serves the working tree; uncommitted changes are part of the tested version, and `new` records the uncommitted file count.
- Capturing a request template: intercept the screen's request with `page.on('request')` or `page.waitForRequest` in a scratch fragment, save the body to `values/`, then redact it into `.e2e/data/templates/`.
