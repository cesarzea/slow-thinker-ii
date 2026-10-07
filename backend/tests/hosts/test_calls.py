"""Calls: both operations, tool errors, budgets with cancellation and protocol violations."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallFailure, Emission
from support.log import RecordingLog

from .plans import fixture_plan
from .process_fixture import RUN, Targets, context, launched, launcher, settings


async def test_both_operations_reach_their_host(tmp_path: Path) -> None:
    plan = fixture_plan("serve", embedded="serve")
    async with launched(
        plan, settings(tmp_path), Targets(launcher(tmp_path)), RecordingLog()
    ) as hosts:
        emitted = await hosts.activate(context(), {"story": "A cat."})
        selected = await hosts.select_output(context("w1", "output"), {"score": 8}, "A cat.")
        missing = await hosts.activate(context("w9"), "A cat.")
        no_output = await hosts.select_output(context("w9", "output"), 1, 2)
    assert emitted == (Emission("out", {"story": "A cat."}),)
    assert selected == Emission("out", {"received": {"score": 8}, "node_input": "A cat."})
    assert (
        missing
        == no_output
        == CallFailure("host_failed", 'No component host serves the node "w9".')
    )


async def test_tool_errors_become_call_failures(tmp_path: Path) -> None:
    plan = fixture_plan("serve", embedded="serve")
    failing: JsonValue = {"fail": ["fixture_failed", "No."]}
    async with launched(
        plan, settings(tmp_path), Targets(launcher(tmp_path)), RecordingLog()
    ) as hosts:
        failure = await hosts.activate(context(), failing)
        refused = await hosts.select_output(context("w1", "output"), failing, "A cat.")
        invalid = await hosts.activate(context(), {"fail": ["Not a code", "Bad."]})
    assert failure == refused == CallFailure("fixture_failed", "No.")
    assert isinstance(invalid, CallFailure) and invalid.code == "component_error"


async def test_an_expired_budget_cancels_the_request_in_the_host(tmp_path: Path) -> None:
    run_directory = tmp_path / "workspace" / RUN
    plan = fixture_plan("serve")
    async with launched(
        plan, settings(tmp_path), Targets(launcher(tmp_path)), RecordingLog()
    ) as hosts:
        expired = await hosts.activate(context(budget_ms=300), {"wait": True})
        async with asyncio.timeout(5):
            while not (run_directory / "cancelled-a1").exists():
                await asyncio.sleep(0.01)
        later = await hosts.activate(context(), "Still serving.")
    assert expired == CallFailure("timeout", "The call exceeded its time budget of 300 ms.")
    assert later == (Emission("out", "Still serving."),)


async def test_cancelling_a_call_cancels_it_in_the_host(tmp_path: Path) -> None:
    run_directory = tmp_path / "workspace" / RUN
    plan = fixture_plan("serve")
    async with launched(
        plan, settings(tmp_path), Targets(launcher(tmp_path)), RecordingLog()
    ) as hosts:
        waiting = asyncio.create_task(hosts.activate(context(), {"wait": True}))
        await asyncio.sleep(0.3)
        waiting.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.gather(waiting)
        async with asyncio.timeout(5):
            while not (run_directory / "cancelled-a1").exists():
                await asyncio.sleep(0.01)


async def test_oversized_messages_are_refused_in_both_directions(tmp_path: Path) -> None:
    plan, limit = fixture_plan("serve"), 65_536
    async with launched(
        plan, settings(tmp_path), Targets(launcher(tmp_path)), RecordingLog()
    ) as hosts:
        outbound = await hosts.activate(context(), "x" * limit)
        healthy = await hosts.activate(context(), "small")
        inbound = await hosts.activate(context(), {"big": limit})
        broken = await hosts.activate(context(), "small")
    assert isinstance(outbound, CallFailure) and outbound.code == "message_too_large"
    assert outbound.message.endswith(f"exceeds the protocol limit of {limit} bytes.")
    assert healthy == (Emission("out", "small"),)
    assert inbound == CallFailure(
        "message_too_large", f"A message exceeds the protocol limit of {limit} bytes."
    )
    assert broken == inbound


async def test_a_host_that_dies_answers_with_failures(tmp_path: Path) -> None:
    plan, targets = fixture_plan("serve"), Targets(launcher(tmp_path))
    async with launched(plan, settings(tmp_path), targets, RecordingLog()) as hosts:
        crashed = await hosts.activate(context(), {"crash": True})
        later = await hosts.activate(context(), "A cat.")
    message = "The component host stopped answering: Connection closed."
    assert crashed == later == CallFailure("host_failed", message)


async def test_concurrent_calls_share_one_host(tmp_path: Path) -> None:
    plan = fixture_plan("serve")
    async with launched(
        plan, settings(tmp_path), Targets(launcher(tmp_path)), RecordingLog()
    ) as hosts:
        started = asyncio.get_running_loop().time()
        replies = await asyncio.gather(
            *(hosts.activate(context(), {"sleep": 0.6, "call": index}) for index in range(3))
        )
        elapsed = asyncio.get_running_loop().time() - started
    assert replies == [(Emission("out", {"sleep": 0.6, "call": index}),) for index in range(3)]
    assert elapsed < 1.2
