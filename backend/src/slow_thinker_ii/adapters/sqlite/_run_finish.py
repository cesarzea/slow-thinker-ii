"""T5 publishes final outputs only while no stop, expired deadline or call blocks completion."""

import json
import sqlite3

from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import RunRecord
from slow_thinker_ii.execution import stopped_outcome

from ._run_events import append_event
from ._run_rows import bounded_json, read_run
from ._run_stop import stop_run


def finish_run(
    connection: sqlite3.Connection,
    run_id: str,
    runtime_id: str,
    now: float,
    output_json: str | None,
    limit: int,
    *,
    executing: bool,
) -> RunRecord:
    run = read_run(connection, run_id)
    if run.runtime_id != runtime_id:
        raise AccessDenied("runtime_mismatch")
    if run.state not in ("created", "running", "stopping"):
        return run
    reason = rejection(connection, run, now, output_json, executing=executing)
    if reason is not None:
        stop_run(connection, run_id, reason, "stopping", limit)
        run = read_run(connection, run_id)
    state = stopped_outcome(run.reason) if run.state == "stopping" else "completed"
    output = None if state != "completed" else output_json
    if output is not None:
        bounded_json(connection, output, limit)
    connection.execute("UPDATE managed_runs SET state=? WHERE run_id=?", (state, run_id))
    payload = json.dumps({"state": state, "reason": run.reason, "output_json": output})
    append_event(connection, run_id, "run.finished", None, payload, limit)
    return read_run(connection, run_id)


def rejection(
    connection: sqlite3.Connection,
    run: RunRecord,
    now: float,
    output_json: str | None,
    *,
    executing: bool,
) -> str | None:
    if run.state == "stopping":
        return None
    if now >= run.deadline:
        return "run_deadline"
    if run.state != "running" or output_json is None:
        return "incomplete_execution"
    active = connection.execute(
        "SELECT 1 FROM managed_calls WHERE run_id=? AND state IN ('reserved','dispatched') LIMIT 1",
        (run.run_id,),
    ).fetchone()
    return "unfinished_calls" if executing or active is not None else None
