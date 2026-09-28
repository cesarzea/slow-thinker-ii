"""Implement run state, call records and budget changes on one SQLite connection."""

import sqlite3
import time
from collections.abc import Callable

from slow_thinker_ii.access import InvocationEnd
from slow_thinker_ii.application import (
    CallReceipt,
    PreparedCall,
    ReceiptOutcome,
    RunEvent,
    RunRecord,
    RunState,
    SavedReceipt,
    StoredCall,
)

from ._ledger import SqliteLedgerTransaction
from ._receipt_rows import check_receipt, read_receipt
from ._receive import receive
from ._reservation_money import reserve_charge
from ._run_events import append_event, read_events
from ._run_finish import finish_run
from ._run_rows import CHARGE, CONTEXT, bounded_json, read_call, read_run, require_parent
from ._run_stop import cancel_call, stop_run


class SqliteRunTransaction(SqliteLedgerTransaction):
    def __init__(
        self,
        connection: sqlite3.Connection,
        payload_limit: int,
        wall: Callable[[], float] = time.time,
    ) -> None:
        super().__init__(connection)
        self._db, self._limit = connection, payload_limit
        self._wall = wall

    def reserve_charge(self, call: PreparedCall, run: RunRecord) -> None:
        reserve_charge(self._db, call, run, self._wall, self._limit)

    def create_run(self, record: RunRecord) -> None:
        if record.state != "created" or record.reason is not None:
            raise ValueError("New runs must be created without a terminal reason")
        bounded_json(self._db, record.snapshot_json, self._limit)
        self._db.execute(
            "INSERT INTO managed_runs(run_id,graph_revision,session_id,month_id,runtime_id,"
            "deadline,snapshot_json,state) VALUES(?,?,?,?,?,?,?,'created')",
            (
                record.run_id,
                record.graph_revision,
                record.session_id,
                record.month_id,
                record.runtime_id,
                record.deadline,
                record.snapshot_json,
            ),
        )
        self.event(record.run_id, "run.created", None, record.snapshot_json)

    def run(self, run_id: str) -> RunRecord:
        return read_run(self._db, run_id)

    def start(self, run_id: str) -> None:
        changed = self._db.execute(
            "UPDATE managed_runs SET state='running' WHERE run_id=? AND state='created'", (run_id,)
        )
        if changed.rowcount != 1:
            raise ValueError("Only a created run can start")
        self.event(run_id, "run.started", None, "{}")

    def record_call(self, call: PreparedCall) -> None:
        context = call.context
        require_parent(self._db, call)
        request = bounded_json(self._db, call.request_json, self._limit)
        charge = None if call.charge is None else CHARGE.dump_json(call.charge).decode()
        if call.charge is not None:
            bounded_json(self._db, call.charge.pricing_json, self._limit)
        self._db.execute(
            "INSERT INTO managed_calls(call_id,attempt_id,run_id,parent_call_id,context_json,"
            "request_json,charge_json,state) VALUES(?,?,?,?,?,?,?,'reserved')",
            (
                context.call_id,
                context.attempt_id,
                context.run_id,
                context.parent_call_id,
                CONTEXT.dump_json(context).decode(),
                request,
                charge,
            ),
        )
        self.event(context.run_id, "call.requested", context.call_id, request)

    def call(self, call_id: str) -> StoredCall:
        return read_call(self._db, call_id)

    def cancel_call(self, call_id: str) -> None:
        cancel_call(self._db, call_id, self._limit)

    def authorize(self, call_id: str) -> None:
        call = self.call(call_id)
        require_parent(self._db, call.prepared)
        changed = self._db.execute(
            "UPDATE managed_calls SET state='dispatched' WHERE call_id=? AND state='reserved'",
            (call_id,),
        )
        if changed.rowcount != 1:
            raise ValueError("A managed call can be dispatched only once")
        self.event(call.prepared.context.run_id, "call.dispatch_authorized", call_id, "{}")

    def stop(self, run_id: str, reason: str, state: RunState = "stopping") -> None:
        if not reason or state not in ("stopping", "interrupted"):
            raise ValueError("Invalid stop disposition")
        stop_run(self._db, run_id, reason, state, self._limit)

    def event(self, run_id: str, event: str, call_id: str | None, payload: str) -> None:
        append_event(self._db, run_id, event, call_id, payload, self._limit)

    def events(self, run_id: str) -> tuple[RunEvent, ...]:
        return read_events(self._db, run_id)

    def receipt(self, receipt_id: str) -> SavedReceipt | None:
        return read_receipt(self._db, receipt_id)

    def check_receipt(self, receipt: CallReceipt) -> ReceiptOutcome | None:
        return check_receipt(self._db, receipt, self._limit)

    def receive(
        self,
        receipt: CallReceipt,
        gate: InvocationEnd,
        now: float,
        runtime_id: str,
    ) -> ReceiptOutcome:
        return receive(self._db, receipt, gate, now, runtime_id, self._limit)

    def unfinished(self) -> tuple[RunRecord, ...]:
        rows = self._db.execute(
            "SELECT run_id FROM managed_runs WHERE state IN ('created','running','stopping')"
        )
        return tuple(self.run(str(row[0])) for row in rows)

    def finish_run(
        self, run_id: str, runtime_id: str, now: float, output_json: str | None, *, executing: bool
    ) -> RunRecord:
        return finish_run(
            self._db, run_id, runtime_id, now, output_json, self._limit, executing=executing
        )
