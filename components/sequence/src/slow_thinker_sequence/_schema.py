"""The installed controller publishes its own protocol-independent operation contract."""

from slow_thinker_host import JsonObject, Operation


def object_schema(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def sequence_operation() -> Operation:
    node: JsonObject = {"type": "string", "pattern": "^[a-z][a-z0-9_.-]*$"}
    request = object_schema(
        {"completed_nodes": {"type": "array", "items": node, "uniqueItems": True}}
    )
    scheduled = object_schema(
        {
            "action": {"const": "schedule"},
            "nodes": {"type": "array", "items": node, "minItems": 1, "maxItems": 1},
        }
    )
    completed = object_schema(
        {"action": {"const": "complete"}, "nodes": {"type": "array", "maxItems": 0}}
    )
    return Operation("next", request, {"type": "object", "oneOf": [scheduled, completed]})
