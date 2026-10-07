"""Replies outside the protocol, and hosts that stop reading, fail calls without hanging."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.engine import CallFailure
from support.log import RecordingLog

from .plans import fixture_plan
from .process_fixture import PROTOCOL_FIXTURE, Targets, context, launched, launcher, settings


@pytest.mark.parametrize(
    ("mode", "code", "message"),
    [
        (
            "bad_result",
            "invalid_result",
            "The component's result does not match the activate schema.",
        ),
        (
            "bad_error",
            "invalid_result",
            "The component reported an error without a code and a message.",
        ),
        (
            "bad_reply",
            "invalid_result",
            "The component's reply to activate is not a valid tool result.",
        ),
        (
            "nan_payload",
            "invalid_result",
            "The component's result does not match the activate schema.",
        ),
    ],
)
async def test_replies_outside_the_protocol_are_invalid_results(
    tmp_path: Path, mode: str, code: str, message: str
) -> None:
    plan, targets = fixture_plan(mode), Targets(launcher(tmp_path, PROTOCOL_FIXTURE))
    async with launched(plan, settings(tmp_path), targets, RecordingLog()) as hosts:
        reply = await hosts.activate(context(), "A cat.")
    assert reply == CallFailure(code, message)


async def test_an_invalid_selection_is_an_invalid_result(tmp_path: Path) -> None:
    plan = fixture_plan("serve", embedded="bad_result")
    targets = Targets(launcher(tmp_path, PROTOCOL_FIXTURE))
    async with launched(plan, settings(tmp_path), targets, RecordingLog()) as hosts:
        reply = await hosts.select_output(context("w1", "output"), 1, 2)
    message = "The component's result does not match the select_output schema."
    assert reply == CallFailure("invalid_result", message)


async def test_a_host_that_closes_its_input_fails_later_calls(tmp_path: Path) -> None:
    plan, targets = fixture_plan("deaf"), Targets(launcher(tmp_path, PROTOCOL_FIXTURE))
    async with launched(plan, settings(tmp_path), targets, RecordingLog()) as hosts:
        lost = await hosts.activate(context(budget_ms=500), "A cat.")
        refused = await hosts.activate(context(), "A cat.")
    assert lost == CallFailure("timeout", "The component did not answer within 500 ms.")
    assert isinstance(refused, CallFailure) and refused.code == "host_failed"


async def test_a_host_that_never_answers_times_out_after_its_budget_and_a_grace(
    tmp_path: Path,
) -> None:
    plan, targets = fixture_plan("silent_call"), Targets(launcher(tmp_path, PROTOCOL_FIXTURE))
    async with launched(plan, settings(tmp_path), targets, RecordingLog()) as hosts:
        started = asyncio.get_running_loop().time()
        reply = await hosts.activate(context(budget_ms=300), "A cat.")
        elapsed = asyncio.get_running_loop().time() - started
    assert reply == CallFailure("timeout", "The component did not answer within 300 ms.")
    assert 0.75 < elapsed < 2
