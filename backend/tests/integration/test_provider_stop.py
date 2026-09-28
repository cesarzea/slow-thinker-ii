"""Stop reaps both real processes while retaining the dispatched provider obligation."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.application import (
    ManagedRun,
    ModelBinding,
    NativeModelGateway,
    RunFinalization,
)
from support.authority import MODEL
from support.mediated_llm import GenerateProgram
from support.native_model import model_case
from support.native_server import gateway_app, serve
from support.process_fixture import assert_reaped
from support.provider_environment import ProviderEnvironment
from support.run_admission import outstanding
from support.upstream import Upstream


async def test_stop_during_upstream_request_preserves_uncertain_cost(tmp_path: Path) -> None:
    case, upstream = model_case(tmp_path, start=False), Upstream(blocked=True)
    async with serve(upstream.app) as provider_port:
        environment = ProviderEnvironment(tmp_path, provider_port)
        finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
        runtime = ManagedRun(
            case.authority, case.service, finish, environment, case.clock() + 30, 1
        )
        gateway = NativeModelGateway(
            case.authority, runtime, (ModelBinding("proposer", "bound-model", MODEL),)
        )
        async with serve(gateway_app(gateway)) as gateway_port:
            environment.gateway_port = gateway_port
            task = asyncio.create_task(runtime.execute(GenerateProgram()))
            try:
                await asyncio.wait_for(upstream.entered.wait(), 5)
                runtime.stop()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 5)
            finally:
                upstream.release.set()
                if not task.done():
                    task.cancel()
    assert len(upstream.requests) == 1 and outstanding(case) == (262_506_000,) * 3
    for process in environment.processes:
        assert_reaped(process, forced=False)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "cancelled"
        assert transaction.run("run").reason == "operator_stop"
