"""Bounded, immutable calculator settings and ordinary configuration schema."""

from dataclasses import dataclass

from slow_thinker_host import JsonObject, validate_value

CONFIG_SCHEMA: JsonObject = {
    "type": "object",
    "properties": {
        "max_expression_bytes": {"type": "integer", "minimum": 1, "maximum": 4096, "default": 4096},
        "max_nodes": {"type": "integer", "minimum": 1, "maximum": 128, "default": 128},
        "max_exponent": {"type": "integer", "minimum": 0, "maximum": 100, "default": 100},
        "max_result_bytes": {"type": "integer", "minimum": 1, "maximum": 4096, "default": 4096},
    },
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Settings:
    max_expression_bytes: int = 4096
    max_nodes: int = 128
    max_exponent: int = 100
    max_result_bytes: int = 4096


def settings(config: JsonObject) -> Settings:
    validate_value(config, CONFIG_SCHEMA)
    defaults = Settings()
    values = [config.get(name, getattr(defaults, name)) for name in Settings.__dataclass_fields__]
    if any(type(value) is not int for value in values):
        raise ValueError("Calculator limits require integers")
    return Settings(*(int(value) for value in values if isinstance(value, int)))
