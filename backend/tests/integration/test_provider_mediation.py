"""Real agent and model resource processes cross both mediated and upstream HTTP boundaries."""

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
from support.provider_process import SECRET
from support.run_admission import outstanding
from support.upstream import Upstream


@pytest.mark.parametrize("status", [200, 429])
async def test_full_mediation_with_independent_model_resource(tmp_path: Path, status: int) -> None:
    case, upstream = model_case(tmp_path, start=False), Upstream(status)
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
            result = await runtime.execute(GenerateProgram())
    assert result.state == ("completed" if status == 200 else "failed")
    assert len(upstream.requests) == 1 and upstream.credentials == [f"Bearer {SECRET}"]
    assert upstream.requests[0]["model"] == "gpt-6-luna"
    for process in environment.processes:
        assert_reaped(process, forced=False)
    assert outstanding(case) == ((0,) * 3 if status == 200 else (262_506_000,) * 3)
    with case.store.begin() as transaction:
        assert all(
            scope.settled == (2390 if status == 200 else 0)
            for scope in transaction.scopes(case.keys)
        )
        assert SECRET not in str(transaction.events("run"))
    assert all(SECRET not in path.read_text() for path in tmp_path.glob("*.json"))
