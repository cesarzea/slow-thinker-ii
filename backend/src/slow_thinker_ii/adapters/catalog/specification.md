# Graph catalog and compilation: specification

Loads bundled experiment definitions and compiles them against installed component contracts.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- BundledDefinitionStore lists summaries and returns an exact graph revision.
- SequenceCompiler validates definitions and resolves finite execution plans.
- InstalledGraphCompiler resolves registered component installations and effective operation schemas.
- InstalledPlan and installation records carry the resolved runtime inputs.

## Required behavior

- Validate graph syntax, bindings, permissions and effective schemas before execution.
- Use immutable graph revisions and exact installed component identities.
- Reject invalid earlier-output references rather than inferring data flow.

## Dependencies and ownership

Definition and application public contracts plus component installation services; no provider calls during compilation.

## Acceptance criteria

- All bundled Sequence examples compile through the same path.
- Undeclared operations, unknown resources and invalid input bindings fail before dispatch.

## Shared contracts

- [graphs](../../../../../docs/contracts/graphs.md)
- [component-installation](../../../../../docs/contracts/component-installation.md)

## Verification

All five bundled graphs compile against the seven-target installation bundle. Tests reject invalid routes, missing bindings and containment cycles; existing Sequence checks pass.

## Sprint additions

- [conditional-routing](../../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [inspection-projections](../../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

Installed compilation selects the separate bounded conditional compiler and validates effective RoutedCall worker schemas, operations and router ports. The catalog includes bounded-review, explicit input schemas, containment and typed relationship projections.
