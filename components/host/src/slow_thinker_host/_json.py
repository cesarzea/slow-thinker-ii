"""Finite JSON boundary values, with duplicate-key rejection and canonical encoding."""

import json
import math
from typing import TypeGuard

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


def _list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _dictionary(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def json_value(value: object) -> JsonValue:
    if value is None or isinstance(value, str | bool | int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if _list(value):
        return [json_value(item) for item in value]
    if _dictionary(value) and all(isinstance(key, str) for key in value):
        return {str(key): json_value(item) for key, item in value.items()}
    raise ValueError("Expected a finite JSON value")


def json_object(value: object) -> JsonObject:
    result = json_value(value)
    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object")
    return result


def _unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON property")
        result[key] = value
    return result


def decode_json(value: str) -> JsonValue:
    raw: object = json.loads(value, object_pairs_hook=_unique)
    return json_value(raw)


def encode_json(value: JsonValue) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
