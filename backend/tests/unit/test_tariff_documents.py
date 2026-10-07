"""Reviewed tariff documents convert exactly to per-token rates and reject every malformation."""

from fractions import Fraction

import pytest
from slow_thinker_ii.accounting import Rates, Window, parse_tariff
from slow_thinker_ii.contracts import JsonObject

from .step_one import FLASH, LUNA, changed, removed, step_one_tariff

PER_MILLION = Fraction(1, 1_000_000)


def usd(text: str) -> Fraction:
    return Fraction(text) * PER_MILLION


def test_luna_rates_and_long_context() -> None:
    tariff = parse_tariff(step_one_tariff(LUNA))
    assert tariff.reviewed_on == "2026-09-28"
    assert tariff.source == "https://developers.openai.com/api/docs/pricing"
    assert tariff.rates == Rates(usd("0.10"), usd("0.01"), usd("0.125"), usd("0.50"))
    assert tariff.rates.input == Fraction(1, 10_000_000)
    assert tariff.long_context_above == 272_000
    assert tariff.long_context == Rates(usd("0.20"), usd("0.02"), usd("0.25"), usd("0.75"))
    assert tariff.windows == ()
    assert tariff.byte_bounded_input is True
    assert tariff.input_capacity is None


def test_flash_rates_and_windows() -> None:
    tariff = parse_tariff(step_one_tariff(FLASH))
    assert tariff.reviewed_on == "2026-10-02"
    assert tariff.rates == Rates(usd("0.15"), usd("0.003"), None, usd("0.60"))
    assert tariff.long_context_above is None
    assert tariff.long_context is None
    peak = Rates(usd("0.30"), usd("0.006"), None, usd("1.20"))
    weekdays = frozenset({1, 2, 3, 4, 5})
    assert tariff.windows == (Window(weekdays, 60, 240, peak), Window(weekdays, 360, 600, peak))
    assert [window.rates.cache_write for window in tariff.windows] == [None, None]


def test_input_capacity_for_providers_without_byte_bounded_input() -> None:
    tariff = parse_tariff(step_one_tariff(LUNA), byte_bounded_input=False, input_capacity=400_000)
    assert (tariff.byte_bounded_input, tariff.input_capacity) == (False, 400_000)
    assert parse_tariff(step_one_tariff(LUNA), input_capacity=1).input_capacity == 1
    with pytest.raises(ValueError, match="^A tariff without byte-bounded input requires an input"):
        parse_tariff(step_one_tariff(LUNA), byte_bounded_input=False)
    with pytest.raises(
        ValueError, match="^The input capacity must be a positive number of tokens$"
    ):
        parse_tariff(step_one_tariff(LUNA), input_capacity=0)


def test_a_window_may_end_at_midnight() -> None:
    document = changed(step_one_tariff(FLASH), ("windows", 1, "end"), "24:00")
    assert parse_tariff(document).windows[1].end_minute == 1440


def test_adjacent_windows_and_disjoint_weekdays_do_not_overlap() -> None:
    adjacent = changed(step_one_tariff(FLASH), ("windows", 1, "start"), "04:00")
    assert parse_tariff(adjacent).windows[1].start_minute == 240
    weekend = changed(step_one_tariff(FLASH), ("windows", 1, "weekdays"), [6, 7])
    other_days = changed(weekend, ("windows", 1, "start"), "02:00")
    assert parse_tariff(other_days).windows[1].weekdays == frozenset({6, 7})


def test_windows_and_long_context_are_optional() -> None:
    tariff = parse_tariff(removed(step_one_tariff(LUNA), "windows", "long_context"))
    assert (tariff.windows, tariff.long_context, tariff.long_context_above) == ((), None, None)
    threshold = ("long_context", "above_input_tokens")
    assert parse_tariff(changed(step_one_tariff(LUNA), threshold, 0)).long_context_above == 0


def test_window_minutes_and_reverse_ordered_adjacent_windows() -> None:
    later: JsonObject = {
        "weekdays": [1],
        "start": "06:30",
        "end": "10:15",
        "rates": {"input": "1", "output": "1"},
    }
    earlier: JsonObject = {
        "weekdays": [1],
        "start": "01:45",
        "end": "06:30",
        "rates": {"input": "1", "output": "1"},
    }
    tariff = parse_tariff(changed(step_one_tariff(FLASH), ("windows",), [later, earlier]))
    minutes = [(window.start_minute, window.end_minute) for window in tariff.windows]
    assert minutes == [(390, 615), (105, 390)]
