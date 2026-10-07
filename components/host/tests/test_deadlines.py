"""Relative budgets from `_meta` bound each call, including its wait for a free slot."""

import asyncio
from collections.abc import Sequence

from host_fixtures import Recorder, bootstrap, connect, error_of, meta
from slow_thinker_host import Context, Emission, JsonValue, create_server


class Clock:
    """Records the remaining time it sees, then optionally fails with its own timeout."""

    def __init__(self, own_timeout: bool = False) -> None:
        self.remaining: list[float] = []
        self.own_timeout = own_timeout

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        self.remaining.append(context.remaining_seconds())
        await asyncio.sleep(0.02)
        self.remaining.append(context.remaining_seconds())
        if self.own_timeout:
            raise TimeoutError("an inner operation timed out")
        return [Emission("out", message)]


async def test_handler_sees_its_remaining_budget() -> None:
    handler = Clock()
    async with connect(create_server(bootstrap(), node=handler)) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta(budget_ms=1500))
    assert not result.is_error
    first, second = handler.remaining
    assert 1.0 < first <= 1.5 and second < first


async def test_expired_budget_cancels_the_handler_and_reports_timeout() -> None:
    handler = Recorder()
    handler.release.clear()
    async with connect(create_server(bootstrap(), node=handler)) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta(budget_ms=50))
    assert error_of(result) == {
        "code": "timeout",
        "message": "The call exceeded its time budget of 50 ms.",
    }
    assert handler.messages == [1] and handler.running == 0


async def test_zero_budget_times_out() -> None:
    handler = Recorder()
    handler.release.clear()
    async with connect(create_server(bootstrap(), node=handler)) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta(budget_ms=0))
    assert error_of(result)["code"] == "timeout"


async def test_a_timeout_raised_by_the_handler_is_a_component_error() -> None:
    async with connect(create_server(bootstrap(), node=Clock(own_timeout=True))) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert error_of(result) == {
        "code": "component_error",
        "message": "The component raised TimeoutError: an inner operation timed out",
    }


async def test_waiting_for_a_slot_counts_against_the_budget() -> None:
    handler = Recorder()
    handler.release.clear()
    server = create_server(bootstrap(concurrency=1), node=handler)
    async with connect(server) as client:
        first = asyncio.create_task(client.call_tool("activate", {"message": 1}, meta=meta()))
        while handler.running < 1:
            await asyncio.sleep(0.005)
        waiting = await client.call_tool("activate", {"message": 2}, meta=meta(budget_ms=60))
        handler.release.set()
        completed = await first
    assert error_of(waiting)["code"] == "timeout"
    assert handler.messages == [1]
    assert completed.structured_content == {"emissions": [{"port": "out", "payload": 1}]}
