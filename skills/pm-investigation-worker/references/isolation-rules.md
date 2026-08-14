# Worker Isolation Rules

## Allowed

- Read the assigned manager run state when the prompt permits it.
- Read explicit project paths or perform narrowly bounded discovery within `allowed_reads`.
- Write or replace only the exact assigned findings artifact.
- Use read-only commands whose execution does not generate persistent output outside `run_dir`.

## Forbidden

- Any write outside the assigned artifact.
- Product source, specification, configuration, database, or external-system mutation.
- Builds, tests, formatters, package managers, or tools that generate files outside `run_dir` unless the human first grants a specific exception.
- Creating a worktree, branch, commit, factory run, manager case, or library entry.
- Updating manager root status or backlog.
- Nested delegation.

If a required diagnostic violates isolation, return `needs-input` with the exact operation and why it is necessary.
