# Configurable resource-aware agent composition

`slow_thinker_contextual_call` exports `ContextualCall(config, endpoint)` and
`ContextualCallHost`, version `0.1.0`. The required `worker` slot binds an ordinary
agent operation. Optional `calculator` and `memory` slots bind declared resources.
All nested calls use the invocation-scoped standard managed MCP client.

Configuration requires object `input_schema`, `worker_operation` and object
`worker_output_schema`. `calculation_enabled`, `memory_read` and `memory_write`
default to false. Their stages run only when enabled: memory get, calculator,
worker, then memory put of a successful selected worker result.

The default expression pointer is `/expression`, calculation target field
`calculation`, memory key `context`, memory field `memory` and result pointer `""`
(the complete worker result). Target fields are top-level input names and cannot
overwrite supplied arguments; simultaneous context fields must differ. JSON
Pointers support escaped keys and array indices. An absent memory value injects
null. Calculator output injects its decimal string. Resource and worker reply
schemas are checked, and the unchanged worker result is returned.

Failures are MCP errors with an explicit stage and bounded reason. A failed
memory write never repeats the successful worker. Cancellation propagates; the
managed client retains permissions, aliases, deadlines and accounting. A worker
may be RoutedCall through its ordinary `invoke` operation and matching schemas.

Prepare with `python -m tooling.components --component contextual-call`. Trusted
bootstrap supplies only the platform `mcp` record. The canonical
[descriptor](contextual-call.component.json) and [registration](registration.json)
are setup artifacts. See [specification.md](specification.md) and the
[shared contract](../../docs/contracts/tools-memory.md). Functional and mandatory shared verification passed; see the checkpoint below.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
