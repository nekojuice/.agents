# Completion Precedence

## Levels

Use these two distinct completion levels:

### `completed-pm`

The PM judges the outcome complete from available implementation, verification, specification, and delivery evidence. The PM may assign or later revoke this level when evidence changes.

### `completed-human`

The human explicitly accepts the outcome. This outranks PM assessment. Record who accepted it, when, and what was accepted.

## Precedence

```text
completed-human
> completed-pm
> verifying
> in-delivery
> handed-off
> approved-for-factory
> candidate
> investigating
> inbox
```

## Regression after human acceptance

Do not silently downgrade historical human acceptance. Create a linked suspected or confirmed bug and surface it to the human. Reopen the accepted outcome only after an explicit human decision.

## Conflicting evidence

When PM evidence conflicts with human acceptance:

1. Preserve `completed-human`.
2. Record the new evidence and confidence.
3. Open a linked risk or bug case.
4. Ask whether the accepted outcome should be reopened.
