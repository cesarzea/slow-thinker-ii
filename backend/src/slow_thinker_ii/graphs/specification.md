# graphs: specification

Implements the [graph document](../../../../docs/contracts/graph-document.md):
validation with diagnostics and compilation into run plans. Pure domain code.

## Public interface (`slow_thinker_ii.graphs`)

```python
@dataclass(frozen=True)
class Diagnostic:
    severity: Literal["error", "warning"]
    code: str
    message: str                       # English sentence for users
    path: str                          # JSON Pointer into the document
    node_id: str | None
    def document(self) -> JsonObject   # {"severity", "code", "message", "path", "node_id"}

def validate_document(document: JsonValue, catalog: Catalog) -> tuple[Diagnostic, ...]
def has_errors(diagnostics: Iterable[Diagnostic]) -> bool

@dataclass(frozen=True)
class Limits:
    max_activations: int
    max_running_nodes: int
    time_limit_seconds: int
    budget_nanos: int

@dataclass(frozen=True)
class PlanComponent:
    declaration: ComponentDeclaration
    config: JsonObject
    llm_entries: frozenset[str]        # entry ids selected at its declared uses

@dataclass(frozen=True)
class PlanNode:
    id: str
    name: str
    kind: Literal["trigger", "output", "package"]
    host: PlanComponent
    embedded_output: PlanComponent | None
    embedded_memory: PlanComponent | None
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]           # effective outputs
    stateful: bool                     # true if the host or an embedded component is stateful

@dataclass(frozen=True)
class RunPlan:
    graph_id: str
    version: int | None                # None for a change never activated
    name: str
    limits: Limits
    nodes: Mapping[str, PlanNode]      # document order
    routes: Mapping[tuple[str, str], tuple[tuple[str, str], ...]]   # (node, port) -> targets in document order
    trigger_id: str
    def node(self, node_id: str) -> PlanNode

class GraphInvalid(ValueError):
    diagnostics: tuple[Diagnostic, ...]

def compile_plan(document: JsonValue, catalog: Catalog, version: int | None) -> RunPlan   # raises GraphInvalid
```

## Behaviour

- Validation follows the contract's table of codes exactly, in this order: JSON
  Schema (`invalid_document`; when present, no other check runs), identity and
  names, components and placements, configuration, service selections, ports and
  connections, trigger count, limits, warnings. Diagnostics are sorted by path,
  comparing array indices as numbers, then by code; identical diagnostics appear once.
- Configuration problems use the component's interface labels: for a field
  declared in `ui`, the message starts with its label, for example
  `Instructions is required.` Map JSON Schema keywords to plain sentences:
  `minLength` of 1 or `required` → “is required”, `type` → “has the wrong type”,
  `enum` → “must be one of …”, `minimum`/`maximum` → “must be at least/at most …”,
  `pattern` → “has an invalid format”, `maxLength`/`maxItems` → “is too long”,
  others → “is invalid”. Paths point to the exact value.
- Schema problems, their phrases and labels come from `catalog.schema_problems` and
  `SchemaProblem.label_of`.
- The label is that of the deepest `ui` field containing the value; otherwise a readable
  form of the last property name (`output_format` → `Output format`), or
  `Configuration` for the whole configuration. Service parameters use their schema
  `title`. `invalid_document` uses the same sentences with the graph's own field
  labels (`Graph name`, `Node name`, `Maximum activations`, `Budget per run`, …).
- An absent or `null` value at a declared `llm` use gives `service_not_selected` with
  the message `Select a model.` and no `invalid_config` for the same value. A
  selection other than `{"llm": <string>, "parameters": <object>}` gives
  `invalid_config` `<label> is invalid.` unless the schema already reported that value.
- Trigger and Output nodes accept no embedded components: each embedded component of
  such a node gets `placement_not_allowed` at its `component`, instead of that
  component's own availability and placement checks.
- Output names come from `output_ports`; configured names at `outputs_from` (host or
  embedded component) that violate the port name pattern or repeat give
  `invalid_port_name` at the item. That item, and the list's `uniqueItems` error, are
  not also reported as `invalid_config`; other list problems remain `invalid_config`.
- Connections at a node whose ports are unknown (its component is not available) are
  not checked. Any connection to a node counts as incoming for `unconnected_input`.
- A configuration schema whose references cannot be resolved gives `invalid_config`
  `Configuration is invalid.` at the configuration. Validation never fetches remote
  references.
- `node_id` names the node concerned: the node of the component, configuration or
  `/nodes/<i>` path, or the existing node at a connection end; graph-wide diagnostics
  have none.
