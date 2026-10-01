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
