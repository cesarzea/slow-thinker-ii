# SQLite persistence

Stores graphs and their versions, runs and their event logs, and the budget ledger in one
SQLite file, behind the application ports `GraphStore`, `RunStore` and `Ledger`.
`SqliteDatabase` owns the file: its owner lock, its schema and its transactions.

Use the [public entry point](__init__.py); private implementation files are not an
integration API. See [specification.md](specification.md) for the schema, the behaviour and
the acceptance criteria.
