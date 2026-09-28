"""The final commit checks runtime identity, recording bounds and durable pending calls."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import RecordingError, RunFinalization
from support.authority import PROPOSER
from support.run_admission import CHARGE, outstanding, run_case


def test_foreign_runtime_cannot_finalize_or_record_cleanup(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    finish = RunFinalization(case.authority, case.store, "run", "foreign", case.clock)
    with pytest.raises(AccessDenied, match="runtime_mismatch"):
        finish.finish("{}")
    with pytest.raises(AccessDenied, match="runtime_mismatch"):
        finish.cleanup("{}")
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "running"


@pytest.mark.parametrize("output", ["invalid", '"' + "x" * 5000 + '"'])
def test_invalid_final_output_rolls_back_the_success_decision(tmp_path: Path, output: str) -> None:
    case = run_case(tmp_path / "run.sqlite")
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    with pytest.raises(RecordingError):
        finish.finish(output)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "running"


def test_unstarted_run_cannot_be_reported_as_successful(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", start=False)
    result = RunFinalization(case.authority, case.store, "run", "runtime", case.clock).finish("{}")
    assert result.state == "failed" and result.reason == "incomplete_execution"


def test_durable_unsent_call_blocks_completion_after_transient_occupancy_ends(
    tmp_path: Path,
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.authority.finish(lease.context.call_id, succeeded=False)
    result = RunFinalization(case.authority, case.store, "run", "runtime", case.clock).finish("{}")
    assert result.reason == "unfinished_calls" and outstanding(case) == (0, 0, 0)


def test_expired_deadline_takes_priority_over_a_new_stop_request(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    case.clock.now = 100
    case.service.stop("operator_stop")
    result = RunFinalization(case.authority, case.store, "run", "runtime", case.clock).finish()
    assert result.state == "timed_out" and result.reason == "run_deadline"
