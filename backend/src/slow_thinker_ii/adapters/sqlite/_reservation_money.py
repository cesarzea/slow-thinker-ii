"""Assign each billable attempt to its own UTC admission period atomically."""

import calendar
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.accounting import Reservation, ScopeKeys, admit
from slow_thinker_ii.application import PreparedCall, RunRecord
from slow_thinker_ii.contracts import encode_json

from ._ledger import SqliteLedgerTransaction
from ._operator_profiles import ensure_scope, period
from ._reservation_policy import ReservationPolicy, reservation_policy
from ._run_events import append_event


def admission_period(db: sqlite3.Connection, timestamp: float) -> tuple[str, str, str]:
    try:
        month = period(timestamp)
        start = datetime.fromtimestamp(timestamp, UTC).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=calendar.monthrange(start.year, start.month)[1])
    except (ValueError, OverflowError, OSError) as error:
        raise AccessDenied("invalid_clock") from error
    last = db.execute("SELECT last_admitted_at FROM operator_workspace").fetchone()[0]
    if last is not None and timestamp < float(last):
        raise AccessDenied("clock_regressed")
    return month, start.isoformat(), end.isoformat()


def reserve_charge(
    db: sqlite3.Connection,
    call: PreparedCall,
    run: RunRecord,
    wall: Callable[[], float],
    limit: int,
) -> None:
    if call.charge is None:
        return
    timestamp = wall()
    interval = admission_period(db, timestamp)
    policy = reservation_policy(db, run)
    ensure_scope(db, "month", interval[0], policy.month_scope_cap)
    ledger = SqliteLedgerTransaction(db)
    keys = ScopeKeys(run.run_id, run.session_id, interval[0])
    admit(policy.constrain(ledger.scopes(keys)), call.charge.bound)
    ledger.reserve(Reservation(call.context.attempt_id, keys, call.charge.bound))
    record_admission(db, call, timestamp, interval, policy, limit)
    db.execute("UPDATE operator_workspace SET last_admitted_at=?", (timestamp,))


def record_admission(
    db: sqlite3.Connection,
    call: PreparedCall,
    timestamp: float,
    interval: tuple[str, str, str],
    policy: ReservationPolicy,
    limit: int,
) -> None:
    payload = encode_json(
        {
            "attempt_id": call.context.attempt_id,
            "admitted_at": timestamp,
            "month_id": interval[0],
            "timezone": "UTC",
            "period_start": interval[1],
            "period_end": interval[2],
            "admitted_policy_revision": policy.admitted_revision,
            "current_policy_revision": policy.current_revision,
            "session_cap": policy.session_cap,
            "month_cap": policy.month_cap,
        }
    )
    append_event(
        db, call.context.run_id, "accounting.reserved", call.context.call_id, payload, limit
    )
