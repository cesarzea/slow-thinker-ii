# Trusted resource state bindings: specification

## Active S04–S06 contract

Follow [the shared contract](../../../../../docs/contracts/tools-memory.md) and the
[delivery ownership/acceptance matrix](../../../../../docs/contracts/../specification/s04-s06-delivery.md).
Implementation owner: B.

Export MemoryResourceAdapter(storage_root).configure(HostRequest)->HostProfile. Require runtime_id for run retention; derive logical namespace from graph_id, instance_id, configured namespace and optional runtime_id. Supply clients.memory_store with trusted SQLite path and effective namespace. No business memory calls in configure/describe. No graph-controlled file path.

Use exact public dependency entry points named in the shared contract. Keep
implementation-local choices local; report missing cross-package decisions.
Constructors/imports perform no external business I/O. All managed calls retain
permissions, deadlines, evidence and applicable budgets.

Development delivery must map acceptance IDs to code and identify verification
remaining. Test implementation belongs to the later testing phase under M06.

## Development implementation

The public interfaces and their implemented local limits, defaults, state and error
behavior are described in [readme.md](readme.md). Canonical descriptors and
registration records are maintained at the package ownership boundary where applicable.
Targeted functional tests, strict typing, lint, formatting and Python size checks
pass. Mandatory whole-system verification remains pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
