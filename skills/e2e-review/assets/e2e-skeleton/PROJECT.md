# Project profile

Verified skill version: `{{SKILL_VERSION}}`

Read this file before every review task. It holds everything project-specific; the e2e-review skill holds none of it.

## System under test

| Item | Value |
| --- | --- |
| Site | <name and purpose> |
| URL | see `config/env.json` (`baseUrl`) |
| Checklist source | <where acceptance checklists live> |
| Navigation and routes | <file that defines menus or routes> |
| Permission model | <where roles and permission nodes are defined> |
| Tested version | <how to tell: repos listed in `config/env.json` `repos`> |

## Operating limits

- Environment: <test environment only; never production>
- Browser: <browser>
- Writable data: <data scope the worker may write, and what needs superior approval>
- Untouchable data: <data the worker must never write or log in to>
- External services: <none unless the user approves a scope>
- Pending confirmation: <items the superior or user must decide>

## Accounts

Keys in `config/accounts.local.json` (local only, never committed). Artifacts record keys, never passwords.

| Key | User | Role and purpose |
| --- | --- | --- |
| <key> | <user id> | <role, what it is used for> |

## Audit trail

| Item | Value |
| --- | --- |
| Source | <table, log, or API> |
| Adapter | `audit/fetch.mjs` |
| Action codes | <code → meaning> |

## Scripts

Update this section whenever a script is promoted, changed, or deleted.

### actions

| Script | Args | Returns |
| --- | --- | --- |

### probes

| Script | Args | Returns |
| --- | --- | --- |

### scenarios

| Scenario | Checklist items | Writes |
| --- | --- | --- |

## Known pitfalls

- <project-specific behavior that looks like a bug but is by design, flaky spots, workarounds>
