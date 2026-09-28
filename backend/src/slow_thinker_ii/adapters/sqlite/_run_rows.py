"""Validate persisted records and bound JSON before including it in a transaction."""

import sqlite3

from pydantic import TypeAdapter

from slow_thinker_ii.access import CallContext
from slow_thinker_ii.application import (
    CallState,
    ChargeBasis,
    PreparedCall,
    RecordingError,
    RunRecord,
    StoredCall,
)

from ._rows import text

CONTEXT = TypeAdapter(CallContext)
CHARGE = TypeAdapter(ChargeBasis)
RUN = TypeAdapter(RunRecord)
CALL_STATE: TypeAdapter[CallState] = TypeAdapter(CallState)


def read_run(connection: sqlite3.Connection, run_id: str) -> RunRecord:
    row = connection.execute("SELECT * FROM managed_runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        raise ValueError("Unknown managed run")
    return RUN.validate_python(dict(row))


def read_call(connection: sqlite3.Connection, call_id: str) -> StoredCall:
    row = connection.execute("SELECT * FROM managed_calls WHERE call_id=?", (call_id,)).fetchone()
    if row is None:
        raise ValueError("Unknown managed call")
    charge = None if row["charge_json"] is None else CHARGE.validate_json(text(row, "charge_json"))
    prepared = PreparedCall(
        CONTEXT.validate_json(text(row, "context_json")), text(row, "request_json"), charge
    )
    return StoredCall(prepared, CALL_STATE.validate_python(text(row, "state")))


def bounded_json(connection: sqlite3.Connection, value: str, limit: int) -> str:
    if len(value.encode("utf-8")) > limit:
        raise RecordingError("Payload exceeds the configured recording limit")
    if connection.execute("SELECT json_valid(?)", (value,)).fetchone()[0] != 1:
        raise RecordingError("Recorded payload must be valid JSON")
    return value


def require_parent(connection: sqlite3.Connection, call: PreparedCall) -> None:
    context = call.context
    if context.parent_call_id is None:
        return
    parent = read_call(connection, context.parent_call_id)
    origin = parent.prepared.context
    if parent.state != "dispatched" or origin.run_id != context.run_id:
        raise ValueError("The originating call must remain active in the same run")
    if context.caller != origin.target.instance or context.activation_id != origin.activation_id:
        raise ValueError("Saved causal identities do not match the originating call")
