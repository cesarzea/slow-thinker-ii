"""Terminal success, failed process cleanup and failed recording are separate facts."""

import json
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied, OperationAddress
from slow_thinker_ii.application import (
    ManagedCalls,
    ManagedRun,
    OperationPort,
    RecordingError,
    RunFinalization,
)
from support.authority import PROPOSER
from support.managed_calls import RealClock
from support.run_admission import RunCase, run_case


class FixtureEnvironment:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail, self.closed = fail, False

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncGenerator[Mapping[OperationAddress, OperationPort]]:
        del deadline
        try:
            yield {}
        finally:
            self.closed = True
            if self.fail:
                raise RuntimeError("private cleanup diagnostic")

    def report(self) -> str:
        return json.dumps({"status": "cleanup_failed" if self.fail else "complete"})


class CompletedProgram:
    async def execute(self, calls: ManagedCalls) -> str:
        del calls
        return '{"done":true}'


def managed(case: RunCase, environment: FixtureEnvironment) -> ManagedRun:
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    return ManagedRun(case.authority, case.service, finish, environment, case.clock() + 30, 1)


async def test_failed_cleanup_does_not_replace_success_or_hide_cleanup_failure(
    tmp_path: Path,
) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock(), start=False)
    environment = FixtureEnvironment(fail=True)
    result = await managed(case, environment).execute(CompletedProgram())
    assert result.state == "completed" and environment.closed
    with case.store.begin() as transaction:
        events = transaction.events("run")
        assert sum(event.event == "run.finished" for event in events) == 1
        cleanup = json.loads(events[-1].payload_json)
        assert json.loads(cleanup["environment_json"])["status"] == "cleanup_failed"
        assert cleanup["error_type"] == "RuntimeError"
        assert "private" not in events[-1].payload_json


async def test_failed_final_recording_is_raised_after_environment_cleanup(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock(), start=False)
    environment = FixtureEnvironment()
    with case.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken_finish BEFORE INSERT ON run_events "
            "WHEN NEW.event='run.finished' BEGIN SELECT RAISE(ABORT,'fixture failure'); END"
        )
    with pytest.raises(RecordingError):
        await managed(case, environment).execute(CompletedProgram())
    assert environment.closed
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "stopping"
        assert all(event.event != "run.finished" for event in transaction.events("run"))
        assert '"RecordingError"' in transaction.events("run")[-1].payload_json
    with pytest.raises(AccessDenied):
        case.authority.schedule(PROPOSER)
