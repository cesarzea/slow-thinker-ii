"""Persist launch ownership before spawning and retain uncertain recovery explicitly."""

import sqlite3

from pydantic import TypeAdapter

from slow_thinker_ii.application import OwnedLaunch, ProcessIdentity
from slow_thinker_ii.contracts import encode_json

from ._database import SqliteDatabase
from ._process_reconcile import reconcile_cleanup
from ._run_events import append_event

IDENTITY = TypeAdapter(ProcessIdentity)


class SqliteProcessJournal:
    def __init__(self, database: SqliteDatabase, limit: int) -> None:
        self._database, self._limit = database, limit

    def prepare(self, launch: OwnedLaunch) -> None:
        with self._database.transaction() as db:
            require_run_owner(db, launch)
            db.execute(
                "INSERT INTO "
                "process_ownership(marker,run_id,runtime_id,instance_id,workspace,state) "
                "VALUES(?,?,?,?,?,'launching')",
                (
                    launch.marker,
                    launch.run_id,
                    launch.runtime_id,
                    launch.instance_id,
                    launch.workspace,
                ),
            )
            append_event(
                db,
                launch.run_id,
                "host.state_changed",
                None,
                encode_json(
                    {"instance": launch.instance_id, "state": "launching", "marker": launch.marker}
                ),
                self._limit,
            )

    def started(self, identity: ProcessIdentity) -> None:
        with self._database.transaction() as db:
            changed = db.execute(
                "UPDATE process_ownership SET identity_json=?,state='running' "
                "WHERE marker=? AND state='launching'",
                (IDENTITY.dump_json(identity).decode(), identity.marker),
            )
            if changed.rowcount != 1:
                raise ValueError("Process ownership requires its persisted launch intention")

    def stopped(self, marker: str, reason: str) -> None:
        self._state(marker, "stopped", reason)

    def unconfirmed(self, marker: str, reason: str) -> None:
        self._state(marker, "unconfirmed", reason)

    def _state(self, marker: str, state: str, reason: str) -> None:
        with self._database.transaction() as db:
            row = db.execute(
                "SELECT run_id,instance_id FROM process_ownership WHERE marker=?", (marker,)
            ).fetchone()
            if row is None:
                raise ValueError("Unknown owned process marker")
            db.execute(
                "UPDATE process_ownership SET state=?,reason=? WHERE marker=?",
                (state, reason, marker),
            )
            append_event(
                db,
                str(row["run_id"]),
                "host.state_changed",
                None,
                encode_json(
                    {"instance": str(row["instance_id"]), "state": state, "reason": reason}
                ),
                self._limit,
            )

    def pending(self) -> tuple[OwnedLaunch, ...]:
        with self._database.transaction() as db:
            rows = db.execute("SELECT * FROM process_ownership WHERE state!='stopped'").fetchall()
            return tuple(
                OwnedLaunch(
                    str(row["marker"]),
                    str(row["run_id"]),
                    str(row["runtime_id"]),
                    str(row["instance_id"]),
                    str(row["workspace"]),
                    None
                    if row["identity_json"] is None
                    else IDENTITY.validate_json(str(row["identity_json"])),
                )
                for row in rows
            )

    def reconcile(self) -> None:
        with self._database.transaction() as db:
            reconcile_cleanup(db, self._limit)

    def diagnostic(self, marker: str, payload_json: str) -> None:
        with self._database.transaction() as db:
            row = db.execute(
                "SELECT run_id FROM process_ownership WHERE marker=?", (marker,)
            ).fetchone()
            if row is None:
                raise ValueError("Unknown process diagnostic source")
            append_event(db, str(row[0]), "host.diagnostic", None, payload_json, self._limit)


def require_run_owner(db: sqlite3.Connection, launch: OwnedLaunch) -> None:
    row = db.execute(
        "SELECT runtime_id,state FROM managed_runs WHERE run_id=?", (launch.run_id,)
    ).fetchone()
    if (
        row is None
        or row["runtime_id"] != launch.runtime_id
        or row["state"] not in ("created", "running")
    ):
        raise ValueError("Only the admitted runtime can own a component launch")
