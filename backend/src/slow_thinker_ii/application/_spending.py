"""The money of a model call: reservation, settlement with the reply's usage, overrun check."""

from slow_thinker_ii.accounting import Scope, charge

from ._active import ActiveCall
from ._admission import Admitted
from ._budgets import call_scopes
from ._call_record import CallRecord
from ._ports import Clock, Ledger
from ._values import BudgetLimits, ProviderReply


class CallSpending:
    def __init__(self, ledger: Ledger, budgets: BudgetLimits, clock: Clock) -> None:
        self._ledger = ledger
        self._budgets = budgets
        self._clock = clock

    def reserve(self, call: ActiveCall, admitted: Admitted, record: CallRecord) -> Scope | None:
        """Reserves the bound against the run, day and month; returns the exhausted scope."""
        now = self._clock.now()
        run_id = call.caller.run_id
        record.scopes = call_scopes(run_id, call.run.plan.limits.budget_nanos, self._budgets, now)
        exhausted = self._ledger.reserve(record.call_id, run_id, record.scopes, admitted.bound, now)
        record.reserved = admitted.bound if exhausted is None else 0
        return exhausted

    def settle(self, admitted: Admitted, record: CallRecord, reply: ProviderReply) -> None:
        """Charges the reported usage at the rates in force; unknown usage is the reservation."""
        record.cost, record.estimated = record.reserved, True
        if reply.usage is not None:
            try:
                started, ended = reply.started_at, reply.ended_at
                record.cost, record.rates = charge(
                    admitted.model.tariff, reply.usage, started, ended
                )
                record.usage, record.estimated = reply.usage, False
            except ValueError:
                record.cost, record.rates = record.reserved, None
        self._ledger.settle(record.call_id, record.cost, record.estimated, self._clock.now())

    def exceeded(self, record: CallRecord) -> Scope | None:
        """After a charge above its reservation, the first scope now over its limit."""
        if record.cost <= record.reserved:
            return None
        for scope in record.scopes:
            used = self._ledger.used(scope.kind, scope.key)
            if used > scope.limit:
                return Scope(scope.kind, scope.key, scope.limit, used)
        return None
