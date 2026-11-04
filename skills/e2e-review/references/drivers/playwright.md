# Playwright Driver

The current driver operates the browser through `playwright-cli`; see the `playwright-cli` skill for the raw command set. All driver calls go through `scripts/playwright/driver.mjs`.

## How fragments run

`run` composes the fragment with the injected `P` and `H` into one `async page => {}` function, writes it to a temporary file inside the execution workspace, runs `playwright-cli run-code --filename=<file>`, and deletes the file. The temporary file is the only place a password exists outside `accounts.local.json`, and only for the duration of the call.

Constraints of `run-code`:

- The code is a single function expression; no `import` or `require`, and `URL` is unavailable. Fragments take everything from `P` and `H`.
- Return values come back as JSON; keep them small and serializable.

## Browser-side helpers

| Helper | Purpose |
| --- | --- |
| `H.settle(page)` | Wait for network idle and running CSS animations before screenshots or layout checks |
| `H.uiLint(page, scope)` | Generic UI lint rules; see [../ui-checks.md](../ui-checks.md) |
| `.e2e/helpers/<name>.js` | Project helpers, injected as `H.<name>`; `uiLintExtra` is merged by the `ui-lint` probe |

## Generic probes

| Probe | Args | Returns |
| --- | --- | --- |
| `probes/shot` | `--name`, `--full=1` | Viewport screenshot (full page when asked) |
| `probes/ui-lint` | `--scope`, `--shot` | Lint findings from generic and project rules |
| `probes/contact-sheet` | called by `sheet` | Screenshots of the contact-sheet pages |

## Known pitfalls

- The first browser launch occasionally fails; `open` retries once.
- `playwright-cli` writes snapshots and console logs to `<cwd>/.playwright-cli/`. The tool sets the current directory to the execution workspace so these stay out of the project.
- Full-page screenshots of fixed layouts repeat the top bar and side menu mid-image. Judge layout from viewport screenshots.
- A screenshot taken right after a message appears catches the entry animation and looks clipped. Settle first.
- Leftover dialogs block persistent controls such as top-bar buttons. Close them before clicking.
- The browser keeps the last logged-in account between scenarios. Log in explicitly before checks that depend on permissions.
- Audit rows usually land about one second after the step that caused them; report attribution allows 1.5 s after a step ends.
- A dev server serves the working tree; uncommitted changes are part of the tested version, and `new` records the uncommitted file count.
