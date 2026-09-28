"""Atomic admission and idempotent settlement on a real SQLite store."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import pytest
from slow_thinker_ii.accounting import BudgetExceeded, Reservation
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteLedgerStore
from slow_thinker_ii.application import BudgetLedger

from .conftest import LedgerFixture, balances


def test_competing_reservations_cannot_spend_the_same_allowance(ledger_case: LedgerFixture) -> None:
    def reserve(identifier: str) -> bool:
        try:
            ledger_case.ledger.reserve(Reservation(identifier, ledger_case.keys, 600))
            return True
        except BudgetExceeded:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, ("a", "b")))
    assert sum(results) == 1
    assert all(scope.outstanding == 600 for scope in balances(ledger_case))


def test_settlement_releases_unused_money_once(ledger_case: LedgerFixture) -> None:
    ledger = ledger_case.ledger
    ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger.dispatched("a")
    assert ledger.settle("a", 250, "provider-1") == "applied"
    assert ledger.settle("a", 250, "provider-1") == "duplicate"
    assert all(scope.settled == 250 and scope.outstanding == 0 for scope in balances(ledger_case))


def test_unknown_cost_survives_reopening_the_database(ledger_case: LedgerFixture) -> None:
    ledger_case.ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger_case.ledger.dispatched("a")
    database = SqliteDatabase(ledger_case.path)
    database.initialize()
    restarted = BudgetLedger(SqliteLedgerStore(database))
    with pytest.raises(ValueError, match="cannot be released"):
        restarted.release_unsent("a")
    assert all(scope.outstanding == 400 for scope in balances(ledger_case))
    assert restarted.settle("a", 90, "late-response") == "applied"


def test_conflicting_usage_is_retained_without_double_charging(ledger_case: LedgerFixture) -> None:
    ledger = ledger_case.ledger
    ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger.dispatched("a")
    ledger.settle("a", 200, "original")
    assert ledger.settle("a", 250, "correction") == "conflict"
    with closing(sqlite3.connect(ledger_case.path)) as connection, connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM spending_evidence WHERE event='settlement_conflict'",
        ).fetchone()[0]
    assert count == 1
    assert all(scope.settled == 200 for scope in balances(ledger_case))


def test_duplicate_reservation_rolls_back_every_scope(ledger_case: LedgerFixture) -> None:
    request = Reservation("a", ledger_case.keys, 400)
    ledger_case.ledger.reserve(request)
    with pytest.raises(sqlite3.IntegrityError):
        ledger_case.ledger.reserve(request)
    assert all(scope.outstanding == 400 for scope in balances(ledger_case))


def test_excess_charge_is_recorded_in_full(ledger_case: LedgerFixture) -> None:
    ledger = ledger_case.ledger
    ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger.dispatched("a")
    ledger.settle("a", 1_100, "excess")
    assert all(scope.settled == 1_100 and scope.outstanding == 0 for scope in balances(ledger_case))
    with pytest.raises(BudgetExceeded):
        ledger.reserve(Reservation("b", ledger_case.keys, 1))


def test_definitely_unsent_reservation_can_be_released(ledger_case: LedgerFixture) -> None:
    ledger_case.ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger_case.ledger.release_unsent("a")
    assert all(scope.outstanding == 0 and scope.settled == 0 for scope in balances(ledger_case))
