# Context Sanitization

## Include

- Human-approved outcome.
- Confirmed behavior, constraints, facts, and decisions relevant to the outcome.
- Precise source or project paths the factory may inspect.
- Known dependencies and exclusions.
- Open questions clearly labeled as open.
- Acceptance intent without inventing implementation details.

## Exclude

- Any `.manager` path or PM-origin metadata.
- PM scratch notes and internal deliberation.
- Worker transcripts or unsupported conclusions.
- Unrelated library entries.
- Customer-identifying or sensitive material not needed for implementation.
- Premature technical design that the factory discussion should decide.
- PM-only terminology or instructions to report back upstream.

## Convert by value

When a manager fact or decision is necessary, restate the confirmed content in the intake and cite the authoritative project source when one exists. Do not transfer it only as a link into `.manager`.
