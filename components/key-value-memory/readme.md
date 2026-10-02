# Scoped key/value memory resource

`slow_thinker_key_value_memory` exports `KeyValueMemory` and `KeyValueMemoryHost`,
version `0.1.0`. The component owns a dedicated SQLite file supplied by trusted
bootstrap. Graph configuration cannot supply a filesystem path.

Configuration requires `namespace`; `retention` defaults to `run`, `max_entries`
to 1000 and `max_value_bytes` to 65536. Their ceilings are 10000 entries and 65536
canonical JSON UTF-8 bytes. Keys and configured namespace labels contain one to
256 UTF-8 bytes. The preparation adapter scopes a namespace by graph ID, resource
instance ID and label, adding runtime ID for run retention. Revisions share an
explicit persistent namespace; separate resource instances never merge by label.
Two agents share data by binding the same resource instance.

`get({key})` returns `{found,value,version}`. `put({key,value,expected_version})`
returns `{version}`; `delete({key,expected_version})` returns `{deleted}`.
An omitted precondition is unconditional, null requires absence, and a positive
integer requires the current version. Versions are transactional, increase across
replacement and reinsertion, and conflicts preserve the previous value.
`list({limit,after})` returns `{items:[{key,version}],next_key}` in key order.
The default/maximum page size is 100; it never returns a value dump.

Storage opens lazily on invoked operations, with immediate transactions, WAL and
full synchronization. Description, construction and readiness perform no business
memory I/O. Closing the host never deletes data. Data concurrency is transactional;
agent activations retain the platform's existing scheduling behavior.

Prepare with `python -m tooling.components --component key-value-memory`. Trusted
bootstrap supplies `clients.memory_store={path,namespace}`; the canonical
[descriptor](key-value-memory.component.json) and [registration](registration.json)
are setup artifacts. See [specification.md](specification.md) and the
[shared contract](../../docs/contracts/tools-memory.md). Functional and mandatory shared verification passed; see the checkpoint below.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
