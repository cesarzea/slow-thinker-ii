"""Versioned schema installation retains a verified SQLite backup before migration."""

import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4


def migrate(connection: sqlite3.Connection, path: Path) -> None:
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version not in (0, 1, 2, 3, 4):
        raise ValueError("Unsupported database schema version")
    if version == 4:
        return
    before = connection.execute("PRAGMA data_version").fetchone()[0]
    if version > 0:
        backup(connection, path)
    connection.execute("BEGIN IMMEDIATE")
    try:
        if connection.execute("PRAGMA data_version").fetchone()[0] != before:
            raise RuntimeError("Database changed during migration preparation")
        if version == 2:
            require_stopped(connection)
        for name in ("schema.sql", "execution.sql", "receipts.sql", "operator.sql")[version:]:
            execute_schema(connection, Path(__file__).with_name(name).read_text())
        connection.execute("PRAGMA user_version=4")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise


def require_stopped(connection: sqlite3.Connection) -> None:
    active = connection.execute(
        "SELECT 1 FROM managed_runs WHERE state IN ('created','running','stopping') LIMIT 1"
    ).fetchone()
    if active is not None:
        raise ValueError("Schema migration requires recovered or terminal runs")


def execute_schema(connection: sqlite3.Connection, source: str) -> None:
    statement = ""
    for line in source.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            connection.execute(statement)
            statement = ""
    if statement.strip():
        raise ValueError("Incomplete migration statement")


def backup(connection: sqlite3.Connection, path: Path) -> None:
    original = connection.execute("PRAGMA user_version").fetchone()[0]
    backup = path.with_name(f"{path.name}.v{original}.{uuid4().hex}.backup")
    with closing(sqlite3.connect(backup)) as destination:
        connection.backup(destination)
        integrity = destination.execute("PRAGMA integrity_check").fetchone()[0]
        version = destination.execute("PRAGMA user_version").fetchone()[0]
        if integrity != "ok" or version != original:
            raise RuntimeError("Pre-migration backup failed validation")
