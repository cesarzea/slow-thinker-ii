"""Validate one bounded controller decision against independently determined progress."""

from slow_thinker_ii.contracts import JsonObject


class ActivationLimitReached(ValueError):
    """The valid conditional history needs more activations than its declared bound."""


def require_conditional_decision(
    value: JsonObject, expected: str | None, completed: int, maximum: int
) -> None:
    if expected is None:
        valid = value == {"action": "complete"}
    elif completed >= maximum:
        valid = value == {"action": "exhausted", "reason": "activation_limit_reached"}
        if valid:
            raise ActivationLimitReached("activation_limit_reached")
    else:
        valid = value == {"action": "activate", "nodes": [expected]}
    if not valid:
        raise ValueError("Controller decision does not match the bounded transition history")
