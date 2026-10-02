# Local application composition: specification

Builds the backend from explicit configuration and manages its local runtime lifetime.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- create_app builds the FastAPI application from configured persistence, tariff and execution services.
- configured_app loads the local startup configuration.
- load_execution_setup validates configuration; ExecutionSetup builds ExecutionServices.

## Required behavior

- Validate configuration before component startup and keep credentials outside graph definitions.
- Own database startup, exclusive runtime ownership, recovery, tariff refresh and bounded shutdown.
- Public monetary configuration follows the decimal USD boundary; internal LimitsProfile values use integer quanta.

## Dependencies and ownership

Application ports and concrete adapters; this is the backend composition root.

## Acceptance criteria

- Invalid startup configuration fails before provider or component work.
- Startup recovery retains unresolved costs and does not replay interrupted calls.

## Shared contracts

- [accounting-policy](../../../../docs/contracts/accounting-policy.md)
- [0011-local-persistence](../../../../docs/adr/0011-local-persistence.md)

## Verification

Startup tests verify exact decimal USD conversion and rejection before credential resolution; recovery preserves interrupted outcomes and blocks unconfirmed cleanup.

## Sprint additions

- [managed-gateway](../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

Public startup limits require decimal USD strings under run_budget, session_budget and month_budget. PublicLimits converts them through parse_limit before loading credentials. Composition attaches /mcp and recovery of durable owned-process records before admission.

## October 2026 maintenance: Generator typing compatibility

The decorated `TariffLifetime.lifespan` implementation uses
`AsyncGenerator[None]` for Pyright 1.1.414. Its yielded value remains `None`;
preserve startup, recovery and bounded shutdown behavior.

## S03 personal experiment library

Follow the [shared contract](../../../../docs/contracts/personal-experiments.md) for wire values, data origins,
public interfaces, validation scope, errors, immutable identity, paging and failure
handling. Implementation owner: A.

Compose ExperimentLibrary with trusted bundled source, SQLite repository,
GraphDefinitionValidator and a >=32-byte process-local cursor signing key. Install
definition_router only when execution is explicitly configured, under the existing
operator boundary. Keep viewer/legacy graph routes bundled and read-only. Use an
equivalent same-database library reader in ExecutionSetup.preparer; preserve the
existing ExecutionComposition.build(database, root) public signature. No database
I/O in constructors. Normal lifetime migration precedes request/admission reads.

Acceptance follows the shared S03 scenarios. Development delivery does not claim
testing is complete. Keep module-private choices within these public contracts.

## S03 development implementation

`experiment_library` composes the public library, local descriptor validator and
SQLite repository with a random 32-byte signing key. `create_app` adds definition
routes inside the configured operator boundary. `ExecutionSetup.preparer` creates
an equivalent reader using the same persistent database and immutable bundled
source. `ExecutionComposition.build(database, root)` retains its signature and
the existing lifespan initializes/migrates storage before serving requests.
Coordinator review and configured/viewer composition verification remain pending.

## S04–S06 active delivery

Follow [the shared contract](../../../../docs/contracts/product-workspace.md). Implementation owner: Coordinator.

Compose provider-neutral preparation, optional scoped tariff reader/independent DeepSeek refresh, memory storage adapter, discovery and bounded configuration services. Legacy setup signatures and offline injection remain compatible. Startup limits are UI ceilings; provider secrets remain launch-only.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
