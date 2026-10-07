"""Today's and this month's spending against the platform budgets."""

from slow_thinker_ii.accounting import day_key, format_usd, month_key
from slow_thinker_ii.contracts import JsonObject

from ._ports import Clock, Ledger
from ._values import BudgetLimits


class UsageService:
    def __init__(self, ledger: Ledger, budgets: BudgetLimits, clock: Clock) -> None:
        self._ledger = ledger
        self._budgets = budgets
        self._clock = clock

    def usage(self) -> JsonObject:
        """`GET /usage`: used amounts include open reservations."""
        now = self._clock.now()
        return {
            "day": self._scope("day", day_key(now), self._budgets.daily_nanos),
            "month": self._scope("month", month_key(now), self._budgets.monthly_nanos),
        }

    def _scope(self, kind: str, key: str, limit: int) -> JsonObject:
        used = self._ledger.used(kind, key)
        return {"key": key, "limit_usd": format_usd(limit), "used_usd": format_usd(used)}
