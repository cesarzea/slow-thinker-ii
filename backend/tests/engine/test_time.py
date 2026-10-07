"""The run's time limit, call budgets, grants per call and timeouts, with a controllable clock.

Clock advances use binary fractions (for example 299.9921875 s) so budgets are exact; the real
time left to wait is then 7.8 ms.
"""

from slow_thinker_ii.access import Caller
from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, Emission
from support.clock import FakeClock
from support.examples import J1, J2, journey_plan
from support.hosts import hang
from support.selections import route_by_score

from .harness import STORY, harness

ROUTE = {"judge": route_by_score("funny", "not_funny")}


async def test_a_hanging_host_stops_the_run_at_its_time_limit() -> None:
    run = harness(journey_plan(J1), {"proposer": hang()})
    run.log.when("message.sent", lambda: run.clock.advance(299.9921875))
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("stopped", "time_limit")
    assert outcome.detail == "The run reached its time limit of 300 seconds."
    assert run.hosts.calls[0].budget_ms == 8  # 7.8125 ms left, rounded up: the run's deadline binds
    cancelled = run.log.of("activation.cancelled")
    assert [(event.activation_id, event.data) for event in cancelled] == [
        ("a2", {"reason": "time_limit"})
    ]
    call = run.log.of("component.called")[0]
    assert call.data["error"] == {
        "code": "cancelled",
        "message": "The call was cancelled because the run is ending.",
    }
    assert run.grants.revoked == [issued.token for issued in run.grants.issued]


async def test_a_deadline_passed_before_waiting_stops_the_run_at_once() -> None:
    run = harness(journey_plan(J1), {"proposer": hang()})
    run.log.when("message.sent", lambda: run.clock.advance(301))
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("stopped", "time_limit")
    assert not run.hosts.calls
    started, cancelled = run.log.of("activation.started"), run.log.of("activation.cancelled")
    assert [event.activation_id for event in started] == ["a1", "a2"]
    assert [(event.activation_id, event.data) for event in cancelled] == [
        ("a2", {"reason": "time_limit"})
    ]


async def test_a_call_beyond_the_activation_budget_fails_with_timeout() -> None:
    run = harness(journey_plan(J1), {"proposer": hang()}, max_activation_seconds=1)
    run.log.when("activation.started", lambda: run.clock.advance(0.9921875), node_id="proposer")
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "activation_failed")
    assert (
        outcome.detail == "Proposer activation 1 failed: the component did not answer within 7 ms."
    )
    failed = run.log.of("activation.failed")[0]
    message = "The component did not answer within 7 ms."
    assert failed.data == {"error": {"code": "timeout", "message": message}, "duration_ms": 992}
    assert run.log.of("component.called")[0].data["error"] == {
        "code": "timeout",
        "message": message,
    }


async def test_each_call_gets_the_time_left_and_a_grant_for_it() -> None:
    clock = FakeClock()

    async def slow_judge(_context: CallContext, _message: JsonValue) -> tuple[Emission, ...]:
        clock.advance(1.5)
        return (Emission("out", {"score": 8}),)

    plan = journey_plan(J2)
    run = harness(plan, {"judge": slow_judge}, ROUTE, max_activation_seconds=60, clock=clock)
    outcome = await run.engine.run(STORY)
    assert outcome.status == "completed"
    assert [context.budget_ms for context in run.hosts.calls] == [60_000, 58_500]
    assert [(issued.caller, issued.ttl_seconds) for issued in run.grants.issued] == [
        (Caller("run-1", "judge", "node", "a2"), 60.0),
        (Caller("run-1", "judge", "output", "a2"), 58.5),
    ]
    tokens = [issued.token for issued in run.grants.issued]
    assert [context.grant for context in run.hosts.calls] == tokens
    assert run.grants.revoked == tokens
    assert all(run.grants.grants.resolve(token) is None for token in tokens)
    assert run.log.of("activation.completed")[1].data["duration_ms"] == 1500


async def test_an_activation_stopped_before_its_first_step_is_cancelled() -> None:
    run = harness(journey_plan(J1), {"proposer": hang()})
    run.log.when("activation.started", lambda: run.engine.stop("cancelled", "Stop."), "proposer")
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.detail) == ("cancelled", "Stop.")
    assert (run.hosts.calls, run.grants.issued) == ([], [])
    assert run.log.kinds()[-2:] == ["activation.started", "activation.cancelled"]


async def test_a_deadline_passed_during_a_call_stops_the_run_at_the_time_limit() -> None:
    clock = FakeClock()

    async def overrunning(_context: CallContext, _message: JsonValue) -> tuple[Emission, ...]:
        clock.advance(301)
        return (Emission("out", {"score": 8}),)

    run = harness(journey_plan(J2), {"judge": overrunning}, ROUTE, clock=clock)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("stopped", "time_limit")
    assert len(run.hosts.calls) == 1
    cancelled = run.log.of("activation.cancelled")
    assert [(event.activation_id, event.data) for event in cancelled] == [
        ("a2", {"reason": "time_limit"})
    ]


async def test_an_activation_without_time_left_fails() -> None:
    clock = FakeClock()

    async def slow(_context: CallContext, _message: JsonValue) -> tuple[Emission, ...]:
        clock.advance(2)
        return (Emission("out", {"score": 8}),)

    run = harness(journey_plan(J2), {"judge": slow}, ROUTE, max_activation_seconds=1, clock=clock)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "activation_failed")
    assert outcome.detail == (
        "Judge activation 1 failed: the activation has no time left to call its component."
    )
    assert len(run.hosts.calls) == 1
