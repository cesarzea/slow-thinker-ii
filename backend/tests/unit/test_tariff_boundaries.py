"""Category and capacity boundary cases found through mutation testing."""

from dataclasses import replace
from fractions import Fraction

import pytest
from slow_thinker_ii.accounting import TokenRates, TokenUsage
from slow_thinker_ii.adapters.tariffs import parse_catalog
from support.catalog import PAYLOAD


@pytest.mark.parametrize("negative", [0, 1, 2, 3])
def test_every_rate_must_be_nonnegative(negative: int) -> None:
    rates = [Fraction(0)] * 4
    rates[negative] = Fraction(-1)
    with pytest.raises(ValueError):
        TokenRates(*rates)


@pytest.mark.parametrize("counts", [(10, -1, 0, 0), (10, 0, -1, 0)])
def test_negative_cache_counts_are_rejected(counts: tuple[int, int, int, int]) -> None:
    with pytest.raises(ValueError):
        TokenUsage(*counts)


def test_all_input_can_be_cached() -> None:
    tariff = parse_catalog(PAYLOAD, 0).tariff
    assert tariff.charge(TokenUsage(100, 40, 60, 0)) == Fraction("0.0000079")


def test_supported_capacity_endpoints_remain_usable() -> None:
    tariff = parse_catalog(PAYLOAD, 0).tariff
    assert tariff.reservation(1) == 262_500_750
    assert tariff.reservation(128000) == 358_500_000
    assert tariff.charge(TokenUsage(1050000, 0, 0, 128000)) == Fraction("0.306")


@pytest.mark.parametrize("highest", [0, 1, 2])
def test_each_input_category_can_set_the_reservation(highest: int) -> None:
    rates = [Fraction(0)] * 4
    rates[highest] = Fraction("0.000001")
    zero = TokenRates(*([Fraction(0)] * 4))
    tariff = replace(parse_catalog(PAYLOAD, 0).tariff, short=TokenRates(*rates), long=zero)
    assert tariff.reservation(1) == 1_050_000_000


def test_explicit_zero_tariff_is_representable() -> None:
    zero = TokenRates(*([Fraction(0)] * 4))
    tariff = replace(parse_catalog(PAYLOAD, 0).tariff, short=zero, long=zero)
    assert tariff.reservation(128000) == 0
    assert tariff.charge(TokenUsage(0, 0, 0, 0)) == 0
