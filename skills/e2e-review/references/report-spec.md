# Report Spec

Every task produces one round folder with a report for the superior. The superior reviews it and decides what counts as done.

## Round folder

`<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/`

| Path | Required | Content |
| --- | --- | --- |
| `result.json` | Yes | Structured result; schema below |
| `report.md` | Yes | Rendered from `result.json` by `report` or `close` |
| `shots/` | With a web surface | Evidence screenshots, including `final.png` |
| `values/` | When used | Value evidence: page reads, API responses, query results, `audit.json`, `audit-side.json`; older files of a rerun as `<name>.<n>.json` |
| `exchanges/` | With an api surface | One file per API call: method, URL, status, account key (login calls name the account being logged in), redacted request and response (bodies over 20,000 characters truncated) |
| `data/manifest.json` | When data was written | Machine-readable record of data this round created or changed: `events` (every write in order: automatic entries for API write calls, entries from `api.record` and `ctx.addWrite`) and `latest` (one entry per type and id, fields merged in event order) |
| `dry/<name>/` | With `--dry` runs | Per scenario, fragment, recipe step, or `api`: steps (with blocked requests), values, exchanges, and result; never judged |
| `rehearse/<name>/` | With `run --rehearse` | Steps and values of real web operations cancelled before saving; never judged |
| `downloads/` | With `web:probes/download` | Downloaded files |
| `review/` | Optional | Visual review aids such as contact sheets; not evidence |
| `scratch/` | Optional | Ad-hoc scripts of this round, by surface (`scratch/web/`, `scratch/api/`); cite them as evidence when a check relies on one |
| `steps.jsonl` | Automatic | One line per step: start, end, surface, kind, driver, script, arguments, success; agent steps add evidence and note |
| `init-proposal/` | When needed | Proposed `.e2e/` for an uninitialized project |

The timestamp tells a returning superior whether the round ran before or after a fix; `r<NN>` is the round; `<short>` separates blocks in one parent.

## Round kinds

| Kind | Use | Report conclusion |
| --- | --- | --- |
| `review` | Verifying checklist items (default) | Verdict from the checks |
| `prep` | Preparing test data, no acceptance checks | "This round prepared data; no acceptance checks" |
| `init` | Initializing project assets | "This round initialized assets; no acceptance checks" |

`prep` and `init` rounds that record checks are judged like `review` rounds; the report states the round kind beside the verdict, and the return names it in `notes`. Without checks, `result.verdict` stays `inconclusive` and the return block says so, with no items and the round kind in `notes`; the superior reads the kind, not the verdict.

## Report sections

| Section | Required | Content |
| --- | --- | --- |
| Conclusion | Yes | Overall verdict and reason, failed checks, checks needing human verification, limits on passed checks, checks judged on agent steps; the round kind when it is not `review` |
| Checklist item map | With items | Suggested status per item, its checks, remaining human work; a title that repeats its item id is shown once |
| Comparison with previous round | With `--prev` | Status change per item |
| Task | Yes | Source text, requester, round, round kind, round basis; the scenarios that ran in the round and their verdicts when there are several |
| Environment | Yes | URL, surfaces with drivers and base URLs, data scope, account keys (from every step, the accounts a fragment switched to or read, and the API exchanges), browser, start time, tested versions, skill version and the version PROJECT.md was verified with |
| Checks | Yes | Expected, actual, verdict, source, verification route, evidence per check |
| Screenshots | With a web surface | Screenshots cited by checks, plus the final state |
| UI findings | Yes | Issues found beyond the checklist; "none" when empty |
| Writes | Yes | Data written, with time; API write calls from the manifest; "none, login entries only" for read-only tasks |
| Steps and audit trail | With logins or writes | Step timeline (surface, step kind) with the audit rows each step produced; script steps run while an agent step was open are shown nested under it |
| Audit rows during dry runs and rehearsals | When fetched | Rows in the dry-run and rehearsal window (`values/audit-side.json`) with the step they belong to; rows that clearly belong to a formal step run in between stay only in the formal section; rows with no step are kept and marked (an unlogged operation, another person on the same account), and uncertain ones are marked; never judged |
| `.e2e/` changes | When `report` or `close` ran | Versioned `.e2e/` files added, changed, deleted ("(deleted)"), or renamed ("<old path> → <new path>") since `new` (`result.assetsChanged`); a round started before `.e2e/` existed in a git project lists the whole new `.e2e/`; "cannot compare" without git |
| Value files kept from reruns | When any | Older value files of the same name |
| Check amendments | When any | Time, check, original verdict, fields before and after, reason, evidence links |
| Issues | Yes | Blockers, changed methods, assumptions, coverage gaps, version mismatch |
| Observations | Optional | Context that is not a UI finding |
| Reproduce | Yes | Commands in order, recorded automatically |

