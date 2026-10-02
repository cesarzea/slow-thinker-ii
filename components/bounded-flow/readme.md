# BoundedFlow

A stateless controller for a declared conditional topology and configured maximum
number of node activations. It validates every transition from the configured entry;
node names and reviewer concepts are not hardcoded.

```python
from slow_thinker_bounded_flow import BoundedFlow, parse_config

flow = BoundedFlow(
    parse_config(
        {
            "entry": "propose",
            "routes": {
                "propose": {"next": "review"},
                "review": {"accept": None, "revise": "propose"},
            },
            "max_activations": 6,
        }
    )
)
```

`flow.next(tuple_of_completed_steps)` returns an immutable `FlowDecision` with
`activate`, `complete` or `exhausted`. Completion on the last permitted activation
wins over exhaustion. Histories that deviate from the topology, continue after a
terminal route or exceed the bound fail explicitly.

`BoundedFlowHost.describe(config)` publishes the effective `next` operation.
Its request is `{"completed":[{"node":...,"port":...}]}`. Activation replies contain
one `nodes` entry, completion contains only `action`, and exhaustion contains
`reason: "activation_limit_reached"`. The controller performs no external calls.

Prepare with `python -m tooling.components --component bounded-flow`. Existing
Sequence configuration, operations and results are unchanged. See
[specification.md](specification.md), the
[bounded example](../../docs/contracts/examples/bounded-review.md) and
[verification record](../../docs/verification.md). Scoped functional, MCP and offline preparation tests pass. Installed whole-system acceptance and repository verification pass.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
