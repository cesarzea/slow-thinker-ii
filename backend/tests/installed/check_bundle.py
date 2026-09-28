"""Run explicitly after preparation with SLOW_THINKER_TEST_BUNDLE pointing to its record."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import HostSettings, InstalledProcess
from slow_thinker_ii.application import (
    ManagedCalls,
    ManagedRun,
    ModelBinding,
    NativeModelGateway,
    RunFinalization,
)
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.authority import MODEL, PROPOSER
from support.native_model import model_case
from support.native_server import gateway_app, serve
from support.process_fixture import assert_reaped
from support.run_admission import outstanding
from support.sequence_plans import plan
from support.sequence_runtime import sequence_process
from support.upstream import Upstream

from .conftest import PreparedBundle
from .environment import InstalledEnvironment


class Program:
    async def execute(self, calls: ManagedCalls) -> str:
        result = await calls.schedule(
            PROPOSER, '{"problem":"p","proposal":"q","available_sources":["a"]}', node_id="draft"
        )
        assert result.outcome.publish
        return result.result.payload_json


async def test_installed_controller_runs_without_changing_environment(
    tmp_path: Path, prepared_bundle: PreparedBundle
) -> None:
    compiled = plan("single-agent")
    sequence_process(tmp_path, compiled)
    controller = next(
        item for item in compiled.instances if item.instance_id == compiled.controller.component
    )
    process = InstalledProcess(
        prepared_bundle.catalog,
        prepared_bundle.identities["sequence"],
        "example.sequence",
        "0.1.0-example",
        HostSettings(tmp_path / "sequence.json", tmp_path, 30, 10, 1_048_576),
        controller.operations,
    )
    async with process.connect() as connection:
        reply = await connection.call("next", '{"completed_nodes":[]}', "fixture-grant", 5)
        assert json_object(decode_json(reply.payload_json))["action"] == "schedule"
    assert_reaped(process, forced=False)


@pytest.mark.parametrize("name", ["llm-call", "grounded-review"])
async def test_installed_agent_and_resource_complete_through_platform(
    tmp_path: Path, prepared_bundle: PreparedBundle, name: str
) -> None:
    case, upstream = model_case(tmp_path, start=False), Upstream()
    upstream.content = '{"summary":"Review","citations":["a"]}'
    async with serve(upstream.app) as provider_port:
        environment = InstalledEnvironment(tmp_path, prepared_bundle, name, provider_port)
        finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
        runtime = ManagedRun(
            case.authority, case.service, finish, environment, case.clock() + 80, 1
        )
        gateway = NativeModelGateway(
            case.authority, runtime, (ModelBinding("proposer", "bound-model", MODEL),)
        )
        async with serve(gateway_app(gateway)) as port:
            environment.gateway_port = port
            result = await runtime.execute(Program())
    assert result.state == "completed" and outstanding(case) == (0,) * 3
    assert len(upstream.requests) == 1
    for process in environment.processes:
        assert_reaped(process, forced=False)
        installed = json_object(decode_json(process.installation_json()))
        assert "slow-thinker-ii" not in encode_json(installed["inspection"])
    with case.store.begin() as transaction:
        assert all(scope.settled == 2390 for scope in transaction.scopes(case.keys))
