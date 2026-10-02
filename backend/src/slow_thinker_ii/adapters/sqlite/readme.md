# SQLite persistence

Stores operator intent, execution evidence, tariffs and budget accounting in local transactions.

`SqliteDefinitionRepository` stores canonical personal definitions with immutable
identity, insertion sequence and optional parent. Schema v6 adds only that table
and its parent index; the existing verified migration backup remains in force.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
