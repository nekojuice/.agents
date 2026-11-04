# Project profile

Verified skill version: `{{SKILL_VERSION}}`

Read this file before every review task. It holds everything project-specific; the e2e-review skill holds none of it.

## System under test

| Item | Value |
| --- | --- |
| Site | <name and purpose> |
| Checklist source | <where acceptance checklists live> |
| Navigation and routes | <file that defines menus or routes> |
| Permission model | <where roles and permission nodes are defined> |
| API contract | <where endpoints are defined: controllers, OpenAPI, or "recorded from screens"> |
| Tested version | <how to tell: repos listed in `config/env.json` `repos`> |

## Surfaces

Registered in `config/env.json` `surfaces`. Keep only the surfaces this project actually has.

| Surface | Driver | Base URL | Login | Use |
| --- | --- | --- | --- | --- |
| web | playwright | see `env.json` | `surfaces/web/actions/login` | <screens under test> |
| api | http | see `env.json` | `surfaces/api/helpers/auth.mjs` | <API checks, test data preparation> |

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

## Test data

| Item | Value |
| --- | --- |
| Templates | `data/templates/`: <template → recorded from which screen request, date> |
| Builders | `data/builders/`: <builder → what it fills> |
| Sets | `data/sets/`: <set → purpose> |
| Created in this environment | `state/data-<env>.json` (not committed); <how to read it, naming prefix of test data> |

## Scripts

Update this section whenever a script is promoted, changed, or deleted.

### web: actions

| Script | Args | Returns |
| --- | --- | --- |

### web: probes

| Script | Args | Returns |
| --- | --- | --- |

### api: actions

| Script | Args | Returns |
| --- | --- | --- |

### api: probes

| Script | Args | Returns |
| --- | --- | --- |

### scenarios

| Scenario | Checklist items | Surfaces | Writes |
| --- | --- | --- | --- |

### recipes

| Recipe | Purpose | Surfaces | Agent steps left |
| --- | --- | --- | --- |

## Known pitfalls

- <project-specific behavior that looks like a bug but is by design, flaky spots, workarounds>
