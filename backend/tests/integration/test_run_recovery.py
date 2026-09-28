"""Recovery preserves uncertain obligations and never resumes previously authorized work."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteRunStore
from slow_thinker_ii.application import RunAdmission, recover_runs
from support.authority import PROPOSER, REVIEWER
from support.run_admission import CHARGE, outstanding, run_case


def test_recovery_releases_only_calls_without_a_dispatch_intent(tmp_path: Path) -> None:
    path = tmp_path / "run.sqlite"
    case = run_case(path)
    sent = case.authority.schedule(PROPOSER)
    unsent = case.authority.schedule(REVIEWER)
    case.service.reserve(sent.token, "{}", CHARGE)
    case.service.reserve(unsent.token, "{}", CHARGE)
    case.service.authorize(sent.token)
    reopened = SqliteRunStore(SqliteDatabase(path), 4096)
    assert recover_runs(reopened) == ("run",)
    assert recover_runs(reopened) == ()
    assert outstanding(case) == (100, 100, 100)
    with reopened.begin() as transaction:
        assert transaction.run("run").state == "interrupted"
        assert transaction.call(sent.context.call_id).state == "interrupted"
        assert transaction.call(unsent.context.call_id).state == "interrupted"
    with pytest.raises(AccessDenied, match="run_closed"):
        case.service.authorize(unsent.token)


def test_new_backend_cannot_use_an_old_runtime_before_recovery(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    replacement = RunAdmission(case.authority, case.store, "run", "new-runtime", case.clock)
    with pytest.raises(AccessDenied, match="run_closed"):
        replacement.authorize(lease.token)
    assert outstanding(case) == (100, 100, 100)


def test_deadline_is_rechecked_after_reservation(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.clock.now = lease.context.deadline
    with pytest.raises(AccessDenied):
        case.service.authorize(lease.token)
    case.service.stop("call_deadline")
    assert outstanding(case) == (0, 0, 0)


def test_primary_stop_reason_survives_secondary_stop_and_recovery(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    case.service.stop("operator_stop")
    with case.store.begin() as transaction:
        count = len(transaction.events("run"))
    case.service.stop("operator_stop")
    with case.store.begin() as transaction:
        assert len(transaction.events("run")) == count
        transaction.stop("run", "call_deadline")
    recover_runs(case.store)
    with case.store.begin() as transaction:
        assert transaction.run("run").reason == "operator_stop"
        assert transaction.run("run").state == "interrupted"
