# Resolved experiment definitions: specification

Represents immutable graph plans and resolves declared input bindings without performing external work.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- GraphSummary and PlannedNode describe selectable experiments.
- SequencePlan, PlanNode, ResolvedInstance and OperationTarget describe resolved execution.
- StaticArgument and OutputArgument define input sources; node_arguments materializes arguments.
- pointer_tokens and read_pointer implement JSON Pointer access.

## Required behavior

- Keep graph identities, component instances and activations distinct.
- Resolve only explicit bindings; report missing referenced output or pointer data.
- The existing Sequence profile refers to earlier completed nodes and remains finite.

## Dependencies and ownership

Public JSON contracts; validation against installed component descriptions belongs to catalog adapters.

## Acceptance criteria

- Literal and previous-output bindings produce the declared argument structure.
- Repeated use of an instance does not overwrite a different activation identity.

## Shared contracts

- [graphs](../../../../docs/contracts/graphs.md)

## Verification

Conditional binding, selected-port, containment and declared-input tests pass, including optional initial omission and activation-specific feedback.

## Sprint additions

- [conditional-routing](../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [inspection-projections](../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

ConditionalPlan, ConditionalNode, LatestOutput and CompletedActivation keep cyclic bindings separate from SequencePlan. graph_detail and graph_input_schema produce presentation-independent definition projections.
