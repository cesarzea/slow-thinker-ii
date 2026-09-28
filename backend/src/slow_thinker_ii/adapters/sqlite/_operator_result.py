"""Read a retained final result without reconstructing success from partial node outputs."""

import sqlite3

from slow_thinker_ii.contracts import decode_json, encode_json, json_object


def final_result(db: sqlite3.Connection, run_id: str) -> str | None:
    run = db.execute("SELECT state FROM managed_runs WHERE run_id=?", (run_id,)).fetchone()
    if run is None:
        return None
    row = db.execute(
        "SELECT payload_json FROM run_events WHERE run_id=? AND event='run.finished' "
        "ORDER BY sequence DESC LIMIT 1",
        (run_id,),
    ).fetchone()
    output = None if row is None else json_object(decode_json(str(row[0]))).get("output_json")
    recorded = run[0] == "completed" and isinstance(output, str)
    return encode_json(
        {
            "schema_version": "0.1-draft",
            "run_id": run_id,
            "status": "recorded" if recorded else "unavailable",
            "content": decode_json(output) if recorded and isinstance(output, str) else None,
        }
    )
