# HTTP Driver

Driver name `http`, for API surfaces. It runs API fragments inside the Node process of `e2e.mjs` and calls the API with Node's built-in `fetch`; no third-party packages. All calls go through `scripts/drivers/http/driver.mjs`.

## Surface entry

```json
"api": { "driver": "http", "baseUrl": "http://localhost:8080/api" }
```

Paths in fragments are relative to `baseUrl`, e.g. `api.get('/orders/123')`.

## Fragments

An API fragment is an ES module in `.e2e/surfaces/<surface>/actions|probes/` (`.mjs`), with `// @driver http` in its first lines and a default export:

```js
// @driver http
// Read one order; returns status and the fields the checks need.
export default async (api, P, H) => {
    const res = await api.get(`/orders/${P.args.id}`)
    return { status: res.status, dueDate: res.body?.dueDate ?? null }
}
```

Unlike web fragments, API fragments may import other modules, e.g. builders from `.e2e/data/builders/`.

## The `api` client

| Member | Does |
| --- | --- |
| `get`, `post`, `put`, `patch`, `del` `(path, { body, query, headers })` | One call; returns `{ status, headers, body }` (body parsed as JSON when possible) |
| `request(method, path, opts)` | Same, with the method as a string |
| `as(accountKey)` | A client logged in as another account, e.g. the approver in a two-person flow |
| `record({ type, id, state, note })` | Add or update an entry with an id in the round's `data/manifest.json` |
| `dry` | True in a dry run |

Fragments also receive `H.account(key)`: a copy of another account's entry, for requests that carry its credentials (e.g. a password change). Its secret fields are redacted in every artifact like any account's, and accounts read this way or switched to with `as()` are listed in the report. `account` is a reserved helper name: a project helper `helpers/account.mjs` is ignored and `check` warns.

- The client is logged in as `--account=<key>`; without an account it sends no credentials.
- In a dry run no request is sent, not even the login: each call returns `{ status: 0, dry: true, request }` with the request it would have sent, and the exchange is still written to `dry/<name>/exchanges/`.
- A failed call is not retried. A write that fails is reported, not resent.

## Login

The project supplies login for each API surface in `.e2e/surfaces/<surface>/helpers/auth.mjs`:

```js
// Log in; cookies from responses are kept automatically. Return headers to add to later requests.
export default async (api, account, ctx) => {
    const res = await api.post('/auth/login', { body: { userId: account.userId, password: account.password } })
    if (res.status >= 400) throw new Error(`login failed for ${ctx.accountKey}: ${res.status}`)
    return {} // or { headers: { authorization: `Bearer ${res.body.token}` } }
}
```

- Login runs once per account key and command; a scenario reuses the session across its steps. Concurrent calls of one account wait for the same login, so none is sent without the session.
- Cookies set by the login response and returned headers are kept in memory only, registered for redaction, and never written to any artifact. Login exchanges keep only method, URL, status, and the key of the account being logged in (`login: true`); their request and response bodies are omitted, because a token in the response is not yet known as a secret when the exchange is written.
- Login logic lives only in `auth.mjs`, so a change of the login method touches one file.

## Logging

| Record | Content |
| --- | --- |
| `steps.jsonl` | One step per fragment run or `api` command, with surface, kind, driver |
| `exchanges/NNN-<label>-<METHOD>.json` | Every call: time, surface, account key, method, URL, status, request headers and body, response headers and body; redacted before truncation; bodies over 20,000 characters truncated with their length |
| `data/manifest.json` | Every successful or failed write call (POST, PUT, PATCH, DELETE) as an automatic event, except login calls; ids and states added with `record`, each as its own event |

## Request templates

- Record a template from the request the screen actually sends (see [playwright.md](playwright.md)), or take it from the project's published API contract; a project without screens relies on the contract alone. Do not construct requests for endpoints outside both, such as undocumented internal or admin endpoints.
- Store templates redacted in `.e2e/data/templates/` with the source screen or document and the date; build real requests with `.e2e/data/builders/`.
- When the backend changes a request shape, re-record the template instead of patching it by guess.

## Known pitfalls

- Dates and times: send them in the format the screen sends; the server may interpret zone-less times as server-local.
- A 401 in the middle of a scenario usually means the session expired; the driver does not log in again on its own. Sessions last for one command, so rerun the step as a new command.
- Ad-hoc `api` calls with a body take the body from a JSON file (`--body=<file>`), so it can be reviewed and promoted as a template.
