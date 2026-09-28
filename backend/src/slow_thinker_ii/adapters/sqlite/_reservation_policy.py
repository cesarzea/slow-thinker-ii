"""Resolve frozen run ceilings and currently effective shared spending limits."""

import sqlite3
from dataclasses import dataclass, replace

from slow_thinker_ii.accounting import BudgetScope, ScopeKeys
from slow_thinker_ii.application import RunRecord

from ._ledger import SqliteLedgerTransaction
from ._operator_profiles import PROFILE, current_profile


@dataclass(frozen=True)
class ReservationPolicy:
    session_cap: int
    month_cap: int
    month_scope_cap: int
    admitted_revision: str | None
    current_revision: str | None

    def constrain(
        self, scopes: tuple[BudgetScope, BudgetScope, BudgetScope]
    ) -> tuple[BudgetScope, BudgetScope, BudgetScope]:
        run, session, month = scopes
        return (
            run,
            replace(session, cap=min(session.cap, self.session_cap)),
            replace(month, cap=min(month.cap, self.month_cap)),
        )


def reservation_policy(db: sqlite3.Connection, run: RunRecord) -> ReservationPolicy:
    row = db.execute(
        "SELECT p.profile_json FROM operator_runs r JOIN operator_profiles p "
        "ON p.revision=r.profile_revision WHERE r.run_id=?",
        (run.run_id,),
    ).fetchone()
    current = current_profile(db)
    if row is None:
        _, session, month = SqliteLedgerTransaction(db).scopes(
            ScopeKeys(run.run_id, run.session_id, run.month_id)
        )
        return ReservationPolicy(session.cap, month.cap, month.cap, None, None)
    admitted = PROFILE.validate_json(str(row[0]))
    if current is None:
        raise ValueError("An admitted operator run requires an active configuration")
    return ReservationPolicy(
        min(admitted.limits.session_budget, current.limits.session_budget),
        min(admitted.limits.month_budget, current.limits.month_budget),
        current.limits.month_budget,
        admitted.revision,
        current.revision,
    )
