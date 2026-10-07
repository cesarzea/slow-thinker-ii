# adapters.sqlite: specification

Persistence for step 1 behind the application ports `GraphStore`, `RunStore` and
`Ledger` ([application specification](../../application/specification.md)).

## Public interface (`slow_thinker_ii.adapters.sqlite`)

```python
class SqliteDatabase:
    def __init__(self, path: Path) -> None
    def initialize(self) -> None                     # creates or migrates; refuses a newer schema
    def ownership(self) -> ContextManager[None]       # exclusive owner lock on "<path>.owner"
    def transaction(self) -> ContextManager[sqlite3.Connection]   # BEGIN IMMEDIATE

class SqliteGraphStore(GraphStore): def __init__(self, database: SqliteDatabase) -> None
class SqliteRunStore(RunStore):     def __init__(self, database: SqliteDatabase, max_payload_bytes: int = 262_144) -> None
class SqliteLedger(Ledger):         def __init__(self, database: SqliteDatabase) -> None
```

Every transaction opens its own connection, so the stores can be used from any thread.
Connections set and check `foreign_keys=ON`, `journal_mode=DELETE` and `synchronous=EXTRA`
(`RuntimeError` otherwise), a five-second busy timeout and `sqlite3.Row` rows.
`transaction()` commits when its block ends and rolls back when it raises.

## Schema, version 4

| Table           | Columns                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------- |
| `graphs`        | `id` PK, `created_at`                                                                          |
| `graph_branches`| `graph_id`, `name`, `folded`, `created_at`, `from_version`, `from_change`; PK (`graph_id`, `name`), unique (`graph_id`, `folded`) |
| `graph_changes` | `graph_id`, `change`, `branch`, `at`, `name`, `document_json`; PK (`graph_id`, `change`)       |
| `graph_versions`| `graph_id`, `version`, `branch`, `parent`, `change`, `created_at`; PK (`graph_id`, `version`); (`graph_id`, `change`) references `graph_changes`, (`graph_id`, `parent`) `graph_versions` |
| `runs`          | `id` PK, `graph_id`, `graph_version` (null for a change never activated), `graph_change`, `status`, `reason`, `detail`, `input_json`, `created_at`, `ended_at`, `totals_json`; (`graph_id`, `graph_change`) references `graph_changes` |
| `run_events`    | `run_id`, `seq`, `at`, `elapsed_ms`, `kind`, `evidence`, `node_id`, `activation_id`, `data_json`; PK (`run_id`, `seq`) |
| `ledger`        | `call_id` PK, `run_id`, `day_key`, `month_key`, `reserved`, `charge` NULL, `estimated`, `reserved_at`, `settled_at` |

