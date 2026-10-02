# Deterministic calculator resource: specification

## Active S04–S06 contract

Follow [the shared contract](../../docs/contracts/tools-memory.md) and the
[delivery ownership/acceptance matrix](../../docs/contracts/../specification/s04-s06-delivery.md).
Implementation owner: B.

Implement public Calculator.calculate and CalculatorHost with bounded decimal arithmetic, no eval, explicit operation/configuration schemas and no external calls. Reject executable and excessive input. Keep functional evaluation separate from host metadata.

Use exact public dependency entry points named in the shared contract. Keep
implementation-local choices local; report missing cross-package decisions.
Constructors/imports perform no external business I/O. All managed calls retain
permissions, deadlines, evidence and applicable budgets.

Development delivery must map acceptance IDs to code and identify verification
remaining. Test implementation belongs to the later testing phase under M06.

## Reviewed public interface skeleton

```python
class Calculator:
    def __init__(
        self,
        *,
        max_expression_bytes: int = 4096,
        max_nodes: int = 128,
        max_exponent: int = 100,
        max_result_bytes: int = 4096,
    ) -> None: ...
    def calculate(self, expression: str) -> JsonObject: ...


class CalculatorHost(HostedComponent): ...
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
