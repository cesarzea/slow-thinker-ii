# Personal experiment library

Status: Implementation contract for the authorized S03 scope. The canonical
[graph schema](schemas/graph.schema.json) and existing execution contracts remain
unchanged. This document closes the interactions required by
[S03](../specification/personal-experiments-sprint.md).

## Definitions, identities and lineage

- A definition is the raw domain graph, not its structural or execution projection.
  `graph_id` and nonempty `revision` remain exact schema-defined strings. Revisions
  may contain Unicode, slashes or spaces; HTTP reads use query parameters. Start
  must not impose the old revision regex or 128-character restriction.
- Strict UTF-8 JSON rejects duplicate keys and nonfinite numbers. Canonical equality
  uses the existing `encode_json` output, including its numeric representation.
- Bundled definitions remain trusted files; personal definitions are append-only
  SQLite rows with a unique `(graph_id, revision)` key and insertion sequence.
  Identical canonical saves replay successfully; different content at an occupied
  identity returns `definition_conflict`. Bundled identities follow the same rule.
- Optional `derived_from` identifies an existing bundled or personal parent. Reject
  a missing parent or self-reference. Check personal parent existence and insertion
  atomically. Immutable existing parents make lineage cycles impossible.
- A changed version or manual variant uses a new revision. No replace/delete API
  is introduced. Existing admitted runs and installation snapshots are unchanged.

## Validation boundary

Static validation checks the canonical graph/schema, declared input/configuration
schemas, exact registered type versions, component containment, controller role,
operation/resource/permission references, supported profile, route/step coverage,
node references and JSON Pointer syntax. Sequence output references must be
backward; conditional references obey the existing latest-completed profile.
Validate literal values where their declared input schema is available. Registry
resolution must remain local; validation starts no component or provider calls.
For components using the documented LLMCall configuration, reject the reserved
`parameters` fields listed in the [public LLMCall contract](llm-call.md): `model`,
`messages`, `stream`, `response_format`, `n`, `base_url`, `api_key`, `timeout` and
`max_retries`. SDK-dependent support for other generation options remains installed
preflight validation; the static validator must not reconstruct a private SDK matrix.

Descriptor contracts are the save-time authority. Installed effective contracts,
run-input values, trusted provider/limit profiles, tariff freshness, budgets and
actual availability remain execution preflight checks. A valid saved definition
is not a promise that a future invocation will succeed. Diagnostic pointers and
fixed messages identify errors without echoing values, secrets or exceptions.

## Operator routes and wire values

These routes are installed only with explicit execution configuration and inherit
operator authentication, origin/host rules and `no-store` behavior. Unconfigured
viewer routes continue exposing bundled graphs only. Existing `/graphs` routes
remain compatible. Successful responses use the configured representation size
bound. Error envelopes have an independent maximum of 4096 UTF-8 bytes so that
even a small configured payload limit permits a valid diagnostic response.

| Method and path | Contract |
| --- | --- |
| `GET /api/v1/definitions?limit=50&cursor=...` | Bounded library page; default 50, range 1–100. |
| `GET /api/v1/definitions/detail?graph_id=...&revision=...` | Existing `GraphDetail` for the exact identity. |
| `GET /api/v1/definitions/source?graph_id=...&revision=...` | Exact domain JSON text, canonicalized without changing numeric values; no projection envelope or view token. |
| `POST /api/v1/definitions/draft` | Source/target identities; returns an unsaved domain JSON variant without inserting or reserving an identity. |
| `POST /api/v1/definitions/validate` | Raw graph JSON; successful validation result below. |
| `POST /api/v1/definitions` | Raw graph JSON; 201 on insert, 200 on identical replay. |

Example validation response:

```json
{"graph_id":"single-agent","revision":"personal-1","validation_scope":"definition"}
```

A draft request contains exactly these two identities:

```json
{"source":{"graph_id":"single-agent","revision":"example-2"},"target":{"graph_id":"single-agent","revision":"personal-1"}}
```

