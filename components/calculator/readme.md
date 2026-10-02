# Deterministic calculator resource

`slow_thinker_calculator` exports independent `Calculator` and standard MCP
`CalculatorHost`. The package is version `0.1.0` and has no external service,
mutable business state or billable operations.

```python
from slow_thinker_calculator import Calculator

result = Calculator().calculate("6 * 12 + 3 * 8")
# {"expression": "6 * 12 + 3 * 8", "value": "96"}
```

Arithmetic supports decimal literals, parentheses, unary `+`/`-` and
`+`, `-`, `*`, `/`, `//`, `%`, `**`. Division/remainder follow Decimal semantics;
integer division truncates toward zero. Inexact arithmetic, including recurring
division, fails explicitly. Names, functions, attributes, indexing, booleans,
statements, excessive trees and unbounded powers are rejected without `eval`.

Default ceilings are 4096 UTF-8 expression bytes, 128 AST nodes, an absolute
literal/power exponent of 100 and 4096 result bytes. Configuration may lower these
bounds. The result is a plain decimal string and retains the original expression.

Prepare with `python -m tooling.components --component calculator`. The canonical
[descriptor](calculator.component.json) and [registration](registration.json) are
trusted setup artifacts. `CalculatorHost.describe(config)` is side-effect-free;
`python -m slow_thinker_calculator BOOTSTRAP` uses the public host SDK.
See [specification.md](specification.md) and the [shared contract](../../docs/contracts/tools-memory.md).
Functional and mandatory shared verification passed; see the checkpoint below.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
