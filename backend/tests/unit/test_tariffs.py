"""Known arithmetic, category partitions and admission bounds across price bands."""

from fractions import Fraction

import pytest
from slow_thinker_ii.accounting import MAX_QUANTA, TokenRates, TokenUsage, account_fraction
from slow_thinker_ii.adapters.tariffs import parse_catalog
from support.catalog import PAYLOAD


def test_known_standard_cost_and_capacity_bound() -> None:
    tariff = parse_catalog(PAYLOAD, 0).tariff
    assert tariff.reservation(2048) == 264_036_000
    assert account_fraction(tariff.charge(TokenUsage(1000, 0, 0, 1000))) == 600_000
    assert tariff.charge(TokenUsage(100, 40, 20, 100)) == Fraction("0.0000569")


def test_context_band_boundary_is_inclusive_only_for_long_band() -> None:
    tariff = parse_catalog(PAYLOAD, 0).tariff
    assert tariff.charge(TokenUsage(272000, 0, 0, 0)) == Fraction("0.0272")
    assert tariff.charge(TokenUsage(272001, 0, 0, 0)) == Fraction("0.0544002")


@pytest.mark.parametrize("output", [0, -1, 128001])
def test_invalid_output_limit(output: int) -> None:
    with pytest.raises(ValueError):
        parse_catalog(PAYLOAD, 0).tariff.reservation(output)


@pytest.mark.parametrize("usage", [(1, 2, 0, 0), (1, 1, 1, 0), (-1, 0, 0, 0), (1, 0, 0, -1)])
def test_invalid_category_counts(usage: tuple[int, int, int, int]) -> None:
    with pytest.raises(ValueError):
        TokenUsage(*usage)


@pytest.mark.parametrize("usage", [TokenUsage(1050001, 0, 0, 0), TokenUsage(0, 0, 0, 128001)])
def test_provider_capacity_violation(usage: TokenUsage) -> None:
    with pytest.raises(ValueError):
        parse_catalog(PAYLOAD, 0).tariff.charge(usage)


def test_fraction_rounding_is_once_and_upward() -> None:
    assert account_fraction(Fraction("0.0000000004")) == 1
    assert account_fraction(Fraction(0)) == 0
    assert account_fraction(Fraction(MAX_QUANTA, 1_000_000_000)) == MAX_QUANTA
    with pytest.raises(ValueError):
        account_fraction(Fraction(-1))
    with pytest.raises(ValueError):
        account_fraction(Fraction(MAX_QUANTA))


def test_negative_rate_is_invalid() -> None:
    with pytest.raises(ValueError):
        TokenRates(Fraction(-1), Fraction(0), Fraction(0), Fraction(0))
