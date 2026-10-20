---
name: doc-openapi-guide
description: Implementing or revising OpenAPI documentation in any language or framework — operation summaries and descriptions, parameter and field descriptions, response descriptions, examples, document-level information — and the documentation-related code that makes Swagger UI, Scalar, or another viewer render it correctly and readably. Extends doc-general-guide; this guide wins on conflict. Supports an external audience (default; strict control of exposed logic) and an internal audience (more detail allowed); asks for audience, language, and whether a draft preview is wanted before starting. Respects the project's existing error-handling design. Use when creating, revising, or auditing API docs generated from code.
disable-model-invocation: false
metadata:
  author: Claude Code Opus 5.5
  version: "1.2"
  last_updated: "2026-10-20T15:44:21"
extends: doc-general-guide
---

# OpenAPI Documentation Guide

API documentation is written for **the people who integrate with the API**. A caller should be able to integrate without asking anyone: what an endpoint does, what to send, what comes back, and what each error means.

This guide covers the documentation text and the **documentation-related code** behind it: annotations and metadata that carry the text, examples, document generator settings, document transforms, viewer settings, and the document URL. It applies to any language and framework.

This guide **extends doc-general-guide**. Read that guide for the shared foundations. Where the two conflict, **this guide wins**.

## 0. Confirm inputs before starting

| Input | Options | Default |
|---|---|---|
| Audience | `external` — consumers outside the team; `internal` — developers of the same organization | `external` |
| Language | Any single language | The project's primary language, judged from its existing docs and UI text |
| Draft preview | Draft the whole document's text for a quick review before implementing — yes or no | Ask; not needed when revising, because the review report in §8 plays that role |

If the user has not stated these inputs, **ask once, in one question, showing the defaults, and wait for the answer before any work**. If no answer can be obtained (non-interactive run), proceed with the defaults, skip the draft, and state the choices at the top of the deliverable.

### Audience differences

| Aspect | External | Internal |
|---|---|---|
| Processing logic | Forbidden: no flow, decision method, calculation, ordering, or concurrency details | Allowed when it changes how a caller must call or read the result; still short |
| Internal component names | Replace with the function name | Allowed when the caller interacts with that component |
| Usage risks | State only what the caller observes | May add operational risks such as cost or rate impact |

Rules that hold for **both** audiences: identifying information and secrets follow doc-general-guide §2.16, and credentials and resource identifiers are never shown either.

## 1. Inherited from doc-general-guide

| Inherited rule | Meaning here |
|---|---|
| §0 document types | §0 routes API documentation here. Endpoint descriptions belong in the OpenAPI document only, not in README or other document types |
| §1 verification rules: verify against real files, flag defects, treat a poor existing doc as a negative example | The code's actual behavior is the source of truth; existing annotations are re-derived, not trusted |
| §2.7 name only objects the reader types or sees | The reader is the caller: paths, parameters, fields, status codes, enum values, error strings |
| §2.10–2.11 minimum concept, default of no design rationale | No implementation notes in descriptions |
| §2.13 no invented terms | Observable behavior instead of jargon, see §3 |
| §2.14 single language | The language chosen in §0 holds for every text |
| §2.16 placeholders and invented names for identifying information | Every example uses invented values, never real identifiers |
| §2.5 tables for inventory-type information | The exposure analysis, draft, and review report are tables |
| §3 headings name the real scope, no status in the heading | Applies to operation summaries, see §4 |
| §4 parentheses discipline | Applies unchanged to every description and error message |

### Overrides

| doc-general-guide rule | Here |
|---|---|
| §1 material order with openspec as semantic authority | The code is the authority for behavior; specs state intent. Report any mismatch |
| §2.1–2.4, §2.8, §5 command and code-block rules | Not applicable: the text lives in code annotations and metadata |
| §2.6 one-line scope statement | Not applicable; the document-level description in §7 introduces the API |
| §2.9 two-line section openings | Replaced by the glance-length rule in §4 |
| §2.12 `>` notes | Not applicable; descriptions are plain text in annotations |
| §7 completion checklist | Replaced by §10 |

## 2. Exposure analysis — do this first

Build one table before writing anything:

| Endpoint | Shown in docs, per environment | Reachable | Reader |
|---|---|---|---|

