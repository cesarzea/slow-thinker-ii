"""Startup monetary values are exact USD strings; ledger profiles remain integer quanta."""

from pydantic import BaseModel

from slow_thinker_ii.accounting import parse_limit
from slow_thinker_ii.application import LimitsProfile


class PublicLimits(BaseModel, extra="forbid", strict=True, frozen=True):
    revision: str
    run_seconds: float
    call_seconds: float
    startup_seconds: float
    shutdown_seconds: float
    max_calls: int
    max_depth: int
    max_payload_bytes: int
    run_budget: str
    session_budget: str
    month_budget: str

    def internal(self) -> LimitsProfile:
        return LimitsProfile(
            self.revision,
            self.run_seconds,
            self.call_seconds,
            self.startup_seconds,
            self.shutdown_seconds,
            self.max_calls,
            self.max_depth,
            self.max_payload_bytes,
            parse_limit(self.run_budget),
            parse_limit(self.session_budget),
            parse_limit(self.month_budget),
        )
