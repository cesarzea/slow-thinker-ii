"""Run all bundled JSON graphs with installed controllers, agents and model resources."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import HostLimits, InstalledGraphEnvironment
from slow_thinker_ii.application import (
    ManagedRun,
    NativeModelGateway,
    RunFinalization,
    SequenceProgram,
)
from slow_thinker_ii.contracts import decode_json
from slow_thinker_ii.definitions import SequencePlan
from support.native_server import gateway_app, serve
from support.run_admission import RunCase, outstanding
from support.upstream import Upstream

from .conftest import PreparedBundle
from .graph_admission import admission
from .graph_helpers import RunRouter, compile_graph, host_bindings, model_bindings


@pytest.mark.parametrize("name", ["single-agent", "handoff", "review-cycle", "repeated-review"])
async def test_complete_installed_graph(
    tmp_path: Path, prepared_bundle: PreparedBundle, name: str
) -> None:
    installed = await asyncio.to_thread(compile_graph, prepared_bundle, name)
    assert isinstance(installed.plan, SequencePlan)
    case, upstream, router = admission(tmp_path, installed), Upstream(), RunRouter()
    gateway = NativeModelGateway(case.authority, router, model_bindings(installed))
    async with serve(upstream.app) as provider_port, serve(gateway_app(gateway)) as gateway_port:
        environment = InstalledGraphEnvironment(
            prepared_bundle.catalog,
            installed,
            tmp_path / "hosts",
            host_bindings(installed, gateway_port, provider_port),
            HostLimits(30, 10, 1_048_576),
        )
        finish = RunFinalization(case.authority, case.store, case.keys.run, "runtime", case.clock)
        runtime = ManagedRun(
            case.authority, case.service, finish, environment, case.clock() + 80, 1
        )
        router.runtime = runtime
        result = await runtime.execute(SequenceProgram(installed.plan))
    assert result.state == "completed" and outstanding(case) == (0,) * 3
    assert_outcome(case, environment, upstream, len(installed.plan.nodes))


def assert_outcome(
    case: RunCase, environment: InstalledGraphEnvironment, upstream: Upstream, count: int
) -> None:
    assert len(upstream.requests) == count
    cleanup = decode_json(environment.report())
    assert isinstance(cleanup, list) and all(
        isinstance(item, dict) and item["status"] == "stopped" for item in cleanup
    )
    with case.store.begin() as transaction:
        assert all(scope.settled == 2390 * count for scope in transaction.scopes(case.keys))
        assert (
            sum(event.event == "call.requested" for event in transaction.events(case.keys.run))
            == 3 * count + 1
        )
