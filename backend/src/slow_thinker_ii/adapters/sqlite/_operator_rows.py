"""Store comparable command bodies and receipts in the same transaction as their effects."""

import sqlite3

from pydantic import TypeAdapter

from slow_thinker_ii.application import CommandConflict, CommandKind, CommandReceipt, CommandResult
from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ._run_rows import bounded_json

RECEIPT = TypeAdapter(CommandReceipt)


def comparable(command_id: str, body: str, limit: int) -> str:
    if not command_id or len(command_id.encode("utf-8")) > limit:
        raise ValueError("A bounded command identity is required")
    return encode_json(json_object(decode_json(body)))


def previous(
    db: sqlite3.Connection, command_id: str, kind: CommandKind, body: str
) -> CommandResult | None:
    row = db.execute("SELECT * FROM operator_commands WHERE command_id=?", (command_id,)).fetchone()
    if row is None:
        return None
    if row["kind"] != kind or (row["request_json"] is not None and row["request_json"] != body):
        raise CommandConflict("command_conflict")
    return CommandResult(RECEIPT.validate_json(str(row["receipt_json"])), True)


def save(
    db: sqlite3.Connection, receipt: CommandReceipt, body: str | None, limit: int
) -> CommandResult:
    serialized = RECEIPT.dump_json(receipt).decode()
    bounded_json(db, serialized, limit)
    if body is not None:
        bounded_json(db, body, limit)
    db.execute(
        "INSERT INTO operator_commands(command_id,kind,request_json,receipt_json) VALUES(?,?,?,?)",
        (receipt.command_id, receipt.kind, body, serialized),
    )
    return CommandResult(receipt, False)


def read_receipt(db: sqlite3.Connection, command_id: str) -> CommandReceipt | None:
    row = db.execute(
        "SELECT receipt_json FROM operator_commands WHERE command_id=?", (command_id,)
    ).fetchone()
    return None if row is None else RECEIPT.validate_json(str(row[0]))
