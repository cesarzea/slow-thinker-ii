"""The run's deadline and the time budget of each host call, read from the clock when armed."""

import math
from dataclasses import dataclass

from ._ports import Clock
from ._state import Activation


@dataclass(frozen=True)
class CallBudget:
    milliseconds: int  # passed to the host; the grant lives as long; never negative
    timeout: float | None  # seconds; None when the run's deadline is the binding limit


class Timing:
    def __init__(self, clock: Clock, max_activation_seconds: int) -> None:
        self._clock = clock
        self._max_activation = float(max_activation_seconds)
        self._deadline = math.inf

    def start(self, time_limit_seconds: int) -> None:
        self._deadline = self._clock.monotonic() + time_limit_seconds

    def now(self) -> float:
        return self._clock.monotonic()

    def remaining(self) -> float:
        return self._deadline - self._clock.monotonic()

    def budget(self, activation: Activation) -> CallBudget:
        """The smaller of the run's remaining time and the activation's own remaining time.

        A run-bound budget rounds up, so a host that times out after `budget_ms` never answers
        before the run's deadline and the engine decides `time_limit`. An activation-bound
        budget rounds down, because the engine's own timeout for the call decides.
        """
        now = self._clock.monotonic()
        run_left = self._deadline - now
        activation_left = activation.started + self._max_activation - now
        if activation_left < run_left:
            return CallBudget(_milliseconds(activation_left), activation_left)
        return CallBudget(_milliseconds_up(run_left), None)

    def elapsed_ms(self, since: float) -> int:
        return _milliseconds(self._clock.monotonic() - since)


def _milliseconds(seconds: float) -> int:
    return max(0, math.floor(seconds * 1000))


def _milliseconds_up(seconds: float) -> int:
    return max(0, math.ceil(seconds * 1000))
