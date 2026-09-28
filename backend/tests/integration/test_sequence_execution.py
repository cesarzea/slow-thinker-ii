"""Bundled JSON graphs execute with real MCP control and distinct persisted activations."""

import json
from pathlib import Path

import pytest
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.application import SequenceProgram
from slow_thinker_ii.contracts import decode_json
from support.process_fixture import assert_reaped
from support.sequence_plans import plan
from support.sequence_runtime import configured_runtime


@pytest.mark.parametrize("name", ["single-agent", "handoff", "review-cycle", "repeated-review"])
async def test_every_bundled_graph_executes_its_declared_data_flow(
    tmp_path: Path, name: str
) -> None:
    compiled = plan(name)
    case, runtime, environment = configured_runtime(tmp_path, compiled)
    result = await runtime.execute(SequenceProgram(compiled))
    assert result.state == "completed"
    assert_reaped(environment.process, forced=False)
    with case.store.begin() as transaction:
        calls = [
            transaction.call(event.call_id)
            for event in transaction.events("run")
            if event.event == "call.requested" and event.call_id
        ]
        node_ids = [
            call.prepared.context.node_id for call in calls if call.prepared.context.activation_id
        ]
        assert node_ids == [node.node_id for node in compiled.nodes]
        assert len(calls) == 2 * len(compiled.nodes) + 1
        final = next(event for event in transaction.events("run") if event.event == "run.finished")
        outputs = json.loads(json.loads(final.payload_json)["output_json"])["nodes"]
        assert set(outputs) == set(node_ids)


async def test_review_inputs_use_previous_values_without_implicit_history(tmp_path: Path) -> None:
    compiled = plan("review-cycle")
    _, runtime, environment = configured_runtime(tmp_path, compiled)
    assert (await runtime.execute(SequenceProgram(compiled))).state == "completed"
    proposer = environment.agents[OperationAddress("proposer", "generate")]
    reviewer = environment.agents[OperationAddress("reviewer", "generate")]
    assert decode_json(reviewer.calls[0][0]) == {
        "problem": "Design a workshop",
        "proposal": "proposer-1",
    }
    assert decode_json(proposer.calls[1][0]) == {
        "problem": "Design a workshop",
        "proposal": "proposer-1",
        "review": "reviewer-1",
    }
