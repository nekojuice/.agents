# Grouping and Deduplication

Group reports only when at least one of these relationships is supported:

- Same confirmed or strongly suspected root cause.
- Same desired project outcome.
- One report is a symptom or dependency of another.
- One factory change would resolve all grouped reports without unrelated scope.

Do not group merely because reports mention the same screen, repository, customer, or date.

For every group, preserve:

- Original source identifiers and wording.
- Distinct environments and impacts.
- Evidence for the relationship.
- Remaining differences.
- Confidence in the grouping.

If grouping is uncertain, keep separate source items linked by `possibly-related` until investigation resolves it.
