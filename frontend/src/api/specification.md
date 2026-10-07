# api: specification

Validated access to the [operator API](../../../docs/contracts/operator-api.md).

## Public interface (`api/index.ts`)

- `OperatorClient(credential: string | null)`: a `null` credential sends no
  Authorization header, for a server without operator authentication. `access()`
  reads `GET /access` as `Access {authentication: "token" | "none"}` and never sends
  the token. Graphs (ADR 0024), in `GraphClient`, which `OperatorClient` extends:
  `validate(document)`, `graphs()`, `createGraph(document)` → `{id, branch, change}`,
  `graph(id)`, `branches(id)`, `createBranch(id, name, {version} | {change})`,
  `saveChange(id, branch, document)` → `{change, at}` (a 200 for an unchanged document
  is accepted like the 201), `changes(id, {branch?, before?, limit?})`,
  `change(id, n)`, `activate(id, change)` → `{version, branch, change}` and
  `version(id, n)`. Runs and the rest: `catalog()`, `startRun(graphId, source, input)`
  with a `RunSource` `{version}` or `{change}`, `runs(graphId?)`, `run(runId)`,
  `runDocument(run)` (the document a run executed: its version's, or its change's when
  never activated), `events(runId, after)`, `stopRun(runId)`, `usage()`.
  Every method takes an optional `AbortSignal` and returns parsed, validated data or
  throws `ApiError`. There is no version-from-document save.
- `ApiError { status: number; code: string; message: string; diagnostics: Diagnostic[] }`
  and `errorMessage(error)`, the text to show for any thrown value.
- Wire types, each with a zod schema: `Access`, `ComponentDeclaration`, `UiSection`,
  `UiField`, `LlmEntry`, `Catalog`, `GraphDocument`, `GraphNode`, `Connection`,
  `Limits`, `Diagnostic`, `GraphSummary`, `GraphDetail`, `Branch`, `VersionSummary`,
  `ChangeSummary`, `ChangeRecord`, `Activation`, `RunSummary` (with `change`, and
  `version` null for a change never activated),
  `RunDetail`, `RunEvent`, `Usage`, and `BranchOrigin` for requests; the other reply
  types are the methods' return types. Shapes follow the contracts exactly; unknown
  fields are rejected. Change documents are read with the graph document schema.
- Observation points (ADR 0025): `PointId`, `NodeFacet`, `RUN_POINT`, `nodePoint(id,
facet)`, `connectionPoint(from, to)`, `isPoint(value)`, `nodeFacets(node, catalog)`,
  `documentPoints(document, catalog)` and `eventPoint(event)`, which places each recorded
  event at its connection (`message.sent`), its node's facet or the run.
- `observeAuthentication(credential, onInvalidated)` registers the connection told when
  the credential, or `null` for a connection without one, stops being accepted;
  `captureAuthentication`, used by the transport, stays internal.
- `EVENT_PAGE_LIMIT` (500), the page size of `events`.

## Behaviour

Port from `archive/s06-c11-wip`: `frontend/src/api/transport.ts`, `authentication.ts` and
`response-body.ts` (bounded reading for every response, including commands), and the
error-code table pattern of `definition-errors.ts`. Requests use `credentials: 'omit'`
and `cache: 'no-store'`; a 401 or 403 invalidates the credential.

- Base path `/api/v2`; bearer credential unless it is `null`; JSON bodies;
  `POST /runs/{id}/stop` sends `{}`.
- Each method expects the documented success status (200; `201` for creation,
  branches, changes and activation, where a change also accepts 200; `202` for runs and
  stop); any other status or a reply that fails its schema is `invalid_response`.
- Error replies must use the envelope `{"error": {"code", "message", "diagnostics"?}}`.
  Codes the operator API documents must arrive with their status (`graph_exists` and
  `too_many_runs` 409, `graph_not_found`, `version_not_found` and `run_not_found` 404,
  `invalid_document` 422); other codes keep the server's status and message. A 401 or
  403 without an envelope is `access_denied`.
- Transport failures are `network_error`, `timeout` (30 s) or `aborted` (status 0).
  Replies are read up to 4 MiB, event pages up to 64 MiB; larger replies are
  `response_too_large`. Malformed JSON or UTF-8 is `invalid_response`.
- A run summary's `totals` is `null` while the run has none; an empty object is read
  as `null`. Statuses and reasons are those of the execution contract.
- Event `data` is validated per kind as listed in the recording contract. Where the
  contract leaves a type open, the interface accepts: `llm.called.status` as an integer
  or a string, `usage` as `null` when unknown, `response`/`error` and `result`/`error`
  as optional alternatives, error objects as `{code, message, type?}`, `rates` as a map
  of decimal strings and `run.finished.dropped` as a count or a list of message ids.

## Acceptance

Unit tests against a fake fetch cover every method, schema rejection, bounded bodies,
error mapping and authentication invalidation.
