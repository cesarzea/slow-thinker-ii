"""No graph work starts after stopped admission or incomplete host readiness."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import ProcessFleet, ProcessHost
from slow_thinker_ii.application import ManagedRun, RunFinalization
from support.process_fixture import assert_reaped
from support.run_runtime import FixtureProgram, runtime_case


async def test_stop_before_start_launches_no_process(tmp_path: Path) -> None:
    case, runtime, hosts = runtime_case(tmp_path)
    runtime.stop()
    program = FixtureProgram()
    result = await runtime.execute(program)
    assert result.state == "cancelled" and result.reason == "operator_stop"
    assert not program.called and all(host.process.outcome() is None for host in hosts)
    with case.store.begin() as transaction:
        assert transaction.events("run")[-1].event == "run.cleanup"


async def test_stop_during_readiness_cancels_startup_and_reaps_owned_children(
    tmp_path: Path,
) -> None:
    case, runtime, hosts = runtime_case(tmp_path, mode="stubborn")
    program = FixtureProgram()
    task = asyncio.create_task(runtime.execute(program))
    async with asyncio.timeout(5):
        while not (tmp_path / "second/started").exists():
            await asyncio.sleep(0.01)
    runtime.stop()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 3)
    assert not program.called
    assert_reaped(hosts[0].process, forced=False)
    assert_reaped(hosts[1].process, forced=True)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "cancelled"


async def test_startup_consumes_the_run_deadline(tmp_path: Path) -> None:
    case, _, hosts = runtime_case(tmp_path, mode="stubborn")
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    runtime = ManagedRun(
        case.authority, case.service, finish, ProcessFleet(hosts), case.clock() + 0.1, 1
    )
    program = FixtureProgram()
    result = await runtime.execute(program)
    assert result.state == "timed_out" and result.reason == "run_deadline"
    assert not program.called
    for host in hosts:
        outcome = host.process.outcome()
        assert outcome is None or outcome.returncode is not None


async def test_operation_bindings_must_match_all_ready_contracts(tmp_path: Path) -> None:
    case, _, hosts = runtime_case(tmp_path)
    invalid = ProcessHost(hosts[0].instance, hosts[0].process, (("unknown", None),))
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    runtime = ManagedRun(
        case.authority, case.service, finish, ProcessFleet((invalid,)), case.clock() + 5, 1
    )
    program = FixtureProgram()
    result = await runtime.execute(program)
    assert result.state == "failed" and result.reason == "startup_failure"
    assert not program.called
    assert_reaped(hosts[0].process, forced=False)
