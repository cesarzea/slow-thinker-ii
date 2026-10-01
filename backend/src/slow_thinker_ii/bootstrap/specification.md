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
