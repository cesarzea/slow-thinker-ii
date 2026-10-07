"""Ports of the engine: component hosts, the run log, the clock and invocation grants."""

from dataclasses import dataclass, field
from typing import Literal, Protocol

from slow_thinker_ii.access import Caller
from slow_thinker_ii.contracts import JsonObject, JsonValue

Position = Literal["node", "output", "memory"]


@dataclass(frozen=True)
class Emission:
    """A payload emitted on a port, by a host or selected by an embedded output component."""

    port: str
    payload: JsonValue


@dataclass(frozen=True)
class CallFailure:
    """A failed host operation; `code` matches ^[a-z][a-z0-9_]{0,63}$, `message` is English."""

    code: str
    message: str


@dataclass(frozen=True)
class CallContext:
    """What a host call needs besides its arguments; the grant is valid for this call only."""

    run_id: str
    node_id: str
    position: Position
    activation_id: str
    grant: str = field(repr=False)
    budget_ms: int  # time remaining for this call, relative to its start


class Hosts(Protocol):
    """Component hosts of one run, implemented by `adapters.hosts` for package nodes."""

    async def activate(
        self, context: CallContext, message: JsonValue
    ) -> tuple[Emission, ...] | CallFailure: ...

    async def select_output(
        self, context: CallContext, received: JsonValue, node_input: JsonValue
    ) -> Emission | CallFailure: ...

    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure:
        """What the node receives instead of `message`, from its memory."""
        ...

    async def remember(
        self, context: CallContext, received: JsonValue, replied: JsonValue
    ) -> None | CallFailure: ...


class RunLog(Protocol):
    """Appends observed events to the run's event log; implemented by the application."""

    def record(
        self,
        kind: str,
        data: JsonObject,
        *,
        node_id: str | None = None,
        activation_id: str | None = None,
    ) -> None: ...


class Clock(Protocol):
    def monotonic(self) -> float: ...


class GrantIssuer(Protocol):
    """Satisfied by `slow_thinker_ii.access.Grants`; one grant per host call."""

    def issue(self, caller: Caller, ttl_seconds: float) -> str: ...

    def revoke(self, token: str) -> None: ...
