# Evidence Ranking

## Evidence classes

### Human authority

An explicit human project decision or acceptance. This determines `completed-human` and accepted project direction.

### Direct observation

Current source, configuration, specification, runtime output supplied in scope, or a verification artifact that directly supports the claim.

### Corroborated inference

Multiple current sources support the same conclusion, but no single source directly proves the whole claim.

### Single-source inference

One source suggests a conclusion. Use medium or low confidence depending on its authority and freshness.

### Report or historical note

An unverified report, old note, scratch file, or stale status claim. Treat it as an investigation input, not proof.

## Confidence

- `high`: direct current evidence or explicit human authority; no material contradiction.
- `medium`: coherent inference with partial evidence or one unresolved qualifier.
- `low`: incomplete, stale, indirect, or contradictory evidence.

Human authority outranks PM assessment, but a later technical observation may still justify a linked bug or risk. Preserve both rather than silently rewriting history.
