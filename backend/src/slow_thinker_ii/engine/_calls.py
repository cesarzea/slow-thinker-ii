"""Host calls of an activation: a grant per call, its time budget and `component.called`."""

import asyncio
from collections.abc import Awaitable, Callable

from slow_thinker_ii.access import Caller
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import PlanComponent

from ._call_values import (
    CallRecord,
    bounded,
    emitted,
    identity,
    recalled,
    remembered,
    selected,
    unexpected,
)
from ._ports import CallContext, CallFailure, Emission, GrantIssuer, Hosts, Position, RunLog
from ._state import Activation
from ._timing import Timing

type Outcome = JsonObject | CallFailure  # a call's recorded result or error
_CANCELLED = CallFailure("cancelled", "The call was cancelled because the run is ending.")
_NO_TIME = CallFailure("timeout", "The activation has no time left to call its component.")


class ComponentCalls:
    def __init__(
        self, run_id: str, hosts: Hosts, log: RunLog, grants: GrantIssuer, timing: Timing
    ) -> None:
        self._run_id = run_id
        self._hosts = hosts
        self._log = log
        self._grants = grants
        self._timing = timing

    async def activate(
        self, activation: Activation, message: JsonValue
    ) -> tuple[Emission, ...] | CallFailure:
        """Calls the host with the message it receives: the activation's, or with memory."""
        host = activation.node.host

        def invoke(context: CallContext) -> Awaitable[tuple[Emission, ...] | CallFailure]:
            return self._hosts.activate(context, message)

        return await self._call(activation, host, "node", {"message": message}, invoke, emitted)

    async def select_output(
        self, activation: Activation, component: PlanComponent, received: JsonValue
    ) -> Emission | CallFailure:
        node_input = activation.message
        arguments: JsonObject = {"received": received, "node_input": node_input}

        def invoke(context: CallContext) -> Awaitable[Emission | CallFailure]:
            return self._hosts.select_output(context, received, node_input)

        return await self._call(activation, component, "output", arguments, invoke, selected)

    async def recall(
        self, activation: Activation, component: PlanComponent
    ) -> JsonValue | CallFailure:
        """What the node receives from its memory instead of the activation's message."""
        message = activation.message

        def invoke(context: CallContext) -> Awaitable[JsonValue | CallFailure]:
            return self._hosts.recall(context, message)

        arguments: JsonObject = {"message": message}
        return await self._call(
            activation, component, "memory", arguments, invoke, recalled, "recall"
        )

    async def remember(
        self, activation: Activation, component: PlanComponent, replied: JsonValue
    ) -> None | CallFailure:
        """Gives the node's memory the received message and one of the node's replies."""
        received = activation.message

        def invoke(context: CallContext) -> Awaitable[None | CallFailure]:
            return self._hosts.remember(context, received, replied)

        arguments: JsonObject = {"received": received, "replied": replied}
        return await self._call(
            activation, component, "memory", arguments, invoke, remembered, "remember"
        )

    async def _call[T](
        self,
        activation: Activation,
        component: PlanComponent,
        position: Position,
        arguments: JsonObject,
        invoke: Callable[[CallContext], Awaitable[T | CallFailure]],
        document: Callable[[T], JsonObject],
        operation: str | None = None,
    ) -> T | CallFailure:
        budget = self._timing.budget(activation)
        if budget.milliseconds < 1:
            return _NO_TIME
        caller = Caller(self._run_id, activation.node.id, position, activation.id)
        token = self._grants.issue(caller, budget.milliseconds / 1000)
        context = CallContext(*identity(caller), token, budget.milliseconds)
        named = operation or ("activate" if position == "node" else "select_output")
        record = CallRecord(activation, component, position, named, arguments, self._timing.now())
        try:
            result = await bounded(invoke(context), budget)
        except asyncio.CancelledError:
            self._record(record, _CANCELLED)
            raise
        except Exception as error:
            self._record(record, CallFailure("internal_error", unexpected(error)))
            raise
        finally:
            self._grants.revoke(token)
        self._record(record, result if isinstance(result, CallFailure) else document(result))
        return result

    def _record(self, record: CallRecord, outcome: Outcome) -> None:
        data: JsonObject = {
            "position": record.position,
            "component": str(record.component.declaration.ref),
            "operation": record.operation,
            "arguments": record.arguments,
        }
        if isinstance(outcome, CallFailure):
            data["error"] = {"code": outcome.code, "message": outcome.message}
        else:
            data["result"] = outcome
        data["duration_ms"] = self._timing.elapsed_ms(record.started)
        activation = record.activation
        self._log.record(
            "component.called", data, node_id=activation.node.id, activation_id=activation.id
        )
