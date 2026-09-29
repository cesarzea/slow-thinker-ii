# BoundedFlow: specification

Selects one next activation from a declared conditional topology and bounded completed history.

## Public Python boundary

- `BoundedFlowConfig` records entry node, route table and positive max_activations.
- `CompletedStep` records node and selected port; `FlowDecision` represents activate, complete or exhausted.
- `parse_config(value: JsonObject) -> BoundedFlowConfig` validates the declared topology.
- `BoundedFlow(config: BoundedFlowConfig).next(completed: tuple[CompletedStep, ...]) -> FlowDecision` validates history from entry.
- `BoundedFlowHost` exposes `next`; export public contracts through `slow_thinker_bounded_flow`.

## Behavior and errors

- Validate every completed transition against the declared entry and route table.
- A terminal route completes, including on the last allowed activation.
- If another activation would exceed the bound, return exhausted with activation_limit_reached.
- Invalid history or unknown routes fail explicitly rather than selecting a fallback node.
- Remain stateless and make no external calls; do not change the Sequence component.

## Shared contracts

- [Conditional routing](../../docs/contracts/conditional-routing.md) defines exact wire shapes, configuration and acceptance cases.
- [Managed gateway](../../docs/contracts/managed-gateway.md) defines outgoing client setup and authority.
- [Component installation](../../docs/contracts/component-installation.md) defines packaging and isolated execution.

No backend implementation imports are permitted. First-cycle implementation and local acceptance checks are complete.
