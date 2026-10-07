"""Migration of a schema 1 database: each version becomes the change it is activated from."""

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

import pytest
from slow_thinker_ii.adapters import sqlite as adapter
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteGraphStore,
    SqliteLedger,
    SqliteRunStore,
)
from slow_thinker_ii.application import (
    BranchSummary,
    ChangeSummary,
    GraphRecord,
    VersionRecord,
    VersionSummary,
)
from slow_thinker_ii.contracts import JsonObject

from .stores import pragma

CHAIN = "slow_thinker_ii.adapters.sqlite._migrations.MIGRATIONS"
RELEASED = tuple(Path(str(adapter.__file__)).with_name(f"schema-{n}.sql") for n in (1, 2, 3, 4))
FIRST, SECOND = '{"id":"funny-story","name":"Funny story"}', '{"id":"funny-story","name":"Funnier"}'
VERSION_ROWS = [
    ("funny-story", 1, "Funny story", FIRST, "2026-10-05T12:00:00.000000Z"),
    ("funny-story", 2, "Funnier", SECOND, "2026-10-05T12:01:00.000000Z"),
    ("story-triage", 1, "Story triage", '{"id":"story-triage"}', "2026-10-05T12:02:00.000000Z"),
]


def at(minute: int) -> datetime:
    return datetime(2026, 10, 5, 12, minute, tzinfo=UTC)


def schema_1(directory: Path, monkeypatch: pytest.MonkeyPatch) -> SqliteDatabase:
    """A version 1 database with two graphs, a run of version 2 and its spending."""
    database = SqliteDatabase(directory / "state.sqlite3")
    monkeypatch.setattr(CHAIN, RELEASED[:1])
    database.initialize()
    monkeypatch.setattr(CHAIN, RELEASED)
    with database.transaction() as connection:
        for graph_id, _, name, _, stamp in VERSION_ROWS[::2]:
            connection.execute(
                "INSERT INTO graphs VALUES (?, ?, 1, ?, ?)", (graph_id, name, stamp, stamp)
            )
        connection.execute("UPDATE graphs SET latest_version = 2 WHERE id = 'funny-story'")
        connection.executemany("INSERT INTO graph_versions VALUES (?, ?, ?, ?, ?)", VERSION_ROWS)
        connection.execute(
            "INSERT INTO runs VALUES ('r1', 'funny-story', 2, 'completed', NULL, '', '\"Hi\"', "
            "'2026-10-05T12:03:00.000000Z', '2026-10-05T12:04:00.000000Z', '{}')"
        )
        connection.execute(
            "INSERT INTO ledger VALUES ('c1', 'r1', '2026-10-05', '2026-10', 5, 3, 0, "
            "'2026-10-05T12:03:00.000000Z', '2026-10-05T12:04:00.000000Z')"
        )
    return database


def test_versions_become_changes_of_branch_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = schema_1(tmp_path, monkeypatch)
    database.initialize()
    assert pragma(tmp_path / "state.sqlite3", "user_version") == 4
    store = SqliteGraphStore(database)
    assert [(item.id, item.active_version, item.latest_change) for item in store.graphs()] == [
        ("story-triage", 1, 1),
        ("funny-story", 2, 2),
    ]
    main = BranchSummary("main", at(0), None, None, 2, 2)
    assert store.graph("funny-story") == GraphRecord(
        "funny-story",
        "Funnier",
        2,
        2,
        (main,),
        (
            VersionSummary(1, "main", None, 1, "Funny story", at(0)),
            VersionSummary(2, "main", 1, 2, "Funnier", at(1)),
        ),
    )
    assert store.changes("funny-story", "main", None, 10) == (
        ChangeSummary(2, "main", at(1), "Funnier", 2),
        ChangeSummary(1, "main", at(0), "Funny story", 1),
    )


def test_migrated_records_stay_readable_and_writable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = schema_1(tmp_path, monkeypatch)
    database.initialize()
    store = SqliteGraphStore(database)
    document: JsonObject = {"id": "funny-story", "name": "Funnier"}
    version = VersionRecord("funny-story", 2, "main", 1, 2, at(1), document)
    assert store.version("funny-story", 2) == version
    run = SqliteRunStore(database).run("r1")
    assert run is not None and (run.version, run.status) == (2, "completed")
    assert SqliteLedger(database).used("run", "r1") == 3
    assert store.add_change("funny-story", "main", "Third", {"id": "funny-story"}, at(5)) == 3
    assert store.add_version("funny-story", 3, 2, at(6)) == 3


def test_the_previous_version_is_backed_up_before_migrating(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema_1(tmp_path, monkeypatch).initialize()
    (backup,) = tmp_path.glob("state.sqlite3.v1.*.backup")
    assert pragma(backup, "user_version") == 1
    with closing(sqlite3.connect(backup)) as connection:
        rows = connection.execute("SELECT * FROM graph_versions ORDER BY rowid").fetchall()
    assert rows == VERSION_ROWS


def test_a_migration_that_would_break_a_reference_changes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = schema_1(tmp_path, monkeypatch)
    path = tmp_path / "state.sqlite3"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("DELETE FROM graphs WHERE id = 'story-triage'")  # keys are off here
    with pytest.raises(RuntimeError, match="would break a foreign key"):
        database.initialize()
    assert pragma(path, "user_version") == 1
    with closing(sqlite3.connect(path)) as connection:
        names = {row[0] for row in connection.execute("SELECT name FROM sqlite_schema")}
    assert "graph_changes" not in names and "graph_versions" in names
