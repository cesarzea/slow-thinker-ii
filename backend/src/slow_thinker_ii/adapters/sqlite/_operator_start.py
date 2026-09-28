"""T1 admits one prepared workflow with its command, scopes, snapshot and event atomically."""

import math
import sqlite3
from uuid import uuid4

from slow_thinker_ii.application import CommandReceipt, CommandResult, PreparedStart, RunRecord

from ._operator_cleanup import blocker
from ._operator_profiles import current_profile, ensure_scope, period
from ._operator_rows import comparable, previous, save
from ._run_transaction import SqliteRunTransaction


def rejection(
    db: sqlite3.Connection, prepared: PreparedStart, timestamp: float
) -> tuple[str, str | None] | None:
    if prepared.admit_before is not None and timestamp >= prepared.admit_before:
        return "preparation_expired", None
    if current_profile(db) != prepared.configuration:
        return "configuration_changed", None
    if (
        db.execute(
            "SELECT 1 FROM operator_sessions WHERE session_id=?", (prepared.intent.session_id,)
        ).fetchone()
        is None
    ):
        return "unknown_session", None
    last = db.execute("SELECT last_admitted_at FROM operator_workspace").fetchone()[0]
    if last is not None and timestamp < float(last):
        return "clock_regressed", None
    return blocker(db)


def admit(
    db: sqlite3.Connection,
    command_id: str,
    prepared: PreparedStart,
    timestamp: float,
    monotonic: float,
    limit: int,
) -> CommandResult:
    body = comparable(command_id, prepared.intent.to_json(), limit)
    existing = previous(db, command_id, "start", body)
    if existing is not None:
        return existing
    month = period(timestamp)
    denied = rejection(db, prepared, timestamp)
    if denied is not None:
        reason, target = denied
        return save(
            db, CommandReceipt(command_id, "start", "rejected", target, reason), body, limit
        )
    identity = uuid4().hex
    record = run_record(identity, prepared, month, monotonic)
    return persist_admission(db, command_id, prepared, record, timestamp, limit)


def persist_admission(
    db: sqlite3.Connection,
    command_id: str,
    prepared: PreparedStart,
    record: RunRecord,
    timestamp: float,
    limit: int,
) -> CommandResult:
    identity, month = record.run_id, record.month_id
    SqliteRunTransaction(db, limit).create_run(record)
    ensure_scope(db, "run", identity, prepared.configuration.limits.run_budget)
    ensure_scope(db, "month", month, prepared.configuration.limits.month_budget)
    receipt = save(
        db,
        CommandReceipt(command_id, "start", "accepted", identity),
        prepared.intent.to_json(),
        limit,
    )
    db.execute(
        "INSERT INTO operator_runs(run_id,command_id,profile_revision,created_at) VALUES(?,?,?,?)",
        (identity, command_id, prepared.configuration.revision, timestamp),
    )
    db.execute("UPDATE operator_workspace SET last_admitted_at=?", (timestamp,))
    return receipt


def run_record(identity: str, prepared: PreparedStart, month: str, monotonic: float) -> RunRecord:
    if isinstance(monotonic, bool) or not math.isfinite(monotonic):
        raise ValueError("A finite monotonic admission time is required")
    snapshot = prepared.record_json()
    return RunRecord(
        identity,
        prepared.intent.graph_revision,
        prepared.intent.session_id,
        month,
        prepared.runtime_id,
        monotonic + prepared.configuration.limits.run_seconds,
        snapshot,
    )
