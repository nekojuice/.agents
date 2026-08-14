# Library Provenance

## Promotion rule

Manager runs contain working memory. Promote only information that is durable, project-wide enough to reuse, and supported by an identifiable source.

## Fact entry

Record:

- Title.
- Status: `observed`, `confirmed`, `disputed`, or `superseded`.
- Scope.
- Statement.
- Source paths, human decision, or evidence artifacts.
- Observed or confirmed date.
- Confidence.
- Qualifications and exceptions.
- `superseded_by`, when applicable.

Do not label a PM inference as confirmed unless a sufficient source or human confirmation exists.

## Decision entry

Record:

- Title.
- Status: `proposed`, `accepted`, or `superseded`.
- Context.
- Decision.
- Rationale.
- Consequences.
- Decision date and authority.
- Related cases, milestones, or factory runs.
- `superseded_by`, when applicable.

## Index

Keep `_library/index.md` short. List each entry with type, status, scope, one-line summary, and relative path. Load full entries only when relevant.

## Correction

Do not erase a previously relied-on fact or decision. Mark it superseded or disputed, link the replacement, and preserve the reason for the change.
