"""Scripted `engine.Hosts`: one behaviour per node, every call's context kept for assertions."""

import asyncio
from collections.abc import Awaitable, Callable, Mapping

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission

type Activate = Callable[[CallContext, JsonValue], Awaitable[tuple[Emission, ...] | CallFailure]]
type Select = Callable[[CallContext, JsonValue, JsonValue], Awaitable[Emission | CallFailure]]
type Recall = Callable[[CallContext, JsonValue], Awaitable[JsonValue | CallFailure]]


class ScriptedHosts:
    """Engine `Hosts` fake. `activate` and `select` map node ids to behaviours.

    `calls` lists each call's context in order; `peak` is the highest number of concurrent
    `activate` calls, for checks of `max_running_nodes`.
    """

    def __init__(
        self,
        activate: Mapping[str, Activate],
        select: Mapping[str, Select] | None = None,
        recall: Mapping[str, Recall] | None = None,
    ) -> None:
        self._activate = dict(activate)
        self._select = dict(select or {})
        self._recall = dict(recall or {})
        self.remembered: list[tuple[str, JsonValue, JsonValue]] = []
        self.forget: CallFailure | None = None
        self.calls: list[CallContext] = []
        self.running = 0
        self.peak = 0

    async def activate(
        self, context: CallContext, message: JsonValue
    ) -> tuple[Emission, ...] | CallFailure:
        self.calls.append(context)
        self.running += 1
        self.peak = max(self.peak, self.running)
        try:
            return await self._activate[context.node_id](context, message)
        finally:
            self.running -= 1

    async def select_output(
        self, context: CallContext, received: JsonValue, node_input: JsonValue
    ) -> Emission | CallFailure:
        self.calls.append(context)
        return await self._select[context.node_id](context, received, node_input)

    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure:
        """The node's memory: its `recall` behaviour, or the message with what it remembered."""
        self.calls.append(context)
        behaviour = self._recall.get(context.node_id)
        if behaviour is not None:
            return await behaviour(context, message)
        kept = [replied for node, _, replied in self.remembered if node == context.node_id]
        return {"remembered": kept, "message": message}

    async def remember(
        self, context: CallContext, received: JsonValue, replied: JsonValue
    ) -> None | CallFailure:
        self.calls.append(context)
        if self.forget is not None:
            return self.forget
        self.remembered.append((context.node_id, received, replied))
        return None


class Gate:
    """Holds behaviours until the test calls `open`."""

    def __init__(self) -> None:
        self._event = asyncio.Event()

    def open(self) -> None:
        self._event.set()

    async def wait(self) -> None:
        await self._event.wait()


def emit(*emissions: Emission, gate: Gate | None = None) -> Activate:
    """Emits the given emissions, after `gate` opens when one is given."""

    async def behaviour(_context: CallContext, _message: JsonValue) -> tuple[Emission, ...]:
        if gate is not None:
            await gate.wait()
        return emissions

    return behaviour


def echo(port: str = "out") -> Activate:
    """Emits the received message after yielding once, so that started calls overlap."""

    async def behaviour(_context: CallContext, message: JsonValue) -> tuple[Emission, ...]:
        await asyncio.sleep(0)
        return (Emission(port, message),)

    return behaviour


def scores(*values: int) -> Activate:
    """Emits `{"score": value}` on `out`, one value per activation, repeating the last one."""
    remaining = list(values)

    async def behaviour(_context: CallContext, _message: JsonValue) -> tuple[Emission, ...]:
        score = remaining.pop(0) if len(remaining) > 1 else remaining[0]
        return (Emission("out", {"score": score}),)

    return behaviour


def fail(code: str, message: str) -> Activate:
    async def behaviour(_context: CallContext, _message: JsonValue) -> CallFailure:
        return CallFailure(code, message)

    return behaviour


def hang() -> Activate:
    """Never answers; only cancellation or a timeout ends the call."""

    async def behaviour(_context: CallContext, _message: JsonValue) -> CallFailure:
        await asyncio.Event().wait()
        return CallFailure("unreachable", "Never returned.")

    return behaviour
