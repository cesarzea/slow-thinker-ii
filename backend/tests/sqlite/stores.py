"""Temporary databases and the records the store tests share."""

import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteGraphStore
from slow_thinker_ii.application import NewEvent, RunRecord
from slow_thinker_ii.contracts import JsonObject, JsonValue

AT = datetime(2026, 10, 5, 12, 0, 0, 123_456, tzinfo=UTC)
GRAPH = "funny-story"


def initialized(directory: Path) -> SqliteDatabase:
    database = SqliteDatabase(directory / "state.sqlite3")
    database.initialize()
    return database


def later(seconds: float) -> datetime:
    return AT + timedelta(seconds=seconds)


def with_graph(database: SqliteDatabase, graph_id: str = GRAPH) -> SqliteDatabase:
    """The database with version 1 of `graph_id`, activated from change 1; runs reference it."""
    store = SqliteGraphStore(database)
    store.create(graph_id, "Funny story", {"id": graph_id}, AT)
    store.add_version(graph_id, 1, None, AT)
    return database


def starting(
    run_id: str, graph_id: str = GRAPH, at: datetime = AT, input: JsonValue = "Hi"
) -> RunRecord:
    return RunRecord(run_id, graph_id, 1, 1, "starting", None, "", input, at, None, None)


def observed(kind: str = "run.running", data: JsonObject | None = None) -> NewEvent:
    return NewEvent(AT, 5, kind, "observed", None, None, {} if data is None else data)


def pragma(path: Path, name: str) -> object:
    """A header value read without the adapter, for checks on refused files."""
    with closing(sqlite3.connect(path)) as connection:
        value: object = connection.execute(f"PRAGMA {name}").fetchone()[0]
    return value
