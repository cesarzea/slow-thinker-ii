"""Budget admission names the first exhausted scope; day and month keys are UTC."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone

import pytest
from slow_thinker_ii.accounting import Scope, day_key, first_exhausted, month_key


def scopes(run_used: int, day_used: int, month_used: int) -> tuple[Scope, Scope, Scope]:
    return (
        Scope("run", "run-1", 100, run_used),
        Scope("day", "2026-10-04", 1000, day_used),
        Scope("month", "2026-10", 5000, month_used),
    )


def test_a_reservation_up_to_every_limit_is_admitted() -> None:
    assert first_exhausted(scopes(90, 990, 4990), 10) is None
    assert first_exhausted(scopes(0, 0, 0), 0) is None
    assert first_exhausted((), 10**9) is None


def test_the_first_exhausted_scope_is_named_in_order() -> None:
    exhausted = first_exhausted(scopes(91, 991, 4991), 10)
    assert exhausted == Scope("run", "run-1", 100, 91)
    day = first_exhausted(scopes(0, 991, 4991), 10)
    assert day is not None
    assert (day.kind, day.key, day.limit, day.used) == ("day", "2026-10-04", 1000, 991)
    month = first_exhausted(scopes(0, 0, 4991), 10)
    assert month is not None and month.kind == "month"


def test_order_is_the_given_order() -> None:
    run, day, month = scopes(100, 1000, 5000)
    assert first_exhausted((month, day, run), 1) == month


def test_day_and_month_keys_are_utc() -> None:
    minus_two = timezone(timedelta(hours=-2))
    late = datetime(2026, 10, 4, 23, 30, tzinfo=minus_two)
    assert day_key(late) == "2026-10-05"
    assert month_key(late) == "2026-10"
    assert day_key(datetime(2026, 10, 31, 23, 0, tzinfo=minus_two)) == "2026-11-01"
    assert month_key(datetime(2026, 10, 31, 23, 0, tzinfo=minus_two)) == "2026-11"
    assert day_key(datetime(987, 1, 2, tzinfo=UTC)) == "0987-01-02"
    assert month_key(datetime(987, 1, 2, tzinfo=UTC)) == "0987-01"


@pytest.mark.parametrize("key", [day_key, month_key])
def test_keys_require_timezone_aware_times(key: Callable[[datetime], str]) -> None:
    with pytest.raises(ValueError, match="^A time must be timezone-aware$"):
        key(datetime(2026, 10, 4, 12))
