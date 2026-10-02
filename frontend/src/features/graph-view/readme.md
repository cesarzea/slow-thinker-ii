# Agent collaboration canvas

Shows declared agent steps, visible input/output connectors and control routes with optional inline model
configuration and symbolic system mediation. Execution mode annotates the same
cards; exact activations, calls, internal components and resources remain
selectable below the canvas.
Exterior arrows show the declared entry and terminal routes without extra boxes.

Import `GraphView` and `GraphSelection` through [index.ts](index.ts). The caller
supplies validated graph details and recorded execution pages, and owns inspector
navigation through `onSelect`. The module performs no network calls.

See [specification.md](specification.md) and the
[approved sprint](../../../../docs/specification/agent-canvas-sprint.md).

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
