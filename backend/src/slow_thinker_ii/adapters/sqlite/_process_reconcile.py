"""Recovered cleanup closes only when every persisted launch is proven stopped."""

import sqlite3

from slow_thinker_ii.contracts import JsonValue, encode_json

from ._run_events import append_event


def reconcile_cleanup(db: sqlite3.Connection, limit: int) -> None:
    runs = db.execute(
        "SELECT DISTINCT p.run_id FROM process_ownership p JOIN managed_runs r USING(run_id) "
        "WHERE r.state NOT IN ('created','running','stopping')"
    ).fetchall()
    for row in runs:
        hosts = db.execute(
            "SELECT instance_id,state FROM process_ownership WHERE run_id=?", (row[0],)
        ).fetchall()
        if any(host["state"] != "stopped" for host in hosts):
            continue
        values: list[JsonValue] = [
            {"instance": str(host["instance_id"]), "status": "stopped"} for host in hosts
        ]
        append_event(
            db,
            str(row[0]),
            "run.cleanup",
            None,
            encode_json(
                {
                    "environment_json": encode_json(values),
                    "pending_calls": [],
                    "error_type": None,
                    "source": "verified_process_recovery",
                }
            ),
            limit,
        )
