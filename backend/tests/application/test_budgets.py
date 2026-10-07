"""Budget denial at each scope, charges above their reservation, and the usage report."""

import pytest
from slow_thinker_ii.accounting import Usage
from slow_thinker_ii.contracts import JsonObject
from support.examples import J1, LUNA, changed, graph_document
from support.platform import Platform
from support.providers import reply

TODAY, MONTH = "2026-10-05", "2026-10"


def with_budget(amount: str) -> JsonObject:
    return changed(graph_document(J1), ("limits", "budget_usd"), amount)


@pytest.mark.parametrize(
    ("budget", "day", "spent", "reason", "detail"),
    [
        ("0.000001", TODAY, 0, "budget_run", "The run budget of 0.000001 USD is exhausted."),
        ("0.10", TODAY, 999_900_000, "budget_day", "The daily budget of 1.00 USD is exhausted."),
        ("0.10", "2026-10-01", 4_999_900_000, "budget_month", "The monthly budget of 5.00 USD"),
    ],
)
async def test_a_denied_reservation_stops_the_run_with_its_scope(
    budget: str, day: str, spent: int, reason: str, detail: str
) -> None:
    platform = Platform()
    platform.ledger.spent("earlier", "another-run", day, MONTH, spent)
    run_id = await platform.started(with_budget(budget))
    record = await platform.finish(run_id)
    assert (record.status, record.reason) == ("stopped", reason)
    assert record.detail.startswith(detail)
    [call] = platform.run_store.of(run_id, "llm.called")
    error = call.data["error"]
    assert isinstance(error, dict) and isinstance(error["message"], str)
    assert (call.data["status"], error["code"], error["type"]) == (
        402,
        "budget_exhausted",
        "budget_error",
    )
    assert "cannot cover this call's reservation of 0.000" in error["message"]
    assert call.data["reserved_usd"] == "0.000000000"
    assert list(platform.ledger.rows) == ["earlier"]
    assert platform.provider.requests == []
    cancelled = platform.run_store.of(run_id, "activation.cancelled")
    assert [event.data["reason"] for event in cancelled] == [reason]


async def test_a_charge_above_its_reservation_stops_an_exceeded_run() -> None:
    platform = Platform(steps={LUNA: [reply("Long.", Usage(10, 0, 0, 10_000))]})
    run_id = await platform.started(with_budget("0.001"))
    record = await platform.finish(run_id)
    assert (record.status, record.reason) == ("stopped", "budget_run")
    assert record.detail == "The run budget of 0.001 USD is exhausted."
    [call] = platform.run_store.of(run_id, "llm.called")
    assert (call.data["status"], call.data["cost_usd"]) == (200, "0.005001000")
    assert platform.ledger.used("run", run_id) == 5_001_000
    assert platform.runs.run(run_id).results == ()


async def test_a_charge_above_its_reservation_within_budgets_continues() -> None:
    platform = Platform(steps={LUNA: [reply("Longer.", Usage(10, 0, 0, 2_000))]})
    record = await platform.completed(J1)
    assert record.status == "completed"
    assert record.totals is not None and record.totals["cost_usd"] == "0.001001000"


async def test_usage_reports_the_day_and_the_month() -> None:
    platform = Platform()
    platform.ledger.spent("earlier", "another-run", "2026-10-01", MONTH, 250_000_000)
    record = await platform.completed(J1)
    assert record.totals is not None
    cost = record.totals["cost_usd"]
    assert isinstance(cost, str)
    usage = platform.usage.usage()
    assert usage["day"] == {"key": TODAY, "limit_usd": "1.000000000", "used_usd": cost}
    month = usage["month"]
    assert isinstance(month, dict)
    assert (month["key"], month["limit_usd"]) == (MONTH, "5.000000000")
    assert month["used_usd"] == f"0.{250_000_000 + int(cost.split('.')[1]):09d}"
