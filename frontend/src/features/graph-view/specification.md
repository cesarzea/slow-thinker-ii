# Agent collaboration canvas: specification

## Boundary and data

`index.ts` exports `GraphView` and `GraphSelection`. GraphView accepts `graph` and
optional `detail`, `execution` and `onSelect`. Selection retains a component,
planned node, activation or call identity; the caller owns inspection.

Use only public API records and local React Flow presentation. Domain records
remain separate from geometry. Missing detail shows catalog steps and an explicit
unavailable message. Missing execution differs from a recorded empty page.

## Implemented presentation

- One card per declared step, keyed by its planned node ID. Built-in LLMCall and
  RoutedCall cards use an accessible AI icon; unknown types preserve their type
  with a generic icon. Display names capitalize the first character only.
- Control routes connect cards. Terminal anchors are invisible, nonselectable and
  nonfocusable. Returning routes use separate lower handles and curved lanes.
- Agent cards show their left input and right output connectors independently of
  system elements. Geometry-only return and boundary handles remain hidden.
- An incoming arrow starts in empty space and reaches the declared entry step.
  Resolve the entry from the built-in bounded-flow controller's `config.entry` or
  sequence controller's first `config.steps` item, using saved configuration when
  available. Unsupported, missing or invalid entry metadata creates no invented
  entry. Invisible boundary anchors add no visible boxes or selectable records.
- Entry and terminal arrows extend 112 canvas units horizontally from the card's
  current connector, including after configuration changes or dragging. System
  elements add the entry route's midpoint marker; terminal routes retain their
  midpoint and endpoint markers. These presentation routes do not imply calls.
- Structure and Execution modes share the cards. Execution mode shows the latest
  recorded status by ordinal and the number of recorded activations for that step.
  It never adds invocation cards or interprets a route as an observed call.
- Configuration and system elements start off. Optional configuration is limited
  to model and reasoning effort, with Saved configuration or Graph configuration
  provenance per value. LLMCall follows its model binding; RoutedCall follows
  worker bindings with cycle protection. Saved instance config takes precedence.
  Only explicit worker parameters or the saved model complete operation's
  request-schema constant identify effort; absent effort is Not specified.
- Unsupported or missing model information is Unavailable. Malformed optional
  metadata cannot expose arbitrary config fields or credentials.
- System mediation appears as small black circles at route midpoints and terminal
  endpoints. These markers have no inspection action and assert no observed call.
- Resources lists declared resource roles. Explore graph and evidence provides
  keyboard-accessible component, step, activation and exact call selections,
  including internal calls. Evidence stays available in either display mode.

## Geometry and state

Cards have a fixed width with wrapping content and horizontal spacing sufficient
for inline configuration. The canvas supports pan, zoom, fit and narrow containers.
Dragged positions and viewport remain stable during polling. Reorganize graph,
changed graph identity and the arrival of a detailed definition remount the canvas
with initial positions and fit. Configuration changes increase canvas height.
Controlled nodes process React Flow dimension and position changes, retaining
measured geometry while current graph props update presentation data.

Local state holds mode, display options, layout generation and dragged positions.
All product-authored text is English; API identifiers and recorded evidence remain
unchanged. No mutations, provider calls or protocol changes occur here.

## Acceptance and verification

Follow the complete acceptance cases in the
[approved sprint](../../../../docs/specification/agent-canvas-sprint.md).
Frontend unit and browser checks cover card rendering, declared entry resolution,
configuration provenance and malformed data, visible connectors, exterior arrows
after expansion/dragging, polling state and exact inspector selection. Frontend
typing, ESLint, formatting, boundaries, dead-code checks and build pass.
See the [verification record](../../../../docs/verification.md) for coverage,
corrections, exact command scope and remaining publication limitations.

### Browser polling regression

The polling journey must scroll the selected saved-run agent into the browser
viewport before sending pointer input, establish its initial CSS transform, and
verify that the drag changes that transform. Compare node and viewport transforms
across a successful execution-poll response, then require Reorganize graph to
restore the initial node transform. Comparing the entire inline style can accept
transient visibility changes without proving movement or layout reset.

Geometry checks must wait for both expected agent cards to be rendered and visible.
An empty collection or hidden initialization state must not count as fitted.
Observe containment and separation from stable DOM geometry, retrying condition
checks through Playwright assertions across definition arrival and layout remounts.