Labels follow the round's report language (`task.locale`, taken from the PROJECT.md line `Report language: <locale>` when the round is created; `zh-TW` or `en`, default `zh-TW`); stored values stay in English. Check counts are rendered by the report, not stored in the summary. Values of any shape render readably: objects, and objects inside arrays, as compact JSON.

## Verdicts

### Check verdict

| Value | Meaning |
| --- | --- |
| `pass` | Actual matches expected, with evidence |
| `fail` | Actual differs; `actual` states the difference |
| `inconclusive` | Not reached, element missing, evidence insufficient, environment missing, or tool error; a human must look |

### Overall verdict

- All checks pass: `pass`.
- Any check fails: `fail`.
- No failure but some inconclusive: `inconclusive`.
- Every scenario save and every `report` or `close` rewrites `verdict` and `stats` in `result.json` from all checks of the round; with no checks they are left as they are.

### Check source

| Value | Meaning | Confidence |
| --- | --- | --- |
| `script` | The comparison is coded in a scenario or scratch script | High |
| `value` | A script read the values; the agent compared them, or the superior must decide | Medium |
| `visual` | The agent judged from screenshots only | Low |
| `not-run` | Environment or condition unavailable, or the item is human-only | None |
| `run-error` | A tool or script error stopped the check | None |

- `visual`, `not-run`, and `run-error` checks are always `inconclusive`; `note` states the missing condition or the error.
- A check not reached because an earlier step failed is `inconclusive`, never `fail`.
- Check sources are the tool's internal classification, not the superior's acceptance rule.

### Verification route

`checks[].via` records how a check was verified, separate from the source:

| Value | Meaning |
| --- | --- |
| `web` | Observed on a web surface |
| `api` | Observed through an API surface |
| `db` | Read from the database |

- A checklist item about screen behavior that was verified only through `api` or `db` is a limit on that check, not a full pass; list it under `limits`.
- A rejection the screen blocks before sending a request says nothing about the server's rejection; when the item concerns server behavior (for example "rejected saves leave no record"), verify it through `api` as well.
- `checks[].agent` marks a judgment that rests on an agent-operated recipe step. Recipes are not yet an acceptance basis: the report lists these checks under the conclusion, and an item with such a check stays `needs-human` even when it passes.

### Conclusion wording

- Overall `pass`: "通過" with the summary and the check counts.
- Otherwise: "整體不算通過", the overall verdict in parentheses, and the reason, e.g. "2 checks inconclusive, need human verification".
- `prep` and `init` without checks: the round kind and "no acceptance checks"; with checks: the verdict as above, then the round kind.
- Below the conclusion: failed checks with the difference; inconclusive checks with the reason and the condition needed; limits on passed checks with when to re-verify.

### Checklist item status

The renderer derives a suggested status for each item in `result.items` from its checks, in this order:

| Status | Condition |
| --- | --- |
| `product-fail` | Any check failed |
| `run-error` | Any check is inconclusive with source `run-error` |
| `needs-human` | Any check is inconclusive for another reason, any check rests on an agent step, or the item has no checks |
| `verified-with-limits` | All checks pass and at least one appears in `limits` |
| `verified` | All checks pass with no limits |

Remaining human work combines the item's `humanWork`, the notes of non-passing checks, and the re-verification of limits.

### Comparison with the previous round

With `previousReport` set, each item shows the previous and current status and whether it improved, regressed, is new, or is unchanged.

## Evidence

- Prefer value evidence: text or numbers that can be compared, such as a menu item list, a field value, an API response, or a query result.
- Attach `shots/final.png` for every task that used a web surface, and a screenshot for every failed screen check.
- Cite the `exchanges/` file for checks that rest on an API response.
- When expected values come from a database, record the query and store the result in `values/`.
- Never put passwords in any artifact. Record account keys instead.

## Redaction

Every artifact the tool writes passes through value-based redaction (the recorded reproduce commands included, where a `--key` whose name looks secret is masked as well): every string field of each `accounts.local.json` entry except `userId` and `note` (the password, and any further secret such as a second password for a change test), and tokens and cookies obtained at login, are replaced with `<redacted>` wherever they appear; values under keys named like secrets (exactly `pass`, `pwd`, `jwt`, or `sid`, or names ending in password, passwd, secret, token, credential, cookie, authorization, apikey or api key, session id) are masked whole, while ordinary fields such as `passed` or `passDate` stay readable. Login exchanges omit their bodies. When quoting checklist text that contains a password, mask it yourself.

