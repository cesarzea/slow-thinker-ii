"""Call budgets round up when the run's deadline binds and down when the activation's does.

A host that times out after `budget_ms` then never answers before the run's deadline, so the
engine, not the host, decides `time_limit`.
"""

from collections.abc import Awaitable, Callable

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure
from support.clock import FakeClock
from support.examples import J1, journey_plan

from .harness import STORY, harness, rewrite

TIMED_OUT = "The call did not finish within its budget."


async def test_a_run_bound_budget_rounds_up_to_the_next_millisecond() -> None:
    run = harness(journey_plan(J1), {"proposer": rewrite})
    run.log.when("message.sent", lambda: run.clock.advance(298.9995))
    outcome = await run.engine.run(STORY)
    assert outcome.status == "completed"
    assert run.hosts.calls[0].budget_ms == 1001  # 1.0005 s left
    assert run.grants.issued[0].ttl_seconds == 1.001


async def test_an_activation_bound_budget_rounds_down() -> None:
    run = harness(journey_plan(J1), {"proposer": rewrite}, max_activation_seconds=1)
    run.log.when("activation.started", lambda: run.clock.advance(0.0005), node_id="proposer")
    outcome = await run.engine.run(STORY)
    assert outcome.status == "completed"
    assert run.hosts.calls[0].budget_ms == 999  # 0.9995 s left
    assert run.grants.issued[0].ttl_seconds == 0.999


async def test_a_host_timeout_at_the_deadline_stops_the_run_at_the_time_limit() -> None:
    clock = FakeClock()
    run = harness(journey_plan(J1), {"proposer": _times_out(clock, 300)}, clock=clock)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("stopped", "time_limit")
    assert outcome.detail == "The run reached its time limit of 300 seconds."
    assert run.log.of("component.called")[0].data["error"] == {
        "code": "timeout",
        "message": TIMED_OUT,
    }
    assert run.log.of("activation.cancelled")[0].data == {"reason": "time_limit"}
    assert not run.log.of("activation.failed")


async def test_a_host_timeout_before_the_deadline_fails_the_activation() -> None:
    clock = FakeClock()
    run = harness(journey_plan(J1), {"proposer": _times_out(clock, 299.999)}, clock=clock)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "activation_failed")
    assert outcome.detail == f"Proposer activation 1 failed: t{TIMED_OUT[1:]}"


def _times_out(
    clock: FakeClock, seconds: float
) -> Callable[[CallContext, JsonValue], Awaitable[CallFailure]]:
    """A host that answers its own `timeout` after `seconds` on the fake clock."""

    async def behaviour(_context: CallContext, _message: JsonValue) -> CallFailure:
        clock.advance(seconds)
        return CallFailure("timeout", TIMED_OUT)

    return behaviour