Versions 2 and 3 follow [ADR 0024](../../../../../docs/adr/0024-working-copy-and-activated-versions.md):
a graph has branches, `main` first, each with a working copy of append-only changes; a version
names its branch, the change it was activated from (whose document it is) and the version it
follows (`parent`). Branch names are unique per graph ignoring case: `folded` holds
`str.casefold()` of the name. A branch records the version or change it started from. The graph's name, latest change, active version (the
highest) and `updated_at` (the latest change's time) are read from changes and versions, not
stored twice.

The tables are `STRICT`, with `NOT NULL` wherever a value is required. Foreign keys tie
changes and versions to graphs, versions to their change, runs to their graph version and
events to their run; `evidence` is
`observed` or `reported`; amounts and counts are non-negative. Times are stored as UTC text
`YYYY-MM-DDTHH:MM:SS.ffffffZ` (sortable, microseconds kept) and come back aware; naive
times are refused with `ValueError`. JSON columns keep object keys in their given order
(compact, UTF-8) and are decoded with duplicate-key and finiteness checks.

`ledger` amounts are integer quanta. A scope's used amount is the sum of
`coalesce(charge, reserved)` over its rows. `reserve` reads the three scopes and
inserts the reservation in one `BEGIN IMMEDIATE` transaction; `append` assigns
`seq = max(seq) + 1` in its own transaction. Payloads in `data_json` larger than
`max_payload_bytes` are truncated exactly as the [recording contract](../../../../../docs/contracts/recording.md)
specifies, before storage.

## Schema versions

`PRAGMA user_version` is the schema version and `PRAGMA application_id` (`0x53543249`)
marks a database created here. `initialize()` creates the schema in an empty file, does
nothing at the current version, and otherwise migrates in one transaction: script `n`
(`schema-<n+1>.sql`) brings version `n` to `n + 1`. Scripts may rebuild tables, so foreign
keys are off during the transaction and `PRAGMA foreign_key_check` must find nothing before
it commits (`RuntimeError` otherwise, nothing changed). Migration 1 → 2 turns each version
into the change of the same number, document, name and time, linked to that version, and
keeps runs, events and the ledger unchanged. Migration 2 → 3 adds branch `main` to every
graph (created with the graph, started from nothing), puts every change and version on it,
and makes each version's `parent` the previous version. Migration 3 → 4 gives every run
the change of its version in `graph_change` and lets `graph_version` be null. Before migrating a database of version
1 or later it copies it to `<path>.v<version>.<uuid>.backup` and checks the copy
(`integrity_check` and version), and it aborts if the file changed meanwhile. It refuses,
leaving the file unchanged, a newer version (`Unsupported database schema version …`) and
any non-empty file without the application id, whatever its version, such as a database of
the previous implementation (`Unsupported database <path>: it was created by another
application or an earlier Slow Thinker II implementation. …`).

## Behaviour

- **Graphs.** `create` stores branch `main` with change 1 and no version, or raises
  `GraphExists`. `create_branch` raises `GraphNotFound` or `BranchExists` (the name taken
  ignoring case) and otherwise stores the branch, its start and its first change.
  `add_change` raises `GraphNotFound` or `BranchNotFound`, returns the branch's latest
  number without storing anything when the document's stored JSON (compact, keys in their
  order) equals that change's, and otherwise appends the graph's next number: a reorder of
  keys is a change. `changes(graph_id, branch, before, limit)` lists the changes of one
  branch (every branch when `None`) numbered below `before`, newest first, at most `limit`,
  each with the latest version activated from it. `add_version` raises `ChangeNotFound` for
  an absent change and otherwise stores the graph's next version on that change's branch,
  following the given `parent`, also for a change activated before. Change and version
  numbers are per graph across branches, read and used in one `BEGIN IMMEDIATE`
  transaction, so concurrent writers never leave gaps. `graphs()` is ordered by the latest
  change's time descending, ties by the latest created graph; branches are listed oldest
  first with their latest change and head version, versions oldest first.
- **Runs.** `create` stores the record as given (`starting`, no end, no totals).
  `finish` sets the terminal status, reason, detail, totals and end once: an unknown run
  raises `RunNotFound`, a finished one `ValueError`. `runs` is ordered by `created_at`
  descending, ties by the latest insertion; `unfinished` (no end time) oldest first. A
  `limit` of zero or less returns nothing. A run of a missing graph version, or an event of
  a missing run, raises `sqlite3.IntegrityError`.
- **Bounds.** Only the top-level payload-like fields of an event's data are bounded:
  `payload`, `input`, `arguments`, `result`, `request`, `response` and `content`; usage,
  amounts and every other field are kept intact. A field whose serialization (compact JSON,
  keys in their order, UTF-8) exceeds `max_payload_bytes` becomes `{"truncated": true,
  "bytes": <serialized size>, "preview": <its first 4096 bytes as text>}`, dropping a
  character cut at the end. `append` returns the event as stored.
- **Ledger.** `reserve` ignores the callers' `Scope.used`, returns the first exhausted scope
  with its current used amount, or inserts the reservation and returns `None`. The row takes
  the day and month keys of the given scopes, or those of `at` when a scope is absent.
  `settle` replaces an open reservation once (`LookupError` otherwise); `settle_open` turns
  a run's open reservations into estimated charges equal to them; `used` of an unknown scope
  kind raises `ValueError`.

## Porting

Start from `origin/main` (`backend/src/slow_thinker_ii/adapters/sqlite/`):
`_database.py`, `_ownership.py`, `_rows.py` and the backup-and-verify part of
`_migrations.py` (a fresh migration chain starting at version 1). Carry and adapt
`backend/tests/integration/test_database.py` and `test_backend_ownership.py`.
Nothing else from the previous schema is carried.

## Acceptance

Tests with temporary databases cover each store method, version numbering, conflicts,
seq allocation under concurrent appends from threads, atomic reservation under
concurrent reservations that together exceed a limit, settlement, estimated settlement
of open reservations, truncation, the owner lock and refusing a newer schema; for version
2 and 3, the migrations of schema 1 and 2 databases with their backups, branches started
from a version and from a change, names unique ignoring case, deduplication against the
branch's latest change, paging of changes, the version lineage, and gap-free change and
version numbers under concurrent writers on several branches. Branch coverage at least 90%.
