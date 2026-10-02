"""Nonbillable memory configuration and bounded operation descriptions."""

from slow_thinker_host import JsonObject, Operation, json_object

CONFIG_SCHEMA: JsonObject = {
    "type": "object",
    "properties": {
        "namespace": {"type": "string", "minLength": 1, "maxLength": 256},
        "retention": {"enum": ["run", "persistent"], "default": "run"},
        "max_entries": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 1000},
        "max_value_bytes": {"type": "integer", "minimum": 1, "maximum": 65536, "default": 65536},
    },
    "required": ["namespace"],
    "additionalProperties": False,
}
_KEY: JsonObject = {"type": "string", "minLength": 1, "maxLength": 256}
_VERSION: JsonObject = {"type": ["integer", "null"], "minimum": 1}


def object_schema(properties: JsonObject, required: list[str]) -> JsonObject:
    return json_object(
        {
            "type": "object",
            "properties": properties,
            "required": list(required),
            "additionalProperties": False,
        }
    )


def value_operations() -> tuple[Operation, ...]:
    return (
        Operation(
            "get",
            object_schema({"key": _KEY}, ["key"]),
            object_schema(
                {
                    "found": {"type": "boolean"},
                    "value": {},
                    "version": _VERSION,
                },
                ["found", "value", "version"],
            ),
        ),
        Operation(
            "put",
            object_schema(
                {"key": _KEY, "value": {}, "expected_version": _VERSION}, ["key", "value"]
            ),
            object_schema({"version": {"type": "integer", "minimum": 1}}, ["version"]),
        ),
        Operation(
            "delete",
            object_schema({"key": _KEY, "expected_version": _VERSION}, ["key"]),
            object_schema({"deleted": {"type": "boolean"}}, ["deleted"]),
        ),
    )


def operations() -> tuple[Operation, ...]:
    incoming = object_schema(
        {
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 100},
            "after": _KEY,
        },
        [],
    )
    outgoing = object_schema(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": object_schema(
                    {
                        "key": _KEY,
                        "version": {"type": "integer", "minimum": 1},
                    },
                    ["key", "version"],
                ),
            },
            "next_key": {"type": ["string", "null"]},
        },
        ["items", "next_key"],
    )
    return (*value_operations(), Operation("list", incoming, outgoing))