- **Endpoints hidden behind a feature flag** are still reviewed, but always-on endpoints never mention the hidden feature.
- **Endpoints shown only in development** may follow the internal-audience rules.
- **Error messages are more exposed than the docs**: they are returned in every environment and seen without opening the docs. Judge their exposure by who can call the endpoint, never more loosely than the docs.

## 3. Content rules

The examples use an invented library-loan API.

| Rule | Write | Instead of |
|---|---|---|
| Only what the caller needs: what it does, what to send, what comes back, what each error means | "Renews a loan and returns the new due date" | "Each renewal is also copied to the reporting archive" |
| No processing logic (external) | "`dueDate` is the day the item must be returned" | "Checks the member's three borrowing limits in turn and keeps the strictest", "adds 14 days, then skips closed days one at a time", "queries every branch at once" |
| No internal components or operations detail: no cloud services, permissions, resource identifiers, or log locations | "The catalog search is temporarily unavailable" | "The search cluster did not answer; see the indexer log", "check the access key of the sync job" |
| No unreleased features | "Places a hold on the item for the member" | "Holds placed here also appear in the mobile app" when the mobile app is not released |
| Observable behavior instead of jargon | "A loan that was already returned cannot be renewed" | "Renewal is guarded by the loan state machine" |
| Name the function, not the call pattern | "List overdue loans" | "Scan overdue loans page by page" |

## 4. Wording and length

- **Glance length.** No fixed character count, because it differs by language. Every text must be read comfortably at a glance:
  - operation description — one short sentence;
  - field and parameter description — a short phrase;
  - response description and error message — one sentence.

  Needing a second sentence usually means internal logic or duplicated information slipped in.
- **Summary** — a short title in the document language, with no parentheses and no status code.
- **Punctuation** follows the document language's convention, such as full-width punctuation for CJK text.
- **Enum values** stay literal, each followed by its meaning: `ON_LOAN` checked out, `RETURNED` back on the shelf.
- **Response descriptions** are written in the document language; replace framework default reason phrases such as `OK` or `Bad Request`.
- **Do not repeat** what another part of the document already shows: the content type belongs to the request body, rejection conditions belong to the responses.
- **Long-content fields** use a placeholder naming the content kind as the example, not a huge string.

## 5. Error responses

### Enumerate from code

Generators do not know which errors an endpoint returns. Enumerate them by hand:

1. Read every endpoint handler and list every return path: status code, situation, actual response body.
2. Include failures that surface later in asynchronous results, such as every possible value of an error field in a status-query response.
3. List responses the framework or middleware returns **before the handler runs**, such as an oversized request, an unparsable body, authentication, or routing failures. List them for the user to decide whether to document or handle them; do not change them on your own.
4. Compare declarations with actual responses and flag three mismatches:
   - a framework built-in error format is declared, but a custom shape is returned;
   - a status code is declared without a body schema;
   - a response that actually occurs is not declared at all.

### Respect the project's design

The project owns its error design. When it already maps situations to specific status codes and messages, **document that design as it is**; do not restructure it.

| Topic | Handling |
|---|---|
| Message wording | Rewrite to the rules in §3–§4 only through the review in §8; for new docs, list every rewritten message at delivery for the user to confirm, §8 |
| Exposure problems in a message — raw exception text, secrets, internal detail | Always flag, with a suggested fixed text; change only after the user agrees |
| Dynamic parts of a message | Suggest limiting them to values the caller sent or limits already published to callers, such as a maximum count or allowed file types |
| Failures the caller cannot fix | For an external audience, suggest merging them into one sentence that asks the caller to contact the system administrator, keeping details in logs |
| Status codes and error body shape | API contract. Suggest one shared error shape when the project has none, but list any change as a decision for the user; never change it as a documentation fix |

Declare the project's error shape on every error status and give each an example.

## 6. Examples

| Rule | Detail |
|---|---|
| Every status code with a body has an example | Without one, viewers render type placeholders such as `"string"`, `0`, `additionalProp1` |
| A whole-body example, not only field-level examples | Field-level examples assembled by the viewer often contradict each other, such as an item marked available that still shows a due date, or a shared schema showing a success body under an error status |
| One example per situation | A status code with several situations gets several examples, such as on loan, returned, lost |
| Matches the real response | Same format, fields, null values, and error message text as the code returns. Share one source for message text and examples when the framework allows; otherwise lock them with a test, §8 |
| Not borrowed across endpoints | A follow-up request does not reuse the first request's example |

