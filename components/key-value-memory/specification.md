# Scoped key/value memory resource: specification

## Active S04–S06 contract

Follow [the shared contract](../../docs/contracts/tools-memory.md) and the
[delivery ownership/acceptance matrix](../../docs/contracts/../specification/s04-s06-delivery.md).
Implementation owner: B.

Implement public KeyValueMemory and KeyValueMemoryHost with get/put/delete/list, bounded JSON, transactional versions and namespaces. Bootstrap owns the storage path; config owns namespace/retention/bounds. Instance data is isolated unless agents explicitly bind the same resource. Declare fresh invocation objects with externally persisted resource data; do not claim serialized agent execution.

Use exact public dependency entry points named in the shared contract. Keep
implementation-local choices local; report missing cross-package decisions.
Constructors/imports perform no external business I/O. All managed calls retain
permissions, deadlines, evidence and applicable budgets.

Development delivery must map acceptance IDs to code and identify verification
remaining. Test implementation belongs to the later testing phase under M06.

## Reviewed public interface skeleton

```python
class KeyValueMemory:
    def __init__(
        self, path: Path, namespace: str, *, max_entries: int = 1000, max_value_bytes: int = 65536
    ) -> None: ...
    def get(self, arguments: JsonObject) -> JsonObject: ...
    def put(self, arguments: JsonObject) -> JsonObject: ...
    def delete(self, arguments: JsonObject) -> JsonObject: ...
    def list(self, arguments: JsonObject) -> JsonObject: ...


class KeyValueMemoryHost(HostedComponent): ...
```

The existing host HostedComponent constructor/describe/invoke contract remains authoritative.
Local immutable value types may be named by the implementer; package entry points
export the declared functional API. No backend imports or direct peer calls.

## Development implementation

The public interfaces and their implemented local limits, defaults, state and error
behavior are described in [readme.md](readme.md). Canonical descriptors and
registration records are maintained at the package ownership boundary where applicable.
Targeted functional tests, strict typing, lint, formatting and Python size checks
pass. Mandatory whole-system verification remains pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