- `compile_plan` uses the same validation and refuses any error;
  `GraphInvalid.diagnostics` holds the complete result, warnings included. `kind` is
  `trigger` or `output` for the platform components and `package` otherwise. `routes`
  contains every effective output port, with an empty tuple when unconnected. `nodes`
  and `routes` are read-only; configurations are copies of the document's.
- `budget_usd` is converted with `slow_thinker_ii.accounting.parse_usd`.
- `view`, optional and for presentation only, accepts only `connections` (`curved`,
  `simple` or `routed`), `curvature` (a number from 0 to 1) and `observe` (up to 1,000
  unique strings of 1–200 characters, the observed points), all optional; a bad shape or
  value is `invalid_document` at its path (labels `View`, `Connection style`, `Curvature`,
  `Observed points`). It never
  enters the run plan.
- `port_sides`, optional and for presentation only, maps at most 200 node identifiers to
  at most 64 port names (1–40 characters) with a side: `left`, `right`, `top` or
  `bottom`. A malformed shape or an unknown side is `invalid_document` at its path
  (labels `Port sides`, `Node port sides`, `Port side`, and `Port name` for a refused
  name). An entry naming a node that does not exist, or a port that is not one of the
  node's inputs or effective outputs, is the warning `unknown_port_side`; entries of a
  node whose components are not available are not checked. Port sides never enter the
  run plan.
- Every JSON Schema `pattern` (graph document, configuration schemas and LLM parameter
  schemas) follows ECMA-262: `$` matches only at the very end of the string, never
  before a final newline.

## Messages

| Code                           | Path                              | Message                                                                 |
| ------------------------------ | --------------------------------- | ----------------------------------------------------------------------- |
| `invalid_document`, `invalid_config`, `invalid_service_parameters` | The value | `<label> <sentence>.`                                     |
| `duplicate_node_id`            | `/nodes/<i>/id`                   | `Node identifier “<id>” is already used by another node.`               |
| `duplicate_node_name`          | `/nodes/<i>/name`                 | `Node name “<name>” is already used by another node.`                   |
| `unknown_component`            | `…/component`                     | `Component “<ref>” is not installed.`                                   |
| `placement_not_allowed`        | `…/component`                     | `<label> cannot be used as a node.`, `<label> cannot be embedded at the node's output.` (or `memory`) or `<host label> nodes cannot contain embedded components.` |
| `duplicate_embedding_position` | `…/embedded/<j>/position`         | `Only one component can be embedded at the node's output.` (or `memory`) |
| `service_not_selected`         | `…/config<pointer>`               | `Select a model.`                                                       |
| `unknown_service_entry`        | `…/config<pointer>/llm`           | `Model “<id>” is not available; select another model.`                  |
| `invalid_port_name`            | `…/config<outputs_from>/<k>`      | `<label> contains “<name>”, which is not a valid name. Names start with a lowercase letter and contain only lowercase letters, digits and underscores, up to 32 characters.` or `<label> contains “<name>” more than once.` |
| `trigger_count`                | `/nodes`                          | `The graph needs a Trigger node.` or `The graph has <n> Trigger nodes; keep only one.` |
| `unknown_port`                 | `/connections/<i>/from` or `/to`  | `The connection starts at node “<id>”, which does not exist.` (`ends` for `to`) or `<name> has no output “<port>”.` (`input` for `to`) |
| `wrong_port_direction`         | `/connections/<i>/from` or `/to`  | `A connection cannot start at the input “<port>” of <name>.` or `A connection cannot end at the output “<port>” of <name>.` |
| `duplicate_connection`         | `/connections/<i>`                | `The connection from “<from>” to “<to>” is repeated.`                   |
| `invalid_limits`               | `/limits/budget_usd`              | `Budget per run must be greater than zero.`                             |
| `unconnected_input`            | `/nodes/<i>`                      | `<name> has no incoming connection and never runs.`                     |
| `unconnected_output`           | `/nodes/<i>`                      | `Output “<port>” of <name> is not connected; messages sent there are discarded.` |
| `no_output_node`               | `/nodes`                          | `The graph has no Output node, so runs produce no results.`             |
| `unknown_layout_node`          | `/layout/<key>`                   | `The layout entry “<key>” does not match a node and is ignored.`        |
| `unknown_port_side`            | `/port_sides/<key>` or `/port_sides/<key>/<port>` | `The port sides entry “<key>” does not match a node and is ignored.` or `<name> has no port “<port>”; its side is ignored.` |

## Acceptance

- The three journey examples validate without errors and compile; J3's route
  `reviewer.revise` targets `proposer.in`.
- Every diagnostic code has at least one test producing it, with its exact message.
- An LLM Call created from `initial_config` produces `Instructions is required.` and
  `Select a model.`
- Branch coverage of the package is at least 90%.
