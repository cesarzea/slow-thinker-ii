"""Validate the JSON fields consumed by verification."""

import json
from pathlib import Path

from tooling.quality.json_shapes import json_array, json_object

from ._types import CodeQLFailure


def object_value(value: object, context: str) -> dict[str, object]:
    if not json_object(value):
        raise CodeQLFailure(f"{context} must be an object")
    return value


def array_value(value: object, context: str) -> list[object]:
    if not json_array(value):
        raise CodeQLFailure(f"{context} must be an array")
    return value


def text_value(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise CodeQLFailure(f"{context} must be a nonempty string")
    return value


def index_value(value: object, size: int, context: str) -> int:
    if type(value) is not int or not 0 <= value < size:
        raise CodeQLFailure(f"{context} must reference an existing entry")
    return value


def read_object(path: Path) -> dict[str, object]:
    try:
        value: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise CodeQLFailure(f"Cannot read JSON evidence {path}: {error}") from error
    return object_value(value, str(path))


def objects(value: object, context: str) -> list[dict[str, object]]:
    return [object_value(item, context) for item in array_value(value, context)]
