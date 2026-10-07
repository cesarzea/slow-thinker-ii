"""The run engine: FIFO deliveries within the plan's limits until completion or the first stop."""

import asyncio
from contextlib import suppress

from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import RunPlan

from ._activations import Activations
from ._calls import ComponentCalls
from ._emitter import endpoint
from ._outcome import RunOutcome, StopReason, status_of, time_limit_detail
from ._pipeline import Pipeline
from ._ports import Clock, GrantIssuer, Hosts, RunLog
from ._state import Control, Delivery, RunState
from ._timing import Timing


class RunEngine:
    """Executes one run of a plan; `run` never raises and `stop` keeps the first cause."""

    def __init__(
        self,
        run_id: str,
        plan: RunPlan,
        hosts: Hosts,
        log: RunLog,
        grants: GrantIssuer,
        clock: Clock,
        *,
        max_activation_seconds: int = 300,
    ) -> None:
        self._plan = plan
        self._log = log
        self._state = RunState()
        self._control = Control()
        self._timing = Timing(clock, max_activation_seconds)
        calls = ComponentCalls(run_id, hosts, log, grants, self._timing)
        pipeline = Pipeline(calls)
        self._activations = Activations(
            plan, log, self._state, self._control, self._timing, pipeline
        )

    async def run(self, input_message: JsonValue) -> RunOutcome:
        try:
            if self._control.cause is None:
                await self._schedule(input_message)
        except Exception as error:
            self.stop("internal_error", f"The run failed unexpectedly: {_describe(error)}")
        finally:
            await self._terminate()
        return self._outcome()

    def stop(self, reason: StopReason, detail: str) -> None:
        """Requests the end of the run; call it from the event loop. The first cause wins."""
        self._control.stop(reason, detail)

    async def _schedule(self, input_message: JsonValue) -> None:
        self._log.record("run.running", {})
        self._timing.start(self._plan.limits.time_limit_seconds)
        self._activations.trigger(input_message)
        while self._control.cause is None:
            self._dispatch()
            if self._control.cause is not None or self._state.idle():
                return
            await self._wait()

    def _dispatch(self) -> None:
        limits = self._plan.limits
        queue = self._state.queue
        while queue and self._state.running() < limits.max_running_nodes:
            if self._state.started >= limits.max_activations:
                name = self._plan.node(queue[0].target[0]).name
                detail = (
                    f"The run reached its limit of {limits.max_activations} activations "
                    f"before {name} could start."
                )
                self.stop("activation_limit", detail)
                return
            self._activations.start(queue.popleft())
            if self._control.cause is not None:
                return

    async def _wait(self) -> None:
        remaining = self._timing.remaining()
        if remaining > 0 and await self._control.wait(remaining):
            return
        self.stop("time_limit", time_limit_detail(self._plan.limits.time_limit_seconds))

    async def _terminate(self) -> None:
        """Cancels running activations and records pending deliveries as dropped."""
        tasks = self._state.tasks()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._control.finished = True
        with suppress(Exception):
            for activation in self._state.tracked():  # cancelled before their first step
                self._activations.cancelled(activation)
            while self._state.queue:
                self._dropped(self._state.queue.popleft())

    def _dropped(self, delivery: Delivery) -> None:
        data: JsonObject = {
            "message_id": delivery.message_id,
            "to": endpoint(delivery.target),
            "reason": "run_ending",
        }
        self._log.record("message.dropped", data, node_id=delivery.target[0])

    def _outcome(self) -> RunOutcome:
        cause = self._control.cause
        reason = None if cause is None else cause.reason
        return RunOutcome(
            status=status_of(reason),
            reason=reason,
            detail="" if cause is None else cause.detail,
            results=tuple(self._state.results),
            activations=self._state.started,
            messages=self._state.sent,
        )


def _describe(error: Exception) -> str:
    return f"{type(error).__name__}: {error}"
