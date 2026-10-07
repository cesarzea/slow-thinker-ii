"""Settlement charges and reservation bounds for the step 1 tariffs."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from fractions import Fraction

import pytest
from slow_thinker_ii.accounting import (
    Rates,
    Tariff,
    Usage,
    charge,
    input_bound,
    parse_tariff,
    reservation_bound,
)

from .step_one import FLASH, LUNA, changed, step_one_tariff

MONDAY = datetime(2026, 10, 5, tzinfo=UTC)
NOON = MONDAY + timedelta(hours=12)


def luna() -> Tariff:
    return parse_tariff(step_one_tariff(LUNA))


def flash() -> Tariff:
    return parse_tariff(step_one_tariff(FLASH))


def test_luna_charge_uses_each_category() -> None:
    tariff = luna()
    usage = Usage(input=1000, cached_input=200, cache_write=100, output=500)
    assert usage.input + usage.cached_input + usage.cache_write + usage.output == 1800
    assert charge(tariff, usage, NOON, NOON) == (364_500, tariff.rates)


def test_luna_long_context_charge() -> None:
    tariff = luna()
    amount, rates = charge(tariff, Usage(272_001, 0, 0, 0), NOON, NOON)
    assert (amount, rates) == (54_400_200, tariff.long_context)
    assert charge(tariff, Usage(271_000, 1000, 0, 0), NOON, NOON)[0] == 27_110_000
    # The threshold applies to the reported input tokens of all categories.
    assert charge(tariff, Usage(272_000, 1, 0, 0), NOON, NOON)[0] == 54_400_020
    assert charge(tariff, Usage(272_000, 0, 1, 0), NOON, NOON)[0] == 54_400_250


def test_flash_charges_in_and_outside_windows() -> None:
    tariff = flash()
    usage = Usage(input=1000, cached_input=1000, cache_write=1000, output=100)
    assert charge(tariff, usage, NOON, NOON) == (213_000, tariff.rates)
    peak = MONDAY + timedelta(hours=2)
    assert charge(tariff, usage, peak, peak) == (426_000, tariff.windows[0].rates)


def test_a_call_spanning_a_window_edge_uses_the_higher_rates() -> None:
    tariff = flash()
    started, ended = MONDAY + timedelta(minutes=59), MONDAY + timedelta(minutes=61)
    assert charge(tariff, Usage(1000, 0, 0, 100), started, ended) == (
        420_000,
        tariff.windows[0].rates,
    )
    assert charge(tariff, Usage(1000, 0, 0, 100), ended, started)[1] == tariff.windows[0].rates


def test_each_category_takes_its_own_higher_rate() -> None:
    document = changed(
        step_one_tariff(FLASH),
        ("windows", 0, "rates"),
        {"input": "0.30", "cache_write": "0.50", "output": "0.10"},
    )
    tariff = parse_tariff(document)
    started, ended = MONDAY + timedelta(minutes=59), MONDAY + timedelta(minutes=61)
    amount, rates = charge(tariff, Usage(1000, 1000, 1000, 1000), started, ended)
    per_token = Fraction(1, 1_000_000)
    assert rates == Rates(
        Fraction("0.30") * per_token,
        Fraction("0.003") * per_token,
        Fraction("0.50") * per_token,
        Fraction("0.60") * per_token,
    )
    assert amount == 1_403_000
    assert charge(tariff, Usage(1000, 1000, 1000, 1000), ended, started) == (amount, rates)


def test_charges_round_up_to_the_next_nano_dollar() -> None:
    tariff = parse_tariff(changed(step_one_tariff(FLASH), ("rates", "input"), "0.0005"))
    assert charge(tariff, Usage(1, 0, 0, 0), NOON, NOON)[0] == 1
    assert charge(tariff, Usage(3, 0, 0, 0), NOON, NOON)[0] == 2
    assert charge(tariff, Usage(4, 0, 0, 0), NOON, NOON)[0] == 2
    assert charge(tariff, Usage(0, 0, 0, 0), NOON, NOON)[0] == 0


@pytest.mark.parametrize("field", ["input", "cached_input", "cache_write", "output"])
def test_usage_counts_must_be_non_negative(field: str) -> None:
    usage = replace(Usage(1, 1, 1, 1), **{field: -1})
    with pytest.raises(ValueError, match="^Token counts must be non-negative$"):
        charge(luna(), usage, NOON, NOON)


def test_input_bound() -> None:
    assert input_bound(1000, 2) == 1096
    assert input_bound(0, 0) == 64
    assert input_bound(0, 1) == 80
    for request_bytes, messages in ((-1, 0), (0, -1)):
        with pytest.raises(ValueError, match="^Request sizes must be non-negative$"):
            input_bound(request_bytes, messages)


def test_reservation_bounds_use_the_highest_rates_of_every_set() -> None:
    assert reservation_bound(luna(), 1096, 300) == 499_000
    assert reservation_bound(flash(), 1096, 50) == 388_800
    assert reservation_bound(flash(), 0, 0) == 0
    assert reservation_bound(luna(), 1, 0) == 250


def test_cached_categories_count_as_input_rates() -> None:
    base = step_one_tariff(FLASH)
    cached = parse_tariff(changed(base, ("rates", "cached_input"), "5"))
    assert reservation_bound(cached, 1000, 0) == 5_000_000
    written = parse_tariff(changed(base, ("rates", "cache_write"), "7"))
    assert reservation_bound(written, 1000, 0) == 7_000_000


def test_without_byte_bounded_input_the_capacity_is_reserved() -> None:
    tariff = parse_tariff(step_one_tariff(LUNA), byte_bounded_input=False, input_capacity=272_000)
    assert reservation_bound(tariff, 10, 0) == 68_000_000
    missing = replace(tariff, input_capacity=None)
    with pytest.raises(ValueError, match="^A tariff without byte-bounded input requires an input"):
        reservation_bound(missing, 10, 0)


@pytest.mark.parametrize(("input_tokens", "output_tokens"), [(-1, 0), (0, -1)])
def test_reservation_bounds_reject_negative_sizes(input_tokens: int, output_tokens: int) -> None:
    with pytest.raises(ValueError, match="^Token bounds must be non-negative$"):
        reservation_bound(luna(), input_tokens, output_tokens)