## UI findings

Record unreasonable UI behavior seen during the task; findings never affect verdicts. Categories, automatic rules, and the review method are in [ui-checks.md](ui-checks.md).

- Attach evidence to each finding; a screenshot first, the read value for wording issues.
- Describe the phenomenon and location only; no causes, no fixes.
- Skip behavior PROJECT.md lists as by design.

## Write traceability

For tasks with logins or writes, show which audit entries this task produced and which step produced each, including reruns.

- The round folder is the task identity. Reruns in the same round append to `steps.jsonl`; failed steps stay (with their error). Dry runs and rehearsals log under `dry/<name>/` and `rehearse/<name>/` and never mix in.
- Every write in `writes` carries a local time; writes from earlier runs in the same round are kept. API write calls also appear in `data/manifest.json`, whose `events` keep every intermediate state of a record (e.g. created, submitted, approved).
- `close` or `audit` with `--users`, `--actions` (action codes), or `--system` (rows the system wrote without a user) fetches audit rows through the project's adapter: the formal window into `values/audit.json`, and the window of dry runs and rehearsals into `values/audit-side.json`. Each window runs from the first step's start to the last step's end plus 1.5 s, the same allowance attribution uses. The two files never share a row and lose none: a row clearly owned by a dry-run or rehearsal step goes to the side file; every other row inside the formal window goes to the formal file; every row outside it goes to the side file. Login, logout, and query rows a dry run left are listed there, not judged. When `close` cannot fetch because the adapter fails, it adds one issue owned by `tool:audit` (the `tool:` prefix keeps tool notes apart from scenario-owned entries); a later failure replaces it, and a successful audit removes it.
- Attribution of each audit row, in order:
  1. A step that declared the row in `expects` (`[{ "object": "<target>", "action": "<code>" }]`; each value must equal the row's target or action, or its first word, so `<code>` matches `<code> <label>`) and whose window covers the row.
  2. Rows with millisecond times: the last step that started at or before the row; when that step ended more than 1.5 s earlier, an agent step still open at that time (its own operation after a nested script step).
  3. Rows cut to whole seconds by their source: the one step active in that second, script steps before agent steps; when several are active the row is marked as uncertain. Declare `expects` on short steps whose rows arrive with whole-second times.
  - A row more than 1.5 s after its step ended is listed as unattributed, with an explanation such as an unlogged ad-hoc command or another person using the same account. Scenarios use `ctx.ownerStep(time, row)` for the same rule.

## Reruns and corrections

| Entry | Source tag | On a rerun of the same scenario |
| --- | --- | --- |
| `checks`, `items`, `limits`, `issues`, `uiFindings`, `observations` recorded by a scenario | `src: <scenario name>` | Replaced by the rerun's entries, in the same place |
| The same fields added with `add` | `src: manual` (plain strings for `issues` and `observations`) | Kept |
| Entries of other scenarios in the round | their scenario | Kept |
| `writes` | — | Kept; duplicates (same what and time) skipped |
| Value files | — | Latest wins; older ones kept as `<name>.<n>.json` |

- When only the checking code was wrong, do not rerun a scenario that writes: write a scratch script in the round folder (`scratch/`) that reads the round's existing value files and recomputes the check without sending any request, save its output in `values/`, then record the correction with `amend`, citing the script and its output as evidence. The superior reviews each correction.
- `amend` changes fields of one check, marks it `amended`, and logs `{ at, check, original, before, after, reason, evidence }` under `amendments` (`original`: the verdict, source, and actual value before the correction). Reason and evidence are required. The report shows the original judgment beside the correction with its evidence. A later rerun replaces the check itself; the amendment log stays.
- In a formal scenario run, once a write step (a fragment under `actions/`) fails, later write steps are skipped (their `step` is marked `skipped`) and logged as issues. Checks recorded afterwards with `pass` null become `run-error`. A check with `pass` false becomes `run-error` too unless it is clearly unrelated to the skipped steps: it cites evidence, and every piece of it is a value file (`values/<save>.json`) written before the first write failed (then the failure stands). Evidence written after the failure (for example a probe that reads back what the skipped write should have created), a skipped step's value, or no evidence at all cannot be told apart: `run-error`. To keep a real failure visible, run and save the steps it rests on before the writes, and cite those files. Steps passed `{ always: true }`, such as restoring a system-wide setting the round changed under `data_write`, still run. Dry runs never skip.
- `ctx.addWrite` with missing `where` or `how` still records the write (missing fields shown as `—`) and adds an issue; it never stops the scenario.

## result.json

```json
{
  "task": { "title": "<title>", "source": "<checklist text>", "requester": "<superior>", "kind": "review", "locale": "zh-TW" },
  "round": 2,
  "previousReport": "<previous round folder>",
  "basis": "<fix this round verifies>",
  "verdict": "inconclusive",
  "summary": "<scenario's own words>",
  "stats": { "checks": 12, "failed": 0, "inconclusive": 2 },
  "env": {
    "url": "<web base url>",
    "surfaces": { "web": { "driver": "playwright", "baseUrl": "<url>" }, "api": { "driver": "http", "baseUrl": "<url>" } },
    "dataScope": "<test data scope>",
    "accounts": ["<account key>"],
    "browser": "<browser>",
    "startedAt": "2026-11-03T13:40:00.000",
    "versions": { "web": "abc1234 (+3 uncommitted)" },
    "skillVersion": "1.3",
    "projectVerifiedSkillVersion": "1.3",
    "assetsBaseline": { "<path relative to .e2e/>": "<content hash, or deleted>" }
  },
  "assetsChanged": ["surfaces/api/probes/<name>.mjs", "scenarios/<old>.mjs (deleted)"],
  "parts": { "<scenario name>": { "verdict": "pass", "summary": "<its words>", "stats": { "checks": 12, "failed": 0, "inconclusive": 2 }, "mode": "formal", "at": "<time>" } },
  "items": [{ "id": "12", "title": "<item>", "checks": ["12-1", "12-2"], "humanWork": "", "src": "<scenario name>" }],
  "checks": [{
    "id": "12-1", "title": "<check>", "expected": "<expected>", "actual": "<actual>",
    "verdict": "pass", "by": "script", "via": "web", "agent": false, "evidence": ["values/menu.json", "shots/menu.png"], "note": "", "src": "<scenario name>"
  }],
  "uiFindings": [{ "type": "display", "rule": "iso-datetime", "where": "<screen>", "what": "<phenomenon>", "samples": ["<value>"], "evidence": ["shots/x.png"], "auto": true }],
  "writes": [{ "what": "<write>", "where": "<table or screen>", "how": "<who, where>", "at": "2026-11-03T13:41:18.903" }],
  "limits": [{ "check": "12-2", "limit": "<restricted condition>", "retest": "<when and how to re-verify>" }],
  "issues": ["<text added with add>", { "text": "<text recorded by a scenario>", "src": "<scenario name>" }],
  "observations": [],
  "amendments": [{ "at": "<time>", "check": "12-1", "original": { "verdict": "pass", "by": "script", "actual": "<actual>" }, "before": { "verdict": "pass" }, "after": { "verdict": "fail", "by": "value" }, "reason": "<why>", "evidence": ["scratch/api/recheck-12.mjs", "values/recheck-12.json"] }],
  "reproduce": ["node <skill>/scripts/e2e.mjs scenario scenarios/<name>"]
}
```

Shapes `add` and `ctx.addWrite` enforce (a wrong shape is refused with the missing fields):

| Field | Required |
| --- | --- |
| `items` | `id`, `title`, `checks` (array of check ids) |
| `checks` | `id`, `title`, `verdict`, `by`, and `via` when given |
| `uiFindings` | `type`, `where`, `what` or `rule` |
| `writes` | `what`, `where`, `how` (`at` optional, local time) |
| `limits` | `check`, `limit`, `retest` |
| `issues`, `observations` | Non-empty text |

| Field | Values |
| --- | --- |
| `task.kind` | `review`, `prep`, `init` |
| `verdict`, `checks[].verdict` | `pass`, `fail`, `inconclusive` |
| `checks[].by` | `script`, `value`, `visual`, `not-run`, `run-error` |
| `checks[].via` | `web`, `api`, `db`, or null |
| `uiFindings[].type` | `operation`, `layout`, `wording`, `display`, `error`; `auto` marks automatic findings, `scenario` findings a scenario added |
| `items[]` | Item id, title, check ids, remaining human work; status is derived; a title need not repeat the id |
| `src` | Scenario name, `manual` for `add` (plain strings from `add` carry none), or `tool:<name>` for entries the tool adds itself (e.g. `tool:audit`) |
| steps `kind` | `script` (promoted or generic fragment), `adhoc` (scratch script or `api` call), `agent` (recipe step logged with `log`) |
