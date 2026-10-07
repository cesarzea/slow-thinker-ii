"""Run admission, startup, stops and failures of the background task."""

import pytest
from slow_thinker_ii.accounting import Scope
from slow_thinker_ii.application import (
    GraphInvalid,
    GraphNotFound,
    RunNotFound,
    RunSettings,
    TooManyRuns,
    VersionNotFound,
)
from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.engine import Hosts
from slow_thinker_ii.graphs import RunPlan
from support.examples import J1, step_one_components
from support.hosts import Gate
from support.platform import Platform
from support.waiting import until

from .held import held_call, stopped

STORY = "A cat tried to learn to fly."


async def test_unknown_graphs_and_versions_cannot_run() -> None:
    platform = Platform()
    with pytest.raises(GraphNotFound):
        await platform.runs.start("missing", 1)
    graph_id = platform.saved(J1)
    with pytest.raises(VersionNotFound) as raised:
        await platform.runs.start(graph_id, 2)
    assert str(raised.value) == "Graph “funny-story” has no version 2."


async def test_a_version_no_longer_valid_is_refused_with_its_diagnostics() -> None:
    platform = Platform()
    graph_id = platform.saved(J1)
    platform.catalog = Catalog(step_one_components(), [])
    with pytest.raises(GraphInvalid) as raised:
        await platform.runs.start(graph_id, 1)
    assert [item.code for item in raised.value.diagnostics] == ["unknown_service_entry"]
    assert platform.run_store.unfinished() == ()


async def test_active_runs_are_limited() -> None:
    platform = Platform(settings=RunSettings(max_active_runs=1))
    context = await held_call(platform)
    with pytest.raises(TooManyRuns) as raised:
        await platform.runs.start("funny-story", 1)
    assert str(raised.value) == "The limit of 1 active runs is reached; wait until a run ends."
    await stopped(platform, context)
    platform.hold = None
    record = await platform.finish(await platform.runs.start("funny-story", 1))
    assert record.status == "completed"


async def test_the_input_defaults_to_the_trigger_message() -> None:
    platform = Platform()
    first = await platform.completed(J1)
    assert first.input == STORY
    started = platform.run_store.of(first.run_id, "run.started")[0]
    assert (started.node_id, started.activation_id, started.elapsed_ms) == (None, None, 0)
    assert started.data == {
        "graph_id": "funny-story",
        "graph_version": 1,
        "graph_change": 1,
        "input": STORY,
        "limits": {
            "max_activations": 20,
            "max_running_nodes": 4,
            "time_limit_seconds": 300,
            "budget_usd": "0.100000000",
        },
        "budgets": {"run_usd": "0.100000000", "day_usd": "1.000000000", "month_usd": "5.000000000"},
    }
    second = await platform.finish(await platform.runs.start("funny-story", 1, {"story": "Hi"}))
    assert second.input == {"story": "Hi"}


async def test_stopping_a_running_run_cancels_it() -> None:
    platform = Platform()
    context = await held_call(platform)
    status = platform.runs.stop(context.run_id)
    assert status == "running"
    record = await platform.finish(context.run_id)
    assert (record.status, record.reason) == ("cancelled", "cancelled")
    assert record.detail == "The operator stopped the run."
    final = platform.runs.stop(context.run_id)
    assert final == "cancelled"
    with pytest.raises(RunNotFound):
        platform.runs.stop("missing")


async def test_a_stop_while_hosts_start_takes_effect_once_they_are_ready() -> None:
    platform = Platform()
    gate = Gate()
    platform.launcher.gate = gate
    run_id = await platform.started(J1)
    await until(lambda: platform.launcher.launched == [run_id])
    status = platform.runs.stop(run_id)
    assert status == "starting"
    platform.runs.stop_for_budget(run_id, Scope("run", run_id, 1, 2))
    platform.runs.stop_for_budget("finished-long-ago", Scope("run", "finished-long-ago", 1, 2))
    gate.open()
    record = await platform.finish(run_id)
    assert (record.status, record.detail) == ("cancelled", "The operator stopped the run.")
    assert "run.running" not in platform.run_store.kinds(run_id)
    assert platform.launcher.closed == [run_id]


async def test_a_host_that_fails_to_start_fails_the_run() -> None:
    platform = Platform()
    failure = "Proposer's llm-call@1.0.0 host was not ready within 20 seconds."
    platform.launcher.failure = failure
    run_id = await platform.started(J1)
    record = await platform.finish(run_id)
    assert (record.status, record.reason, record.detail) == ("failed", "startup_failed", failure)
    assert platform.run_store.kinds(run_id) == ["run.started", "host.failed", "run.finished"]
    assert platform.launcher.closed == []
    assert record.totals is not None and record.totals["activations"] == 0


async def test_an_unexpected_launch_error_is_an_internal_error() -> None:
    def broken(_plan: RunPlan) -> Hosts:
        raise RuntimeError("no hosts")

    platform = Platform(hosts=broken)
    record = await platform.completed(J1)
    assert (record.status, record.reason) == ("failed", "internal_error")
    assert record.detail == "The run failed unexpectedly: RuntimeError: no hosts"


async def test_an_unavailable_store_never_breaks_the_background_task() -> None:
    platform = Platform()
    context = await held_call(platform)
    platform.run_store.appends_fail = True
    platform.runs.stop(context.run_id)
    await platform.runs.shutdown()
    assert platform.run_store.unfinished() == (context.run_id,)
    assert platform.launcher.closed == [context.run_id]
    assert platform.grants.active(context.run_id) == 0
