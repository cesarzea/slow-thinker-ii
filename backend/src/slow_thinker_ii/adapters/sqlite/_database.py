"""Backend-owned SQLite connections with explicit durability and transactions."""

import sqlite3
from collections.abc import Iterator
from contextlib import AbstractContextManager, closing, contextmanager
from pathlib import Path

from ._migrations import migrate
from ._ownership import own_store


class SqliteDatabase:
    def __init__(self, path: Path) -> None:
        self._path = path

    def initialize(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            migrate(connection, self._path)

    def ownership(self) -> AbstractContextManager[None]:
        return own_store(self._path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, isolation_level=None, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            self._configure(connection)
        except BaseException:
            connection.close()
            raise
        return connection

    @staticmethod
    def _configure(connection: sqlite3.Connection) -> None:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=EXTRA")
        values = [
            connection.execute(f"PRAGMA {key}").fetchone()[0]
            for key in ("foreign_keys", "journal_mode", "synchronous")
        ]
        if values != [1, "delete", 3]:
            raise RuntimeError("SQLite durability settings were not applied")

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            with connection:
                yield connection
