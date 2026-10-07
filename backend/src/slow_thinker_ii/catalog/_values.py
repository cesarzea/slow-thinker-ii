"""Total projections of JSON values whose shape a JSON Schema has already checked."""

from slow_thinker_ii.contracts import JsonObject, JsonValue


def member(value: JsonValue, key: str) -> JsonValue:
    return value.get(key) if isinstance(value, dict) else None


def items(value: JsonValue) -> list[JsonValue]:
    return value if isinstance(value, list) else []


def text(value: JsonValue) -> str:
    return value if isinstance(value, str) else ""


def mapping(value: JsonValue) -> JsonObject:
    return value if isinstance(value, dict) else {}