The draft operation reads the exact saved source in the backend, changes only
`graph_id`, `revision` and `derived_from`, then performs existing static validation.
Its successful response is the canonical graph text with JSON content type and
`no-store`; it does not save the document. The target must differ from the source.
Malformed identities/body or self-derivation return `invalid_definition`/422;
an unknown source returns `definition_not_found`/404. Occupied target identities
remain Save's authority. Source reads use the same strict query rules as detail.
Both routes retain all configured transport, authorization and response bounds.

Example save response:

```json
{"graph_id":"single-agent","revision":"personal-1","created":true}
```

A page is `{ "items": [...], "next_cursor": null }`. Each item has the existing
GraphSummary fields (`graph_id`, `revision`, `participants`, `nodes`, `input_schema`),
plus `origin` (`bundled` or `personal`) and nullable `derived_from` identity.
Bundled entries come first in their existing order; personal entries follow their
insertion sequence. A signed cursor fixes the initial personal upper sequence,
bundle position and last personal sequence; new saves do not enter later pages.
Cursors are valid for the backend process; after a restart, begin a fresh listing.
Page size and cursor bindings must be validated rather than silently clamped.

POST bodies preserve original JSON text, have the configured payload byte bound,
require JSON content type; reject query options as invalid_query/400 and content
encoding as unsupported_transport_options/400. Duplicate/non-JSON Content-Type uses
json_content_required/415. GET rejects
unknown/duplicate query fields. Apply complete-response bounds rather than truncate.
Error envelopes retain `schema_version`, `error.code`, fixed `error.message` and
`request_id`; invalid-definition errors may add at most ten `error.issues`, each
with `pointer` and a fixed message (maximum 160 characters each).
Remove trailing issues until the complete error envelope fits its 4096-byte limit;
never truncate encoded JSON. A save response may fail after insertion. Transport
failure, `response_too_large` and `operator_service_unavailable` therefore leave the
save outcome uncertain and require identical-source replay for confirmation.

| Error | HTTP status |
| --- | --- |
| `invalid_json`, `invalid_query`, `invalid_cursor`, `unsupported_transport_options` | 400 |
| `definition_not_found` | 404 |
| `definition_conflict` | 409 |
| `request_too_large`, `response_too_large` | 413 |
| `json_content_required` | 415 |
| `invalid_definition`, `definition_parent_missing` | 422 |
| `operator_service_unavailable` | 503 |

Authentication/authorization failures retain existing 401/403 behavior. Unexpected
failures use the stable service-unavailable response, never internal messages.

## Public implementation boundary

The public `application.library` namespace owns immutable records, repository and
validator ports, and `ExperimentLibrary`. It is exported through the application
entry point. Consumers use `from slow_thinker_ii.application import library` rather
than application internals. Its skeleton signatures are authoritative.

`ValidatedDefinition` carries `GraphReference`, canonical `definition_json`, optional
parent and `GraphSummary`. `DefinitionRepository.read` returns canonical text or
None; `insert(document, parent_is_bundled)` returns created/replayed, with conflict
and lineage checks in one transaction. `page(after, through, limit)` returns ordered
canonical definitions, fixed through sequence, last sequence and `has_more`; zero
limit permits obtaining a boundary while a page contains only bundled entries.
`GraphDefinitionValidator` implements validate and detail from registered public
descriptors and local schemas. `ExperimentLibrary` combines the trusted bundled
source, repository and validator; its definition reader is used by both selection
and `InstalledWorkflowPreparer`. Composition can create equivalent reader instances
against the same database and immutable bundled files; constructors perform no I/O.

`ExperimentLibrary.draft(source: GraphReference, target: GraphReference) -> str`
returns the validated canonical unsaved variant. Numeric values remain Python
JSON values throughout source loading, identity changes and serialization; a
browser JSON parse/stringify round trip must never construct authoring source.

SQLite migration v6 adds only the personal-definition table/index/lineage columns.
Retain the existing verified pre-migration backup and transactional migration rules.
No migration changes existing run, call, receipt, budget or installation records.

