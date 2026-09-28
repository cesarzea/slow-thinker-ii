"""Stop admission and release only obligations whose dispatch was never authorized."""

import json
import sqlite3

from slow_thinker_ii.application import RunState

from ._ledger import SqliteLedgerTransaction
from ._rows import text
from ._run_events import append_event
from ._run_rows import read_run


def stop_run(
    connection: sqlite3.Connection,
    run_id: str,
    reason: str,
    state: RunState,
    limit: int,
) -> None:
    run = read_run(connection, run_id)
    if run.state not in ("created", "running", "stopping"):
        append_event(connection, run_id, "run.stop_observed", None, json.dumps(reason), limit)
        return
    if run.state == "stopping" and state == "stopping":
        if run.reason != reason:
            append_event(connection, run_id, "run.stop_requested", None, json.dumps(reason), limit)
        return
    connection.execute(
        "UPDATE managed_runs SET state=?,reason=COALESCE(reason,?) WHERE run_id=?",
        (state, reason, run_id),
    )
    _cancel_calls(connection, run_id, state, limit)
    event = "run.finished" if state == "interrupted" else "run.stop_requested"
    append_event(connection, run_id, event, None, json.dumps(reason), limit)


def _cancel_calls(connection: sqlite3.Connection, run_id: str, state: RunState, limit: int) -> None:
    rows = connection.execute(
        "SELECT * FROM managed_calls WHERE run_id=? AND state IN ('reserved','dispatched')",
        (run_id,),
    ).fetchall()
    cancel_rows(connection, rows, state, limit)


def cancel_rows(
    connection: sqlite3.Connection,
    rows: list[sqlite3.Row],
    state: RunState,
    limit: int,
) -> None:
    ledger = SqliteLedgerTransaction(connection)
    for row in rows:
        if text(row, "state") == "reserved" and row["charge_json"] is not None:
            ledger.release_unsent(text(row, "attempt_id"))
        identity, run_id = text(row, "call_id"), text(row, "run_id")
        disposition = "interrupted" if state == "interrupted" else "cancelled"
        connection.execute(
            "UPDATE managed_calls SET state=? WHERE call_id=?", (disposition, identity)
        )
        append_event(
            connection, run_id, "call.cancel_requested", identity, json.dumps(disposition), limit
        )


def cancel_tree(connection: sqlite3.Connection, call_id: str, limit: int) -> None:
    rows = connection.execute(
        "WITH RECURSIVE children(call_id) AS ("
        "SELECT call_id FROM managed_calls WHERE parent_call_id=? UNION ALL "
        "SELECT c.call_id FROM managed_calls c JOIN children p ON c.parent_call_id=p.call_id) "
        "SELECT c.* FROM managed_calls c JOIN children d ON c.call_id=d.call_id "
        "WHERE c.state IN ('reserved','dispatched')",
        (call_id,),
    ).fetchall()
    cancel_rows(connection, rows, "stopping", limit)


def cancel_call(connection: sqlite3.Connection, call_id: str, limit: int) -> None:
    cancel_tree(connection, call_id, limit)
    rows = connection.execute(
        "SELECT * FROM managed_calls WHERE call_id=? AND state IN ('reserved','dispatched')",
        (call_id,),
    ).fetchall()
    cancel_rows(connection, rows, "stopping", limit)
