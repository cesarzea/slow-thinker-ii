"""Schema installation and migration; refuses newer or foreign databases and backs up before change.

`MIGRATIONS[n]` is the SQL script that brings a database from version `n` to `n + 1`. The version is
`PRAGMA user_version`; `PRAGMA application_id` marks databases created by this package, so that a
file with an unrelated schema is never mistaken for one of ours, whatever its user version.
"""

import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4

APPLICATION_ID = 0x53543249  # "ST2I"
MIGRATIONS = (
    Path(__file__).with_name("schema-1.sql"),
    Path(__file__).with_name("schema-2.sql"),
    Path(__file__).with_name("schema-3.sql"),
    Path(__file__).with_name("schema-4.sql"),
)


def migrate(connection: sqlite3.Connection, path: Path) -> None:
    """Brings the database to the current version in one transaction, after a verified backup."""
    version = _version(connection, path)
    if version == len(MIGRATIONS):
        return
    before = _scalar(connection, "PRAGMA data_version")
    if version > 0:
        backup(connection, path, version)
    connection.execute("PRAGMA foreign_keys=OFF")  # scripts rebuild tables; checked below
    connection.execute("BEGIN IMMEDIATE")
    try:
        if _scalar(connection, "PRAGMA data_version") != before:
            raise RuntimeError("The database changed while its migration was prepared")
        for script in MIGRATIONS[version:]:
            execute_script(connection, script.read_text(encoding="utf-8"))
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise RuntimeError("The migration would break a foreign key")
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute(f"PRAGMA user_version={len(MIGRATIONS)}")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys=ON")


def execute_script(connection: sqlite3.Connection, source: str) -> None:
    """Executes complete statements one by one, inside the caller's transaction."""
    statement = ""
    for line in source.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            connection.execute(statement)
            statement = ""
    if statement.strip():
        raise ValueError("Incomplete migration statement")


def backup(connection: sqlite3.Connection, path: Path, version: int) -> None:
    """Copies the database next to it and checks the copy before anything is changed."""
    target = path.with_name(f"{path.name}.v{version}.{uuid4().hex}.backup")
    with closing(sqlite3.connect(target)) as destination:
        connection.backup(destination)
        integrity = _scalar(destination, "PRAGMA integrity_check")
        copied = _scalar(destination, "PRAGMA user_version")
    if integrity != "ok" or copied != version:
        raise RuntimeError("Pre-migration backup failed validation")


def _version(connection: sqlite3.Connection, path: Path) -> int:
    application = _scalar(connection, "PRAGMA application_id")
    version = _scalar(connection, "PRAGMA user_version")
    objects = _scalar(connection, "SELECT count(*) FROM sqlite_schema")
    if application == version == objects == 0:
        return 0
    if application != APPLICATION_ID:
        raise ValueError(
            f"Unsupported database {path}: it was created by another application or an earlier "
            "Slow Thinker II implementation. Move it away or configure another database file."
        )
    if not isinstance(version, int) or version > len(MIGRATIONS):
        raise ValueError(f"Unsupported database schema version in {path}: newer than this release")
    return version


def _scalar(connection: sqlite3.Connection, query: str) -> object:
    value: object = connection.execute(query).fetchone()[0]
    return value
