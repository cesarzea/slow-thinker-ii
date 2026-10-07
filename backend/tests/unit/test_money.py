"""Amounts cannot gain precision, and charges cannot lose positive amounts through rounding."""

from decimal import localcontext
from fractions import Fraction

import pytest
from slow_thinker_ii.accounting import (
    MAX_QUANTA,
    QUANTA_PER_USD,
    account_fraction,
    format_usd,
    parse_usd,
)


@pytest.mark.parametrize(
    "value",
    ["NaN", "Infinity", "-1", "-0.01", "0.0000000001", "bad", "", "1e20", "9223372036.854775808"],
)
def test_invalid_amounts(value: str) -> None:
    with pytest.raises(ValueError):
        parse_usd(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("0", 0), ("1", QUANTA_PER_USD), ("0.000000001", 1), ("0.05", 50_000_000), ("1e-9", 1)],
)
def test_exact_amounts(value: str, expected: int) -> None:
    assert parse_usd(value) == expected


def test_errors_name_the_problem() -> None:
    with pytest.raises(ValueError, match="^A budget must be a decimal amount$"):
        parse_usd("bad")
    with pytest.raises(ValueError, match="^An amount must be finite, nonnegative and within"):
        parse_usd("-1")
    with pytest.raises(ValueError, match="^A budget exceeds supported precision or range$"):
        parse_usd("0.0000000015")


@pytest.mark.parametrize("amount", [-1, MAX_QUANTA + 1])
def test_invalid_display_amount(amount: int) -> None:
    with pytest.raises(ValueError, match="^Invalid ledger amount$"):
        format_usd(amount)


def test_public_decimal_roundtrip() -> None:
    assert QUANTA_PER_USD == 1_000_000_000
    assert MAX_QUANTA == 9_223_372_036_854_775_807
    assert format_usd(0) == "0.000000000"
    assert format_usd(1) == "0.000000001"
    assert format_usd(50_000_000) == "0.050000000"
    assert format_usd(MAX_QUANTA) == "9223372036.854775807"
    assert parse_usd(format_usd(MAX_QUANTA)) == MAX_QUANTA


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (Fraction(0), 0),
        (Fraction(4, 10**10), 1),
        (Fraction(1, 10**9), 1),
        (Fraction(11, 10**10), 2),
        (Fraction(1, 10**30), 1),
        (Fraction(5, 100), 50_000_000),
        (Fraction(MAX_QUANTA, QUANTA_PER_USD), MAX_QUANTA),
    ],
)
def test_charges_round_up_once(amount: Fraction, expected: int) -> None:
    assert account_fraction(amount) == expected


@pytest.mark.parametrize(
    "amount", [Fraction(-1, 10**12), Fraction(-1), Fraction(MAX_QUANTA + 1, QUANTA_PER_USD)]
)
def test_charges_outside_the_ledger_range(amount: Fraction) -> None:
    with pytest.raises(ValueError, match="^Charge exceeds ledger range$"):
        account_fraction(amount)


def test_decimal_context_cannot_round_amounts() -> None:
    with localcontext(prec=2):
        assert parse_usd("9223372036.854775807") == MAX_QUANTA
        assert parse_usd("0.123456789") == 123_456_789
        assert format_usd(MAX_QUANTA) == "9223372036.854775807"
        with pytest.raises(ValueError):
            parse_usd("1.00000000000000000000000000000001")


def test_extreme_exponents_fail_without_expansion() -> None:
    with pytest.raises(ValueError, match="precision or range"):
        parse_usd("1e-999999999")
    with pytest.raises(ValueError, match="ledger range"):
        parse_usd("1e999999999")
