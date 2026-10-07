"""Component reports: reported evidence for the grant's activation, or a clear refusal."""

import pytest
from slow_thinker_ii.access import Caller
from slow_thinker_ii.application import InvalidGrant, InvalidReport
from support.examples import J2
from support.platform import Platform

from .held import held_call, stopped


async def test_reports_are_recorded_as_reported_evidence() -> None:
    platform = Platform()
    context = await held_call(platform)
    platform.reports.report(context.grant, "step", {"text": "Messages built."})
    platform.reports.report(context.grant, "state", "x" * 65_534)
    first, second = platform.run_store.of(context.run_id, "report")
    assert (first.evidence, first.node_id, first.activation_id) == ("reported", "proposer", "a2")
    assert first.data == {"kind": "step", "content": {"text": "Messages built."}}
    assert second.data["kind"] == "state"
    await stopped(platform, context)


async def test_reports_need_a_live_grant_a_known_kind_and_bounded_content() -> None:
    platform = Platform()
    context = await held_call(platform)
    with pytest.raises(InvalidGrant) as unknown:
        platform.reports.report("not-a-grant", "step", "Hello.")
    assert str(unknown.value) == "The grant is missing, unknown or expired."
    with pytest.raises(InvalidReport) as kind:
        platform.reports.report(context.grant, "diary", "Hello.")
    assert str(kind.value) == (
        "Report kind “diary” is not one of explanation, progress, reasoning, state, step."
    )
    with pytest.raises(InvalidReport) as size:
        platform.reports.report(context.grant, "state", "x" * 65_535)
    assert str(size.value) == "Report content exceeds 65536 bytes."
    assert platform.run_store.of(context.run_id, "report") == []
    await stopped(platform, context)


async def test_an_embedded_component_reports_for_its_node() -> None:
    platform = Platform()
    context = await held_call(platform, J2)
    caller = Caller(context.run_id, "judge", "output", context.activation_id)
    grant = platform.grants.issue(caller, 10)
    call = platform.runs.active_call(grant)
    assert call is not None
    assert str(call.component.declaration.ref) == "router@1.0.0"
    platform.reports.report(grant, "explanation", "Score 8 routes to funny.")
    [event] = platform.run_store.of(context.run_id, "report")
    assert (event.node_id, event.activation_id) == ("judge", context.activation_id)
    await stopped(platform, context)
