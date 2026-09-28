"""Explicit, versioned execution bounds; absent values never imply unlimited work."""

import math
from dataclasses import dataclass

from slow_thinker_ii.accounting import MAX_QUANTA
from slow_thinker_ii.contracts import encode_json


@dataclass(frozen=True)
class LimitsProfile:
    revision: str
    run_seconds: float
    call_seconds: float
    startup_seconds: float
    shutdown_seconds: float
    max_calls: int
    max_depth: int
    max_payload_bytes: int
    run_budget: int
    session_budget: int
    month_budget: int

    def __post_init__(self) -> None:
        if not self.revision:
            raise ValueError("A limits profile needs a revision")
        durations = (
            self.run_seconds,
            self.call_seconds,
            self.startup_seconds,
            self.shutdown_seconds,
        )
        if any(
            isinstance(value, bool) or not math.isfinite(value) or value <= 0 for value in durations
        ):
            raise ValueError("Execution deadlines must be finite and positive")
        if self.call_seconds > self.run_seconds:
            raise ValueError("A call cannot outlive the run limit")
        if any(
            type(value) is not int or value < 1
            for value in (self.max_calls, self.max_depth, self.max_payload_bytes)
        ):
            raise ValueError("Count and capture limits must be positive integers")
        if any(
            type(value) is not int or not 0 <= value <= MAX_QUANTA
            for value in (self.run_budget, self.session_budget, self.month_budget)
        ):
            raise ValueError("Budget limits must be exact nonnegative ledger amounts")

    def to_json(self) -> str:
        return encode_json(
            {
                "revision": self.revision,
                "run_seconds": self.run_seconds,
                "call_seconds": self.call_seconds,
                "startup_seconds": self.startup_seconds,
                "shutdown_seconds": self.shutdown_seconds,
                "max_calls": self.max_calls,
                "max_depth": self.max_depth,
                "max_payload_bytes": self.max_payload_bytes,
                "run_budget": self.run_budget,
                "session_budget": self.session_budget,
                "month_budget": self.month_budget,
            }
        )
