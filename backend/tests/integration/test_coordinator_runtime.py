"""The coordinator owns real MCP children through completion and cancellation."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessPolicy
from slow_thinker_ii.adapters.process import ProcessFleet, ProcessHost
from support.coordinator import coordinator_case, eventually
from support.process_fixture import assert_reaped, fixture_process
from support.run_runtime import FIRST, SECOND, FixtureProgram


@pytest.mark.parametrize("stop", [False, True])
async def test_operator_command_owns_real_processes(tmp_path: Path, stop: bool) -> None:
    case = coordinator_case(tmp_path)
    hosts: list[ProcessHost] = []
    for name in ("first", "second"):
        directory = tmp_path / name
        directory.mkdir()
        hosts.append(ProcessHost(name, fixture_process(directory, "normal"), (("wait", None),)))
    case.preparer.policy = AccessPolicy((FIRST, SECOND), (), (FIRST, SECOND))
    case.preparer.environment = ProcessFleet(hosts)
    case.preparer.program = FixtureProgram('{"wait":true}' if stop else "{}")
    result = await case.coordinator.start("start", case.base.prepared().intent)
    assert result.receipt.target_id is not None
    if stop:
        await eventually(lambda: (tmp_path / "first/invoked").exists())
        await case.coordinator.stop("stop", result.receipt.target_id)
    await eventually(lambda: not case.coordinator.pending().runs)
    for host in hosts:
        assert_reaped(host.process, forced=False)
    with case.runs.begin() as transaction:
        assert transaction.run(result.receipt.target_id).state == (
            "cancelled" if stop else "completed"
        )
    assert not (await case.coordinator.close()).runs
