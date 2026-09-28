"""Validate self-contained schemas without implicit remote reference resolution."""

from jsonschema import Draft202012Validator, ValidationError, validate
from referencing import Registry

from ._json import JsonObject, JsonValue


def _references(value: JsonValue) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("$ref", "$dynamicRef") and (
                not isinstance(item, str) or not item.startswith("#")
            ):
                raise ValueError("Only local schema references are supported")
            _references(item)
    elif isinstance(value, list):
        for item in value:
            _references(item)


def check_schema(schema: JsonObject) -> None:
    _references(schema)
    Draft202012Validator.check_schema(schema)


def validate_value(value: JsonValue, schema: JsonObject) -> None:
    try:
        validate(value, schema, cls=Draft202012Validator, registry=Registry[JsonValue]())
    except ValidationError as error:
        raise ValueError(error.message) from error
