"""Stop and withdrawal receipts serialize against Start and preserve the primary cause."""

import sqlite3

from slow_thinker_ii.application import CommandConflict, CommandReceipt, CommandResult
from slow_thinker_ii.contracts import encode_json

from ._operator_rows import RECEIPT, comparable, previous, read_receipt, save
from ._run_rows import bounded_json, read_run
from ._run_stop import stop_run


def stop_receipt(
    db: sqlite3.Connection, command_id: str, run_id: str, now: float, limit: int
) -> CommandReceipt:
    row = db.execute("SELECT 1 FROM managed_runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        return CommandReceipt(command_id, "stop", "rejected", reason="unknown_run")
    run = read_run(db, run_id)
    if run.state not in ("created", "running", "stopping"):
        return CommandReceipt(command_id, "stop", "already_terminal", run_id, run.reason)
    reason = "run_deadline" if now >= run.deadline else "operator_stop"
    stop_run(db, run_id, reason, "stopping", limit)
    return CommandReceipt(command_id, "stop", "accepted", run_id, read_run(db, run_id).reason)


def stop(
    db: sqlite3.Connection, command_id: str, run_id: str, now: float, limit: int
) -> CommandResult:
    body = comparable(command_id, encode_json({"run_id": run_id}), limit)
    existing = previous(db, command_id, "stop", body)
    if existing is not None:
        return existing
    return save(db, stop_receipt(db, command_id, run_id, now, limit), body, limit)


def withdraw(db: sqlite3.Connection, command_id: str, now: float, limit: int) -> CommandResult:
    comparable(command_id, "{}", limit)
    previous_withdrawal = db.execute(
        "SELECT receipt_json FROM operator_withdrawals WHERE command_id=?", (command_id,)
    ).fetchone()
    if previous_withdrawal is not None:
        return CommandResult(RECEIPT.validate_json(str(previous_withdrawal[0])), True)
    original = read_receipt(db, command_id)
    if original is not None and original.kind != "start":
        raise CommandConflict("Only a Start intention can be withdrawn")
    if original is None:
        original = CommandReceipt(command_id, "start", "withdrawn", reason="operator_withdrawal")
        save(db, original, None, limit)
    result = withdrawal_receipt(db, original, now, limit)
    serialized = bounded_json(db, RECEIPT.dump_json(result).decode(), limit)
    db.execute("INSERT INTO operator_withdrawals VALUES(?,?)", (command_id, serialized))
    return CommandResult(result, False)


def withdrawal_receipt(
    db: sqlite3.Connection, original: CommandReceipt, now: float, limit: int
) -> CommandReceipt:
    if original.disposition == "accepted" and original.target_id is not None:
        stopped = stop_receipt(db, original.command_id, original.target_id, now, limit)
        return CommandReceipt(
            original.command_id, "start", "withdrawn", original.target_id, stopped.reason
        )
    return CommandReceipt(original.command_id, "start", "withdrawn", reason="operator_withdrawal")
