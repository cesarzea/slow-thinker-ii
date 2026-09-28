"""Execute the installed controller over MCP in an independently owned process."""

import json
import os
import sys
from pathlib import Path

import pytest
from jsonschema import ValidationError
from slow_thinker_host import decode_json, encode_json, json_object
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessLaunch
from slow_thinker_ii.contracts import OperationContract

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def controller(tmp_path: Path) -> tuple[ComponentProcess, OperationContract]:
    manifest = json_object(
        decode_json((ROOT / "docs/contracts/examples/sequence.component.json").read_text())
    )
    operation = json_object(json_object(manifest["operations"])["next"])
    contract = OperationContract(
        "next", encode_json(operation["input_schema"]), encode_json(operation["output_schema"])
    )
    bootstrap = tmp_path / "bootstrap.json"
    bootstrap.write_text(
        json.dumps(
            {
                "config": {"steps": ["draft", "review"]},
                "operations": [
                    {
                        "name": "next",
                        "input_schema": operation["input_schema"],
                        "output_schema": operation["output_schema"],
                    }
                ],
            }
        )
    )
    launch = ProcessLaunch(
        Path(sys.executable), "slow_thinker_sequence", bootstrap, tmp_path, 5, 3, 1_048_576
    )
    return ComponentProcess(launch, (contract,)), contract


async def test_sequence_process_has_real_readiness_and_is_reaped(
    controller: tuple[ComponentProcess, OperationContract],
) -> None:
    process, _ = controller
    assert process.outcome() is None
    async with process.connect() as connection:
        state = process.outcome()
        assert state is not None and state.pid != os.getpid() and state.returncode is None
        first = await connection.call("next", '{"completed_nodes":[]}', "test-grant-1", 2)
        last = await connection.call(
            "next", '{"completed_nodes":["draft","review"]}', "test-grant-2", 2
        )
        assert decode_json(first.payload_json) == {"action": "schedule", "nodes": ["draft"]}
        assert decode_json(last.payload_json) == {"action": "complete", "nodes": []}
        assert not first.is_error and not last.is_error
    stopped = process.outcome()
    assert stopped is not None and stopped.returncode == 0 and not stopped.forced
    with pytest.raises(ProcessLookupError):
        os.kill(stopped.pid, 0)


async def test_bad_calls_are_denied_before_dispatch(
    controller: tuple[ComponentProcess, OperationContract],
) -> None:
    process, _ = controller
    async with process.connect() as connection:
        with pytest.raises(ValueError, match="Invalid managed"):
            await connection.call("other", "{}", "grant", 2)
        with pytest.raises(ValueError, match="Invalid managed"):
            await connection.call("next", "{}", "", 2)
        with pytest.raises(ValidationError):
            await connection.call("next", '{"completed_nodes":3}', "grant", 2)
        result = await connection.call("next", '{"completed_nodes":[]}', "grant", 2)
        assert not result.is_error


async def test_stopped_process_handle_cannot_be_restarted(
    controller: tuple[ComponentProcess, OperationContract],
) -> None:
    process, _ = controller
    async with process.connect():
        pass
    with pytest.raises(RuntimeError, match="cannot be reused"):
        async with process.connect():
            pytest.fail("A completed process must never silently restart")
