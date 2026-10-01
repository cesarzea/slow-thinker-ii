"""Durable operator commands; preparation and component launch remain outside transactions."""

import sqlite3
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager

from slow_thinker_ii.application import (
    CommandReceipt,
    CommandResult,
    ExecutionConfiguration,
    PreparedStart,
    RecordingError,
    SavedSession,
    StartIntent,
)

from ._database import SqliteDatabase
from ._operator_profiles import activate, current_profile, period
from ._operator_rows import comparable, previous, read_receipt, save
from ._operator_sessions import create_session
from ._operator_start import admit
from ._operator_stops import stop, withdraw
from ._run_rows import bounded_json


class SqliteOperatorStore:
    def __init__(
        self,
        database: SqliteDatabase,
        max_command_bytes: int,
        clock: Callable[[], float] = time.monotonic,
        wall: Callable[[], float] = time.time,
    ) -> None:
        if type(max_command_bytes) is not int or max_command_bytes < 1:
            raise ValueError("A positive command recording limit is required")
        self._database, self._limit = database, max_command_bytes
        self._clock, self._wall = clock, wall

    @contextmanager
    def _unit(self) -> Generator[sqlite3.Connection]:
        try:
            with self._database.transaction() as db:
                yield db
        except sqlite3.Error as error:
            raise RecordingError("Unable to record operator command") from error

    def configure(self, profile: ExecutionConfiguration) -> None:
        with self._unit() as db:
            bounded_json(db, profile.to_json(), self._limit)
            activate(db, profile, self._wall())

    def profile(self) -> ExecutionConfiguration | None:
        with self._unit() as db:
            return current_profile(db)

    def create_session(self, command_id: str, name: str) -> CommandResult:
        with self._unit() as db:
            timestamp = self._wall()
            period(timestamp)
            return create_session(db, command_id, name, timestamp, self._limit)

    def session(self, identity: str) -> SavedSession | None:
        with self._unit() as db:
            row = db.execute(
                "SELECT * FROM operator_sessions WHERE session_id=?", (identity,)
            ).fetchone()
            return (
                None
                if row is None
                else SavedSession(
                    str(row["session_id"]), str(row["name"]), float(row["created_at"])
                )
            )

    def command(self, command_id: str) -> CommandReceipt | None:
        with self._unit() as db:
            return read_receipt(db, command_id)

    def resolve(self, command_id: str, intent: StartIntent) -> CommandResult | None:
        with self._unit() as db:
            body = comparable(command_id, intent.to_json(), self._limit)
            return previous(db, command_id, "start", body)

    def admit(self, command_id: str, prepared: PreparedStart) -> CommandResult:
        with self._unit() as db:
            return admit(db, command_id, prepared, self._wall(), self._clock(), self._limit)

    def reject(self, command_id: str, intent: StartIntent, reason: str) -> CommandResult:
        if not reason:
            raise ValueError("A rejected intention needs a reason")
        with self._unit() as db:
            body = comparable(command_id, intent.to_json(), self._limit)
            existing = previous(db, command_id, "start", body)
            if existing is not None:
                return existing
            return save(
                db,
                CommandReceipt(command_id, "start", "rejected", reason=reason),
                body,
                self._limit,
            )

    def stop(self, command_id: str, run_id: str) -> CommandResult:
        with self._unit() as db:
            return stop(db, command_id, run_id, self._clock(), self._limit)

    def withdraw(self, command_id: str) -> CommandResult:
        with self._unit() as db:
            return withdraw(db, command_id, self._clock(), self._limit)
