"""Durable connections, the current schema, refusal of newer or foreign files, backups."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from slow_thinker_ii.adapters import sqlite as adapter
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteGraphStore

from .stores import AT, initialized, pragma

TABLES = [
    "graph_branches",
    "graph_changes",
    "graph_versions",
    "graphs",
    "ledger",
    "run_events",
    "runs",
]
CHAIN = "slow_thinker_ii.adapters.sqlite._migrations.MIGRATIONS"
RELEASED = tuple(Path(str(adapter.__file__)).with_name(f"schema-{n}.sql") for n in (1, 2, 3, 4))
CURRENT = len(RELEASED)
STAMP = "2026-10-05T12:00:00.123456Z"  # a stored time


def tables(database: SqliteDatabase) -> list[str]:
    with database.transaction() as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name"
        ).fetchall()
    return [str(row["name"]) for row in rows]


def test_every_transaction_is_durable_and_returns_rows(tmp_path: Path) -> None:
    database = initialized(tmp_path)
    with database.transaction() as connection:
        assert connection.row_factory is sqlite3.Row
        assert connection.in_transaction
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 3


def insert_graph(database: SqliteDatabase, graph_id: str, failure: Exception | None) -> None:
    """Inserts a graph and its first change in one transaction, then raises `failure` if given."""
    with database.transaction() as connection:
        connection.execute("INSERT INTO graphs VALUES (?, ?)", (graph_id, STAMP))
        connection.execute(
            "INSERT INTO graph_branches VALUES (?, 'main', 'main', ?, NULL, NULL)",
            (graph_id, STAMP),
        )
        connection.execute(
            "INSERT INTO graph_changes VALUES (?, 1, 'main', ?, 'G', '{}')", (graph_id, STAMP)
        )
        if failure is not None:
            raise failure


def test_a_transaction_commits_its_block_or_nothing(tmp_path: Path) -> None:
    database = initialized(tmp_path)
    with pytest.raises(RuntimeError, match="abandoned"):
        insert_graph(database, "abandoned", RuntimeError("abandoned"))
    assert SqliteGraphStore(database).graphs() == ()
    insert_graph(database, "kept", None)
    assert [graph.id for graph in SqliteGraphStore(database).graphs()] == ["kept"]


def test_initialization_creates_the_current_schema_once(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "state.sqlite3"
    database = SqliteDatabase(path)
    database.initialize()
    SqliteGraphStore(database).create("g", "G", {"id": "g"}, AT)
    database.initialize()
    assert tables(database) == TABLES
    assert pragma(path, "user_version") == CURRENT
    assert pragma(path, "application_id") == 0x53543249
    assert [summary.id for summary in SqliteGraphStore(database).graphs()] == ["g"]
    assert sorted(item.name for item in path.parent.iterdir()) == ["state.sqlite3"]


def test_a_newer_schema_is_refused_and_left_unchanged(tmp_path: Path) -> None:
    database = initialized(tmp_path)
    path = tmp_path / "state.sqlite3"
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(f"PRAGMA user_version={CURRENT + 1}")
    with pytest.raises(ValueError, match="Unsupported database schema version"):
        database.initialize()
    assert pragma(path, "user_version") == CURRENT + 1


@pytest.mark.parametrize("version", [0, 1, 6])
def test_a_database_of_another_application_is_refused_unchanged(
    tmp_path: Path, version: int
) -> None:
    path = tmp_path / "state.sqlite3"
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("CREATE TABLE budget_scopes (kind TEXT, cap INTEGER)")
        connection.execute(f"PRAGMA user_version={version}")
    with pytest.raises(ValueError, match="another application or an earlier Slow Thinker II"):
        SqliteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as connection:
        names = [row[0] for row in connection.execute("SELECT name FROM sqlite_schema")]
    assert names == ["budget_scopes"]
    assert pragma(path, "user_version") == version


def test_a_migration_keeps_a_verified_backup_of_the_previous_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = initialized(tmp_path)
    SqliteGraphStore(database).create("g", "G", {"id": "g"}, AT)
    script = tmp_path / "schema-next.sql"
    script.write_text(
        "-- The next version, for this test.\nCREATE TABLE notes (text TEXT) STRICT;\n"
    )
    monkeypatch.setattr(CHAIN, (*RELEASED, script))
    database.initialize()
    assert "notes" in tables(database)
    assert pragma(tmp_path / "state.sqlite3", "user_version") == CURRENT + 1
    (backup,) = tmp_path.glob(f"state.sqlite3.v{CURRENT}.*.backup")
    assert pragma(backup, "user_version") == CURRENT
    with closing(sqlite3.connect(backup)) as connection:
        assert connection.execute("SELECT id FROM graphs").fetchall() == [("g",)]


def test_an_incomplete_migration_script_changes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = initialized(tmp_path)
    script = tmp_path / "schema-next.sql"
    script.write_text("CREATE TABLE notes (text TEXT) STRICT;\nCREATE TABLE half (")
    monkeypatch.setattr(CHAIN, (*RELEASED, script))
    with pytest.raises(ValueError, match="Incomplete migration statement"):
        database.initialize()
    assert "notes" not in tables(database)
    assert pragma(tmp_path / "state.sqlite3", "user_version") == CURRENT
