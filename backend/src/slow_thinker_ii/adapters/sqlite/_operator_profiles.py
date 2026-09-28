"""Trusted profile activation changes higher-scope caps without resetting commitments."""

import math
import sqlite3
from datetime import UTC, datetime

from pydantic import TypeAdapter

from slow_thinker_ii.application import ExecutionConfiguration

PROFILE = TypeAdapter(ExecutionConfiguration)


def period(timestamp: float) -> str:
    if isinstance(timestamp, bool) or not math.isfinite(timestamp) or timestamp < 0:
        raise ValueError("A finite UTC admission timestamp is required")
    return datetime.fromtimestamp(timestamp, UTC).strftime("%Y-%m")


def current_profile(db: sqlite3.Connection) -> ExecutionConfiguration | None:
    row = db.execute(
        "SELECT profile_json FROM operator_profiles p JOIN operator_workspace w "
        "ON p.revision=w.profile_revision WHERE w.singleton=1"
    ).fetchone()
    return None if row is None else PROFILE.validate_json(str(row[0]))


def activate(db: sqlite3.Connection, profile: ExecutionConfiguration, timestamp: float) -> None:
    month = period(timestamp)
    existing = db.execute(
        "SELECT profile_json FROM operator_profiles WHERE revision=?", (profile.revision,)
    ).fetchone()
    if existing is not None and PROFILE.validate_json(str(existing[0])) != profile:
        raise ValueError("A configuration revision is immutable")
    change_caps(db, "session", profile.limits.session_budget, None)
    change_caps(db, "month", profile.limits.month_budget, month)
    db.execute(
        "INSERT OR IGNORE INTO operator_profiles VALUES(?,?)", (profile.revision, profile.to_json())
    )
    db.execute("UPDATE operator_workspace SET profile_revision=?", (profile.revision,))


def change_caps(db: sqlite3.Connection, kind: str, cap: int, identity: str | None) -> None:
    rows = db.execute(
        "SELECT scope_id,settled,reserved FROM budget_scopes WHERE kind=? "
        "AND (? IS NULL OR scope_id=?)",
        (kind, identity, identity),
    ).fetchall()
    if any(int(row[1]) + int(row[2]) > cap for row in rows):
        raise ValueError("A limit cannot fall below existing commitments")
    db.execute(
        "UPDATE budget_scopes SET cap=? WHERE kind=? AND (? IS NULL OR scope_id=?)",
        (cap, kind, identity, identity),
    )


def ensure_scope(db: sqlite3.Connection, kind: str, identity: str, cap: int) -> None:
    db.execute(
        "INSERT OR IGNORE INTO budget_scopes(kind,scope_id,cap) VALUES(?,?,?)",
        (kind, identity, cap),
    )
