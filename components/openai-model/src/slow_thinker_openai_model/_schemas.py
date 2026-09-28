"""Native request subset and lossless parsed response envelopes advertised through MCP."""

from slow_thinker_host import JsonObject, JsonValue, Operation, json_object, validate_value

from ._config import ModelConfig

FIXED: tuple[tuple[str, JsonValue], ...] = (
    ("reasoning_effort", "none"),
    ("stream", False),
    ("n", 1),
    ("store", False),
    ("service_tier", "default"),
)


def object_schema(properties: JsonObject, required: list[JsonValue]) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def fixed_fields() -> JsonObject:
    return {
        key: {
            "const": value,
            "type": "boolean"
            if isinstance(value, bool)
            else "integer"
            if isinstance(value, int)
            else "string",
        }
        for key, value in FIXED
    }


def request_schema(config: ModelConfig) -> JsonObject:
    message = object_schema(
        {
            "role": {"enum": ["system", "developer", "user", "assistant"]},
            "content": {"type": "string"},
        },
        ["role", "content"],
    )
    fields = fixed_fields()
    fields.update(
        {
            "model": {"const": config.model_alias},
            "messages": {"type": "array", "minItems": 1, "items": message},
            "max_completion_tokens": {
                "type": "integer",
                "minimum": 1,
                "maximum": config.maximum_output_tokens,
            },
        }
    )
    return object_schema(fields, ["model", "messages"])


def effective_operation(config: ModelConfig) -> Operation:
    success = object_schema(
        {
            "response": {"type": "object"},
            "request_id": {"type": ["string", "null"]},
            "redacted": {"type": "boolean"},
        },
        ["response"],
    )
    failure = object_schema(
        {"error": {"type": "object"}, "redacted": {"type": "boolean"}}, ["error"]
    )
    return Operation(
        "complete",
        object_schema({"request": request_schema(config)}, ["request"]),
        {"oneOf": [success, failure]},
    )


def native_request(config: ModelConfig, arguments: JsonObject) -> JsonObject:
    validate_value(arguments, effective_operation(config).input_schema)
    request = json_object(arguments["request"])
    if type(request.get("max_completion_tokens", config.default_output_tokens)) is not int:
        raise ValueError("Output token cap must be an integer")
    for key, value in FIXED:
        if key in request and type(request[key]) is not type(value):
            raise ValueError("Invalid fixed generation setting type")
    return {
        **dict(FIXED),
        **request,
        "model": config.model,
        "max_completion_tokens": request.get("max_completion_tokens", config.default_output_tokens),
    }
