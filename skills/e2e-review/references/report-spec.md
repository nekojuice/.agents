# Report Spec

Every task produces one round folder with a report for the superior. The superior reviews it and decides what counts as done.

## Round folder

`<parent>/e2e-review/<yyyyMMdd-HHmmss>-r<NN>-<short>/`

| Path | Required | Content |
| --- | --- | --- |
| `result.json` | Yes | Structured result; schema below |
| `report.md` | Yes | Rendered from `result.json` by `report` or `close` |
| `shots/` | Yes | Evidence screenshots, including `final.png` |
| `values/` | When used | Value evidence: page reads, API responses, query results, `audit.json` |
| `review/` | Optional | Visual review aids such as contact sheets; not evidence |
| `scratch/` | Optional | Ad-hoc scripts of this round; cite them as evidence when a check relies on one |
| `steps.jsonl` | Automatic | One line per executed step: start, end, script, arguments, success |
| `init-proposal/` | When needed | Proposed `.e2e/` for an uninitialized project |

The timestamp tells a returning superior whether the round ran before or after a fix; `r<NN>` is the round; `<short>` separates blocks in one parent.

## Report sections

| Section | Required | Content |
| --- | --- | --- |
| Conclusion | Yes | Overall verdict and reason, failed checks, checks needing human verification, limits on passed checks |
| Checklist item map | With items | Suggested status per item, its checks, remaining human work |
| Comparison with previous round | With `--prev` | Status change per item |
| Task | Yes | Source text, requester, round, round basis |
| Environment | Yes | URL, data scope, account keys, browser, start time, tested versions, skill version and the version PROJECT.md was verified with |
| Checks | Yes | Expected, actual, verdict, source, evidence per check |
| Screenshots | Yes | Screenshots cited by checks, plus the final state |
| UI findings | Yes | Issues found beyond the checklist; "none" when empty |
| Writes | Yes | Data written, with time; "none, login entries only" for read-only tasks |
| Steps and audit trail | With logins or writes | Step timeline with the audit rows each step produced |
| Issues | Yes | Blockers, changed methods, assumptions, coverage gaps, version mismatch |
| Observations | Optional | Context that is not a UI finding |
| Reproduce | Yes | Commands in order |

The renderer currently writes headings in Traditional Chinese; stored values stay in English.

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
| `value` | A script read the values; the agent compared them | Medium |
| `visual` | The agent judged from screenshots only | Low |
| `not-run` | Environment or condition unavailable, or the item is human-only | None |
| `run-error` | A tool or script error stopped the check | None |

- `visual`, `not-run`, and `run-error` checks are always `inconclusive`; `note` states the missing condition or the error.
- A check not reached because an earlier step failed is `inconclusive`, never `fail`.
- Check sources are the tool's internal classification, not the superior's acceptance rule.

### Conclusion wording

- Overall `pass`: "通過" with the summary.
- Otherwise: "整體不算通過", the overall verdict in parentheses, and the reason, e.g. "2 checks inconclusive, need human verification".
- Below the conclusion: failed checks with the difference; inconclusive checks with the reason and the condition needed; limits on passed checks with when to re-verify.

### Checklist item status

The renderer derives a suggested status for each item in `result.items` from its checks, in this order:

| Status | Condition |
| --- | --- |
| `product-fail` | Any check failed |
| `run-error` | Any check is inconclusive with source `run-error` |
| `needs-human` | Any check is inconclusive for another reason, or the item has no checks |
| `verified-with-limits` | All checks pass and at least one appears in `limits` |
| `verified` | All checks pass with no limits |

Remaining human work combines the item's `humanWork`, the notes of non-passing checks, and the re-verification of limits.

### Comparison with the previous round

With `previousReport` set, each item shows the previous and current status and whether it improved, regressed, is new, or is unchanged.

## Evidence

- Prefer value evidence: text or numbers that can be compared, such as a menu item list, a field value, an API response, or a query result.
- Attach `shots/final.png` for every task and a screenshot for every failed check.
- When expected values come from a database, record the query and store the result in `values/`.
- Never put passwords in any artifact. Record account keys instead.

## UI findings

Record unreasonable UI behavior seen during the task; findings never affect verdicts. Categories, automatic rules, and the review method are in [ui-checks.md](ui-checks.md).

- Attach evidence to each finding; a screenshot first, the read value for wording issues.
- Describe the phenomenon and location only; no causes, no fixes.
- Skip behavior PROJECT.md lists as by design.

## Write traceability

For tasks with logins or writes, show which audit entries this task produced and which step produced each, including reruns.

- The round folder is the task identity. Reruns in the same round append to `steps.jsonl`; failed steps stay.
- Every write in `writes` carries a time; writes from earlier runs in the same round are kept.
- `close --users` or `audit --users` fetches audit rows for the task window through the project's adapter into `values/audit.json`.
- Each audit row goes to the last step that started before it; rows more than 1.5 s after that step ended are listed as unattributed, with an explanation such as an unlogged ad-hoc command or another person using the same account.

## result.json

```json
{
  "task": { "title": "<title>", "source": "<checklist text>", "requester": "<superior>" },
  "round": 2,
  "previousReport": "<previous round folder>",
  "basis": "<fix this round verifies>",
  "verdict": "inconclusive",
  "summary": "<one line>",
  "env": {
    "url": "<url>",
    "dataScope": "<test data scope>",
    "accounts": ["<account key>"],
    "browser": "<browser>",
    "startedAt": "2026-11-03T13:40:00.000",
    "versions": { "web": "abc1234 (+3 uncommitted)" },
    "skillVersion": "1.0",
    "projectVerifiedSkillVersion": "1.0"
  },
  "items": [{ "id": "12", "title": "<item>", "checks": ["12-1", "12-2"], "humanWork": "" }],
  "checks": [{
    "id": "12-1", "title": "<check>", "expected": "<expected>", "actual": "<actual>",
    "verdict": "pass", "by": "script", "evidence": ["values/menu.json", "shots/menu.png"], "note": ""
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
| `verdict`, `checks[].verdict` | `pass`, `fail`, `inconclusive` |
| `checks[].by` | `script`, `value`, `visual`, `not-run`, `run-error` |
| `uiFindings[].type` | `operation`, `layout`, `wording`, `display`, `error`; `auto` marks automatic findings |
| `items[]` | Item id, title, check ids, remaining human work; status is derived |
