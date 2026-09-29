"""Budget and deadline refusal terminate the bounded flow before another participant starts."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.application import ChargeEvidence
from support.conditional_runtime import conditional_case
from support.coordinator import eventually


@pytest.mark.parametrize("mode", ["deadline", "budget", "overrun"])
async def test_condition_limits_prevent_following_review(tmp_path: Path, mode: str) -> None:
    case, environment = conditional_case(tmp_path, "wait" if mode == "deadline" else "accept")
    limits = (
        replace(case.base.profile.limits, call_seconds=0.05)
        if mode == "deadline"
        else case.base.profile.limits
    )
    if mode == "budget":
        limits = replace(limits, run_budget=50)
    profile = replace(case.base.profile, revision="guard-profile", limits=limits)
    case.commands.configure(profile)
    case.preparer.case = replace(case.base, profile=profile)
    if mode == "overrun":
        environment.proposer.evidence = ChargeEvidence("{}", 150, "fixture")
    intent = replace(case.base.prepared().intent, configuration_revision=profile.revision)
    receipt = await case.coordinator.start("start", intent)
    run = receipt.receipt.target_id
    assert run is not None
    await eventually(lambda: not case.coordinator.pending().runs)
    assert not environment.reviewer.calls
    with case.runs.begin() as transaction:
        assert transaction.run(run).state != "completed"
        events = transaction.events(run)
        assert not any(event.event == "activation.routed" for event in events)
    assert len(environment.proposer.calls) == (0 if mode == "budget" else 1)
    assert not (await case.coordinator.close()).runs
