"""Expired admission and recording loss fail closed without launching new work."""

from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from slow_thinker_ii.application import CommandResult, PreparedStart, RecordingError, RunTransaction
from support.coordinator import Environment, coordinator_case, eventually
from support.managed_calls import RealClock


class JumpClock(RealClock):
    def __init__(self) -> None:
        super().__init__()
        self.offset = 0.0

    def __call__(self) -> float:
        return super().__call__() + self.offset


async def test_deadline_expired_after_admission_starts_no_host(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = JumpClock()
    case = coordinator_case(tmp_path, clock=clock)
    admit = case.commands.admit

    def delayed(command: str, prepared: PreparedStart) -> CommandResult:
        result = admit(command, prepared)
        clock.offset += 100
        return result

    monkeypatch.setattr(case.commands, "admit", delayed)
    result = await case.coordinator.start("start", case.base.prepared().intent)
    await eventually(lambda: not case.coordinator.pending().runs)
    assert result.receipt.target_id is not None
    with case.runs.begin() as transaction:
        run = transaction.run(result.receipt.target_id)
        assert run.state == "timed_out" and run.reason == "run_deadline"
    assert (
        isinstance(case.preparer.environment, Environment) and case.preparer.environment.opened == 0
    )
    await case.coordinator.close()


async def test_failed_shutdown_recording_keeps_the_run_closed_to_new_admission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.operation.release.clear()
    result = await case.coordinator.start("start", case.base.prepared().intent)
    await case.preparer.operation.started.wait()

    def unavailable() -> AbstractContextManager[RunTransaction]:
        raise RecordingError("fixture storage loss")

    monkeypatch.setattr(case.runs, "begin", unavailable)
    await case.coordinator.close()
    assert case.coordinator.failures() == ((result.receipt.target_id, "RecordingError"),)
    assert (
        isinstance(case.preparer.environment, Environment) and case.preparer.environment.closed == 1
    )
    denied = case.commands.admit("new", case.base.prepared())
    assert denied.receipt.reason == "active_run_exists"


@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan"), True])
def test_coordinator_requires_bounded_preparation(tmp_path: Path, seconds: float) -> None:
    with pytest.raises(ValueError):
        coordinator_case(tmp_path, preparation=seconds)


@pytest.mark.parametrize("maximum", [0, -1, True])
def test_coordinator_requires_bounded_command_count(tmp_path: Path, maximum: int) -> None:
    with pytest.raises(ValueError):
        coordinator_case(tmp_path, maximum=maximum)
