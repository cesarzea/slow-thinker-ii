"""The LLM service for components: grant, request, model, parameters, budgets, provider, record."""

import uuid
from collections.abc import Iterable

from ._active import ActiveCall
from ._admission import Admitted, CallAdmission, rejected
from ._budgets import budget_label, display_usd
from ._call_record import CallRecord, error_body
from ._ports import Clock, Ledger, LlmProvider
from ._provider_calls import provider_reply, unanswered
from ._runs import RunService
from ._spending import CallSpending
from ._values import BudgetLimits, GatewayReply, LlmModel

UNANSWERED = "The call was cancelled before the provider answered."


class LlmGateway:
    def __init__(
        self,
        *,
        runs: RunService,
        ledger: Ledger,
        provider: LlmProvider,
        models: Iterable[LlmModel],
        budgets: BudgetLimits,
        clock: Clock,
    ) -> None:
        self._runs = runs
        self._provider = provider
        self._clock = clock
        self._admission = CallAdmission(models)
        self._spending = CallSpending(ledger, budgets, clock)

    async def complete(self, grant: str, body: str) -> GatewayReply:
        """Answers one `POST /v1/chat/completions` per the LLM service contract.

        Every call whose grant resolves is recorded as `llm.called`, rejections included.
        """
        call = self._runs.active_call(grant)
        if call is None:
            message = "The grant is missing, unknown or expired."
            return GatewayReply(401, error_body(401, "invalid_grant", message))
        record = CallRecord(uuid.uuid4().hex, self._clock.monotonic())
        admitted = self._admission.admit(call, body, record)
        if isinstance(admitted, GatewayReply):
            return self._record(call, record, admitted)
        call.run.begin_call()
        try:
            return await self._dispatch(call, admitted, record)
        finally:
            call.run.end_call()

    async def _dispatch(
        self, call: ActiveCall, admitted: Admitted, record: CallRecord
    ) -> GatewayReply:
        exhausted = self._spending.reserve(call, admitted, record)
        if exhausted is not None:
            message = (
                f"The {budget_label(exhausted.kind)} budget of {display_usd(exhausted.limit)} "
                f"USD cannot cover this call's reservation of {display_usd(admitted.bound)} USD."
            )
            denied = self._record(call, record, rejected(402, "budget_exhausted", message))
            self._runs.stop_for_budget(call.caller.run_id, exhausted)
            return denied
        reply = unanswered(self._clock.now(), UNANSWERED)
        try:
            model, request = admitted.model, admitted.request
            reply = await provider_reply(self._provider, call, model, request, self._clock)
        finally:  # also when the caller's request is cancelled: settle and record, then re-raise
            self._spending.settle(admitted, record, reply)
            result = self._record(call, record, GatewayReply(reply.status, reply.body))
        exceeded = self._spending.exceeded(record)
        if exceeded is not None:
            self._runs.stop_for_budget(call.caller.run_id, exceeded)
        return result

    def _record(self, call: ActiveCall, record: CallRecord, reply: GatewayReply) -> GatewayReply:
        duration = max(0, int((self._clock.monotonic() - record.started) * 1000))
        data = record.data(reply.status, reply.body, duration)
        caller = call.caller
        call.run.journal.record(
            "llm.called", data, node_id=caller.node_id, activation_id=caller.activation_id
        )
        return reply
