# Trusted resource state bindings

The public `MemoryResourceAdapter(storage_root: Path).configure(HostRequest)`
returns a `HostProfile` containing `clients.memory_store={path,namespace}`.
The trusted file is `storage_root/memory.sqlite3`; graph configuration never
supplies a path. Namespace identity is a canonical JSON array containing graph ID,
resource instance ID and configured namespace, plus runtime ID for run retention.
This preserves private instances, explicit shared bindings and persistent reuse
across revisions without delimiter collisions.

Construction and configuration perform no business storage I/O. A missing runtime
ID for run retention or invalid configuration raises `PreparationRejected` before
host launch. The component owns transactions and persistent data; host teardown
never removes this store. See [specification.md](specification.md) and the
[shared resource contract](../../../../../docs/contracts/tools-memory.md).
Functional and mandatory shared verification passed; see the checkpoint below.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
