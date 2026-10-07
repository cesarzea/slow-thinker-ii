# Agent canvas and English presentation

Approved by the owner on 2026-09-30 after reviewing the working browser UI.
This delivery changes presentation, not graph execution or collaboration rules.
Status: implemented and verified locally; see the [verification record](../verification.md).

## Shared contracts

- Keep `GraphView` and `GraphSelection` public signatures compatible. One visible
  card represents each declared agent step, keyed by its planned node ID. Repeated
  invocations remain separate evidence, never new agent instances on the canvas.
- A card shows an accessible AI-agent icon, component type (`LLMCall` for
  `llm-call`, `RoutedCall` for `routed-call`, original type for other extensions),
  then the instance name (capitalize the first character for display only).
  Unknown extension steps retain their type and a generic component icon.
- Only declared steps and control arrows appear on the canvas. Resource,
  controller, internal component and separate activation boxes are removed.
  Terminal routes end in empty space, using invisible geometry anchors if needed.
- Controls: `Structure`, `Execution`, `Reorganize graph`, `Show configuration`,
  `Show system elements`. Both display options start off. Remove former layer and
  internal-component controls. Reciprocal routes remain visually separate.
- Configuration appears inside each card. Resolve LLMCall's `resources.model`;
  for RoutedCall follow its `resources.worker` with cycle protection. Show only
  model and reasoning effort, never arbitrary configuration or credentials.
  Read saved `execution.instances[id].config` before the original definition's
  config. Label this `Saved configuration` versus `Graph configuration`.
  Read explicit `parameters.reasoning_effort` or `parameters.reasoning.effort`;
  a saved model operation's request-schema constant may identify enforced effort.
  Otherwise show `Not specified`. Missing/unsupported model information is
  explicitly unavailable. Do not invent a model, effort or current provider default.
- Extend the API's `GraphDetail` with optional JSON-object `execution`, already
  supplied by saved-definition responses. No backend or wire-format change is
  needed; validate it as JSON. Existing graph detail consumers remain compatible.
- System elements are small black circles at each route midpoint and, for terminal
  routes, at the endpoint. They symbolize mediation, not extra agents or proof of
  observed calls. Hover/click evidence inspection for these markers is future work.
- Execution mode annotates existing agent-step cards with their latest recorded
  status and activation count. All exact activations/calls stay selectable through
  an accessible evidence list below the canvas. Never substitute one invocation
  for another or infer communications from control arrows.
- Below the canvas, provide `Resources` and a collapsible
  `Explore graph and evidence` list. Preserve component/node/activation/call
  selections and inspector navigation, including internal component calls.
- Dragged positions and viewport survive ordinary polling. Reorganize resets
  layout and fit; arriving definitions fit once. Expanded card configuration must
  not overlap adjacent cards or clip content. Support narrow screens.
- All product-authored text is English: visible UI, accessible labels, errors,
  examples, comments and documentation. Preserve user-supplied content, immutable
  historical evidence, protocol identifiers and meaningful Unicode test inputs.

## Exclusive implementation ownership

| Owner | Whole modules / files | Delivery |
| --- | --- | --- |
| Graph implementer | `frontend/src/features/graph-view/` | Agent canvas, configuration, system markers, resource/evidence lists, local CSS and module documents. |
| Browser implementer | `frontend/src/app/`, `frontend/src/api/`, `frontend/src/ui/`, `frontend/src/features/execution/`, `frontend/src/features/inspector/`, `frontend/src/main.tsx`, `frontend/index.html` | English product text and the additive `GraphDetail.execution` field; preserve behavior and public entry points. |
| Coordinator | Shared documentation and root policy | Review shared contracts, language audit outside assigned modules, delivery review and verification. |

Implementers read the module specifications and tickets, then implement without
functional test work in this phase. Type/lint checks are permitted. No commits,
pushes or paid provider calls. Shared changes require coordinator resolution.

## Delivery review and testing phase

Review individual deliveries and their composition before assigning test work.
Keep graph tests and other browser tests under separate owners. The coordinator
owns shared fixture changes and the final verification run. Check fixture shapes
and the pinned toolchain once before testing. Group corrections by module.

Acceptance cases:

1. Single-agent renders one AI card, LLMCall, Proposer and an outgoing arrow; no
   visible output/resource/controller/activation rectangles.
2. Configuration on/off, actual saved model precedence, explicit/default/missing
   effort, nested RoutedCall, unknown types and malformed optional metadata.
3. System markers off by default, midpoint markers and a terminal endpoint marker
   when enabled; no apparent click action before marker inspection exists.
4. Bounded reviewer return/accept routes, repeated-step identity, live status and
   exact activation/call selection from keyboard-accessible lists.
5. Definition arrival, drag/poll stability, reorganization, fit, readable reciprocal
   routes, expanded cards and narrow viewports in the real browser renderer.
6. English catalog/access/session/start/stop/history/inspection, validation/error
   paths, document language and simulated-provider examples; user evidence intact.
7. Existing recovery, schema validation, cost display and inspector focus behavior
   remain functional. Mandatory type, lint, format, boundary, dead-code, coverage,
   build and browser checks pass without weakening thresholds.

Use simulated providers and existing saved runs; this change needs no paid calls.
Record commands/results and limitations. Do not claim remote CI or CodeQL passed
without running them. This sprint does not authorize publication.

## Approved input/output correction — 2026-09-30

Status: implemented and verified locally; see the verification record.

The owner approved correcting the reviewed LLMCall card: its input/output
connectors were hidden and its graph-entry arrow was absent. The graph module's
[specification](../../../../frontend/src/features/graph-view/specification.md) defines
entry resolution, hidden geometry anchors and horizontal boundary arrows.

The graph implementer owns this cohesive production module; the coordinator owns
documentation, delivery review and subsequent tests. Review the implementation
before changing tests. Acceptance covers visible connectors with system elements
off, declared entry in cyclic graphs, unavailable/invalid entry metadata, saved
configuration precedence, horizontal arrows after expansion/dragging, and existing
catalog/resource/evidence behavior. Run frontend gates and affected browser
journeys, then inspect the live UI without executing a paid model call.
