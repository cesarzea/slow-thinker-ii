"""Mutation-discovered boundary gaps: maximum values and zero-cost admission."""

from decimal import Decimal

from slow_thinker_ii.accounting import (
    MAX_QUANTA,
    BudgetScope,
    admit,
    display_amount,
    rounded_charge,
)


def test_largest_charge_fits_exactly() -> None:
    assert rounded_charge(Decimal(display_amount(MAX_QUANTA))) == MAX_QUANTA


def test_reservation_can_equal_maximum_ledger_value() -> None:
    scopes = (
        BudgetScope("run", "r", MAX_QUANTA, 0, 0),
        BudgetScope("session", "s", MAX_QUANTA, 0, 0),
        BudgetScope("month", "m", MAX_QUANTA, 0, 0),
    )
    admit(scopes, MAX_QUANTA)


def test_zero_reservation_needs_no_additional_allowance() -> None:
    scopes = (
        BudgetScope("run", "r", 0, 0, 0),
        BudgetScope("session", "s", 0, 0, 0),
        BudgetScope("month", "m", 0, 0, 0),
    )
    admit(scopes, 0)
