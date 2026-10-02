"""Memory request bounds and explicit conditional-write semantics."""

from typing import Literal

from slow_thinker_host import JsonObject, JsonValue, encode_json, json_value

type Precondition = int | None | Literal["any"]


def bounded_integer(value: JsonValue, maximum: int) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError("Memory limit requires a bounded positive integer")
    return value


def key(value: JsonValue) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 256:
        raise ValueError("Memory key requires one to 256 UTF-8 bytes")
    return value


def request(arguments: JsonObject, required: set[str], optional: set[str]) -> JsonObject:
    if not required <= set(arguments) or set(arguments) - required - optional:
        raise ValueError("Unsupported memory request fields")
    return arguments


def precondition(arguments: JsonObject) -> Precondition:
    if "expected_version" not in arguments:
        return "any"
    value = arguments["expected_version"]
    if value is None:
        return None
    if type(value) is not int or value <= 0:
        raise ValueError("Expected memory version must be null or a positive integer")
    return value


def value_text(value: JsonValue, maximum: int) -> str:
    text = encode_json(json_value(value))
    if len(text.encode("utf-8")) > maximum:
        raise ValueError("Memory value exceeds its UTF-8 byte bound")
    return text


def check_version(expected: Precondition, version: int | None) -> None:
    if expected != "any" and expected != version:
        raise ValueError("memory_version_conflict")
