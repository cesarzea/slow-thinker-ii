"""Effective operation schemas advertise the reviewed common request boundary."""

from slow_thinker_host import JsonObject, JsonValue, Operation

from ._config import ModelProviderConfig
from ._requests import COMMON, OPENAI, message_roles


def object_schema(properties: JsonObject, required: list[JsonValue]) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def request_schema(config: ModelProviderConfig) -> JsonObject:
    message = object_schema(
        {
            "role": {"enum": list(message_roles(config))},
            "content": {"type": "string"},
        },
        ["role", "content"],
    )
    fields: JsonObject = {
        "model": {"const": config.model_alias},
        "messages": {"type": "array", "minItems": 1, "items": message},
        "max_completion_tokens": {
            "type": "integer",
            "minimum": 1,
            "maximum": config.maximum_output_tokens,
        },
        "reasoning_effort": {"enum": list(config.reasoning_efforts)},
    }
    for name, value in {**COMMON, **(OPENAI if config.provider == "openai" else {})}.items():
        fields[name] = {"const": value}
    if config.provider == "deepseek":
        fields["temperature"] = {"type": "number", "minimum": 0, "maximum": 2}
    return object_schema({"request": generation_schema(config, fields)}, ["request"])


def generation_schema(config: ModelProviderConfig, fields: JsonObject) -> JsonObject:
    request = object_schema(fields, ["model", "messages"])
    if config.provider == "deepseek":
        request["dependentSchemas"] = {
            "temperature": {"properties": {"reasoning_effort": {"const": "none"}}}
        }
    return request


def effective_operation(config: ModelProviderConfig) -> Operation:
    request = request_schema(config)
    return Operation(
        "complete",
        request,
        {
            "type": "object",
            "oneOf": [
                {"required": ["response"], "properties": {"response": {"type": "object"}}},
                {"required": ["error"], "properties": {"error": {"type": "object"}}},
            ],
        },
    )
