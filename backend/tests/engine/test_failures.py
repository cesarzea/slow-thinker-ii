"""Failed activations: undeclared ports, host and router errors, oversized payloads and crashes."""

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission
from support.examples import J1, J2, journey_plan
from support.hosts import echo, emit, fail, scores
from support.selections import select

from .harness import STORY, harness

FAILED = ("failed", "activation_failed")


async def test_an_undeclared_host_port_fails_the_activation() -> None:
    run = harness(journey_plan(J1), {"proposer": emit(Emission("maybe", "text"))})
    outcome = await run.engine.run(STORY)
    message = 'The component emitted on the undeclared output "maybe".'
    assert (outcome.status, outcome.reason) == FAILED
    assert outcome.detail == f"Proposer activation 1 failed: t{message[1:]}"
    failed = run.log.of("activation.failed")[0]
    assert failed.data == {
        "error": {"code": "undeclared_port", "message": message},
        "duration_ms": 0,
    }
    assert (failed.node_id, failed.activation_id) == ("proposer", "a2")
    assert run.log.of("component.called")[0].data["result"] == {
        "emissions": [{"port": "maybe", "payload": "text"}]
    }


async def test_an_undeclared_embedded_port_fails_the_activation() -> None:
    choice = select(Emission("maybe", STORY))
    run = harness(journey_plan(J2), {"judge": scores(8)}, {"judge": choice})
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == FAILED
    assert outcome.detail == (
        'Judge activation 1 failed: the output component selected the undeclared output "maybe".'
    )


async def test_an_error_from_activate_fails_the_run() -> None:
    message = "The model call failed with provider_error."
    run = harness(journey_plan(J1), {"proposer": fail("model_call_failed", message)})
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == FAILED
    assert (
        outcome.detail == "Proposer activation 1 failed: the model call failed with provider_error."
    )
    error = {"code": "model_call_failed", "message": message}
    assert run.log.of("component.called")[0].data["error"] == error
    assert run.log.of("activation.failed")[0].data["error"] == error


async def test_an_error_from_select_output_keeps_the_router_message() -> None:
    failure = CallFailure("invalid_route", 'The script returned the undeclared output "maybe".')
    run = harness(journey_plan(J2), {"judge": scores(8)}, {"judge": select(failure)})
    outcome = await run.engine.run(STORY)
    assert outcome.detail == (
        'Judge activation 1 failed: the script returned the undeclared output "maybe".'
    )
    assert run.log.of("component.called")[1].data["position"] == "output"


async def test_a_message_starting_with_an_acronym_keeps_its_case() -> None:
    run = harness(journey_plan(J1), {"proposer": fail("invalid_reply", "JSON reply is invalid.")})
    outcome = await run.engine.run(STORY)
    assert outcome.detail == "Proposer activation 1 failed: JSON reply is invalid."


async def test_an_exception_from_a_host_is_an_internal_error() -> None:
    async def broken(_context: CallContext, _message: JsonValue) -> CallFailure:
        raise RuntimeError("boom")

    run = harness(journey_plan(J1), {"proposer": broken})
    run.log.when("activation.failed", _raise)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "internal_error")
    assert outcome.detail == (
        "Proposer activation 1 failed: the activation failed unexpectedly: RuntimeError: boom"
    )
    assert run.log.of("component.called")[0].data["error"] == {
        "code": "internal_error",
        "message": "The call failed unexpectedly: RuntimeError: boom",
    }
    assert run.log.of("activation.failed")[0].data["error"] == {
        "code": "internal_error",
        "message": "The activation failed unexpectedly: RuntimeError: boom",
    }


async def test_a_failing_log_ends_the_run_with_an_internal_error() -> None:
    run = harness(journey_plan(J1), {"proposer": echo()})
    run.log.when("run.running", _raise)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "internal_error")
    assert outcome.detail == "The run failed unexpectedly: OSError: The event log is unavailable."


async def test_payloads_above_the_contract_limit_fail_the_activation() -> None:
    large = "x" * 262_144
    run = harness(journey_plan(J1), {"proposer": emit(Emission("out", large))})
    outcome = await run.engine.run(STORY)
    limit = "messages are limited to 262144 bytes."
    assert outcome.detail == (
        f'Proposer activation 1 failed: the output "out" carries 262146 bytes; {limit}'
    )
    assert run.log.of("activation.failed")[0].data["error"] == {
        "code": "payload_too_large",
        "message": f'The output "out" carries 262146 bytes; {limit}',
    }
    trigger = harness(journey_plan(J1), {"proposer": echo()})
    outcome = await trigger.engine.run(large)
    assert outcome.detail.startswith('Story activation 1 failed: the output "out" carries')
    assert (outcome.activations, outcome.messages) == (1, 0)


def _raise() -> None:
    raise OSError("The event log is unavailable.")
