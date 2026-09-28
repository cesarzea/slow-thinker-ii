"""T2 and T3 coordinate current authority, saved requests and all budget scopes."""

import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from threading import RLock

from slow_thinker_ii.access import AccessDenied, CallAuthority
from slow_thinker_ii.accounting import BudgetExceeded

from ._admission_checks import validate_context
from ._receipts import CallReceipt, ReceiptOutcome
from ._run_ports import RecordingError, RunStore, RunTransaction
from ._run_records import ChargeBasis, PreparedCall, RunRecord


class RunAdmission:
    def __init__(
        self,
        authority: CallAuthority,
        store: RunStore,
        run_id: str,
        runtime_id: str,
        clock: Callable[[], float],
    ) -> None:
        self._authority, self._store = authority, store
        self._run_id, self._runtime = run_id, runtime_id
        self._clock, self._lock = clock, RLock()

    def start(self) -> None:
        with self._unit() as transaction:
            self._run(transaction, "created")
            transaction.start(self._run_id)

    def check_start(self) -> None:
        with self._unit() as transaction:
            self._run(transaction, "created")

    def reserve(self, token: str, request_json: str, charge: ChargeBasis | None) -> PreparedCall:
        denied: BudgetExceeded | AccessDenied | None = None
        with self._unit() as transaction:
            context = self._authority.context(token)
            run = self._run(transaction, "running")
            validate_context(context, run, self._clock())
            call = PreparedCall(context, request_json, charge)
            try:
                transaction.reserve_charge(call, run)
            except (BudgetExceeded, AccessDenied) as error:
                reason = error.code if isinstance(error, AccessDenied) else "budget_denied"
                transaction.event(run.run_id, "call.rejected", context.call_id, json.dumps(reason))
                transaction.stop(run.run_id, reason)
                denied = error
            else:
                transaction.record_call(call)
        if denied is not None:
            self._authority.stop()
            raise denied
        return call

    def authorize(self, token: str) -> PreparedCall:
        with self._unit() as transaction:
            context = self._authority.context(token)
            validate_context(context, self._run(transaction, "running"), self._clock())
            call = transaction.call(context.call_id).prepared
            if call.context != context:
                raise AccessDenied("saved_context_mismatch")
            transaction.authorize(context.call_id)
            if call.charge is not None:
                transaction.dispatched(context.attempt_id)
            return call

    def receive(self, receipt: CallReceipt) -> ReceiptOutcome:
        with self._unit() as transaction:
            call = transaction.call(receipt.call_id)
            if call.prepared.context.run_id != self._run_id:
                raise AccessDenied("receipt_run_mismatch")
            previous = transaction.check_receipt(receipt)
            if previous is not None:
                return previous
            gate = self._authority.finish(receipt.call_id, succeeded=receipt.succeeded)
            outcome = transaction.receive(receipt, gate, self._clock(), self._runtime)
            if transaction.run(self._run_id).state != "running":
                self._authority.stop()
            return outcome

    def reject(self, token: str, arguments_json: str, reason: str) -> None:
        with self._unit() as transaction:
            context = self._authority.context(token)
            validate_context(context, self._run(transaction, "running"), self._clock())
            payload: dict[str, str] = {
                "target": context.target.instance,
                "operation": context.target.operation,
                "arguments_json": arguments_json,
                "reason": reason,
            }
            transaction.event(self._run_id, "call.rejected", context.call_id, json.dumps(payload))

    def cancel(self, call_id: str) -> None:
        try:
            with self._unit() as transaction:
                if transaction.call(call_id).prepared.context.run_id != self._run_id:
                    raise AccessDenied("call_run_mismatch")
                transaction.cancel_call(call_id)
        finally:
            self._authority.revoke(call_id)

    def stop(self, reason: str) -> tuple[str, ...]:
        with self._lock:
            try:
                with self._store.begin() as transaction:
                    run = transaction.run(self._run_id)
                    if run.runtime_id != self._runtime:
                        raise AccessDenied("runtime_mismatch")
                    if run.state in ("created", "running") and self._clock() >= run.deadline:
                        reason = "run_deadline"
                    transaction.stop(self._run_id, reason)
            finally:
                cancelled = self._authority.stop()
            return cancelled

    @contextmanager
    def _unit(self) -> Iterator[RunTransaction]:
        with self._lock:
            try:
                with self._store.begin() as transaction:
                    yield transaction
            except RecordingError:
                self._authority.stop()
                raise

    def _run(self, transaction: RunTransaction, expected: str) -> RunRecord:
        run = transaction.run(self._run_id)
        if (
            run.runtime_id != self._runtime
            or run.state != expected
            or self._clock() >= run.deadline
        ):
            raise AccessDenied("run_closed")
        return run


def recover_runs(store: RunStore) -> tuple[str, ...]:
    with store.begin() as transaction:
        runs = transaction.unfinished()
        for run in runs:
            transaction.stop(run.run_id, "backend_interrupted", "interrupted")
        return tuple(run.run_id for run in runs)
