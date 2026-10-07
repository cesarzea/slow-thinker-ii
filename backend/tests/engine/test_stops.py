"""External stops: budgets and cancellation while activations run; the first cause wins."""

import asyncio
from contextlib import suppress

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission, RunOutcome
from support.examples import J1, journey_plan
from support.hosts import Gate, echo, emit
from support.waiting import until

from .documents import fan_out
from .harness import STORY, harness


async def test_a_budget_stop_cancels_the_running_activation() -> None:
    run = harness(journey_plan(J1), {"proposer": emit(Emission("out", "late"), gate=Gate())})
    task = asyncio.create_task(run.engine.run(STORY))
    await until(lambda: run.hosts.running == 1)
    run.engine.stop("budget_run", "The run budget of 0.10 USD is exhausted.")
    run.engine.stop("cancelled", "The operator stopped the run.")
    outcome = await task
    assert (outcome.status, outcome.reason) == ("stopped", "budget_run")
    assert outcome.detail == "The run budget of 0.10 USD is exhausted."
    assert run.log.kinds()[-2:] == ["component.called", "activation.cancelled"]
    assert run.log.of("activation.cancelled")[0].data == {"reason": "budget_run"}
    assert len(run.log.of("message.sent")) == 1
    assert run.grants.revoked == [run.grants.issued[0].token]


async def test_cancelling_drops_the_pending_deliveries() -> None:
    gate = Gate()
    behaviours = {"w1": emit(Emission("out", "late"), gate=gate), "w2": echo(), "w3": echo()}
    run = harness(fan_out(3, 1), behaviours)
    task = asyncio.create_task(run.engine.run(STORY))
    await until(lambda: run.hosts.running == 1)
    run.engine.stop("cancelled", "The operator stopped the run.")
    outcome = await task
    assert (outcome.status, outcome.reason) == ("cancelled", "cancelled")
    dropped = run.log.of("message.dropped")
    assert [(event.data["message_id"], event.node_id) for event in dropped] == [
        ("m2", "w2"),
        ("m3", "w3"),
    ]
    assert run.log.kinds()[-3:] == ["activation.cancelled", "message.dropped", "message.dropped"]


async def test_a_run_stopped_before_it_starts_does_nothing() -> None:
    run = harness(journey_plan(J1), {"proposer": echo()})
    run.engine.stop("cancelled", "The run was stopped while its hosts started.")
    outcome = await run.engine.run(STORY)
    detail = "The run was stopped while its hosts started."
    assert outcome == RunOutcome("cancelled", "cancelled", detail, (), 0, 0)
    assert run.log.events == []


async def test_a_stop_after_completion_changes_nothing() -> None:
    run = harness(journey_plan(J1), {"proposer": echo()})
    outcome = await run.engine.run(STORY)
    recorded = len(run.log.events)
    run.engine.stop("cancelled", "Too late.")
    assert outcome.status == "completed"
    assert len(run.log.events) == recorded


async def test_an_activation_ending_after_the_stop_is_recorded_cancelled() -> None:
    async def stubborn(_context: CallContext, _message: JsonValue) -> CallFailure:
        with suppress(asyncio.CancelledError):
            await asyncio.Event().wait()
        return CallFailure("interrupted", "The host ignored the cancellation.")

    run = harness(journey_plan(J1), {"proposer": stubborn})
    task = asyncio.create_task(run.engine.run(STORY))
    await until(lambda: run.hosts.running == 1)
    run.engine.stop("cancelled", "The operator stopped the run.")
    outcome = await task
    assert (outcome.status, outcome.detail) == ("cancelled", "The operator stopped the run.")
    assert run.log.of("component.called")[0].data["error"] == {
        "code": "interrupted",
        "message": "The host ignored the cancellation.",
    }
    assert run.log.of("activation.cancelled")[0].data == {"reason": "cancelled"}
    assert not run.log.of("activation.failed")


async def test_cancelling_the_run_task_cancels_its_activations() -> None:
    run = harness(journey_plan(J1), {"proposer": emit(Emission("out", "late"), gate=Gate())})
    task = asyncio.create_task(run.engine.run(STORY))
    await until(lambda: run.hosts.running == 1)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled()
    assert run.log.of("activation.cancelled")[0].data == {"reason": "cancelled"}