## 7. Rendering checks

| Item | Rule |
|---|---|
| Every viewer | All viewers the project serves read the same document. Open each one and confirm every changed text and example renders |
| Settings outside the document | Viewer menu names and page titles are not in the OpenAPI document; set them separately |
| Document-level information | The title is the API's name for callers, not the code project name. Add a document description and a description for every tag |
| Sub-path deployment | Point viewers at the document with a relative URL so it loads behind a reverse proxy or under a sub-path |
| File upload fields | Swagger UI shows a file picker only when the array items are an inline binary string schema; generators may emit a reference instead. Check the output and transform it when needed |
| Ignored annotations | Some generators ignore certain annotation forms, such as examples on parameters. Confirm in the viewer that every example actually appears |

## 8. Workflow and deliverables

1. Confirm the inputs, §0.
2. Write the exposure analysis, §2.
3. Enumerate actual responses and error messages from code, §5.
4. Before implementing:
   - **Revising existing docs** — write a before/after review report and change nothing before the user has reviewed it.
   - **New docs** — if the user asked for a draft preview, draft the whole document's text in the report layout below, without a before column, for a quick review.
5. Implement the documentation-related code directly: annotations and metadata, examples, generator settings, document transforms, viewer settings, document URL. Behavior changes listed as decisions in §5 wait for the user.
6. When the project has tests, lock the result:
   - every operation has a summary and description in the document language;
   - no summary contains parentheses or a status code;
   - every parameter and field has a description;
   - no response description is a framework default reason phrase;
   - every status code with a body has a schema and an example;
   - error examples equal the messages the code returns.
7. **New docs** — at delivery, list every error message whose wording was rewritten, before and after, for the user to confirm.

### Review report and draft layout

| Part | Content |
|---|---|
| Opening | Audience, language, exposure analysis, the writing principles applied |
| One section per endpoint | Summary, description, path parameters, request schema and fields, each response description, response schema and fields, actual error messages, examples |
| Each row | Before, after, reason; a draft has no before column |
| Other | Only real decisions the user must make |

Mark dynamic parts of messages as `{name}`. Field names are part of the API contract: never change them, describe them.

Before handing in the report or draft, self-check:

- no hypothetical risks, such as "if a caller parses the message text";
- no items already judged to have no impact;
- no doc updates the user did not ask for, such as adding endpoint lists to a README.

## 9. Frameworks

For any framework, first locate where it takes each of these, then verify each in a viewer:

| Capability | Find |
|---|---|
| Operation summary, description, tags | The annotation or route metadata the generator reads |
| Parameter and field descriptions | Doc comments, annotations, or schema metadata |
| Examples | Field-level and whole-body example mechanisms, and which annotation forms the generator ignores |
| Response declarations | How each status code, its schema, and its description are declared |
| Document-level information | Title, description, tag descriptions |
| Document transforms | The hook for rewriting the generated document |
| Viewer settings | Document URL, menu name, page title |

Framework references hold only techniques verified in practice. Read the matching one when it exists:

- ASP.NET Core minimal API — [references/aspnetcore-minimal-api.md](references/aspnetcore-minimal-api.md)

## 10. Completion checklist

- [ ] Audience, language, and draft preview were confirmed, or defaults were stated when no answer was possible.
- [ ] Exposure analysis exists; hidden features are absent from always-on endpoints.
- [ ] Error messages were judged at least as strictly as the docs; exposure problems were flagged.
- [ ] No processing logic for an external audience; no internal components, operations detail, or secrets for any audience.
- [ ] Every text is glance-length; summaries have no parentheses or status codes; one language throughout.
- [ ] Enum values are literal with meanings; framework reason phrases replaced.
- [ ] Every return path was enumerated, including responses before the handler; the project's error design was documented, not restructured.
- [ ] Contract changes were listed as user decisions, not applied.
- [ ] Every status code with a body has whole-body examples per situation, matching real responses, using invented values.
- [ ] Every viewer was opened; document-level title, description, and tag descriptions exist; relative document URL.
- [ ] Revisions were reviewed before code changed; for new docs, rewritten error messages were listed at delivery for confirmation; field names unchanged.
- [ ] Tests lock the result when the project has tests.
