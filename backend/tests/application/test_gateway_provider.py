"""Provider outcomes: errors, timeouts, unknown usage, and calls cut off by the run's end."""

import asyncio

import pytest
from slow_thinker_ii.accounting import Usage
from support.examples import J1, LUNA
from support.hosts import Gate
from support.platform import Platform
from support.providers import failure, raising, reply
from support.waiting import until

from .held import body, calls, error_code, held_call, stopped


@pytest.mark.parametrize(("status", "code"), [(502, "provider_error"), (504, "provider_timeout")])
async def test_provider_errors_are_settled_at_the_reservation(status: int, code: str) -> None:
    platform = Platform(steps={LUNA: [failure(status, code, "The provider failed.")]})
    context = await held_call(platform)
    answer = await platform.gateway.complete(context.grant, body())
    assert error_code(answer) == (status, code)
    [recorded] = calls(platform, context)
    assert (recorded["status"], recorded["error"]) == (status, answer.body["error"])
    assert (recorded["usage"], recorded["rates"], recorded["estimated"]) == (None, None, True)
    assert recorded["cost_usd"] == recorded["reserved_usd"] != "0.000000000"
    assert platform.ledger.unsettled() == []
    await stopped(platform, context)


async def test_unknown_usage_is_charged_as_estimated() -> None:
    platform = Platform(steps={LUNA: [reply("Fine.", measured=False)]})
    context = await held_call(platform)
    answer = await platform.gateway.complete(context.grant, body())
    assert answer.status == 200
    [recorded] = calls(platform, context)
    assert (recorded["usage"], recorded["estimated"]) == (None, True)
    assert recorded["cost_usd"] == recorded["reserved_usd"]
    await stopped(platform, context)


async def test_unusable_usage_is_charged_as_estimated() -> None:
    platform = Platform(steps={LUNA: [reply("Fine.", Usage(-1, 0, 0, 3))]})
    context = await held_call(platform)
    await platform.gateway.complete(context.grant, body())
    [recorded] = calls(platform, context)
    assert (recorded["usage"], recorded["rates"], recorded["estimated"]) == (None, None, True)
    await stopped(platform, context)


async def test_a_failing_provider_adapter_is_a_provider_error() -> None:
    platform = Platform(steps={LUNA: [raising(RuntimeError("connection reset"))]})
    context = await held_call(platform)
    answer = await platform.gateway.complete(context.grant, body())
    assert error_code(answer) == (502, "provider_error")
    assert answer.body["error"] == {
        "code": "provider_error",
        "message": "The provider adapter failed: RuntimeError.",
        "type": "provider_error",
    }
    await stopped(platform, context)


async def test_the_provider_receives_the_time_left_in_the_call() -> None:
    platform = Platform()
    context = await held_call(platform)
    platform.clock.advance(100)
    await platform.gateway.complete(context.grant, body())
    assert platform.provider.requests[0].timeout_s == 200.0
    await stopped(platform, context)


async def test_a_failed_model_call_fails_the_activation() -> None:
    platform = Platform(steps={LUNA: [failure(502, "provider_error", "Overloaded.")]})
    record = await platform.completed(J1)
    assert (record.status, record.reason) == ("failed", "activation_failed")
    assert record.detail == "Proposer activation 1 failed: the model call failed: provider_error."


async def test_a_call_in_flight_at_the_run_end_is_recorded_before_it() -> None:
    platform = Platform()
    context = await held_call(platform)
    platform.provider.gate = Gate()
    pending = asyncio.create_task(platform.gateway.complete(context.grant, body()))
    await until(lambda: len(platform.provider.requests) == 1)
    platform.runs.stop(context.run_id)
    record = await platform.finish(context.run_id)
    answer = await pending
    assert error_code(answer) == (504, "provider_timeout")
    error = answer.body["error"]
    assert isinstance(error, dict)
    assert error["message"] == "The run ended before the provider answered."
    assert platform.run_store.kinds(context.run_id)[-2:] == ["llm.called", "run.finished"]
    assert record.totals is not None and record.totals["llm_calls"] == 1
    [recorded] = calls(platform, context)
    assert record.totals["cost_usd"] == recorded["reserved_usd"] == recorded["cost_usd"]
    assert platform.ledger.unsettled() == []


async def test_a_cancelled_request_still_settles_and_records_its_call() -> None:
    platform = Platform()
    context = await held_call(platform)
    platform.provider.gate = Gate()
    pending = asyncio.create_task(platform.gateway.complete(context.grant, body()))
    await until(lambda: len(platform.provider.requests) == 1)
    pending.cancel()
    await asyncio.gather(pending, return_exceptions=True)
    assert pending.cancelled()
    [recorded] = calls(platform, context)
    error = recorded["error"]
    assert isinstance(error, dict)
    assert error["message"] == "The call was cancelled before the provider answered."
    assert (recorded["status"], recorded["estimated"]) == (504, True)
    assert platform.ledger.unsettled() == []
    await stopped(platform, context)


async def test_concurrent_calls_of_a_run_are_each_settled() -> None:
    platform = Platform()
    context = await held_call(platform)
    gate = Gate()
    platform.provider.gate = gate
    first = asyncio.create_task(platform.gateway.complete(context.grant, body()))
    second = asyncio.create_task(platform.gateway.complete(context.grant, body()))
    await until(lambda: len(platform.provider.requests) == 2)
    gate.open()
    answers = await asyncio.gather(first, second)
    assert [answer.status for answer in answers] == [200, 200]
    assert len(calls(platform, context)) == 2
    assert platform.ledger.unsettled() == []
    await stopped(platform, context)
