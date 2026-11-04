# Report Spec

Every task produces one round folder with a report for the superior. The superior reviews it and decides what counts as done.

## Round folder

`<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/`

| Path | Required | Content |
| --- | --- | --- |
| `result.json` | Yes | Structured result; schema below |
| `report.md` | Yes | Rendered from `result.json` by `report` or `close` |
| `shots/` | With a web surface | Evidence screenshots, including `final.png` |
| `values/` | When used | Value evidence: page reads, API responses, query results, `audit.json` |
| `exchanges/` | With an api surface | One file per API call: method, URL, status, redacted request and response (bodies over 20,000 characters truncated) |
| `data/manifest.json` | When data was written | Machine-readable record of data this round created or changed: automatic entries for API write calls, entries with ids from `api.record` and `ctx.addWrite` |
| `dry/` | With `--dry` runs | Steps (with write requests the web driver blocked), values, exchanges, and result of rehearsals; never in the report |
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

`prep` and `init` rounds that record checks anyway are judged like `review` rounds. Without checks, `result.verdict` stays `inconclusive` and the return block says so, with no items and the round kind in `notes`; the superior reads the kind, not the verdict.

## Report sections

| Section | Required | Content |
| --- | --- | --- |
| Conclusion | Yes | Overall verdict and reason, failed checks, checks needing human verification, limits on passed checks, checks judged on agent steps |
| Checklist item map | With items | Suggested status per item, its checks, remaining human work |
| Comparison with previous round | With `--prev` | Status change per item |
| Task | Yes | Source text, requester, round, round kind, round basis |
| Environment | Yes | URL, surfaces with drivers and base URLs, data scope, account keys, browser, start time, tested versions, skill version and the version PROJECT.md was verified with |
| Checks | Yes | Expected, actual, verdict, source, verification route, evidence per check |
| Screenshots | With a web surface | Screenshots cited by checks, plus the final state |
| UI findings | Yes | Issues found beyond the checklist; "none" when empty |
| Writes | Yes | Data written, with time; API write calls from the manifest; "none, login entries only" for read-only tasks |
| Steps and audit trail | With logins or writes | Step timeline (surface, step kind) with the audit rows each step produced |
| Issues | Yes | Blockers, changed methods, assumptions, coverage gaps, version mismatch |
| Observations | Optional | Context that is not a UI finding |
| Reproduce | Yes | Commands in order |

The renderer currently writes headings in Traditional Chinese; stored values stay in English. Check counts are rendered by the report, not stored in the summary.

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
- `prep` and `init` without checks: the round kind and "no acceptance checks".
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

Every artifact the tool writes passes through value-based redaction: the passwords in `accounts.local.json`, and tokens and cookies obtained at login, are replaced with `<redacted>` wherever they appear; values under keys named like secrets (`password`, `pass`, `pwd`, `jwt`, or names ending in password, secret, token, credential, cookie, authorization, api key, session id) are masked whole, while ordinary fields such as `passed` or `passDate` stay readable. Login exchanges omit their bodies. When quoting checklist text that contains a password, mask it yourself.

## UI findings

Record unreasonable UI behavior seen during the task; findings never affect verdicts. Categories, automatic rules, and the review method are in [ui-checks.md](ui-checks.md).

- Attach evidence to each finding; a screenshot first, the read value for wording issues.
- Describe the phenomenon and location only; no causes, no fixes.
- Skip behavior PROJECT.md lists as by design.

## Write traceability

For tasks with logins or writes, show which audit entries this task produced and which step produced each, including reruns.

- The round folder is the task identity. Reruns in the same round append to `steps.jsonl`; failed steps stay. Dry runs log under `dry/` and never mix in.
- Every write in `writes` carries a local time; writes from earlier runs in the same round are kept. API write calls also appear in `data/manifest.json`.
- `close --users` or `audit --users` fetches audit rows for the task window through the project's adapter into `values/audit.json`.
- Each audit row goes to the last step that started before it; rows more than 1.5 s after that step ended are listed as unattributed, with an explanation such as an unlogged ad-hoc command or another person using the same account. Scenarios use `ctx.ownerStep` for the same rule.

## result.json

```json
{
  "task": { "title": "<title>", "source": "<checklist text>", "requester": "<superior>", "kind": "review" },
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
    "skillVersion": "1.2",
    "projectVerifiedSkillVersion": "1.2"
  },
  "items": [{ "id": "12", "title": "<item>", "checks": ["12-1", "12-2"], "humanWork": "" }],
  "checks": [{
    "id": "12-1", "title": "<check>", "expected": "<expected>", "actual": "<actual>",
    "verdict": "pass", "by": "script", "via": "web", "agent": false, "evidence": ["values/menu.json", "shots/menu.png"], "note": ""
  }],
  "uiFindings": [{ "type": "display", "rule": "iso-datetime", "where": "<screen>", "what": "<phenomenon>", "samples": ["<value>"], "evidence": ["shots/x.png"], "auto": true }],
  "writes": [{ "what": "<write>", "where": "<table or screen>", "how": "<who, where>", "at": "2026-11-03T13:41:18.903" }],
  "limits": [{ "check": "12-2", "limit": "<restricted condition>", "retest": "<when and how to re-verify>" }],
  "issues": [],
  "observations": [],
  "reproduce": ["node <skill>/scripts/e2e.mjs scenario scenarios/<name>"]
}
```

| Field | Values |
| --- | --- |
| `task.kind` | `review`, `prep`, `init` |
| `verdict`, `checks[].verdict` | `pass`, `fail`, `inconclusive` |
| `checks[].by` | `script`, `value`, `visual`, `not-run`, `run-error` |
| `checks[].via` | `web`, `api`, `db`, or null |
| `uiFindings[].type` | `operation`, `layout`, `wording`, `display`, `error`; `auto` marks automatic findings, `scenario` findings a scenario added |
| `items[]` | Item id, title, check ids, remaining human work; status is derived |
| steps `kind` | `script` (promoted or generic fragment), `adhoc` (scratch script or `api` call), `agent` (recipe step logged with `log`) |
