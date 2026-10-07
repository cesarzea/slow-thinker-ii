# Graph document, format 1

| Contract control | Value                                                                  |
| ---------------- | ---------------------------------------------------------------------- |
| Contract ID      | CORE-GRAPH-1                                                           |
| Format           | `slow-thinker.graph/1`                                                 |
| Schema           | [graph-document-1.schema.json](schemas/graph-document-1.schema.json)  |
| Decisions        | [ADR 0016](../adr/0016-graph-document-model.md), [ADR 0018](../adr/0018-derived-authorization.md) |
| Journeys         | [S06 journeys](../specification/s06-journeys/README.md), V01, V03, V07, V09, V10 |

A graph document is what the user builds and saves. It contains nodes, their
configuration, embedded components, connections, run limits and layout. It never
contains permissions, wrapper nodes or platform identifiers.

## Structure

| Field         | Type                                    | Rule                                                                 |
| ------------- | --------------------------------------- | -------------------------------------------------------------------- |
| `format`      | string                                  | Exactly `slow-thinker.graph/1`                                        |
| `id`          | string                                  | `^[a-z][a-z0-9-]{0,63}$`; immutable across versions                   |
| `name`        | string                                  | 1–120 characters, not only whitespace                                 |
| `limits`      | object                                  | See [Limits](#limits)                                                 |
| `nodes`       | array of [Node](#node)                  | 1–200 items                                                           |
| `connections` | array of [Connection](#connection)      | 0–2000 items                                                          |
| `layout`      | object                                  | Optional. Keys are node identifiers; values are `[x, y]` finite numbers |
| `port_sides`  | object                                  | Optional, presentation only. Keys are node identifiers; values map a port name (1–40 characters) to `left`, `right`, `top` or `bottom`. Ports not listed use the default: inputs on the left, outputs on the right |
| `view`        | object                                  | Optional, presentation only: `connections` is `curved` (default), `simple` (simple curve) or `routed` (around nodes); `curvature` is a number from 0 to 1 (default 0.25) for curved connections; `observe` lists the observation points run mode shows, up to 1,000 unique strings (see below) |

### Node

| Field       | Type                         | Rule                                                                        |
| ----------- | ---------------------------- | --------------------------------------------------------------------------- |
| `id`        | string                       | `^[a-z][a-z0-9_-]{0,63}$`, unique in the graph                              |
| `name`      | string                       | 1–80 characters, unique in the graph ignoring case                         |
| `component` | string                       | `type@major.minor.patch`, for example `llm-call@1.0.0`                      |
| `config`    | object                       | Validated against the component's configuration schema and declared uses   |
| `embedded`  | array of embedded components | Optional, 0–4 items; at most one per position                               |

An embedded component is `{"position": "output" | "memory", "component": "<type@version>", "config": {…}}`.
At `output` it chooses the port of each result; as `memory` the platform asks it, around
each activation, what the node receives and gives it what the node replied (see the
[component protocol](component-protocol.md)). A node may hold one of each.

### Connection

`{"from": "<node id>.<output port>", "to": "<node id>.<input port>"}`. Port names
match `^[a-z][a-z0-9_]{0,31}$`. A connection may target any node, including the
node it starts from.

### Limits

| Field                | Type    | Rule                                                        |
| -------------------- | ------- | ----------------------------------------------------------- |
| `max_activations`    | integer | 1–10000; counts every activation, including Trigger and Output |
| `max_running_nodes`  | integer | 1–64; concurrent activations in the run                    |
| `time_limit_seconds` | integer | 1–86400                                                     |
| `budget_usd`         | string  | Decimal greater than zero, at most nine decimal places      |

New graphs created by the editor start with 20 activations, 4 running nodes,
300 seconds and USD `"0.10"`.

## Effective ports

Ports come from [component declarations](component-declaration.md):

- A node's input ports are its component's declared inputs.
- A node without an embedded `output` component exposes its component's outputs.
- A node with an embedded `output` component exposes the embedded component's
  outputs instead, read from that component's configuration through its
  `outputs_from` pointer. The host component's own outputs are not visible.

## Validation

Validation is a pure function of the document, the installed component
declarations and the LLM catalog. It returns diagnostics; a document is valid when
no diagnostic has severity `error`. Only valid documents can be saved as versions
or run. The editor shows diagnostics continuously.

A diagnostic is `{"severity": "error" | "warning", "code": string, "message": string,
"path": JSON Pointer into the document, "node_id": string | null}`. Messages are
English sentences for users and use the field labels of the component's interface
declaration where a field is concerned, for example `Instructions is required.`

| Code                           | Severity | Condition                                                                      |
| ------------------------------ | -------- | ------------------------------------------------------------------------------ |
| `invalid_document`             | error    | The document does not match the JSON Schema                                    |
| `duplicate_node_id`            | error    | Two nodes share an identifier                                                  |
| `duplicate_node_name`          | error    | Two nodes share a name, ignoring case                                          |
| `unknown_component`            | error    | No installed or platform component has that type and version                   |
| `placement_not_allowed`        | error    | The component cannot be used as a node or embedded at that position, or the host is a Trigger or Output node, which accept no embedded components |
| `duplicate_embedding_position` | error    | Two embedded components use the same position                                  |
| `invalid_config`               | error    | Configuration violates the component's configuration schema                     |
| `service_not_selected`         | error    | A declared service use has no entry selected, for example no model             |
| `unknown_service_entry`        | error    | The selected entry is not in the platform catalog                              |
| `invalid_service_parameters`   | error    | Parameters violate the selected entry's parameter schema                       |
| `invalid_port_name`            | error    | A configured output name violates the port name pattern or repeats             |
| `trigger_count`                | error    | The graph does not contain exactly one Trigger node                            |
| `unknown_port`                 | error    | A connection refers to a node or port that does not exist                      |
| `wrong_port_direction`         | error    | A connection starts at an input or ends at an output                           |
| `duplicate_connection`         | error    | The same connection appears twice                                              |
| `invalid_limits`               | error    | The run budget is not greater than zero                                        |
| `unconnected_input`            | warning  | A node other than the Trigger has no incoming connection and never runs         |
| `unconnected_output`           | warning  | An output port has no connection; messages sent there are discarded            |
| `no_output_node`               | warning  | The graph has no Output node, so runs produce no results                       |
| `unknown_layout_node`          | warning  | A layout key does not match a node; it is ignored                             |
| `unknown_port_side`            | warning  | A `port_sides` entry names a node or port that does not exist; it is ignored  |

Diagnostics are ordered by path. Validation never launches components or calls
model providers.

## Versions

Saving a valid document creates the next version of its graph: versions are
numbered from 1, immutable and kept. The first save creates the graph. A run
records the graph identifier and version it executed. Unsaved edits exist only in
the editor; it may keep them in browser storage as a convenience.

## Examples

[J1](examples/funny-story.graph.json), [J2](examples/story-triage.graph.json) and
[J3](examples/funny-story-with-review.graph.json) are the documents of the
validated journeys.

## Observation points

`view.observe` names what run mode shows live, as strings: `run` (the run's start, end
and totals), `node:<id>/<facet>` for what a node records (`activity`, `calls`, `llm`,
`reports`, `output`, `memory` or `results`, by the event kinds of the
[recording](recording.md)) and `connection:<from>-><to>` for the messages a connection
carries, with `node.port` references. Points that no longer exist are ignored; a
`node:<id>` saved before facets stands for all of that node's facets. Without
`observe`, every connection is observed. Like `layout`, it never changes what a run does.
