"""Nested resource stages use real mediated aliases, durable calls and budget authority."""

from pathlib import Path

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_contextual_call import ContextualCall
from slow_thinker_host import Invocation, JsonObject
from slow_thinker_ii.application import ChargeBasis
from slow_thinker_ii.contracts import decode_json
from support.managed_calls import FixtureOperation
from support.native_server import serve

from .mediated_case import MediatedCase

CONFIG: JsonObject = {
    "input_schema": {"type": "object"},
    "worker_operation": "work",
    "worker_output_schema": {"type": "object"},
    "calculation_enabled": True,
    "memory_read": True,
    "memory_write": True,
    "result_pointer": "/value",
}


async def test_real_gateway_records_all_nested_calls_and_state(tmp_path: Path) -> None:
    case = MediatedCase(tmp_path)
    async with serve(case.app) as port:
        result = await ContextualCall(CONFIG, case.endpoint(port)).invoke(
            {"expression": "6*12+3*8"}, Invocation(case.parent.token, case.parent.context.deadline)
        )
    assert result.value == {"value": {"answer": 96}}
    arguments = decode_json(case.worker.calls[0][0])
    assert arguments == {"expression": "6*12+3*8", "memory": None, "calculation": "96"}
    assert case.worker.calls[0][1] != case.parent.token
    assert case.worker.calls[0][2] <= case.parent.context.deadline
    with case.run.store.begin() as transaction:
        events = transaction.events("run")
    requested = [event for event in events if event.event == "call.requested"]
    assert len(requested) == 5 and len(case.worker.calls) == 1
    assert case.parent.token not in str(events)


@pytest.mark.parametrize("mode", ["permission", "budget"])
async def test_authority_and_budget_rejection_never_execute_worker(
    tmp_path: Path, mode: str
) -> None:
    worker = FixtureOperation(ChargeBasis(5000, "fixture", "{}")) if mode == "budget" else None
    case = MediatedCase(tmp_path, denied=mode == "permission", worker=worker)
    async with serve(case.app) as port:
        with pytest.raises(MCPError):
            await ContextualCall(CONFIG, case.endpoint(port)).invoke(
                {"expression": "1+2"}, Invocation(case.parent.token, case.parent.context.deadline)
            )
    assert not case.worker.calls
    with case.run.store.begin() as transaction:
        assert any(event.event == "call.rejected" for event in transaction.events("run"))
