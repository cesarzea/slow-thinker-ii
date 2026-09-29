"""A disproven tariff bound stays quarantined across runs and backend restarts."""

import sqlite3

from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import ChargeBasis, PreparedCall
from slow_thinker_ii.contracts import encode_json

from ._run_events import append_event


def require_pricing(db: sqlite3.Connection, charge: ChargeBasis) -> None:
    row = db.execute(
        "SELECT 1 FROM pricing_quarantine WHERE tariff_revision=?", (charge.tariff_revision,)
    ).fetchone()
    if row is not None:
        raise AccessDenied("pricing_bound_quarantined")


def quarantine(db: sqlite3.Connection, call: PreparedCall, amount: int) -> None:
    charge = call.charge
    if charge is None or amount <= charge.bound:
        return
    db.execute(
        "INSERT OR IGNORE INTO "
        "pricing_quarantine(tariff_revision,pricing_json,call_id,bound,amount) "
        "VALUES(?,?,?,?,?)",
        (charge.tariff_revision, charge.pricing_json, call.context.call_id, charge.bound, amount),
    )
    append_event(
        db,
        call.context.run_id,
        "accounting.bound_exceeded",
        call.context.call_id,
        encode_json(
            {
                "tariff_revision": charge.tariff_revision,
                "bound": charge.bound,
                "amount": amount,
                "pricing_status": "quarantined",
            }
        ),
        1_048_576,
    )
