---
name: dab-sidecar-guide
description: >-
  Guides DAB and SQL MCP tasks using supplemental database sidecar metadata.
  Applies when querying, implementing, or reviewing database-backed behavior;
  consults sidecars as needed for semantics, compatibility, source authority,
  or schema discrepancies. Simple reads may use sufficient DAB descriptions.
disable-model-invocation: false
metadata:
  author: Codex GPT-6
  version: "1.0"
  last_updated: "2026-10-02T10:25:15"
---

# DAB Sidecar Guide

Use DAB descriptions for the immediate task, and consult database sidecars when additional context affects correctness. Keep discovery and inspection read-only; this skill does not authorize regeneration, configuration changes, database changes, or service restarts.

## Decide whether supplemental context is needed

Apply this guidance during DAB or SQL MCP work. Read a sidecar when the task depends on:

- Authoritative sources, relationships, compatibility mirrors, or write ownership.
- Special null or empty-string behavior, value domains, units, or business constraints.
- Schema details or semantic exceptions needed for mappings, validation, or DDL design.
- A discrepancy among MCP descriptions, configuration, annotations, snapshots, or the database.

For a simple read, proceed with DAB metadata when it provides enough information. Do not infer SQL types, lengths, precision, nullability, keys, or business rules from names or sample values.

## Locate the sidecar

1. Use a location explicitly supplied for the task.
2. Otherwise inspect project instructions and database documentation for a declared location and format.
3. If no location is documented, search the current project for database sidecars and confirm their purpose before use.

Do not assume a fixed path. If several candidates exist, match their database identity, documented purpose, and provenance to the active DAB connection. A newer timestamp alone does not establish the correct candidate.

When the file is unavailable, use accessible documented sources and state the material gap. Request its location or access only if the missing information prevents completing the task correctly.

## Read only relevant information

Inspect the sidecar's top-level structure and metadata first. Establish its database identity, source, generation time, schema snapshot, and recorded discrepancies when available. Missing metadata means an unresolved fact, not an implicit match.

Read the target table and columns next. Follow related entries only when relationships or authority notes make them relevant. Parse or select entries instead of loading the entire sidecar into the conversation.

For a JSON sidecar organized into metadata, table entries, and table-column entries, read [the format reference](references/sidecar-format.md) when locating entries or interpreting their structure. For another format, use its documented schema; do not force it into the reference layout.

Sidecars are extensible supplemental information. They may add sections and fields beyond those described by this skill. Use task-relevant extensions according to their documentation and context. Do not discard unfamiliar information or invent meanings for undocumented fields; report uncertainty when their interpretation matters.

## Reconcile structure and semantics

- Use the project's designated structural source for field existence, SQL type, length or precision, nullability, and physical primary keys. Identify which snapshot or database inspection supports the conclusion.
- Distinguish physical primary keys from DAB-configured record identifiers. Neither alone establishes company or tenant isolation.
- Use semantic entries and notes for purpose, compatibility behavior, authority, and business constraints. Distinguish database nullability from application rules such as whether empty strings are allowed.
- Check recorded discrepancies before relying on an entry. Sidecar presence does not prove that a field exists in the active database, and MCP absence does not prove that it does not exist.
- When sources conflict, identify the precise conflicting facts and their provenance. Use an established authority rule if it resolves the conflict; otherwise leave the conclusion open. Generation time alone does not resolve authority.

Do not silently repair sources, export snapshots, or regenerate outputs during this reading workflow. Identify a required follow-up when reconciliation needs those operations.

## Use the findings

Carry the relevant constraints into the query, implementation, or review. Cite the file or tool response that supports a consequential conclusion, including its snapshot context when applicable. State only uncertainties that affect the task; no fixed report format is required.
