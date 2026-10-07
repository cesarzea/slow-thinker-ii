"""Activations from start to end: Trigger and Output inside the engine, package nodes via hosts."""

import asyncio
from contextlib import suppress

from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import PlanNode, RunPlan

from ._emitter import Emitter, oversized
from ._outcome import RunResult, failure_detail, time_limit_detail
from ._pipeline import Pipeline
from ._ports import CallFailure, Emission, RunLog
from ._state import Activation, Control, Delivery, RunState
from ._timing import Timing

_BUSY = CallFailure("node_busy", "The node is still running an earlier activation.")


class Activations:
    def __init__(
        self,
        plan: RunPlan,
        log: RunLog,
        state: RunState,
        control: Control,
        timing: Timing,
        pipeline: Pipeline,
    ) -> None:
        self._plan = plan
        self._log = log
        self._state = state
        self._control = control
        self._timing = timing
        self._pipeline = pipeline
        self._emitter = Emitter(plan, log, state)

    def trigger(self, message: JsonValue) -> None:
        """The run's first activation: the Trigger emits the input message on `out`."""
        activation = self._begin(self._plan.node(self._plan.trigger_id), None, message)
        self._settle(activation, (Emission("out", message),))

    def start(self, delivery: Delivery) -> None:
        node = self._plan.node(delivery.target[0])
        activation = self._begin(node, delivery.message_id, delivery.payload)
        if node.kind == "output":
            self._output(activation, delivery.message_id)
        elif node.stateful and self._state.busy(node.id):
            self._settle(activation, _BUSY)
        else:
            self._state.track(activation, asyncio.create_task(self._run(activation)))

    def _begin(self, node: PlanNode, message_id: str | None, message: JsonValue) -> Activation:
        activation = self._state.begin(node, message_id, message, self._timing.now())
        data: JsonObject = {"message_id": message_id, "number": activation.number}
        self._record(activation, "activation.started", data)
        return activation

    async def _run(self, activation: Activation) -> None:
        try:
            self._settle(activation, await self._pipeline.run(activation))
        except asyncio.CancelledError:
            self.cancelled(activation)
            raise
        except Exception as error:
            self._crash(activation, error)
        finally:
            self._state.untrack(activation)
            self._control.signal()

    def _settle(self, activation: Activation, outcome: tuple[Emission, ...] | CallFailure) -> None:
        """Completes or fails the activation, or records it cancelled once the run is ending."""
        timed_out = isinstance(outcome, CallFailure) and outcome.code == "timeout"
        if timed_out and self._timing.remaining() <= 0:
            limit = self._plan.limits.time_limit_seconds
            self._control.stop("time_limit", time_limit_detail(limit))
        if self._control.cause is not None:
            self.cancelled(activation)
        elif isinstance(outcome, CallFailure):
            self._fail(activation, outcome)
        else:
            self._complete(activation, outcome)

    def _complete(self, activation: Activation, emissions: tuple[Emission, ...]) -> None:
        failure = oversized(emissions)
        if failure is not None:
            self._fail(activation, failure)
            return
        emitted = self._emitter.emit(activation, emissions)
        duration = self._timing.elapsed_ms(activation.started)
        self._record(
            activation, "activation.completed", {"emitted": emitted, "duration_ms": duration}
        )

    def _output(self, activation: Activation, message_id: str) -> None:
        node = activation.node
        data: JsonObject = {
            "name": node.name,
            "message_id": message_id,
            "payload": activation.message,
        }
        self._record(activation, "run.result", data)
        self._state.results.append(RunResult(node.id, node.name, message_id, activation.message))
        self._record(activation, "activation.completed", {"emitted": [], "duration_ms": 0})

    def _fail(self, activation: Activation, failure: CallFailure) -> None:
        error: JsonObject = {"code": failure.code, "message": failure.message}
        duration = self._timing.elapsed_ms(activation.started)
        self._record(activation, "activation.failed", {"error": error, "duration_ms": duration})
        detail = failure_detail(activation.node.name, activation.number, failure.message)
        self._control.stop("activation_failed", detail)

    def _crash(self, activation: Activation, error: Exception) -> None:
        message = f"The activation failed unexpectedly: {type(error).__name__}: {error}"
        detail = failure_detail(activation.node.name, activation.number, message)
        self._control.stop("internal_error", detail)
        with suppress(Exception):
            failure: JsonObject = {"code": "internal_error", "message": message}
            duration = self._timing.elapsed_ms(activation.started)
            self._record(
                activation, "activation.failed", {"error": failure, "duration_ms": duration}
            )

    def cancelled(self, activation: Activation) -> None:
        cause = self._control.cause
        reason = "cancelled" if cause is None else cause.reason
        self._record(activation, "activation.cancelled", {"reason": reason})

    def _record(self, activation: Activation, kind: str, data: JsonObject) -> None:
        self._log.record(kind, data, node_id=activation.node.id, activation_id=activation.id)
