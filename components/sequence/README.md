# Sequence

A deterministic controller for executing graph nodes in a fixed, finite order.
It selects the next node; the platform performs the actual agent invocation.

## Behavior and configuration

Configure an ordered list of distinct node identifiers:

```json
{"steps": ["draft", "review", "revise"]}
```

The `next` operation receives `completed_nodes`, which must be an exact prefix
of that list. It returns `{"action": "schedule", "nodes": ["review"]}` when
`draft` is complete, or `{"action": "complete", "nodes": []}` after every step.

The controller retains no execution history and makes no LLM calls. It does not
evaluate results, branch conditionally or loop until acceptance. Repeated use of
an agent is represented by distinct nodes, as in the
[proposal/review example](../../docs/contracts/examples/review-cycle.graph.json).

Import `Sequence` and `Decision` from `slow_thinker_sequence` for the functional
API; `SequenceHost` exposes the controller through MCP.

## Development

Requires Python 3.13. From the repository root, run `make setup`, then
`uv run --locked pytest components/sequence/tests`. No provider credentials are
needed. See the [development instructions](../../CONTRIBUTING.md) for managed
installation and the [descriptor](../../docs/contracts/examples/sequence.component.json)
for the component contract.

## Module contract

See [specification.md](specification.md) for the public boundary and acceptance criteria.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
