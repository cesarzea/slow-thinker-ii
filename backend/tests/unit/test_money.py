"""Budget amounts cannot gain precision or lose positive charges through rounding."""

from decimal import Decimal, localcontext

import pytest
from slow_thinker_ii.accounting import MAX_QUANTA, display_amount, parse_limit, rounded_charge


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "0.0000000001", "bad", "1e20"])
def test_invalid_limits(value: str) -> None:
    with pytest.raises(ValueError):
        parse_limit(value)


@pytest.mark.parametrize("value, expected", [("0", 0), ("1", 1_000_000_000), ("0.000000001", 1)])
def test_exact_limits(value: str, expected: int) -> None:
    assert parse_limit(value) == expected


@pytest.mark.parametrize("value", ["NaN", "-0.01", "Infinity", "1e20"])
def test_invalid_charge(value: str) -> None:
    with pytest.raises(ValueError):
        rounded_charge(Decimal(value))


@pytest.mark.parametrize("value, expected", [("0", 0), ("0.0000000004", 1), ("0.000000001", 1)])
def test_round_once_upward(value: str, expected: int) -> None:
    assert rounded_charge(Decimal(value)) == expected


@pytest.mark.parametrize("amount", [-1, MAX_QUANTA + 1])
def test_invalid_display_amount(amount: int) -> None:
    with pytest.raises(ValueError):
        display_amount(amount)


def test_public_decimal_roundtrip() -> None:
    assert display_amount(1) == "0.000000001"
    assert parse_limit(display_amount(MAX_QUANTA)) == MAX_QUANTA
    assert display_amount(0) == "0.000000000"


def test_decimal_context_cannot_round_budgets_or_charges() -> None:
    with localcontext(prec=2):
        assert parse_limit("9223372036.854775807") == MAX_QUANTA
        assert rounded_charge(Decimal("0.12345678901")) == 123456790
        assert display_amount(MAX_QUANTA) == "9223372036.854775807"
        with pytest.raises(ValueError):
            parse_limit("1.00000000000000000000000000000001")


def test_extreme_exponents_do_not_round_to_zero() -> None:
    assert rounded_charge(Decimal("1e-999999999")) == 1
    with pytest.raises(ValueError):
        parse_limit("1e-999999999")
