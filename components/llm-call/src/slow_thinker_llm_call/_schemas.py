"""Publish the concrete input and success/failure schemas for one configured instance."""

from slow_thinker_host import JsonObject, Operation, json_object

from ._config import parse_config
from ._types import LLMCallConfig


def _object(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _failure_schema() -> JsonObject:
    issue = _object(
        {
            "path": {"type": "string", "pattern": r"^(?:/(?:[^~/]|~[01])*)*$"},
            "message": {"type": "string", "minLength": 1},
        }
    )
    error = _object(
        {
            "code": {
                "enum": ["invalid_json", "output_schema_mismatch", "output_validation_failed"]
            },
            "message": {"type": "string", "minLength": 1},
            "raw_output": {"type": "string"},
            "issues": {"type": "array", "minItems": 1, "items": issue},
        }
    )
    return _object({"status": {"const": "error"}, "error": error})


def effective_operation(config: LLMCallConfig) -> Operation:
    settings = parse_config(config)
    output = settings["output"]
    value: JsonObject = {"type": "string"} if output["format"] == "text" else output["schema"]
    value.setdefault("$id", "urn:slow-thinker-ii:llm-output")
    success = _object(
        {"status": {"const": "ok"}, "format": {"const": output["format"]}, "value": value}
    )
    return Operation(
        "generate",
        json_object(settings["input_schema"]),
        {"type": "object", "oneOf": [success, _failure_schema()]},
    )
