"""Completion is a durable decision and cannot overtake Stop, deadlines or active work."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import RecordingError, RunFinalization
from support.authority import PROPOSER
from support.run_admission import CHARGE, outstanding, run_case


def test_completion_publishes_once_and_cannot_be_reopened(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    assert finish.finish('{"answer":1}').state == "completed"
    case.service.stop("operator_stop")
    assert finish.finish('{"answer":2}').state == "completed"
    with case.store.begin() as transaction:
        events = [event for event in transaction.events("run") if event.event == "run.finished"]
        assert len(events) == 1
        assert json.loads(events[0].payload_json)["output_json"] == '{"answer":1}'
    with pytest.raises(AccessDenied):
        case.authority.schedule(PROPOSER)


@pytest.mark.parametrize(
    "reason,state",
    [("operator_stop", "cancelled"), ("budget_denied", "failed"), ("call_deadline", "timed_out")],
)
def test_first_stop_cause_controls_terminal_outcome(
    tmp_path: Path, reason: str, state: str
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    case.service.stop(reason)
    case.clock.now = 200
    case.service.stop("runtime_shutdown")
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    result = finish.finish('{"late":true}')
    assert result.state == state and result.reason == reason
    with case.store.begin() as transaction:
        event = transaction.events("run")[-1]
        assert json.loads(event.payload_json)["output_json"] is None


def test_expired_run_cannot_publish_even_if_timeout_callback_is_late(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    case.clock.now = 100
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    result = finish.finish("{}")
    assert result.state == "timed_out" and result.reason == "run_deadline"


@pytest.mark.parametrize("dispatched", [False, True])
def test_active_calls_prevent_completion_and_preserve_possible_spending(
    tmp_path: Path, *, dispatched: bool
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    if dispatched:
        case.service.authorize(lease.token)
    result = RunFinalization(case.authority, case.store, "run", "runtime", case.clock).finish("{}")
    assert result.state == "failed" and result.reason == "unfinished_calls"
    assert outstanding(case) == ((100, 100, 100) if dispatched else (0, 0, 0))


def test_terminal_record_failure_rolls_back_output_and_closes_authority(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    with case.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken_finish BEFORE INSERT ON run_events "
            "WHEN NEW.event='run.finished' BEGIN SELECT RAISE(ABORT,'fixture failure'); END"
        )
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    with pytest.raises(RecordingError):
        finish.finish("{}")
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "running"
    with pytest.raises(AccessDenied):
        case.authority.schedule(PROPOSER)


def test_stop_racing_completion_has_one_terminal_decision(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    barrier = Barrier(2)

    def complete() -> str:
        barrier.wait(timeout=5)
        return finish.finish("{}").state

    def stop() -> None:
        barrier.wait(timeout=5)
        case.service.stop("operator_stop")

    with ThreadPoolExecutor(max_workers=2) as pool:
        completed, stopped = pool.submit(complete), pool.submit(stop)
        result = completed.result(timeout=5)
        stopped.result(timeout=5)
    assert result in ("completed", "cancelled")
    assert finish.finish("{}").state == result
