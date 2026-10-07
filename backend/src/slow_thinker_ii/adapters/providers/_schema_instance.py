"""The smallest deterministic instance of a JSON Schema, which the simulated provider answers."""

import math

from slow_thinker_ii.contracts import JsonObject, JsonValue


def smallest_instance(schema: JsonValue) -> JsonValue:
    """The first `enum` value, the `const` value, or the smallest value of the schema's type.

    The type is the first non-null one of a list and `object` when absent. Objects have only
    their required properties; integers and numbers are at `maximum`, else `minimum`, else 0;
    strings are `"simulated"`, booleans `true`, arrays empty and `null` stays `null`.
    """
    if not isinstance(schema, dict):
        return {}
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]
    if "const" in schema:
        return schema["const"]
    return _typed(schema, _type(schema.get("type")))


def _type(value: JsonValue) -> str:
    if isinstance(value, list):
        named = [item for item in value if isinstance(item, str)]
        value = next((item for item in named if item != "null"), next(iter(named), None))
    return value if isinstance(value, str) else "object"


def _typed(schema: JsonObject, kind: str) -> JsonValue:
    if kind == "object":
        return _object(schema)
    if kind in ("integer", "number"):
        return _number(schema, integral=kind == "integer")
    if kind == "string":
        return "simulated"
    if kind == "boolean":
        return True
    return [] if kind == "array" else None


def _object(schema: JsonObject) -> JsonObject:
    required, properties = schema.get("required"), schema.get("properties")
    members: JsonObject = properties if isinstance(properties, dict) else {}
    names = (
        [name for name in required if isinstance(name, str)] if isinstance(required, list) else []
    )
    return {name: smallest_instance(members.get(name, {})) for name in names}


def _number(schema: JsonObject, *, integral: bool) -> JsonValue:
    """`maximum` if present, else `minimum`, else 0; an integer bound rounds inwards."""
    for key, inwards in (("maximum", math.floor), ("minimum", math.ceil)):
        bound = schema.get(key)
        if isinstance(bound, int | float) and not isinstance(bound, bool):
            return inwards(bound) if integral else bound
    return 0
