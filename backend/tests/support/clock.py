"""A controllable clock for the engine and application `Clock` ports."""

from datetime import UTC, datetime, timedelta

MONDAY_NOON = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)  # outside every step 1 tariff window


class FakeClock:
    """`monotonic()` and `now()` move together, only when a test calls `advance`.

    Real waits in the engine are armed from a fresh reading, so advancing the clock before a
    wait leaves only the rest of the limit as real time (for example 10 ms of a 1 s limit).
    """

    def __init__(self, start: datetime = MONDAY_NOON, monotonic: float = 1000.0) -> None:
        self._start = start
        self._origin = monotonic
        self.elapsed = 0.0

    def monotonic(self) -> float:
        return self._origin + self.elapsed

    def now(self) -> datetime:
        return self._start + timedelta(seconds=self.elapsed)

    def advance(self, seconds: float) -> None:
        self.elapsed += seconds
