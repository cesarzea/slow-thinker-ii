# Graph and execution projections

Implementation additions for the approved first-cycle visual and operator contracts.
Existing command, evidence and budget wire contracts remain compatible; the server retains authenticated bounded snapshots.

## Definition detail

`GET /api/v1/graphs/{graph_id}/revisions/{revision}` returns:

```typescript
type GraphDetail = Readonly<{
  graph_id: string;
  revision: string;
  input_schema: Readonly<Record<string, unknown>>;
  definition: Readonly<Record<string, unknown>>;
  structure: GraphStructure;
}>;
type GraphStructure = Readonly<{
  components: readonly ComponentView[];
  nodes: readonly PlannedNodeView[];
  edges: readonly RelationshipView[];
}>;
type ComponentView = Readonly<{
  id: string;
  type_id: string;
  type_version: string;
  roles: readonly string[];
  contained_by: string | null;
}>;
type PlannedNodeView = Readonly<{id: string; component: string}>;
type RelationshipView = Readonly<{
  id: string;
  kind: 'control' | 'permission' | 'binding';
  source: string;
  target: string | null;
  label: string;
}>;
```

Control-edge endpoints are planned node IDs; permission/binding endpoints are
component IDs. `null` denotes a declared terminal exit. Prefix renderer identities
by kind to avoid collisions between a node and component with the same name.
The saved `/runs/{run_id}/definition` projection returns all GraphDetail fields
alongside the existing `schema_version`, `run_id` and `execution` fields. Preserve
the existing `execution` envelope; the additional `graph_id`, `revision`,
`definition`, `input_schema` and `structure` come from the admitted snapshot, not
a mutable current catalog record.

Add `input_schema` to graph summaries without removing existing fields. Validate
definitions and projections on both sides; do not execute schemas or evaluate UI
code from a graph. A simple object-schema form handles the bundled examples;
validated JSON input handles supported schema shapes beyond the simple form.
This is run input, not graph editing or file upload. The first-cycle Start API
accepts a JSON object at the root; nested arrays, values and objects remain governed
by the selected schema. Reject root strings, arrays and null visibly before dispatch.

## Live execution projection

`GET /api/v1/runs/{run_id}/execution` returns one bounded consistent page:

```typescript
type ExecutionPage = Readonly<{
  run_id: string;
  graph_revision: string;
  backend_generation: string;
  through_sequence: number;
  activations: readonly ActivationView[];
  calls: readonly CommunicationView[];
  next_cursor: string | null;
}>;
type ActivationView = Readonly<{
  id: string;
  node: string;
  component: string;
  ordinal: number;
  state: string;
  call_id: string;
  selected_port: string | null;
}>;
type CommunicationView = Readonly<{
  id: string;
  caller: string;
  target: string;
  operation: string;
  parent_call_id: string | null;
  activation_id: string | null;
  state: string;
}>;
```

Use stable run-scoped IDs and the existing signed cursor/snapshot rules. Bound
combined entries, never silently drop excess activations or calls. The frontend
loads additional pages explicitly or incrementally and preserves their fixed
snapshot boundary. Fresh polling starts a new snapshot; never mix pages from
different boundaries. Share the selected run's polling lifetime and discard stale
responses. Retain existing money fields and detailed evidence routes as authoritative.

## Internal reports

Add a bounded `reports` array to activation/call detail. Each record has integer
`event_sequence`, string `kind` and `schema_version`, `evidence: "reported"`,
`payload_id: string | null` and `source_occurred_at: number | null`. A missing
source timestamp is represented by null. Follow payload references through the
existing captured-content route.
An empty report collection means no report was supplied; display unavailable
reasoning explicitly rather than an empty transcript. Protocol/host diagnostics
retain their category and do not become provider attempts.

## Frontend public contracts

The API module exports GraphDetail, GraphStructure, ExecutionPage and their record
types, plus validated OperatorClient.graph, definition and execution methods.
Graph/definition reads require exact identities and AbortSignal; execution also
accepts an optional cursor like the existing evidence methods.

The inspector exports `InspectionSelection`, a discriminated union with `kind`
`call`, `activation` or `payload`, and an `id`. Add optional `selection` to Inspector
while preserving its current credential/run inputs. The app bridges graph callbacks
to this selection; graph-view never imports inspector internals or vice versa.

GraphView retains its current `graph` fallback and adds optional `detail`,
`execution` and `onSelect` props. The callback emits `{kind, id}` for `component`,
`node`, `activation` or `call`; it has its own public graph-view type. The app
resolves component/node selection to a list/configuration summary and opens exact
activation/call evidence without substituting another activation silently.

## Acceptance

Show structure before execution and distinct actual activations while running.
Keep control, permission, resource binding and observed communication layers
separate. Display contained components on expansion while preserving main agent
identity. Provide list/keyboard navigation as well as canvas selection. Preserve
positions on status changes, allow explicit reorganization, and never confuse a
redacted/unavailable payload with an empty value. Verify existing inspector focus
behavior, bounded-loop routes, repeated participants, paging and reconnection.
