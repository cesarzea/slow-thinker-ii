"""Bounded controller decisions preserve feedback provenance and terminal meaning."""

from pathlib import Path

import pytest
from slow_thinker_ii.contracts import decode_json, json_object
from support.conditional_runtime import conditional_case
from support.coordinator import eventually


@pytest.mark.parametrize(
    "mode,count,state,reason",
    [
        ("accept", 4, "completed", None),
        ("accept-immediately", 2, "completed", None),
        ("exhaust", 6, "failed", "activation_limit_reached"),
        ("bad-port", 2, "failed", "operation_failed"),
    ],
)
async def test_conditional_outcomes(
    tmp_path: Path, mode: str, count: int, state: str, reason: str | None
) -> None:
    case, environment = conditional_case(tmp_path, mode)
    receipt = await case.coordinator.start("start", case.base.prepared().intent)
    run = receipt.receipt.target_id
    assert run is not None
    await eventually(lambda: not case.coordinator.pending().runs)
    with case.runs.begin() as transaction:
        record = transaction.run(run)
        events = transaction.events(run)
        assert (record.state, record.reason) == (state, reason)
    assert len(environment.proposer.calls) + len(environment.reviewer.calls) == count
    bound = [event for event in events if event.event == "activation.bound"]
    assert len(bound) == count
    if mode == "accept":
        feedback = json_object(decode_json(environment.proposer.calls[1][0]))
        assert feedback["proposal"] == "Proposal 1" and feedback["findings"] == ["Finding 1"]
        sources = json_object(decode_json(bound[2].payload_json))
        assert (
            json_object(sources["proposal"])["activation_id"]
            != json_object(sources["findings"])["activation_id"]
        )
    cleanup = await case.coordinator.close()
    assert not cleanup.runs


async def test_stop_prevents_conditional_review(tmp_path: Path) -> None:
    case, environment = conditional_case(tmp_path, "wait")
    receipt = await case.coordinator.start("start", case.base.prepared().intent)
    run = receipt.receipt.target_id
    assert run is not None
    await environment.proposer.started.wait()
    await case.coordinator.stop("stop", run)
    await eventually(lambda: not case.coordinator.pending().runs)
    assert not environment.reviewer.calls
    with case.runs.begin() as transaction:
        assert transaction.run(run).state == "cancelled"
    await case.coordinator.close()