## Browser interaction

The API exports `DefinitionClient` plus typed `GraphReference`, `LibraryItem`,
`LibraryPage`, `ValidationResult` and `SaveResult`. `list(signal, cursor?, limit?)`,
`detail(reference, signal)`, `source(reference, signal)`,
`draft(reference, target, signal)`, `validate(source, signal)` and `save(source, signal)`
use the routes above and validate replies. Raw POST source must not pass through
JSON.parse/stringify, so duplicate properties remain rejectable by the backend.
`source` and `draft` return the original successful response text after checking
status 200, JSON content type and the exact returned identity. Parsing for those
checks must not replace the returned text. Draft request serialization is safe
because it contains identity strings only. GraphDetail remains a canvas projection.
A `DefinitionError` exposes a stable code and bounded issues, with generic transport
errors for unconfirmed saves. Preserve old OperatorClient.graph for viewer reads.

Connected experiment selection uses the paged library and keys by both identity
fields, using a collision-free encoding such as JSON.stringify([id, revision]).
Refresh explicitly; load more within the same cursor boundary. Disconnect clears
personal library/editor state. Viewer selection keeps the bundled endpoint.

The definition editor uses an explicit local cap of 1,048,576 UTF-8 bytes for
imported files and submitted text. Display that cap; backend configured limits
remain independently authoritative and may be smaller. The editor imports a
UTF-8 JSON file, loads saved source through `DefinitionClient.source`, edits text, validates,
saves and creates a new revision/variant from the selected saved definition.
A variant sets `derived_from` to its exact source and defaults to a fresh revision;
its JSON remains editable. Create it through `DefinitionClient.draft`, never by
reserializing the browser's parsed definition. Draft generation is abortable and
freezes editing while pending; discard stale replies after identity/access changes.
Show validation errors, dirty state and saved identity.
Do not persist source or credentials in browser storage. Disable Start while an
editor draft is dirty, with an explanation; run selection always uses saved JSON.
Graph/source changes and credential changes discard stale read/validation replies.

Save freezes the source while pending. After an uncertain reply, expose recovery
by replaying exactly that source (idempotent), rather than claiming it was not saved
or creating another identity. Save success refreshes/selects the returned exact
revision. Until that selection changes, restore the original selected source as
the editor baseline; a confirmed saved identity remains separately visible. The
editor must not present a new source as the baseline of the old selected identity.
A discarded draft never changes a saved graph or its previous runs.
After a confirmed save, selection may automatically load successive bounded pages
from a fresh listing snapshot until the exact identity appears. Ordinary refresh
and load-more actions remain explicit. Stop at an exhausted or repeated cursor,
and cancel on superseding selection/save actions or credential changes. A listing
failure retains the confirmed saved identity and offers refresh recovery; it must
not turn the successful save into a failed save or invent summary metadata.

## Verification and ownership

Backend owns application library, catalog validator, SQLite migration/repository,
preparation and bootstrap. Boundary owner owns HTTP and frontend API, including
Start's schema-compatible identity fields. Browser owner owns editor, app selection,
execution gating and frontend tests. Root owns shared contracts, location policy,
review and delivery/process records. No overlapping source ownership.

Testing follows development/review. Acceptance includes import/edit/save/reload,
idempotent concurrent saves, conflicts with bundled/personal revisions, lineage,
stable paging across new saves, malformed/duplicate/oversized bodies, authorization,
unsafe diagnostics, all profiles, unusual revision strings, uncertain save recovery,
credential/selection races and unchanged historical runs. Include a representative
composition with `1.0` and `9007199254740993` to verify lossless source replay and
draft creation. Check that a listing failure after Save leaves a subsequent draft
and its parent consistent with the still-selected saved definition. Run one representative
composition first; then expand tests in parallel and run all mandatory gates.
A saved personal graph must execute through production preparation with simulated
provider fixtures; no paid demonstration is required.
