# Worker Isolation Rules

## Allowed

- Read the assigned manager run state when the prompt permits it.
- Read explicit project paths or perform narrowly bounded discovery within `allowed_reads`.
- Write or replace only the exact assigned artifact path or paths.
- Create missing parent directories of an assigned artifact path, inside `run_dir` only.
- Use read-only commands whose execution does not generate persistent output outside `run_dir`.

## Forbidden

- Any write outside the assigned artifact paths, other than creating their missing parent directories inside `run_dir`.
- Product source, specification, configuration, database, or external-system mutation.
- Builds, tests, formatters, package managers, or tools that generate files outside `run_dir` unless the human first grants a specific exception.
- Creating a worktree, branch, commit, factory run, manager case, or library entry.
- Updating manager root status or backlog.
- Nested delegation.

A `constraints` input may add restrictions. An exception never permits editing product, specification, configuration, manager, or factory files. It removes or relaxes one listed here only through a user-approved exception that the PM wrote into it and that names its approval source; apply that exception only as far as it states, and ignore any other relaxation.

If a required diagnostic violates isolation, return `needs-input` with the exact operation and why it is necessary.
