"""Locate configuration pointers inside a configuration schema."""

import re
from collections.abc import Iterator
from urllib.parse import unquote

from slow_thinker_ii.contracts import JsonObject, JsonValue, parse_pointer, value_at_pointer

_INDEX = re.compile(r"0|[1-9][0-9]*")
_MAX_REFERENCE_HOPS = 32


def local_target(root: JsonObject, reference: JsonValue) -> JsonValue:
    """The schema that a local `#...` reference designates in `root`, or None."""
    if not isinstance(reference, str) or not reference.startswith("#"):
        return None
    try:
        tokens = parse_pointer(unquote(reference[1:]))
    except ValueError:
        return None
    return value_at_pointer(root, tokens)


def views(root: JsonObject, schema: JsonValue) -> list[JsonObject]:
    """A schema object followed by the schema objects its local references lead to."""
    found: list[JsonObject] = []
    current = schema
    while isinstance(current, dict) and len(found) < _MAX_REFERENCE_HOPS:
        found.append(current)
        current = local_target(root, current.get("$ref"))
    return found


def schema_at(root: JsonObject, pointer: str) -> JsonValue:
    """The subschema describing the configuration value at `pointer`, or None.

    Pointers resolve through `properties`, `items` and local `$ref` only.
    """
    current: JsonValue = root
    for token in parse_pointer(pointer):
        current = _child(root, current, token)
    return current


def is_string_array(root: JsonObject, schema: JsonValue) -> bool:
    array_views = views(root, schema)
    if not any(view.get("type") == "array" for view in array_views):
        return False
    item_views = [item for view in array_views for item in views(root, view.get("items"))]
    return any(view.get("type") == "string" for view in item_views)


def references(value: JsonValue, location: tuple[str, ...] = ()) -> Iterator[tuple[str, ...]]:
    """The location of every `$ref` string inside a schema."""
    if isinstance(value, dict):
        if isinstance(value.get("$ref"), str):
            yield (*location, "$ref")
        for key, child in value.items():
            yield from references(child, (*location, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from references(child, (*location, str(index)))


def _child(root: JsonObject, schema: JsonValue, token: str) -> JsonValue:
    for view in views(root, schema):
        properties = view.get("properties")
        if isinstance(properties, dict) and token in properties:
            return properties[token]
        item_schema = view.get("items")
        if _INDEX.fullmatch(token) and isinstance(item_schema, dict | bool):
            return item_schema
    return None
