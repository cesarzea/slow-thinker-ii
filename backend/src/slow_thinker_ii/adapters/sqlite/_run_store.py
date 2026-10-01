"""One transactional store for managed run records and their ledger obligations."""

import sqlite3
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager

from slow_thinker_ii.application import RecordingError, RunTransaction

from ._database import SqliteDatabase
from ._run_transaction import SqliteRunTransaction


class SqliteRunStore:
    def __init__(
        self,
        database: SqliteDatabase,
        max_payload_bytes: int,
        wall: Callable[[], float] = time.time,
    ) -> None:
        if type(max_payload_bytes) is not int or max_payload_bytes < 1:
            raise ValueError("A positive payload recording bound is required")
        self._database, self._limit = database, max_payload_bytes
        self._wall = wall

    @contextmanager
    def begin(self) -> Generator[RunTransaction]:
        try:
            with self._database.transaction() as connection:
                yield SqliteRunTransaction(connection, self._limit, self._wall)
        except sqlite3.Error as error:
            raise RecordingError("Unable to record execution") from error
