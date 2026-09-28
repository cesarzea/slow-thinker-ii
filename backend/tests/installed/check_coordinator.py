"""Complete installed graphs and native model traffic have a single application runtime owner."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.accounting import ScopeKeys
from slow_thinker_ii.adapters.sqlite import SqliteRunStore
from slow_thinker_ii.application import ExecutionCoordinator
from support.native_server import gateway_app, serve
from support.upstream import Upstream

from .conftest import PreparedBundle
from .coordinator_fixture import InstalledPreparer, coordinator_setup
from .graph_helpers import compile_graph


@pytest.mark.parametrize(
    "name,stop",
    [
        ("single-agent", False),
        ("handoff", False),
        ("review-cycle", False),
        ("repeated-review", False),
        ("single-agent", True),
    ],
)
async def test_installed_coordinator(
    tmp_path: Path, prepared_bundle: PreparedBundle, name: str, stop: bool
) -> None:
    installed = await asyncio.to_thread(compile_graph, prepared_bundle, name)
    preparer = InstalledPreparer(prepared_bundle, installed, tmp_path)
    coordinator, commands, runs, intent = coordinator_setup(tmp_path, preparer)
    upstream = Upstream(blocked=stop)
    async with serve(upstream.app) as provider, serve(gateway_app(coordinator.gateway)) as gateway:
        preparer.gateway_port, preparer.provider_port = gateway, provider
        result = await coordinator.start("start", intent)
        identity = result.receipt.target_id
        assert identity is not None
        assert (await coordinator.start("start", intent)).replayed
        if stop:
            await asyncio.wait_for(upstream.entered.wait(), 40)
            await coordinator.stop("stop", identity)
        await finished(coordinator)
        upstream.release.set()
        assert commands.command("start") == result.receipt
        assert_accounting(runs, identity, len(installed.plan.nodes), stop=stop)
        assert not (await coordinator.close()).runs
    assert len(upstream.requests) == (1 if stop else len(installed.plan.nodes))
    assert not coordinator.failures()


async def finished(coordinator: ExecutionCoordinator) -> None:
    async with asyncio.timeout(80):
        while coordinator.pending().runs:
            await asyncio.sleep(0.02)


def assert_accounting(runs: SqliteRunStore, identity: str, count: int, *, stop: bool) -> None:
    with runs.begin() as transaction:
        run = transaction.run(identity)
        assert run.state == ("cancelled" if stop else "completed")
        scopes = transaction.scopes(ScopeKeys(run.run_id, run.session_id, run.month_id))
        if stop:
            assert all(scope.outstanding > 0 for scope in scopes)
        else:
            assert all(scope.settled == 2390 * count and scope.outstanding == 0 for scope in scopes)
        assert transaction.events(identity)[-1].event == "run.cleanup"
