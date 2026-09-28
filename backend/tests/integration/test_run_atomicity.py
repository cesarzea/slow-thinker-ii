"""Competing dispatch/Stop and recording failures cannot create partial authorizations."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import RecordingError
from support.authority import PROPOSER
from support.run_admission import CHARGE, outstanding, run_case


def test_failed_dispatch_write_rolls_back_both_call_and_money_state(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    with case.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken_dispatch BEFORE UPDATE ON spending_attempts "
            "WHEN NEW.state='dispatched' BEGIN SELECT RAISE(ABORT,'fixture failure'); END"
        )
    with pytest.raises(RecordingError):
        case.service.authorize(lease.token)
    with case.store.begin() as transaction:
        assert transaction.call(lease.context.call_id).state == "reserved"
        assert not any(
            event.event == "call.dispatch_authorized" for event in transaction.events("run")
        )
    assert outstanding(case) == (100, 100, 100)
    with pytest.raises(AccessDenied):
        case.authority.context(lease.token)


def test_stop_racing_dispatch_has_one_consistent_durable_result(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    barrier = Barrier(2)

    def authorize() -> bool:
        barrier.wait(timeout=5)
        try:
            case.service.authorize(lease.token)
        except AccessDenied:
            return False
        return True

    def stop() -> None:
        barrier.wait(timeout=5)
        case.service.stop("operator_stop")

    with ThreadPoolExecutor(max_workers=2) as pool:
        dispatched, stopped = pool.submit(authorize), pool.submit(stop)
        sent = dispatched.result(timeout=5)
        stopped.result(timeout=5)
    assert outstanding(case) == ((100, 100, 100) if sent else (0, 0, 0))
    with case.store.begin() as transaction:
        events = transaction.events("run")
        assert sum(event.event == "call.dispatch_authorized" for event in events) == int(sent)
