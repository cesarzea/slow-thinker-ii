"""Narrow containers produced by the JSON decoder before field validation."""

from typing import TypeGuard


def json_object(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def json_array(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)
