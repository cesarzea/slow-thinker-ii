"""Real nested composition and post-worker failures retain authority and paid evidence."""

from pathlib import Path

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_contextual_call import ContextualCall
from slow_thinker_host import Invocation
from slow_thinker_ii.access import Permission
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence
from slow_thinker_ii.contracts import OperationResult
from support.managed_calls import FixtureOperation
from support.native_server import serve

from .mediated_case import PUT, WORKER, MediatedCase
from .routed_port import ENGINE, ROUTER, RoutedPort
from .test_contextual_mediation import CONFIG


async def test_routed_worker_composes_through_two_levels_of_managed_calls(tmp_path: Path) -> None:
    route = RoutedPort()
    worker, router = FixtureOperation(), FixtureOperation()
    worker.result = OperationResult('{"value":{"answer":96}}', False)
    router.result = OperationResult('{"port":"done"}', False)
    case = MediatedCase(
        tmp_path,
        overrides={WORKER: route, ENGINE: worker, ROUTER: router},
        permissions=(Permission("worker", ENGINE), Permission("worker", ROUTER)),
    )
    route.case = case.run
    config = {**CONFIG, "memory_read": False, "memory_write": False, "calculation_enabled": False}
    async with serve(case.app) as port:
        route.port = port
        reply = await ContextualCall(config, case.endpoint(port)).invoke(
            {}, Invocation(case.parent.token, case.parent.context.deadline)
        )
    assert reply.value == {
        "status": "succeeded",
        "port": "done",
        "value": {"value": {"answer": 96}},
    }
    assert len(worker.calls) == len(router.calls) == 1
    assert worker.calls[0][1] != router.calls[0][1] != case.parent.token
    with case.run.store.begin() as transaction:
        assert sum(event.event == "call.requested" for event in transaction.events("run")) == 4


async def test_failed_memory_write_retains_settled_worker_without_repeating_it(
    tmp_path: Path,
) -> None:
    worker = FixtureOperation(
        ChargeBasis(100, "fixture", "{}"), ChargeEvidence("{}", 99, "fixture")
    )
    failed = FixtureOperation()
    failed.error = ValueError("fixture memory unavailable")
    case = MediatedCase(tmp_path, worker=worker, overrides={PUT: failed})
    async with serve(case.app) as port:
        with pytest.raises(MCPError) as caught:
            await ContextualCall(CONFIG, case.endpoint(port)).invoke(
                {"expression": "1+2"}, Invocation(case.parent.token, case.parent.context.deadline)
            )
    assert caught.value.data["stage"] == "memory_put" and len(worker.calls) == 1
    with case.run.store.begin() as transaction:
        assert all(scope.settled == 99 for scope in transaction.scopes(case.run.keys))
