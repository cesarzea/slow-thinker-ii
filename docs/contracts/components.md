# Component contract

**Status: Proposed detailed contract.** R02–R03, R05–R06, R08–R10; [ADR 0004](../adr/0004-component-packaging.md), [ADR 0005](../adr/0005-versioned-contracts.md). Independent local processes and familiar outgoing calls through the orchestrator are accepted requirements from the first cycle; the manifest and lifecycle details below remain under review.

## Identity and composition

| Entity | Identifier | Meaning |
| --- | --- | --- |
| Type | `type_id` + `type_version` | Exact implementation contract selected by a graph. |
| Instance | Key in the graph's `components` map | Configuration and resource bindings for one participant. |
| Node | Key in `nodes` | Addressable use of an instance operation. |
| Activation | Platform-assigned runtime ID | One scheduled use; never inferred from the instance or node ID alone. |
| Process | Local deployment identity | May serve instances according to the approved hosting contract. |

Configured instance identity is independent of Python object lifetime. The initial stateless LLMCall host reuses its process while constructing a fresh implementation object and scoped client per invocation, as proposed in the [lifecycle contract](component-lifecycle.md#invocation-and-reuse). This does not impose the same object lifetime on all resource or stateful component types.

Types may declare multiple roles. The initial examples use agent, resource and control roles. Later collaboration and analyzer roles use the same extension concept; the initial executor must reject unsupported roles or behaviors explicitly.

## Implementation inheritance and versions

The owner confirmed optional single implementation inheritance through code for the first cycle, with either an exact base version or a compatible same-major range. [ADR 0008](../adr/0008-component-inheritance-and-versions.md) proposes ordinary Python subclassing, a packaged public extension API and exact dependency resolutions retained with each run. A and its base B have independent version numbers. Configuration of two instances of one type does not itself create an inheritance relationship.

The graph continues to identify an exact component release. Any permitted range belongs to the component's package dependency declaration; its resolved base versions and artifacts must also be recorded. The [registration proposal](component-installation.md) records the base relationship and checks it against the installed code. Detailed metadata, override and resolution rules remain under review in Q20.

The [LLMCall contract](llm-call.md), type ID `llm-call`, specifies one logical model call through the orchestrator with configurable instructions, input schema, generation options and text/JSON output. [ADR 0010](../adr/0010-llm-output-validation.md) accepts explicit validation failure with retained response and no implicit repair. Candidate configuration/result schemas, typed Python hooks, four updated graphs and a derived code specimen are available for Q13/Q20 review. Other implementations may expose different operations through the same platform contracts.

## Proposed manifest fields

| Field | Rule |
| --- | --- |
| `schema_version` | Exact application manifest revision; currently `0.1-draft`. |
| `type_id`, `type_version` | Stable type name and exact version; no floating version selection in a run. |
| `roles` | Non-empty capability categories. A role is not an access grant. |
| `operations` | Named operations with object input/output schemas and an MCP tool mapping. Configurable types such as LLMCall specialize effective instance schemas before discovery and invocation. |
| `config_schema` | Schema for configured instance options; validated independently of invocation inputs. |
| `resource_slots` | Required role, whether a slot is mandatory, and optional `operations` naming required resource operations. |
| `execution` | Declared state scope and concurrency mode. Actual scheduling support must be checked. |
| `billing` | `none`, `mediated`, or `metered`; a declaration, not proof that a charge is bounded. |
| `extensions` | Explicit metadata extension boundary; no implicit executable behavior. |

See [the manifest schema](schemas/component.schema.json) and [LLMCall example](examples/llm-call.component.json). [Trusted registrations](component-installation.md) propose public class/package mappings; process commands, credentials, environment allowlists and SDK versions remain part of the installation profile. They must not be executable strings supplied by arbitrary graph data.

## Operations and mediation

The platform maps an authorized operation to its MCP tool and validates input/output at the boundary. Operations keep their component-specific shapes; the system does not force every agent to accept a universal conversation object.

An agent that consumes a bound model resource calls the platform, not that resource directly. Native provider options must not disappear silently when translated through an adapter. The exact supported subset of each compatibility interface must be documented.

Component authors must be able to keep the supported invocation signatures of their usual clients. Platform connection setup or a compatible adapter supplies routing and scoped authority without adding platform-specific mandatory arguments to ordinary model/tool calls. Identity and parent-activation correlation must survive the process boundary and be validated by the platform. Their exact propagation mechanism remains Q06.

The [compatibility proposal](mcp-profile.md#familiar-client-interfaces) covers outgoing model calls, authorized agent/tool/resource calls, and use inside LangGraph nodes. These calls enter the same authorization, deadline, accounting and observation path as native MCP calls. Component operations remain exposed through MCP; the client-facing compatibility syntax does not change that contract.

## Resource and memory binding

Instance configuration binds a declared slot to a resource instance ID. Two agents can bind to one resource for deliberate sharing or to two instances of the same type for isolation. A packaged default resource may be part of a component definition, but effective managed instances and bindings must still be resolved and recorded.

Tools, memory and context providers use these component and operation boundaries. Their managed calls pass through the platform with the same permissions, evidence, deadlines and applicable cost accounting. Each component decides when to invoke a resource and which returned information to include in subsequent calls; granting access does not automatically inject memory or tool results into prompts. Model-requested tool execution and any further model calls require an explicit component/control policy.

A component may also implement private memory inside its own code. This is internal state rather than a separately managed resource: it must respect the declared lifecycle, and only exposed instrumentation is observable. The contract does not force every memory implementation into a shared service.

Resource sharing, state persistence and process reuse are separate decisions. A private memory may be persistent, and a shared memory may last only for one run. A stateless agent can use a stateful resource without retaining private conversation state. Stopping its host must not implicitly reset or delete that resource's durable data.

New runs start with fresh managed state unless reuse/persistence is explicitly configured. The initial fixture binds stateless agents to a model resource. Tools and memory are near-term extensions to this starting profile, as clarified by the owner on 2026-09-28. Specific implementations and persistent-state semantics remain later functionality; Q05/Q17 must close the binding and ownership rules. Current schema fields do not yet constitute a complete persistent-resource lifecycle contract.

## Concurrency

The initial declared mode is `independent` with state scope `none`. Other candidates include instance serialization and explicitly partitioned state. The schema can describe candidates, but the first executor is required to reject combinations it cannot honor. A graph cannot configure concurrency beyond a type's supported capabilities.

State sharing is never inferred from MCP connection reuse. Whether independent activations receive fresh processes or reuse an immutable worker is an installation/lifecycle decision, not part of the agent identity.

## Internal evidence

Components may report reasoning, state snapshots, progress, and domain events. Such records carry the reporting identity and are not promoted to platform-observed facts. Absence is visible. Optional telemetry does not exempt billable operations from admission and usage reporting.

## Semantic validation beyond JSON Schema

Check version availability, operation/tool-name uniqueness, schema validity, required resource bindings, resource roles, supported state/concurrency combinations, and trusted billing policy. Compare declared operations with discovered MCP capabilities before execution; reject mismatch rather than guessing.
