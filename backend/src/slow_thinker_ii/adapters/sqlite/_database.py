"""The SQLite file: durable connections, immediate transactions, its schema and its owner lock."""

import sqlite3
from collections.abc import Generator
from contextlib import AbstractContextManager, closing, contextmanager
from pathlib import Path

from ._migrations import migrate
from ._ownership import own_store


class SqliteDatabase:
    """One connection per transaction, so that stores can be used from any thread."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def initialize(self) -> None:
        """Creates or migrates the schema; refuses a newer schema or a foreign database."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            migrate(connection, self._path)

    def ownership(self) -> AbstractContextManager[None]:
        """The exclusive owner lock on `<path>.owner`; a second owner gets `RuntimeError`."""
        return own_store(self._path)

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection]:
        """`BEGIN IMMEDIATE`; commits when the block ends, rolls back when it raises."""
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            with connection:
                yield connection

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, isolation_level=None, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            _configure(connection)
        except BaseException:
            connection.close()
            raise
        return connection


def _configure(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA journal_mode=DELETE")
    connection.execute("PRAGMA synchronous=EXTRA")
    values: list[object] = [
        connection.execute(f"PRAGMA {key}").fetchone()[0]
        for key in ("foreign_keys", "journal_mode", "synchronous")
    ]
    if values != [1, "delete", 3]:
        raise RuntimeError("SQLite durability settings were not applied")
