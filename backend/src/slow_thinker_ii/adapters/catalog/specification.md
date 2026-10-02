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

## S03 personal experiment library

Follow the [shared contract](../../../../../docs/contracts/personal-experiments.md) for wire values, data origins,
public interfaces, validation scope, errors, immutable identity, paging and failure
handling. Implementation owner: A.

Add public GraphDefinitionValidator(schema_directory: Path,
descriptor_directory: Path). Its validate(source) returns library.ValidatedDefinition;
detail(source) returns the existing GraphDetail JSON. Use local schemas and exact
registered descriptors; check configuration, graph references, containment and
profile rules without subprocesses, installed contracts or provider calls.
Keep BundledDefinitionStore and existing compilers compatible. Internal helpers
may be grouped by cohesive validation responsibilities within this package.

Acceptance follows the shared S03 scenarios. Development delivery does not claim
testing is complete. Keep module-private choices within these public contracts.

## S03 development implementation

Private `_validation` files group schema/diagnostic handling, registered component
configuration, graph references and profile/input semantics. Descriptor contracts
and configured declared schemas validate literal arguments locally. Runtime values,
installed schema equality and selector availability are deferred to preflight.
LLMCall configuration follows its existing public reserved-parameter and local
fragment-reference policy, without importing provider SDKs or component internals.

Definition JSON rejects duplicate keys, nonfinite numbers and invalid Unicode.
Schema errors expose at most ten fixed messages and JSON Pointers bounded to 160
characters; an oversized pointer uses the root. No submitted value or validation
exception is included in the diagnostic. Validation and detail construct the local
schema catalogue on demand; the public constructor performs no I/O.
Focused S03 acceptance and scoped static checks pass; complete coordinator
verification remains pending.

Partial static input checks preserve boolean schemas reached through local refs
and allOf at the operation or bound-argument level. False rejects even unavailable
values; true retains the ordinary shape/literal checks. Owning schemas preserve
fragment resolution. No general schema satisfiability inference is introduced.
