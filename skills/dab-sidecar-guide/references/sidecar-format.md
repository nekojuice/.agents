# JSON Database Sidecars

Use this reference for sidecars whose documented layout contains metadata, table entries, and table-column entries. The following layout is a supported convention, not a complete or mandatory schema.

## Entry locations

| Section | Typical organization | Read for |
|---|---|---|
| `meta` | An object describing the file and its sources | Database identity, generation context, snapshot selection, and known discrepancies |
| `tables` | An object keyed by table name | Table purpose, key declarations, authority notes, and relationships |
| `semantics` | An object keyed by `Table.Column` | Column structure, meaning, constraints, and compatibility exceptions |

Use exact keys after inspecting the file. A missing entry means this sidecar does not provide that information; it does not establish that the object is absent from the database.

## Metadata and provenance

When present, read:

- `source` for the annotation or other input used to generate the sidecar.
- `generated_at` or `generated_ts` for generation context.
- `database` for the intended database identity.
- `structure_snapshot` and `structure_snapshot_date` for the structural baseline.
- `structure_differences` for recorded annotation-versus-snapshot discrepancies.

Generation context and structural freshness are separate. A newly generated sidecar may still use an older snapshot. An empty discrepancy list only describes the comparison performed by the generator; it does not establish agreement with the current database.

## Table and column interpretation

Read purpose and notes alongside structural facts. Preserve the full SQL type, including any length, precision, or scale. Do not collapse distinct SQL string types into a generic string when the distinction affects the task.

A table's ordered key list describes a composite key only within the authority stated by that format. Check whether it denotes a physical primary key, a configured record identifier, or a logical key. A column-level key flag does not establish the complete key combination.

For nullability and flags, distinguish an explicit false value from an absent field. Do not infer that a missing key flag means a confirmed non-key column. Check contextual notes for exceptions such as empty strings, compatibility mirrors, and reserved fields.

## Extensions

Additional sections may describe parameter semantics, business rules, consumers, mappings, provenance, uncertainty, or other supplemental information. Additional fields may appear inside existing entries.

Inspect relevant extensions without treating the section and field lists above as exhaustive. Interpret them using the sidecar's own documentation. If an extension is undocumented and consequential, identify the ambiguity rather than assigning it a meaning from its name alone.
