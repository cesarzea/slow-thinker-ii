"""Durability configuration, schema rejection and arithmetic overflow fail closed."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from slow_thinker_ii.accounting import MAX_QUANTA, Reservation
from slow_thinker_ii.adapters.sqlite import SqliteDatabase

from .conftest import LedgerFixture, balances


def test_durability_and_row_interface(tmp_path: Path) -> None:
    database = SqliteDatabase(tmp_path / "db.sqlite")
    database.initialize()
    with database.transaction() as connection:
        assert connection.row_factory is sqlite3.Row
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 3


def test_newer_schema_is_never_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "db.sqlite"
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA user_version=999")
    with pytest.raises(ValueError, match="Unsupported database"):
        SqliteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 999


def test_storage_overflow_cannot_convert_money_to_float(ledger_case: LedgerFixture) -> None:
    ledger = ledger_case.ledger
    ledger.reserve(Reservation("a", ledger_case.keys, 1))
    ledger.dispatched("a")
    with closing(sqlite3.connect(ledger_case.path)) as connection, connection:
        connection.execute("UPDATE budget_scopes SET settled=?", (MAX_QUANTA,))
    with pytest.raises(sqlite3.IntegrityError):
        ledger.settle("a", 1, "overflows-storage")
    assert all(scope.settled == MAX_QUANTA for scope in balances(ledger_case))
    assert all(scope.outstanding == 1 for scope in balances(ledger_case))
