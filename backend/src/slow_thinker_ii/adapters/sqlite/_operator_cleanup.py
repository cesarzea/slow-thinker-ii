"""New workflows stay blocked until the owned runtime has recorded confirmed cleanup."""

import sqlite3

from slow_thinker_ii.contracts import decode_json, json_object


def confirmed(payload: str) -> bool:
    try:
        report = json_object(decode_json(payload))
        environment = report["environment_json"]
        if report["pending_calls"] != [] or not isinstance(environment, str):
            return False
        hosts = decode_json(environment)
        return isinstance(hosts, list) and all(
            isinstance(host, dict) and host.get("status") in ("stopped", "not_started")
            for host in hosts
        )
    except (ValueError, KeyError):
        return False


def blocker(db: sqlite3.Connection, *, cache: bool = True) -> tuple[str, str] | None:
    active = db.execute(
        "SELECT run_id FROM managed_runs WHERE state IN ('created','running','stopping') LIMIT 1"
    ).fetchone()
    if active is not None:
        return "active_run_exists", str(active[0])
    pending = db.execute(
        "SELECT run_id FROM process_ownership WHERE state!='stopped' LIMIT 1"
    ).fetchone()
    if pending is not None:
        return "cleanup_unconfirmed", str(pending[0])
    rows = db.execute("SELECT run_id FROM operator_runs WHERE cleanup_confirmed=0").fetchall()
    for row in rows:
        event = db.execute(
            "SELECT payload_json FROM run_events WHERE run_id=? AND event='run.cleanup' "
            "ORDER BY sequence DESC LIMIT 1",
            (row[0],),
        ).fetchone()
        if event is None or not confirmed(str(event[0])):
            return "cleanup_unconfirmed", str(row[0])
        if cache:
            db.execute("UPDATE operator_runs SET cleanup_confirmed=1 WHERE run_id=?", (row[0],))
    return None
