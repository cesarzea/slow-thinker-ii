# Experiment collection, versions and preview APIs

**S06-UX-API / revision 2 / 2026-10-02.** Owner-authorized implementation; locally verified.
Extends [personal experiments](personal-experiments.md) and
[operator reads](operator-api.md); retains their auth, same-origin, no-store,
bounded-body, error-envelope and exact-number requirements.

## Identity, metadata and compatibility

`GraphReference = {graph_id: string, revision: string}` remains exact and opaque.
An experiment groups revisions by `graph_id`. `derived_from` records an exact
parent and can point to a different experiment. Never infer ancestry or numeric
ordering from revision text. Library chronology uses insertion sequence, not labels
or wall-clock order. Bundle ordering is the trusted catalog's stable order only.

Optional graph `extensions["slow-thinker:display"]` contains `version: 1`, `name`
(1–160 characters), `description` (0–2000), `revision_note` (0–2000), and optional
`components`/`nodes` dictionaries of existing IDs to `{name: string}` with the same
name bound. All fields except version are optional. Validate this known namespace
without rejecting other namespaces. Missing names display exact IDs, not invented
human names. Runtime identifiers, semantics and layout remain unchanged. Editing
these saved metadata fields creates a revision like any other definition change.

This namespace is optional in existing graph schemas. Backend library validation
owns its known shape; preview/save reject malformed known metadata with a pointer.
No implicit metadata migration rewrites historical graph JSON. Components' immutable
type versions are independent of graph revisions and of these display labels.

## New reads and application ports

Prefix every route with `/api/v1`. Unknown/repeated query fields, malformed filters,
altered cursors and `limit` outside 1–100 return `invalid_query` (422). Default limit
is 50. Read responses use `schema_version: "1"`; existing endpoints keep their
existing schemas. `q` is optional, trimmed, at most 200 characters, matched
case-insensitively against graph ID, selected display name and description.

| Route                       | Parameters / response                                                                                       |
| --------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `GET /experiments`          | `q?`, `limit?`, `cursor?`; ExperimentPage                                                                   |
| `GET /definitions/versions` | `graph_id`, `limit?`, `cursor?`; VersionPage                                                                |
| `GET /definitions/compare`  | `base_graph_id`, `base_revision`, `target_graph_id`, `target_revision`, `limit?`, `cursor?`; ComparisonPage |
| `POST /definitions/preview` | Raw bounded draft JSON; PreviewResult, without saving, launching components or reserving identity           |
| `GET /experiments/runs`     | `graph_id`, `revision?`, `cursor?`; ExperimentRunPage using the existing operator page-size bound           |

Preserve old definition list/detail/source/draft/save routes and session history.
All new reads require existing operator authority; viewer mode retains its existing
read-only catalog path and clearly unavailable editing/history controls.

Application `library` owns ExperimentPage, VersionPage and ComparisonPage records
and exposes these additions on `ExperimentLibrary`:

Its constructor retains existing positional arguments and accepts keyword-only
`response_limit: int = 1048576`. Bootstrap supplies the configured HTTP response
ceiling; nonpositive limits are invalid. Comparison pages fit that ceiling or
return the existing explicit `response_too_large` failure.

```python
def experiments(self, query: str = "", limit: int = 50,
                cursor: str | None = None) -> ExperimentPage: ...
def versions(self, graph_id: str, limit: int = 50,
             cursor: str | None = None) -> VersionPage: ...
def compare(self, base: GraphReference, target: GraphReference,
            limit: int = 50, cursor: str | None = None) -> ComparisonPage: ...
def preview(self, source: str) -> PreviewResult: ...
```

`PreviewResult` carries `detail_json: str | None` plus existing DefinitionIssue
values. It uses the injected DefinitionValidator, not concrete catalog imports.
Malformed JSON returns `invalid_json` (400); semantically incomplete/invalid drafts
return 200 with null detail and bounded issues. Valid drafts return the existing
GraphDetail wire shape, using static validation only. Failure is not readiness to run.
The HTTP envelope is `{schema_version: "1", detail: GraphDetail | null, issues:
DefinitionIssue[]}`. `detail_json` remains application-internal; HTTP embeds the
validated detail object. Issues retain their existing pointer/message bounds.

Extend the public DefinitionRepository with `latest(graph_id, through)`,
`experiment_page(query, after_graph_id, through, limit)` and
`version_page(graph_id, before_sequence, through, limit)`. Graph/query/after-ID arguments are strings; before_sequence and through are
int-or-None; limit is int. An empty after_graph_id starts collection paging; a null
before_sequence starts newest-first version paging. `latest` receives a captured
non-null through value. Store projections use
`StoredRevision(reference, definition_json, sequence, saved_at)`; `saved_at` is
nullable Unix seconds. Collection pages return immutable records
`StoredExperiment(latest: StoredRevision, revision_count: int)`, one per graph ID,
plus `through`, `last_graph_id`, `has_more`. The count covers personal rows within
that window; application adds eligible bundled counts. Version pages return revisions plus
`through`, `last_sequence`, `has_more`. A null `through` captures MAX(sequence);
later calls honor it. `latest` returns a record or None within that window.
Keep existing read/insert/page port signatures compatible. Database/HTTP types
never cross these ports. Explicit immutable dataclasses belong to application.library.

`OperatorQueries.experiment_runs(graph_id: str, revision: str | None,
cursor: str | None) -> str` supplies JSON using existing operator projections.
It returns an empty page for no matching runs, including missing definitions;
the library separately determines definition availability. All filters bind the
cursor. Existing `session_runs`, command, settlement and recovery behavior is unchanged.

## Collection and version payloads

