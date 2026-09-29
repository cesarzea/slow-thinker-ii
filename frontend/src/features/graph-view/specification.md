# Graph visualization: specification

Renders experiment structure, recorded activations and communication layers with selection callbacks.

## Public boundary

The [public entry point](index.ts) is authoritative for exported names and signatures.

- GraphView accepts a GraphSummary fallback and optional typed detail, execution and selection callbacks.

## Required behavior

- Keep graph data independent of React Flow representation.
- Distinguish component instance identity from repeated activation identity.
- Structure and execution projections retain separate configured and recorded identities.

## Dependencies and ownership

React Flow and public API types; selection coordination belongs to the app.

## Acceptance criteria

- Existing finite graphs render without implying that repeated activations are different agents.
- The full target distinguishes structure, control flow, permissions and observed communications.

## Shared contracts

- [visual-model](../../../../docs/architecture/visual-model.md)

## Sprint additions

- [inspection-projections](../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package boundary; existing supported behavior remains compatible.
- [conditional-routing](../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package boundary; existing supported behavior remains compatible.

## Structure and execution views

GraphView keeps its `graph` fallback and accepts optional `detail`, `execution`
and `onSelect`. Its GraphSelection identifies a component, planned node,
activation or call. Consumers coordinate evidence through callbacks.

Control, permission, resource-binding and observed-call layers can be toggled
independently. Planned nodes and configured components have distinct renderer
identities. Recorded activations use run-scoped IDs and ordinals; call selection
retains the exact call ID. Terminal exits and return edges come from the supplied
relationships. Contained components expand without granting relationships or
changing their recorded identities. A keyboard-accessible list always exposes
components and evidence, including calls inside a collapsed composition.

Status changes preserve generated and user-positioned coordinates. Reorganize
explicitly restores layout. Missing definition or execution detail is labeled.
The graph never derives permissions or calls from visual containment.

## Verification

The frontend feature/API suites pass with 119 tests and the mandatory coverage
thresholds (2026-09-29). Browser journeys verify all five catalog graphs, retained
execution/inspection, bounded rejection then acceptance, exhaustion and responsive
keyboard selection against the simulated-provider backend. Type, lint, formatting,
dead-code and dependency-boundary checks pass. Sprint-wide final verification is
coordinated separately in the shared verification record.

Agent, resource and control roles have explicit canvas/list text and solid, dashed
and double border treatments. Unknown extension role labels remain visible with
the generic treatment; missing roles keep the generic component fallback.

Initial arrival of an exact definition fits its complete collapsed canvas once.
Routine status/cost changes preserve the viewport; explicit Reorganize restores
layout and fit. Reciprocal control-return routes use a separate curved lane so
forward and return labels remain distinct. The browser geometry journey checks
all initial component/terminal bounds, reorganization and label separation.
