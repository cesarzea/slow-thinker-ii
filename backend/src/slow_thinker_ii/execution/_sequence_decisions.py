"""The finite profile checks controller decisions without making those decisions itself."""

from slow_thinker_ii.contracts import JsonObject


def require_sequence_decision(decision: JsonObject, expected: str | None) -> None:
    if set(decision) != {"action", "nodes"}:
        raise ValueError("Unsupported controller decision fields")
    action = "complete" if expected is None else "schedule"
    nodes = [] if expected is None else [expected]
    if decision["action"] != action or decision["nodes"] != nodes:
        raise ValueError("Controller decision violates the admitted finite sequence")
