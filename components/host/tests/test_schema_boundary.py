"""Schemas stay self-contained; violations name their JSON Pointer; `$` follows ECMA-262."""

import pytest
from slow_thinker_host import JsonObject, JsonValue, check_schema, validate_value


@pytest.mark.parametrize(
    "schema",
    [
        {"$ref": "https://untrusted.example/schema"},
        {"allOf": [{"$dynamicRef": "file:///private/data"}]},
        {"$ref": 1},
        {"type": "unknown"},
        {"items": [{"minimum": "one"}]},
    ],
)
def test_external_references_and_invalid_schemas_are_rejected(schema: JsonObject) -> None:
    with pytest.raises(ValueError):
        check_schema(schema)


def test_local_references_are_validated() -> None:
    schema: JsonObject = {"$defs": {"number": {"type": "integer"}}, "$ref": "#/$defs/number"}
    check_schema(schema)
    validate_value(1, schema)
    with pytest.raises(ValueError, match="'1' is not of type 'integer'"):
        validate_value("1", schema)


def test_violations_name_their_escaped_pointer() -> None:
    schema: JsonObject = {"properties": {"a/~b": {"items": {"maximum": 10}}}}
    with pytest.raises(ValueError, match="^/a~1~0b/1: 11 is greater than the maximum of 10$"):
        validate_value({"a/~b": [1, 11]}, schema)


@pytest.mark.parametrize(
    ("value", "valid"), [("story", True), ("story\n", False), ("$", False), ("a]$", True)]
)
def test_dollar_matches_only_at_the_end(value: JsonValue, valid: bool) -> None:
    schema: JsonObject = {"anyOf": [{"pattern": "^[a-z]+$"}, {"pattern": "^[]a$]{3}$"}]}
    if valid:
        validate_value(value, schema)
    else:
        with pytest.raises(ValueError):
            validate_value(value, schema)


def test_patterns_ignore_other_types_and_escaped_dollars() -> None:
    validate_value(7, {"pattern": "^x$"})
    validate_value("cost$", {"pattern": "^cost\\$$"})
    with pytest.raises(ValueError):
        validate_value("cost", {"pattern": "^[^$]cost$"})


def test_unresolvable_local_references_fail_validation() -> None:
    with pytest.raises(ValueError, match="Unresolvable"):
        validate_value(1, {"$ref": "#/$defs/missing"})
