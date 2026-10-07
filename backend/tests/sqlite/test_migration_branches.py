"""Migration of a schema 2 database: everything becomes branch `main`, versions form a lineage."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from slow_thinker_ii.adapters import sqlite as adapter
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteGraphStore,
    SqliteLedger,
    SqliteRunStore,
)

from .stores import pragma

CHAIN = "slow_thinker_ii.adapters.sqlite._migrations.MIGRATIONS"
RELEASED = tuple(Path(str(adapter.__file__)).with_name(f"schema-{n}.sql") for n in (1, 2, 3, 4))
T = "2026-10-05T12:00:00.000000Z"
CHANGE_ROWS = [("g", n, T, f"Name {n}", f'{{"id":"g","name":"Name {n}"}}') for n in (1, 2, 3)]


def schema_2(directory: Path, monkeypatch: pytest.MonkeyPatch) -> SqliteDatabase:
    """A version 2 database: one graph, three changes, versions of changes 1, 3 and 3."""
    database = SqliteDatabase(directory / "state.sqlite3")
    monkeypatch.setattr(CHAIN, RELEASED[:2])
    database.initialize()
    monkeypatch.setattr(CHAIN, RELEASED)
    with database.transaction() as connection:
        connection.execute("INSERT INTO graphs VALUES ('g', ?)", (T,))
        connection.executemany("INSERT INTO graph_changes VALUES (?, ?, ?, ?, ?)", CHANGE_ROWS)
        connection.executemany(
            "INSERT INTO graph_versions VALUES ('g', ?, ?, ?)", [(1, 1, T), (2, 3, T), (3, 3, T)]
        )
        connection.execute(
            f"INSERT INTO runs VALUES ('r1', 'g', 3, 'completed', NULL, '', 'null', '{T}', "
            f"'{T}', '{{}}')"
        )
        connection.execute(
            f"INSERT INTO ledger VALUES ('c1', 'r1', '2026-10-05', '2026-10', 5, 2, 0, '{T}', NULL)"
        )
    return database


def rows(path: Path, query: str) -> list[tuple[object, ...]]:
    with closing(sqlite3.connect(path)) as connection:
        return [tuple(row) for row in connection.execute(query)]


def test_everything_existing_becomes_branch_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema_2(tmp_path, monkeypatch).initialize()
    path = tmp_path / "state.sqlite3"
    assert pragma(path, "user_version") == 4
    assert rows(path, "SELECT * FROM graph_branches") == [("g", "main", "main", T, None, None)]
    assert rows(path, "SELECT change, branch, name FROM graph_changes ORDER BY change") == [
        (1, "main", "Name 1"),
        (2, "main", "Name 2"),
        (3, "main", "Name 3"),
    ]
    assert rows(path, "SELECT version, branch, parent, change FROM graph_versions") == [
        (1, "main", None, 1),
        (2, "main", 1, 3),
        (3, "main", 2, 3),
    ]
    assert rows(path, "PRAGMA foreign_key_check") == []
    record = SqliteGraphStore(SqliteDatabase(path)).graph("g")
    assert record is not None and [(v.version, v.parent) for v in record.versions] == [
        (1, None),
        (2, 1),
        (3, 2),
    ]
    assert [(b.name, b.latest_change, b.head_version) for b in record.branches] == [("main", 3, 3)]


def test_runs_and_spending_are_kept_and_the_previous_schema_is_backed_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = schema_2(tmp_path, monkeypatch)
    database.initialize()
    run = SqliteRunStore(database).run("r1")
    assert run is not None and (run.version, run.change, run.status) == (3, 3, "completed")
    path = tmp_path / "state.sqlite3"
    assert rows(path, "SELECT graph_version, graph_change FROM runs") == [(3, 3)]
    assert SqliteLedger(database).used("run", "r1") == 2
    (backup,) = tmp_path.glob("state.sqlite3.v2.*.backup")
    assert pragma(backup, "user_version") == 2
    assert rows(backup, "SELECT * FROM graph_changes ORDER BY change") == CHANGE_ROWS
