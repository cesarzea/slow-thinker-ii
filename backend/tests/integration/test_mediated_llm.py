"""An independent agent uses its native SDK, platform authority and child-only accounting."""

from pathlib import Path

from slow_thinker_ii.application import (
    ManagedRun,
    ModelBinding,
    NativeModelGateway,
    RunFinalization,
)
from support.authority import MODEL
from support.mediated_llm import GenerateProgram, MediatedEnvironment
from support.native_model import MeteredModel, model_case
from support.native_server import gateway_app, serve
from support.process_fixture import assert_reaped
from support.run_admission import outstanding


async def test_agent_process_uses_the_authenticated_accounted_model_route(tmp_path: Path) -> None:
    case, model = model_case(tmp_path, start=False), MeteredModel()
    environment = MediatedEnvironment(tmp_path, model)
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    runtime = ManagedRun(case.authority, case.service, finish, environment, case.clock() + 30, 1)
    gateway = NativeModelGateway(
        case.authority, runtime, (ModelBinding("proposer", "bound-model", MODEL),)
    )
    async with serve(gateway_app(gateway)) as port:
        environment.port = port
        assert (await runtime.execute(GenerateProgram())).state == "completed"
    assert environment.process is not None
    assert_reaped(environment.process, forced=False)
    assert len(model.calls) == 1 and outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        events = transaction.events("run")
        calls = [
            transaction.call(event.call_id).prepared
            for event in events
            if event.event == "call.requested" and event.call_id
        ]
        assert len(calls) == 2
        assert calls[0].charge is None and calls[1].charge is not None
        assert calls[1].context.parent_call_id == calls[0].context.call_id
        assert calls[1].context.node_id == "draft"
        assert all(scope.settled == 2390 for scope in transaction.scopes(case.keys))
