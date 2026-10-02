"""Dedicated lazy SQLite transactions; host shutdown never deletes resource data."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import cast


@contextmanager
def transaction(path: Path) -> Generator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5, isolation_level=None)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS memory_entries (namespace TEXT NOT NULL, "
            "key TEXT NOT NULL, value_json TEXT NOT NULL, version INTEGER NOT NULL, "
            "PRIMARY KEY(namespace,key))"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS memory_versions "
            "(namespace TEXT PRIMARY KEY, version INTEGER NOT NULL)"
        )
        yield connection
        connection.execute("COMMIT")
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def entry(connection: sqlite3.Connection, namespace: str, key: str) -> tuple[str, int] | None:
    raw: object = connection.execute(
        "SELECT value_json,version FROM memory_entries WHERE namespace=? AND key=?",
        (namespace, key),
    ).fetchone()
    if raw is None:
        return None
    row = cast(tuple[object, object], raw)
    if not isinstance(row[0], str) or type(row[1]) is not int or row[1] <= 0:
        raise ValueError("Invalid durable memory record")
    return row[0], row[1]


def next_version(connection: sqlite3.Connection, namespace: str) -> int:
    raw: object = connection.execute(
        "INSERT INTO memory_versions(namespace,version) VALUES(?,1) "
        "ON CONFLICT(namespace) DO UPDATE SET version=version+1 RETURNING version",
        (namespace,),
    ).fetchone()
    row = cast(tuple[object], raw)
    if type(row[0]) is not int or row[0] <= 0:
        raise ValueError("Memory version counter is exhausted")
    return row[0]


def count(connection: sqlite3.Connection, namespace: str) -> int:
    raw: object = connection.execute(
        "SELECT count(*) FROM memory_entries WHERE namespace=?", (namespace,)
    ).fetchone()
    row = cast(tuple[object], raw)
    if type(row[0]) is not int:
        raise ValueError("Invalid durable memory count")
    return row[0]


def keys(
    connection: sqlite3.Connection, namespace: str, after: str, limit: int
) -> list[tuple[str, int]]:
    raw: object = connection.execute(
        "SELECT key,version FROM memory_entries WHERE namespace=? AND key>? ORDER BY key LIMIT ?",
        (namespace, after, limit),
    ).fetchall()
    result: list[tuple[str, int]] = []
    for row in cast(list[tuple[object, object]], raw):
        if not isinstance(row[0], str) or type(row[1]) is not int or row[1] <= 0:
            raise ValueError("Invalid durable memory key")
        result.append((row[0], row[1]))
    return result
