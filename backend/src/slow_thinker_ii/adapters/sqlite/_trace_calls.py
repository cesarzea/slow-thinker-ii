"""Call inspection joins causal identity with its own attempt, never parent totals."""

import sqlite3

from slow_thinker_ii.accounting import display_amount
from slow_thinker_ii.contracts import JsonObject, decode_json

from ._operator_cursors import OperatorCursors
from ._trace_receipts import receipt_page


def call_details(
    db: sqlite3.Connection,
    run: str,
    call: str,
    cursor: str | None,
    cursors: OperatorCursors,
    size: int,
) -> JsonObject | None:
    row = db.execute(
        "SELECT * FROM managed_calls WHERE run_id=? AND call_id=?", (run, call)
    ).fetchone()
    if row is None:
        return None
    return {
        "schema_version": "0.1-draft",
        "run_id": run,
        "call_id": call,
        "attempt_id": str(row["attempt_id"]),
        "context": decode_json(str(row["context_json"])),
        "state": str(row["state"]),
        "reason": row["reason"],
        "request_payload_id": "request:" + call,
        "pricing_payload_id": None if row["charge_json"] is None else "pricing:" + call,
        "result_receipt_id": row["result_receipt_id"],
        "accounting": attempt_details(db, str(row["attempt_id"])),
        "receipts": receipt_page(db, run, call, cursor, cursors, size),
    }


def attempt_details(db: sqlite3.Connection, attempt: str) -> JsonObject | None:
    row = db.execute("SELECT * FROM spending_attempts WHERE attempt_id=?", (attempt,)).fetchone()
    if row is None:
        return None
    bound = int(row["bound"])
    state = str(row["state"])
    return {
        "currency": "USD",
        "state": state,
        "bound": display_amount(bound),
        "amount": None if row["amount"] is None else display_amount(int(row["amount"])),
        "outstanding": display_amount(bound if state in ("reserved", "dispatched") else 0),
        "source": row["source"],
        "month_id": str(row["month_id"]),
    }
