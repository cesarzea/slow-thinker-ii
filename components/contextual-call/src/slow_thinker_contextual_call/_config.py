"""Freeze reviewed resource-composition settings without business calls."""

import re
from dataclasses import dataclass

from slow_thinker_host import JsonObject, check_schema, encode_json, json_object, validate_value

CONFIG_SCHEMA: JsonObject = {
    "type": "object",
    "properties": {
        "input_schema": {"type": "object"},
        "worker_operation": {"type": "string", "minLength": 1},
        "worker_output_schema": {"type": "object"},
        "calculation_enabled": {"type": "boolean", "default": False},
        "expression_pointer": {
            "type": "string",
            "default": "/expression",
            "pattern": r"^(?:/(?:[^~/]|~[01])*)*$",
        },
        "calculation_field": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256,
            "default": "calculation",
        },
        "memory_read": {"type": "boolean", "default": False},
        "memory_write": {"type": "boolean", "default": False},
        "memory_key": {"type": "string", "minLength": 1, "maxLength": 256, "default": "context"},
        "memory_field": {"type": "string", "minLength": 1, "maxLength": 256, "default": "memory"},
        "result_pointer": {"type": "string", "default": "", "pattern": r"^(?:/(?:[^~/]|~[01])*)*$"},
    },
    "required": ["input_schema", "worker_operation", "worker_output_schema"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Settings:
    input_schema: str
    worker_operation: str
    output_schema: str
    calculation_enabled: bool
    expression_pointer: str
    calculation_field: str
    memory_read: bool
    memory_write: bool
    memory_key: str
    memory_field: str
    result_pointer: str


def text(config: JsonObject, name: str, default: str) -> str:
    value = config.get(name, default)
    if not isinstance(value, str):
        raise ValueError("Composition text settings require strings")
    if name.endswith("pointer") and not re.fullmatch(r"(?:/(?:[^~/]|~[01])*)*", value):
        raise ValueError("Composition extraction requires a JSON Pointer")
    return value


def flag(config: JsonObject, name: str) -> bool:
    value = config.get(name, False)
    if type(value) is not bool:
        raise ValueError("Composition flags require booleans")
    return value


def schema(config: JsonObject, name: str) -> str:
    value = json_object(config[name])
    if value.get("type") != "object":
        raise ValueError("Composition input and worker output require object schemas")
    check_schema(value)
    return encode_json(value)


def settings(config: JsonObject) -> Settings:
    validate_value(config, CONFIG_SCHEMA)
    result = Settings(
        schema(config, "input_schema"),
        text(config, "worker_operation", ""),
        schema(config, "worker_output_schema"),
        flag(config, "calculation_enabled"),
        text(config, "expression_pointer", "/expression"),
        text(config, "calculation_field", "calculation"),
        flag(config, "memory_read"),
        flag(config, "memory_write"),
        text(config, "memory_key", "context"),
        text(config, "memory_field", "memory"),
        text(config, "result_pointer", ""),
    )
    if (
        result.calculation_enabled
        and result.memory_read
        and result.calculation_field == result.memory_field
    ):
        raise ValueError("Calculation and memory context fields must be distinct")
    if len(result.memory_key.encode("utf-8")) > 256:
        raise ValueError("Memory key exceeds its UTF-8 byte bound")
    return result
