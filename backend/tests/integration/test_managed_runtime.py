"""Real run lifetime includes readiness, managed operations, terminal evidence and reaping."""

import asyncio
import json
from pathlib import Path

import pytest
from support.process_fixture import assert_reaped
from support.run_runtime import FixtureProgram, runtime_case


async def test_ready_hosts_execute_and_finish_with_cleanup_evidence(tmp_path: Path) -> None:
    case, runtime, hosts = runtime_case(tmp_path)
    assert (await runtime.execute(FixtureProgram())).state == "completed"
    for host in hosts:
        assert_reaped(host.process, forced=False)
    with case.store.begin() as transaction:
        events = transaction.events("run")
        assert sum(event.event == "call.dispatch_authorized" for event in events) == 2
        assert events[-1].event == "run.cleanup"
        cleanup = json.loads(events[-1].payload_json)
        assert cleanup["pending_calls"] == []
        assert all(host["status"] == "stopped" for host in json.loads(cleanup["environment_json"]))
    with pytest.raises(RuntimeError, match="cannot be restarted"):
        await runtime.execute(FixtureProgram())


async def test_startup_failure_reaps_ready_hosts_without_starting_graph(tmp_path: Path) -> None:
    case, runtime, hosts = runtime_case(tmp_path, mode="malformed")
    program = FixtureProgram()
    result = await runtime.execute(program)
    assert result.state == "failed" and result.reason == "startup_failure"
    assert not program.called
    assert_reaped(hosts[0].process, forced=False)
    assert_reaped(hosts[1].process, forced=True)
    with case.store.begin() as transaction:
        assert not any(event.event == "run.started" for event in transaction.events("run"))


async def test_call_deadline_ends_run_and_reaps_every_owned_host(tmp_path: Path) -> None:
    case, runtime, hosts = runtime_case(tmp_path, seconds=0.05)
    result = await runtime.execute(FixtureProgram('{"wait":true}'))
    assert result.state == "timed_out" and result.reason == "deadline_expired"
    for host in hosts:
        assert_reaped(host.process, forced=False)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "timed_out"


async def test_operator_stop_cancels_work_but_retains_terminal_evidence(tmp_path: Path) -> None:
    case, runtime, hosts = runtime_case(tmp_path)
    task = asyncio.create_task(runtime.execute(FixtureProgram('{"wait":true}')))
    async with asyncio.timeout(5):
        while not (tmp_path / "first/invoked").exists():
            await asyncio.sleep(0.01)
    runtime.stop()
    with pytest.raises(asyncio.CancelledError):
        await task
    for host in hosts:
        assert_reaped(host.process, forced=False)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "cancelled"
        assert transaction.run("run").reason == "operator_stop"


async def test_unhandled_component_failure_is_terminal(tmp_path: Path) -> None:
    _, runtime, hosts = runtime_case(tmp_path)
    result = await runtime.execute(FixtureProgram('{"error":true}'))
    assert result.state == "failed" and result.reason == "operation_failed"
    for host in hosts:
        assert_reaped(host.process, forced=False)
