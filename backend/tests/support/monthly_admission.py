"""Operator-admitted runs share a controlled UTC clock with per-call admission."""

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

from slow_thinker_ii.access import AccessPolicy, CallAuthority, CallLimits, InvocationLease
from slow_thinker_ii.accounting import BudgetScope, ScopeKeys
from slow_thinker_ii.adapters.sqlite import SqliteRunStore
from slow_thinker_ii.application import ChargeBasis, RunAdmission, RunRecord

from .authority import PROPOSER, REVIEWER
from .operator_commands import OperatorCase, operator_case


def timestamp(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()


@dataclass(frozen=True)
class MonthCase:
    operator: OperatorCase
    store: SqliteRunStore
    service: RunAdmission
    authority: CallAuthority
    run: RunRecord

    def move(self, value: str) -> None:
        self.operator.wall.value = timestamp(value)

    def reserve(self, *, second: bool = False, bound: int = 100) -> InvocationLease:
        lease = self.authority.schedule(REVIEWER if second else PROPOSER)
        self.service.reserve(lease.token, "{}", ChargeBasis(bound, "tariff", "{}"))
        self.service.authorize(lease.token)
        return lease

    def scopes(self, month: str) -> tuple[BudgetScope, BudgetScope, BudgetScope]:
        with self.store.begin() as transaction:
            return transaction.scopes(ScopeKeys(self.run.run_id, self.run.session_id, month))


def monthly_case(directory: Path, start: str = "2026-09-30T23:59:59+00:00") -> MonthCase:
    operator = operator_case(directory)
    operator.wall.value = timestamp(start)
    receipt = operator.store.admit("start", operator.prepared()).receipt
    assert receipt.target_id is not None
    store = SqliteRunStore(operator.database, 1_048_576, operator.wall)
    with store.begin() as transaction:
        run = transaction.run(receipt.target_id)
    policy = AccessPolicy((PROPOSER, REVIEWER), (), (PROPOSER, REVIEWER))
    authority = CallAuthority(
        run.run_id, run.graph_revision, policy, CallLimits(10, 3, 20), run.deadline, operator.clock
    )
    service = RunAdmission(authority, store, run.run_id, run.runtime_id, operator.clock)
    service.start()
    return MonthCase(operator, store, service, authority, run)


def configure(case: MonthCase, *, session: int = 5000, month: int = 10000) -> None:
    current = case.operator.profile
    newer = replace(
        current,
        revision="new",
        limits=replace(current.limits, revision="new", session_budget=session, month_budget=month),
    )
    case.operator.store.configure(newer)
