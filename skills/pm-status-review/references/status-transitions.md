# Status Transitions

## Allowed PM transitions

- `inbox -> investigating`: investigation has begun.
- `investigating -> answered`: a question has a supported answer.
- `investigating -> candidate`: evidence supports a coherent product outcome.
- `candidate -> approved-for-factory`: the human explicitly establishes the candidate.
- `approved-for-factory -> handed-off`: a self-contained factory run exists.
- `handed-off -> in-delivery`: current factory artifacts show delivery activity.
- `in-delivery -> verifying`: implementation is present and verification is the remaining gate.
- `candidate -> in-delivery` (orchestrator-pm Non-product route): the PM began editing the managed object under a change decision the user approved.
- `in-delivery -> verifying` (Non-product route): the edit is done and the user's git diff review, or equivalent before/after diff, is pending.
- `verifying -> completed-pm`: PM evidence supports completion.
- `completed-pm -> investigating | verifying`: later evidence invalidates or weakens the PM assessment.

The Non-product route skips `approved-for-factory` and `handed-off`.

## Human transition

Only an explicit human statement sets `completed-human`.

The PM must not silently downgrade `completed-human`. Open a linked case and ask the human whether to reopen the outcome.

## Non-progress transitions

Use `deferred`, `rejected`, or `answered` with a reason and source. Do not use completion states for work intentionally excluded from the project.
