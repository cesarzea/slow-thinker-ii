"""Invalid limits and missing command identities fail before persistence or process work."""

from dataclasses import replace

import pytest
from slow_thinker_ii.application import (
    ExecutionConfiguration,
    LimitsProfile,
    PreparedStart,
    StartIntent,
)


def profile() -> LimitsProfile:
    return LimitsProfile("revision", 90, 10, 5, 3, 100, 8, 4096, 1000, 2000, 3000)


@pytest.mark.parametrize("duration", [0, -1, float("inf"), float("nan"), True])
def test_invalid_time_bounds(duration: float) -> None:
    with pytest.raises(ValueError):
        replace(profile(), run_seconds=duration)


@pytest.mark.parametrize("value", [0, -1, True])
def test_invalid_count_bounds(value: int) -> None:
    with pytest.raises(ValueError):
        replace(profile(), max_calls=value)


@pytest.mark.parametrize("value", [-1, 2**63, True])
def test_invalid_budget_bounds(value: int) -> None:
    with pytest.raises(ValueError):
        replace(profile(), month_budget=value)


def test_invalid_configuration_and_intention() -> None:
    with pytest.raises(ValueError):
        ExecutionConfiguration("", profile(), "{}")
    with pytest.raises(ValueError):
        replace(profile(), revision="")
    with pytest.raises(ValueError):
        replace(profile(), call_seconds=100)
    with pytest.raises(ValueError):
        StartIntent("", "graph", "revision", "profile", "{}")
    with pytest.raises(ValueError):
        StartIntent("session", "graph", "revision", "profile", "[]")
    intent = StartIntent("session", "graph", "revision", "different", "{}")
    with pytest.raises(ValueError):
        PreparedStart(intent, ExecutionConfiguration("config", profile(), "{}"), "runtime", "{}")
