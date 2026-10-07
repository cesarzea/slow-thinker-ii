"""Scripted embedded output components for `support.hosts.ScriptedHosts`."""

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission

from .hosts import Select


def route_by_score(high: str, low: str, threshold: int = 7) -> Select:
    """The journeys' Router script: `high` with the node input when the score reaches 7."""

    async def behaviour(
        _context: CallContext, received: JsonValue, node_input: JsonValue
    ) -> Emission:
        score = received.get("score") if isinstance(received, dict) else None
        high_enough = isinstance(score, int) and score >= threshold
        return Emission(high if high_enough else low, node_input)

    return behaviour


def select(result: Emission | CallFailure) -> Select:
    async def behaviour(
        _context: CallContext, _received: JsonValue, _input: JsonValue
    ) -> Emission | CallFailure:
        return result

    return behaviour
