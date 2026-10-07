# Configurable tools, memory and composition

| Document control | Value |
| --- | --- |
| Contract ID | CONTRACT-RESOURCES-001 |
| Owner | Cesar Zea |
| Date | 2026-10-02 |
| Status | Active S05 delivery specification; implementation/verification pending |

## Scope and ownership

Add separately installed calculator, key/value memory and ContextualCall component
packages, each version `0.1.0`, using the existing host SDK and managed MCP gateway.
Keep functional classes separate from host bootstrap, telemetry and storage I/O.
Managed children and resources remain separate declared instances, even when the
user interface presents them inside an agent. Components may also maintain private
internal state under their declared lifecycle; only reported internal activity is
observable. Future mem0/graph-memory adapters use these same resource boundaries.

## Calculator

`Calculator.calculate(expression: str) -> JsonObject` and MCP `calculate` accept
`{"expression":"6 * 12 + 3 * 8"}` and return
`{"expression":"6 * 12 + 3 * 8","value":"96"}`. Use exact bounded decimal
arithmetic, with numeric literals, parentheses and reviewed arithmetic operators.
Reject names, calls, attributes, indexing, booleans, executable statements,
excessive input/tree size/exponents and undefined arithmetic. Do not use `eval`.
Input/result bounds and operation schemas are explicit; errors are MCP errors.
The calculator is deterministic, stateless, nonbillable and independently usable.

## Key/value memory

`KeyValueMemory` exposes `get`, `put`, `delete`, `list`. Keys are nonempty bounded
strings; values are bounded JSON. `get({key})` returns `{found,value,version}`;
missing means `{found:false,value:null,version:null}`. `put({key,value,
expected_version})` uses an explicit optional version precondition and returns
`{version}`. A null expected version means insert-only; absent means unconditional.
`delete` has the same optional precondition and returns `{deleted}`. `list` returns
bounded keys with versions and no implicit unrestricted dump of stored values.
Version conflicts are explicit failures; writes and versions are transactional.

Configuration declares `namespace`, `retention` (`run` default or `persistent`),
maximum entries and maximum value bytes. Binding two agents to one memory instance
means intentional sharing; separate instances are isolated. Namespace keys include
experiment identity and resource-instance identity. Persistent configuration reuses
that explicit namespace across revisions/runs; run retention also includes runtime
identity. Equal human namespace labels in different private instances do not merge
state. Cross-experiment sharing is outside this initial profile.

The memory component owns a dedicated SQLite resource store, separate from the
platform database and accessed only by the memory resource. Trusted host bootstrap
supplies its file path; graph configuration supplies no arbitrary path. An adapter
connection/host exit never deletes persistent data. New run-retained namespaces
start empty. Private/shared bindings, retention and logical namespace are captured
with the run. Data concurrency is handled transactionally; this does not add
serialized stateful agent scheduling, which remains a later sprint.

Public resource preparation adapter `MemoryResourceAdapter(storage_root: Path)`
implements `configure(HostRequest) -> HostProfile`. `HostRequest.runtime_id` is
required for run retention. It supplies `clients.memory_store` containing the
trusted path and effective namespace. Host description is side-effect-free;
constructors and readiness do not populate, read or write business memory.

## ContextualCall composition

`ContextualCall(config, endpoint).invoke(arguments, invocation)` is an agent
composition around a bound ordinary worker. Required slot `worker` declares its
operation; optional slots `calculator` and `memory` are explicit resource bindings.
Config selects an object input schema, worker operation/output schema, calculation
expression input pointer, target input fields, memory key and worker-result pointer
to store. Flags explicitly enable memory read/write and calculation; binding alone
does not inject data into the prompt or execute a tool.

The managed sequence is: optional memory `get`; optional calculator `calculate`;
worker operation with isolated inputs plus configured context fields; optional
memory `put` of the selected successful worker-result value. Return the unchanged
worker result. Reject missing pointers, unsupported bindings or response shapes.
A failed stage yields an MCP error with stage/reason; no fallback or implicit retry.
A successful paid worker followed by a failed memory write still retains its paid
call and cost evidence. All nested calls use the invocation-scoped standard MCP
client, filtered aliases, remaining deadlines and the same permission/accounting
path. Composition with RoutedCall remains possible through its public `invoke`.

Initial config keys are `input_schema`, `worker_operation`, `worker_output_schema`,
`calculation_enabled`, `expression_pointer`, `calculation_field`, `memory_read`,
`memory_write`, `memory_key`, `memory_field`, `result_pointer`. Configuration and
returned operation schemas validate these fields before execution. Define their
ordinary schema defaults in the descriptor; no business invocation during describe.

## External authored components

Extend the explicit trusted preparation CLI with `--external-project`,
`--registration`, `--descriptor` and repeatable `--dependency-project` inputs.
Use controlled static-version src-layout Hatchling packages, exact public entry
points, descriptor/registration identity agreement and exact wheel/dependency
hashes. Build and resolve only during explicit preparation. Copy the validated
descriptor into the prepared bundle and report the registration/resolution IDs.
No runtime graph import strings, source installation or unreviewed endpoint discovery.

A separately authored example agent uses the public host/LLMCall APIs and normal
managed model/MCP signatures. Prepare it through the external path, register the
result in trusted startup settings and demonstrate its configurable operation
inside a graph. This is a real independent package, not a built-in-only fixture.
B owns the entire tooling/components package and adds built-in recipes for
`model-provider`, `calculator`, `key-value-memory`, `contextual-call` plus the
external example's explicit preparation guide.

Acceptance and ownership are in [the delivery block](../specification/s04-s06-delivery.md).
