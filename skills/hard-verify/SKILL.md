---
name: hard-verify
description: >-
  Runs project hard-gate checks (compile/build, unit tests, lint, optional
  standalone type-check) by discovering the module's real tooling. Read-only
  by default: report only, never auto-fix. Use when the user runs /hard-verify,
  asks for hard checks / 硬檢查 / gate check / build+test+lint, or wants
  post-implementation automated verification without requirement-boundary review.
disable-model-invocation: true
metadata:
  author: Cursor Grok 4.5
  version: "1.0"
  last_updated: "2026-07-23T09:44:00"
---

# hard-verify

Post-implementation **hard-gate** check: discover and run the project's compile/build, unit tests, lint, and (when applicable) standalone type-check. Reports pass/fail/skip with evidence. Does **not** judge requirement boundaries (that is a separate concern).

This skill runs **only** when the user explicitly invokes it (e.g. `/hard-verify`). It does **not** auto-run after apply or any other flow. It may be run **at any time** — do not assume or document a fixed order relative to other checks.

## Goal

Answer: **do the project's automated hard checks pass for the selected scope?**

- In scope: compile/build, unit tests, lint, optional standalone type-check
- Out of scope: requirement-boundary review, security/performance audits, formatters (e.g. prettier write), E2E / browser automation, speculative refactors

## 1. Session defaults (read-only)

Unless the user **explicitly** overrides in this turn:

- **Read-only** — do not edit, create, delete, stage, or format source to "make checks green"
- **Report only** on failure — never self-repair
- **User instructions win** — if they ask to fix, narrow scope, or run extra commands, follow that for this invocation

Do not start long-lived servers (`dev` / watch) as part of this skill.

## 2. Resolve target modules (priority)

Resolve **which module(s)** to check, in this order — stop at the first decisive step:

1. **User-specified** — module paths, include/exclude, or exact commands named in this turn
2. **Infer from conversation context** — e.g. this session changed both web UI and backend API → run **both** corresponding modules
3. **Infer from git** — `git status` / `git diff` (and recent commit paths if needed); map changed paths to owning modules; run those modules
4. **Ask** — if still ambiguous, ask whether to check a specific module or all relevant modules; do not guess

**Scope default:** full project/module suite for each selected module, unless the user named a narrower range or exclusions.

If multiple modules are selected, run each module's discovery + checks separately and report them separately.

## 3. Check categories (always attempt)

For each selected module, attempt these four categories. If a category does not apply or cannot be found, mark **skip** with reason — do not invent a fake pass.

| Category | When to run | Notes |
| --- | --- | --- |
| **Compile / Build** | Always try | Compiled languages (Java, .NET, etc.): must include **compile** (or the project's equivalent build that compiles). Frontends: run the project's **build** script(s). |
| **Unit test** | Always try | Unit-test suite for the module. |
| **Lint** | Always try | All configured linters (e.g. oxlint **and** eslint). Prefer the aggregate lint script if it runs every linter; otherwise run each discovered linter. |
| **Type-check** (optional) | Only if standalone | Run only when the module has a **standalone** type-check command that is **not** already covered by the build you ran. If build already runs type-check, do not duplicate — note that in the report. |

**Never** as part of this skill (unless the user explicitly asks):

- Formatters that rewrite files
- E2E / Playwright / browser clicking
- Requirement or design-doc review

## 4. Tool discovery (priority)

Discover commands **per category** for each module. Do **not** read README files for discovery (they pollute context with unrelated prose).

Priority:

1. **User-specified** commands / scope for this turn
2. **Module scripts & build definitions** — e.g. `package.json` `scripts`, Maven/Gradle tasks, `.csproj` / solution targets, equivalent manifests in the module root
3. **CI config** — extract the **check commands** from jobs/steps that correspond to build/test/lint/type-check; do **not** run the entire pipeline
4. **Language / framework convention fallback** — use common defaults for that stack (examples below); **must report** that fallback was used and which command
5. **Stuck** — for that category: report what was tried, mark skip/blocked, and **ask the user**; do not invent unrelated commands

### Convention fallback examples (not exhaustive)

Use only after scripts/CI yield nothing useful; always disclose.

| Stack | Compile / Build | Unit test | Lint (examples) |
| --- | --- | --- | --- |
| npm / Node (Vue/Vite, etc.) | `npm run build` or project `build-*` | `npm test` / `npm run test:unit` | `npm run lint` or `lint:*` |
| Maven (Java) | `mvn -q compile` / `./mvnw compile` | `mvn test` / `./mvnw test` | Checkstyle/Spotless/`mvn verify` plugins if configured |
| Gradle (Java) | `./gradlew compileJava` or `build` | `./gradlew test` | configured lint tasks if any |
| .NET | `dotnet build` | `dotnet test` | analyzer/`dotnet format --verify-no-changes` only if that is the project's lint gate |
| Go | `go build ./...` | `go test ./...` | `golangci-lint` / `go vet` if present |
| Python | N/A or package build if used | `pytest` | `ruff` / `flake8` / `mypy` if configured |

Prefer running from the **module directory** that owns the change.

### Frontend note (this workspace's Vue app pattern)

When checking a module like `IFRS16.web`, typical discovered gates include: build (often via `build-testing` / `build-production`, which may already chain `type-check`), `test:unit`, and lint (`lint` or `lint:oxlint` + `lint:eslint`). Discover from `package.json`; do not hard-code if scripts differ.

## 5. Execution rules

- Run discovered commands; capture exit code and a **short** failure excerpt (not a full log dump)
- On failure of any category: continue other categories unless a dependency makes later runs meaningless (e.g. compile failed so hard that tests cannot start — then skip dependents and say why)
- Do not install packages or change the environment to "get green" unless the user explicitly allows it
- Do not claim pass without having run the command (or an explicit user waiver for that category)

## 6. Report format (required)

Deliver results **in the conversation** only. Structure:

1. **Targets** — modules, scope, exclusions
2. **Discovery** — tools/commands found and **source** (user / scripts / CI / convention fallback)
3. **Results by category** — pass / fail / skip, with the **exact command** run
4. **Failure summary** — concise error highlights per failed category
5. **Not run / cannot determine** — anything blocked or skipped, with reason
6. **Reminder** — this invocation is read-only and does not auto-fix; next action is the user's choice

Do **not** write check notes into opsx change docs or other project files as part of this skill.

## 7. After the report

Stop after reporting unless the user asks to fix, re-run, or change scope. If they ask to fix, that is a **new** instruction outside this skill's default read-only posture — follow the user, but do not silently expand into unrelated cleanup.
