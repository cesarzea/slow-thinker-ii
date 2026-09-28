"""Run host profiles require finite bounds and unambiguous billing rules."""

import pytest
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.adapters.process import HostBinding, HostLimits
from support.native_model import profile


@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan"), True])
def test_host_limits_reject_unbounded_or_boolean_timeouts(seconds: float) -> None:
    with pytest.raises(ValueError):
        HostLimits(seconds, 1, 1024)
    with pytest.raises(ValueError):
        HostLimits(1, seconds, 1024)


def test_host_binding_rejects_duplicate_prices_and_invalid_capture_limits() -> None:
    price = OpenAIPricePolicy(profile())
    with pytest.raises(ValueError):
        HostBinding(pricing=(("complete", price), ("complete", price)))
    for value in (0, -1, True):
        with pytest.raises(ValueError):
            HostLimits(1, 1, value)
    with pytest.raises(ValueError):
        HostBinding(clients_json="[]")