```json
{
  "schema_version": "1",
  "items": [
    {
      "graph_id": "workshop-planner",
      "name": "Workshop planner",
      "description": "A proposal and review experiment.",
      "selected_revision": "r-20261002-example",
      "origin": "personal",
      "saved_at": 1790942400,
      "participants": 2,
      "revision_count": 3
    }
  ],
  "next_cursor": null
}
```

Times and counts above are illustrative wire values.
Absent display description becomes an empty string; absent revision_note becomes
null. No inferred description or revision note is generated.

Collection chooses the most
recent personal insertion at the captured boundary. If none exists, choose the
first trusted bundled revision and label it Template, not Latest saved. Count all
distinct exact identities in that experiment. Search uses that chosen revision's
metadata, over the complete collection. Sort by graph ID ascending for stable
paging; visual column sorting and last-run summaries are outside this delivery.

```json
{
  "schema_version": "1",
  "graph_id": "workshop-planner",
  "items": [
    {
      "graph_id": "workshop-planner",
      "revision": "r-20261002-example",
      "origin": "personal",
      "saved_at": 1790942400,
      "derived_from": {"graph_id": "workshop-planner", "revision": "example-2"},
      "revision_note": "Clarify the review criteria."
    }
  ],
  "next_cursor": null
}
```

Personal versions appear newest insertion first, then bundled templates in stable
catalog order. Null saved_at is displayed as unavailable, never migration time.
No author field is invented; authentication does not currently supply an identity.
Unknown graph IDs return `definition_not_found` (404) for version/definition reads.

A signed cursor binds route kind, filters, page size, personal upper sequence,
last position and bundled-catalog fingerprint. Changing any invalidates it. New
saves require Refresh to appear; duplicates or omitted entries cannot be hidden by
client filtering. Collection merges ordered personal IDs and eligible bundled IDs;
a personal latest revision suppresses that experiment's bundled row before search.
Fetch enough bounded windows to produce limit+1 unique IDs, never an unbounded
client-side scan. Bundle fingerprint changes invalidate the paging window.

## Comparison semantics

Compare saved sources through exact references. Recursively compare object keys in
Unicode code-point order; preserve array order and treat a changed array as one
replacement. Canonical encoded values determine equality, preserving integers and
distinguishing `1` from `1.0`. Do not compare using JavaScript numeric conversion.
Emit leaf add/remove/replace entries ordered by JSON Pointer; escape `~` and `/`.
An added/removed object is one subtree entry. No inferred rename or generated LLM
summary is involved. Compare root identity/lineage/metadata too, in a distinct group.

```json
{
  "schema_version": "1",
  "base": {"graph_id": "workshop-planner", "revision": "example-2"},
  "target": {"graph_id": "workshop-planner", "revision": "r-20261002-example"},
  "items": [
    {
      "pointer": "/components/reviewer/config/instructions",
      "kind": "replace",
      "before": {"present": true, "omitted": false, "value_json": "\"Review the plan.\""},
      "after": {"present": true, "omitted": false, "value_json": "\"Check every requirement.\""}
    }
  ],
  "next_cursor": null
}
```

Missing values use present=false and null value_json; actual JSON null is the
string `"null"`. Cap each side's encoded UTF-8 value at 4096 bytes; larger values
use present=true, omitted=true, value_json=null, with exact source reads available.
Reduce page size when necessary to respect the existing response-byte ceiling;
continue at the last emitted pointer. Never silently truncate values or invent an
empty result. Cursor binds both references, immutable source digests and position.
No changes yields an empty complete page. Missing references return 404.
UI groups changes by pointer into agents, resources, flow, permissions and metadata;
the exact pointer/kind/value remains available for unsupported shapes.

## Experiment runs, source fidelity and failures

ExperimentRunPage returns `schema_version`, `graph_id`, `revision` (nullable),
`backend_generation`, `items` and `next_cursor`. Items are the existing full
run-summary shape: run/session/graph identities, state, reason, created_at, cleanup,
event sequence and exact budget. Query the saved snapshot's intent.graph_id and
managed run.graph_revision, never the edited graph. Sort operator insertion position
descending. Signed cursor fixes upper position and binds graph/revision filters;
run statuses remain current per page, not an invented immutable event snapshot.

Frontend API adds `OperatorClient.resultSource(runId, signal)` returning bounded
original response text after status/schema/run-identity validation. Existing parsed
result APIs may remain for compatible callers, but must not supply an Original JSON
view. Render numeric values through the existing exact source parser in `ui`.

Definition routes reuse DefinitionError; new malformed known display metadata maps
to `invalid_definition` (422) with a pointer. Read transport failure is retryable;
it is not a save or run failure. Responses from obsolete identity/request generation
are discarded. Large-response errors remain explicit. Source/compare/preview reads
cannot insert definitions, mutate budgets or contact providers.

## Persistence and admission compatibility

Migration 8 adds nullable `personal_definitions.saved_at` (REAL) and useful indices
for experiment/sequence reads; do not rewrite definition_json or parent references.
Inject a wall clock into SqliteDefinitionRepository. Assign saved_at only during a
new insertion, in the same transaction; replay keeps its original time/sequence.
Legacy and bundled timestamps remain null. Retain backup verification, rollback and
forward-version rejection. Review any snapshot-expression index against the actual
stored envelope; no new graph ID is inferred for missing legacy intent metadata.

The repository may query metadata directly from validated definition JSON rather
than add a mutable experiment table. No branch merge, destructive restore, revision
deletion or user attribution is introduced. Saved-run snapshots, cost ledgers and
component installation hashes remain untouched.

## Delivery checkpoint — 2026-10-03

The owner-authorized S06 implementation and unchanged mandatory verification are
complete. The [current sprint report](../progress/sprint-06-status-report.md)
records acceptance evidence and preserved compatibility. Contract revision numbers
and runtime/accounting requirements are unchanged; owner usability review is separate.
