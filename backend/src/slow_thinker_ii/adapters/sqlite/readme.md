# SQLite persistence

Stores operator intent, execution evidence, tariffs and budget accounting in local transactions.

`SqliteDefinitionRepository` stores canonical personal definitions with immutable
identity, insertion sequence and optional parent. Schema v6 adds only that table
and its parent index; the existing verified migration backup remains in force.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.
