"""Invalid transitions and incomplete scopes never authorize paid dispatch."""

import sqlite3
from contextlib import closing

import pytest
from slow_thinker_ii.accounting import MAX_QUANTA, BudgetExceeded, Reservation, ScopeKeys

from .conftest import LedgerFixture, balances


@pytest.mark.parametrize("kind", ["run", "session", "month"])
def test_one_insufficient_scope_denies_all(ledger_case: LedgerFixture, kind: str) -> None:
    with closing(sqlite3.connect(ledger_case.path)) as connection, connection:
        connection.execute("UPDATE budget_scopes SET cap=399 WHERE kind=?", (kind,))
    with pytest.raises(BudgetExceeded):
        ledger_case.ledger.reserve(Reservation("a", ledger_case.keys, 400))
    assert all(scope.outstanding == 0 for scope in balances(ledger_case))


def test_unknown_scope_does_not_create_an_attempt(ledger_case: LedgerFixture) -> None:
    with pytest.raises(ValueError, match="Unknown budget scope"):
        ledger_case.ledger.reserve(Reservation("a", ScopeKeys("missing", "s", "m"), 400))
    assert all(scope.outstanding == 0 for scope in balances(ledger_case))


def test_an_attempt_cannot_dispatch_twice(ledger_case: LedgerFixture) -> None:
    ledger_case.ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger_case.ledger.dispatched("a")
    with pytest.raises(ValueError, match="only once"):
        ledger_case.ledger.dispatched("a")


def test_unknown_attempt_is_not_a_free_call(ledger_case: LedgerFixture) -> None:
    with pytest.raises(ValueError, match="Unknown spending attempt"):
        ledger_case.ledger.dispatched("missing")


def test_settlement_requires_dispatch_intent(ledger_case: LedgerFixture) -> None:
    ledger_case.ledger.reserve(Reservation("a", ledger_case.keys, 400))
    with pytest.raises(ValueError, match="possibly dispatched"):
        ledger_case.ledger.settle("a", 200, "provider")
    assert all(scope.outstanding == 400 for scope in balances(ledger_case))


@pytest.mark.parametrize("amount, source", [(-1, "x"), (MAX_QUANTA + 1, "x"), (0, "")])
def test_invalid_settlement_preserves_obligations(
    ledger_case: LedgerFixture,
    amount: int,
    source: str,
) -> None:
    ledger_case.ledger.reserve(Reservation("a", ledger_case.keys, 400))
    ledger_case.ledger.dispatched("a")
    with pytest.raises(ValueError, match="Invalid settlement"):
        ledger_case.ledger.settle("a", amount, source)
    assert all(scope.outstanding == 400 for scope in balances(ledger_case))
