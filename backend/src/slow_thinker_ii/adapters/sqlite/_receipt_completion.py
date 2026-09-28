"""A receipt does not reopen stopped work or publish past deadlines or active children."""

import sqlite3

from slow_thinker_ii.access import InvocationEnd
from slow_thinker_ii.application import RunRecord, StoredCall


def completion_reason(
    connection: sqlite3.Connection,
    call: StoredCall,
    run: RunRecord,
    gate: InvocationEnd,
    now: float,
    runtime_id: str,
) -> str | None:
    if call.state != "dispatched":
        return "late_response"
    if run.state != "running" or run.runtime_id != runtime_id:
        return "run_closed"
    if now >= min(run.deadline, call.prepared.context.deadline):
        return "deadline_expired"
    children = connection.execute(
        "SELECT 1 FROM managed_calls WHERE parent_call_id=? "
        "AND state IN ('reserved','dispatched') LIMIT 1",
        (call.prepared.context.call_id,),
    ).fetchone()
    if children is not None:
        return "unfinished_children"
    return None if gate.publish else (gate.reason or "authority_closed")


def complete_call(
    connection: sqlite3.Connection,
    call: StoredCall,
    receipt_id: str,
    reason: str | None,
) -> None:
    if call.state != "dispatched":
        return
    connection.execute(
        "UPDATE managed_calls SET state=?,reason=?,result_receipt_id=? WHERE call_id=?",
        (
            "completed" if reason is None else "failed",
            reason,
            receipt_id,
            call.prepared.context.call_id,
        ),
    )
