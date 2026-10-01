"""Public packaged selector for the bounded-review example; performs no external work."""

from slow_thinker_host import JsonValue


def choose(value: JsonValue) -> str:
    """Select a route from a validated ordinary LLMCall review."""
    if not isinstance(value, dict) or not isinstance(value.get("accepted"), bool):
        raise ValueError("A validated review with accepted is required")
    return "accept" if value["accepted"] else "revise"
