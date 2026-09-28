"""Saved sessions have independent run history and share the existing monthly allowance."""

import sqlite3
from uuid import uuid4

from slow_thinker_ii.application import CommandReceipt, CommandResult
from slow_thinker_ii.contracts import encode_json

from ._operator_profiles import current_profile, ensure_scope
from ._operator_rows import comparable, previous, save


def create_session(
    db: sqlite3.Connection, command_id: str, name: str, timestamp: float, limit: int
) -> CommandResult:
    if not name.strip():
        raise ValueError("A session needs a display name")
    body = comparable(command_id, encode_json({"name": name}), limit)
    existing = previous(db, command_id, "session", body)
    if existing is not None:
        return existing
    profile = current_profile(db)
    if profile is None:
        return save(
            db,
            CommandReceipt(command_id, "session", "rejected", reason="no_configuration"),
            body,
            limit,
        )
    identity = uuid4().hex
    db.execute("INSERT INTO operator_sessions VALUES(?,?,?)", (identity, name, timestamp))
    ensure_scope(db, "session", identity, profile.limits.session_budget)
    return save(db, CommandReceipt(command_id, "session", "accepted", identity), body, limit)
