"""Spending cannot lose scope identity or exceed its integer representation."""

import pytest
from slow_thinker_ii.accounting import MAX_QUANTA, Reservation, ScopeKeys


@pytest.mark.parametrize("keys", [("", "s", "m"), ("r", "", "m"), ("r", "s", "")])
def test_all_scopes_are_required(keys: tuple[str, str, str]) -> None:
    with pytest.raises(ValueError):
        ScopeKeys(*keys)


@pytest.mark.parametrize("key, bound", [("", 0), ("a", -1), ("a", MAX_QUANTA + 1)])
def test_invalid_attempt_is_rejected(key: str, bound: int) -> None:
    with pytest.raises(ValueError):
        Reservation(key, ScopeKeys("r", "s", "m"), bound)


@pytest.mark.parametrize("bound", [0, MAX_QUANTA])
def test_reservation_boundaries_are_representable(bound: int) -> None:
    request = Reservation("a", ScopeKeys("r", "s", "m"), bound)
    assert request.bound == bound
    assert request.scopes == ScopeKeys("r", "s", "m")
