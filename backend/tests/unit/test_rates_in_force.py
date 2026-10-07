"""Rates in force: long context first, then the first UTC window containing the time."""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from slow_thinker_ii.accounting import Rates, Tariff, parse_tariff, rates_at

from .step_one import FLASH, LUNA, changed, step_one_tariff

MONDAY = datetime(2026, 10, 5, tzinfo=UTC)


def flash() -> Tariff:
    return parse_tariff(step_one_tariff(FLASH))


def at(day: datetime, hours: int, minutes: int = 0, seconds: float = 0) -> datetime:
    return day + timedelta(hours=hours, minutes=minutes, seconds=seconds)


@pytest.mark.parametrize(
    ("moment", "in_window"),
    [
        (at(MONDAY, 0, 59, 59.999), False),
        (at(MONDAY, 1), True),
        (at(MONDAY, 3, 59, 59.999), True),
        (at(MONDAY, 4), False),
        (at(MONDAY, 5, 59), False),
        (at(MONDAY, 6), True),
        (at(MONDAY, 9, 59, 59), True),
        (at(MONDAY, 10), False),
        (at(MONDAY + timedelta(days=4), 2), True),
        (at(MONDAY + timedelta(days=5), 2), False),
        (at(MONDAY - timedelta(days=1), 2), False),
    ],
)
def test_each_deepseek_window_boundary(moment: datetime, in_window: bool) -> None:
    tariff = flash()
    expected = tariff.windows[0].rates if in_window else tariff.rates
    assert rates_at(tariff, moment, 1000) == expected


def test_window_times_are_utc() -> None:
    tariff = flash()
    plus_two = timezone(timedelta(hours=2))
    assert (
        rates_at(tariff, datetime(2026, 10, 5, 3, 0, tzinfo=plus_two), 0) == tariff.windows[0].rates
    )
    assert rates_at(tariff, datetime(2026, 10, 5, 1, 0, tzinfo=plus_two), 0) == tariff.rates


def test_the_first_containing_window_applies() -> None:
    document = changed(step_one_tariff(FLASH), ("windows", 1, "rates", "input"), "9")
    tariff = parse_tariff(document)
    assert rates_at(tariff, at(MONDAY, 7), 0).input == tariff.windows[1].rates.input
    assert rates_at(tariff, at(MONDAY, 2), 0).input == tariff.windows[0].rates.input


def test_long_context_applies_above_its_threshold() -> None:
    tariff = parse_tariff(step_one_tariff(LUNA))
    assert rates_at(tariff, MONDAY, 272_000) == tariff.rates
    assert rates_at(tariff, MONDAY, 272_001) == tariff.long_context


def test_long_context_takes_precedence_over_windows() -> None:
    windows = step_one_tariff(FLASH)["windows"]
    document = changed(step_one_tariff(LUNA), ("windows",), windows)
    tariff = parse_tariff(document)
    assert rates_at(tariff, at(MONDAY, 2), 272_001) == tariff.long_context
    assert rates_at(tariff, at(MONDAY, 2), 272_000) == tariff.windows[0].rates


def test_without_long_context_the_threshold_is_ignored() -> None:
    tariff = flash()
    assert rates_at(tariff, at(MONDAY, 12), 10**9) == tariff.rates
    partial = Tariff("2026-10-04", "test", tariff.rates, 5, None, (), True, None)
    assert rates_at(partial, MONDAY, 10) == tariff.rates
    rates = Rates(tariff.rates.input, None, None, tariff.rates.output)
    no_threshold = Tariff("2026-10-04", "test", tariff.rates, None, rates, (), True, None)
    assert rates_at(no_threshold, MONDAY, 10) == tariff.rates


def test_times_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="^A time must be timezone-aware$"):
        rates_at(flash(), datetime(2026, 10, 5, 2), 0)
