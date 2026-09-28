"""Invalid control and unavailable prior outputs stop the graph without downstream calls."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.catalog import SequenceCompiler
from slow_thinker_ii.application import ManagedRun, OperationPort, RunFinalization, SequenceProgram
from slow_thinker_ii.contracts import OperationResult, encode_json
from slow_thinker_ii.definitions import read_pointer
from support.managed_calls import FixtureOperation
from support.sequence_plans import SCHEMAS, graph_value, plan, resolved
from support.sequence_runtime import SequenceEnvironment, configured_runtime


class ReplacedController:
    def __init__(self, environment: SequenceEnvironment, result: OperationResult) -> None:
        self.environment = environment
        self.operation = FixtureOperation()
        self.operation.result = result

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        async with self.environment.open(deadline) as operations:
            yield {**operations, OperationAddress("sequence", "next"): self.operation}

    def report(self) -> str:
        return self.environment.report()


@pytest.mark.parametrize("is_error", [False, True])
async def test_bad_controller_does_not_start_any_agent(tmp_path: Path, *, is_error: bool) -> None:
    compiled = plan("single-agent")
    case, _, environment = configured_runtime(tmp_path, compiled)
    replacement = ReplacedController(
        environment, OperationResult('{"action":"complete","nodes":[]}', is_error)
    )
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    runtime = ManagedRun(case.authority, case.service, finish, replacement, case.clock() + 30, 1)
    assert (await runtime.execute(SequenceProgram(compiled))).state == "failed"
    assert not any(agent.calls for agent in environment.agents.values())
    assert len(replacement.operation.calls) == 1


async def test_missing_previous_output_stops_before_invoking_its_consumer(tmp_path: Path) -> None:
    graph = graph_value("review-cycle")
    binding = read_pointer(graph, "/nodes/review/inputs/proposal")
    assert isinstance(binding, dict)
    binding["pointer"] = "/absent"
    compiled = SequenceCompiler(SCHEMAS).compile(
        encode_json(graph), '{"problem":"x"}', resolved(graph)
    )
    _, runtime, environment = configured_runtime(tmp_path, compiled)
    assert (await runtime.execute(SequenceProgram(compiled))).state == "failed"
    assert len(environment.agents[OperationAddress("proposer", "generate")].calls) == 1
    assert not environment.agents[OperationAddress("reviewer", "generate")].calls
