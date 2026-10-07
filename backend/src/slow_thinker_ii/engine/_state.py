"""Mutable state of one run: identifiers, the delivery queue, running activations and the cause."""

import asyncio
from collections import deque
from dataclasses import dataclass

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.graphs import PlanNode

from ._outcome import RunResult, StopCause, StopReason

type Port = tuple[str, str]


@dataclass(frozen=True)
class Delivery:
    message_id: str
    source: Port
    target: Port
    payload: JsonValue


@dataclass(frozen=True)
class Activation:
    id: str
    node: PlanNode
    number: int  # the node's 1-based activation count
    message_id: str | None  # None for the Trigger
    message: JsonValue
    started: float  # monotonic seconds


class RunState:
    """Deliveries waiting in FIFO order, running activations and the run's counters."""

    def __init__(self) -> None:
        self.queue: deque[Delivery] = deque()
        self.results: list[RunResult] = []
        self.started = 0
        self.sent = 0
        self._numbers: dict[str, int] = {}
        self._running: dict[str, tuple[Activation, asyncio.Task[None]]] = {}

    def begin(
        self, node: PlanNode, message_id: str | None, message: JsonValue, at: float
    ) -> Activation:
        self.started += 1
        number = self._numbers.get(node.id, 0) + 1
        self._numbers[node.id] = number
        return Activation(f"a{self.started}", node, number, message_id, message, at)

    def next_message_id(self) -> str:
        self.sent += 1
        return f"m{self.sent}"

    def track(self, activation: Activation, task: asyncio.Task[None]) -> None:
        self._running[activation.id] = (activation, task)

    def untrack(self, activation: Activation) -> None:
        self._running.pop(activation.id, None)

    def busy(self, node_id: str) -> bool:
        return any(activation.node.id == node_id for activation, _ in self._running.values())

    def running(self) -> int:
        return len(self._running)

    def tasks(self) -> list[asyncio.Task[None]]:
        return [task for _, task in self._running.values()]

    def tracked(self) -> list[Activation]:
        """Running activations; after cancellation, those whose task never started."""
        return [activation for activation, _ in self._running.values()]

    def idle(self) -> bool:
        return not self.queue and not self._running


class Control:
    """The first stop cause and the wake-up signal of the scheduling loop."""

    def __init__(self) -> None:
        self.cause: StopCause | None = None
        self.finished = False
        self._wake = asyncio.Event()

    def stop(self, reason: StopReason, detail: str) -> None:
        if self.cause is None and not self.finished:
            self.cause = StopCause(reason, detail)
        self._wake.set()

    def signal(self) -> None:
        self._wake.set()

    async def wait(self, timeout: float) -> bool:
        """Waits for a signal; False when `timeout` seconds pass first."""
        self._wake.clear()
        try:
            await asyncio.wait_for(self._wake.wait(), timeout)
        except TimeoutError:
            return False
        return True
