"""`Ledger`: model-call reservations and charges in integer quanta of 10⁻⁹ USD.

A scope's used amount is the sum of `coalesce(charge, reserved)` over its rows: settled charges
plus open reservations. Admission reads every scope and inserts the reservation in one
`BEGIN IMMEDIATE` transaction, so concurrent reservations cannot exceed a limit together.
"""

import sqlite3
from collections.abc import Sequence
from datetime import datetime
from types import MappingProxyType

from slow_thinker_ii.accounting import Scope, day_key, first_exhausted, month_key

from ._database import SqliteDatabase
from ._rows import integer, stamp

USED = MappingProxyType(
    {
        "run": "SELECT coalesce(sum(coalesce(charge, reserved)), 0) AS used "
        "FROM ledger WHERE run_id = ?",
        "day": "SELECT coalesce(sum(coalesce(charge, reserved)), 0) AS used "
        "FROM ledger WHERE day_key = ?",
        "month": "SELECT coalesce(sum(coalesce(charge, reserved)), 0) AS used "
        "FROM ledger WHERE month_key = ?",
    }
)
RESERVE = (
    "INSERT INTO ledger (call_id, run_id, day_key, month_key, reserved, charge, estimated, "
    "reserved_at, settled_at) VALUES (?, ?, ?, ?, ?, NULL, 0, ?, NULL)"
)


class SqliteLedger:
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def reserve(
        self, call_id: str, run_id: str, scopes: Sequence[Scope], amount: int, at: datetime
    ) -> Scope | None:
        """Reserves `amount` in every scope, or returns the first exhausted scope with its use.

        The callers' `Scope.used` is ignored; the row takes the day and month keys of the
        given scopes (of `at` when a scope is absent).
        """
        keys = {scope.kind: scope.key for scope in scopes}
        day, month = keys.get("day", day_key(at)), keys.get("month", month_key(at))
        with self._database.transaction() as connection:
            current = [
                Scope(scope.kind, scope.key, scope.limit, _used(connection, scope.kind, scope.key))
                for scope in scopes
            ]
            exhausted = first_exhausted(current, amount)
            if exhausted is None:
                connection.execute(RESERVE, (call_id, run_id, day, month, amount, stamp(at)))
        return exhausted

    def settle(self, call_id: str, charge: int, estimated: bool, at: datetime) -> None:
        """Replaces the open reservation by its charge; a call settles once."""
        with self._database.transaction() as connection:
            changed = connection.execute(
                "UPDATE ledger SET charge = ?, estimated = ?, settled_at = ? "
                "WHERE call_id = ? AND charge IS NULL",
                (charge, int(estimated), stamp(at), call_id),
            ).rowcount
        if changed == 0:
            raise LookupError(f"Call “{call_id}” has no open reservation.")

    def used(self, kind: str, key: str) -> int:
        """Settled charges plus open reservations of the scope `kind` (run, day or month)."""
        with self._database.transaction() as connection:
            return _used(connection, kind, key)

    def settle_open(self, run_id: str, at: datetime) -> None:
        """Restart recovery: the run's open reservations become estimated charges."""
        with self._database.transaction() as connection:
            connection.execute(
                "UPDATE ledger SET charge = reserved, estimated = 1, settled_at = ? "
                "WHERE run_id = ? AND charge IS NULL",
                (stamp(at), run_id),
            )


def _used(connection: sqlite3.Connection, kind: str, key: str) -> int:
    query = USED.get(kind)
    if query is None:
        raise ValueError(f"Unknown budget scope kind: {kind}")
    return integer(connection.execute(query, (key,)).fetchone(), "used")
