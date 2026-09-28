"""Real process deadlines, cancellation and failure cleanup."""

import asyncio
import time
from pathlib import Path

import pytest
from mcp.shared.exceptions import MCPError
from support.process_fixture import assert_reaped, fixture_process


async def test_startup_timeout_escalates_to_kill_for_owned_stubborn_child(tmp_path: Path) -> None:
    process = fixture_process(tmp_path, "stubborn")
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        async with process.connect():
            pytest.fail("An unresponsive process cannot become ready")
    assert time.monotonic() - started < 6
    assert (tmp_path / "started").is_file()
    assert_reaped(process, forced=True)


async def test_invalid_wire_data_fails_startup_and_reaps_child(tmp_path: Path) -> None:
    process = fixture_process(tmp_path, "malformed")
    with pytest.raises(MCPError, match="Connection closed"):
        async with process.connect():
            pytest.fail("Invalid protocol data cannot pass readiness")
    assert_reaped(process, forced=True)


async def test_call_timeout_sends_cancellation_and_process_is_reaped(tmp_path: Path) -> None:
    process = fixture_process(tmp_path)
    async with process.connect() as connection:
        with pytest.raises(TimeoutError):
            await connection.call("wait", '{"wait":true}', "grant", 0.15)
        async with asyncio.timeout(2):
            while not (tmp_path / "cancelled").exists():
                await asyncio.sleep(0.01)
        reply = await connection.call("wait", "{}", "fresh-grant", 1)
        assert reply.payload_json == '{"done":true}'
    assert_reaped(process, forced=False)


async def test_cancelling_connection_owner_reaps_child(tmp_path: Path) -> None:
    process = fixture_process(tmp_path)
    ready = asyncio.Event()

    async def use_component() -> None:
        async with process.connect() as connection:
            ready.set()
            await connection.call("wait", '{"wait":true}', "grant", 30)

    task = asyncio.create_task(use_component())
    await asyncio.wait_for(ready.wait(), 5)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert_reaped(process, forced=False)


async def test_expired_absolute_deadline_does_not_send_a_request(tmp_path: Path) -> None:
    process = fixture_process(tmp_path)
    async with process.connect() as connection:
        with pytest.raises(TimeoutError, match="before dispatch"):
            await connection.call("wait", "{}", "grant", 1, deadline=time.monotonic() - 1)
        assert not (tmp_path / "invoked").exists()
        result = await connection.call("wait", "{}", "grant", 1)
        assert not result.is_error and (tmp_path / "invoked").exists()
    assert_reaped(process, forced=False)
