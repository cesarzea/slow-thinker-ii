"""Budget scopes of a model call, the stop reason of an exhausted scope and its detail."""

from datetime import datetime

from slow_thinker_ii.accounting import Scope, day_key, format_usd, month_key
from slow_thinker_ii.engine import StopReason

from ._values import BudgetLimits


def call_scopes(
    run_id: str, run_limit: int, budgets: BudgetLimits, at: datetime
) -> tuple[Scope, ...]:
    """The run, day and month scopes in admission order; the ledger reads their used amounts."""
    return (
        Scope("run", run_id, run_limit, 0),
        Scope("day", day_key(at), budgets.daily_nanos, 0),
        Scope("month", month_key(at), budgets.monthly_nanos, 0),
    )


def budget_reason(kind: str) -> StopReason:
    if kind == "day":
        return "budget_day"
    return "budget_month" if kind == "month" else "budget_run"


def budget_label(kind: str) -> str:
    return {"day": "daily", "month": "monthly"}.get(kind, kind)


def budget_detail(scope: Scope) -> str:
    return f"The {budget_label(scope.kind)} budget of {display_usd(scope.limit)} USD is exhausted."


def display_usd(quanta: int) -> str:
    """USD with at least two decimals and no trailing zeros beyond them: `0.05`, `0.000123`."""
    whole, fraction = format_usd(quanta).split(".")
    return f"{whole}.{fraction.rstrip('0').ljust(2, '0')}"
