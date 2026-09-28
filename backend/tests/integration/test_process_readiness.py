"""Discovery and message bounds apply before any component business operation."""

import time
from pathlib import Path

import pytest
from slow_thinker_ii.contracts import OperationContract
from support.process_fixture import CONTRACT, assert_reaped, fixture_process


@pytest.mark.parametrize(
    "contracts,diagnostic",
    [
        ((), "operation listing"),
        ((OperationContract("other", "{}", "{}"),), "operation names"),
        ((OperationContract("wait", "{}", CONTRACT.output_schema_json),), "input schema"),
        ((OperationContract("wait", CONTRACT.input_schema_json, "{}"),), "output schema"),
    ],
)
async def test_discovery_mismatch_stops_process(
    tmp_path: Path, contracts: tuple[OperationContract, ...], diagnostic: str
) -> None:
    process = fixture_process(tmp_path, contracts=contracts)
    with pytest.raises(ValueError, match=diagnostic):
        async with process.connect():
            pytest.fail("A mismatched process cannot become ready")
    assert_reaped(process, forced=False)


async def test_oversized_outbound_frame_fails_without_waiting_for_call_deadline(
    tmp_path: Path,
) -> None:
    process = fixture_process(tmp_path, frame_limit=1024)
    started = time.monotonic()
    with pytest.raises(ValueError, match="Outgoing protocol frame"):
        async with process.connect() as connection:
            await connection.call("wait", '{"large":"' + "x" * 2000 + '"}', "grant", 20)
    assert time.monotonic() - started < 6
    assert_reaped(process, forced=False)
