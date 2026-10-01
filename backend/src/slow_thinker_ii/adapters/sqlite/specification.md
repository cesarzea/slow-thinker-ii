# SQLite persistence: specification

Stores operator intent, execution evidence, tariffs and budget accounting in local transactions.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- SqliteDatabase owns initialization, runtime ownership and transactions.
- SqliteLedgerStore and SqliteRunStore implement accounting and execution persistence ports.
- SqliteOperatorStore persists configuration, sessions and idempotent commands.
- SqliteOperatorQueries projects runs, calls, activations and retained payloads.
- SqliteTariffStore keeps immutable tariff revisions and refresh state.

## Required behavior

- Keep transactions short and atomic across all affected budget scopes.
- Persist dispatch intent before external effects and retain admission-month attribution.
- Do not replay ambiguous attempts after recovery or rewrite terminal outcomes for late charges.
- Retain scoped payload references, capture status and bounded pagination.

## Dependencies and ownership

SQLite and public application/accounting contracts; no provider or component network calls.

## Acceptance criteria

- Concurrent reservations cannot overspend a shared scope.
- Repeated receipts do not double charge, and late settlement retains the original scopes.
- A recorded charge above its reserved bound is retained and triggers the accounting-policy response.

## Shared contracts

- [0011-local-persistence](../../../../../docs/adr/0011-local-persistence.md)
- [accounting-policy](../../../../../docs/contracts/accounting-policy.md)

## Verification

Storage tests verify schema-v5 backups, over-reservation charges and persistent quarantine, immutable saved definitions, report capture, fixed execution pages and atomic process journals.

## Sprint additions

- [managed-gateway](../../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [conditional-routing](../../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [inspection-projections](../../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

Schema migration v5 adds durable process ownership and pricing quarantine. A first charge above its reservation is retained, recorded and quarantines its frozen tariff revision even with aggregate headroom. Projections retain conditional source references, reported payloads and fixed event-boundary call states. Any pending ownership record blocks admission until verified stopped.

## October 2026 maintenance: Generator typing compatibility

The `@contextmanager` implementations use `Generator[YieldedType]`
for Pyright 1.1.414. `SqliteDatabase.transaction` and `SqliteOperatorStore._unit`
yield `sqlite3.Connection`; `SqliteRunStore.begin` yields `RunTransaction`;
`SqliteLedgerStore.begin` yields `LedgerTransaction`; `own_store` yields `None`.
Preserve transaction/ownership semantics and ordinary iterator interfaces.
