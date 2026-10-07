"""The values of host calls: their record, time bound, caller identity and result documents."""

import asyncio
from collections.abc import Awaitable
from dataclasses import dataclass

from slow_thinker_ii.access import Caller
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import PlanComponent

from ._ports import CallFailure, Emission, Position
from ._state import Activation
from ._timing import CallBudget


@dataclass(frozen=True)
class CallRecord:
    activation: Activation
    component: PlanComponent
    position: Position
    operation: str
    arguments: JsonObject
    started: float


async def bounded[T](call: Awaitable[T | CallFailure], budget: CallBudget) -> T | CallFailure:
    if budget.timeout is None:
        return await call
    try:
        return await asyncio.wait_for(call, budget.timeout)
    except TimeoutError:
        return CallFailure(
            "timeout", f"The component did not answer within {budget.milliseconds} ms."
        )


def identity(caller: Caller) -> tuple[str, str, Position, str]:
    return caller.run_id, caller.node_id, caller.position, caller.activation_id


def unexpected(error: Exception) -> str:
    return f"The call failed unexpectedly: {type(error).__name__}: {error}"


def emitted(emissions: tuple[Emission, ...]) -> JsonObject:
    return {"emissions": [selected(emission) for emission in emissions]}


def selected(emission: Emission) -> JsonObject:
    return {"port": emission.port, "payload": emission.payload}


def recalled(message: JsonValue) -> JsonObject:
    return {"message": message}


def remembered(_: None) -> JsonObject:
    return {}
