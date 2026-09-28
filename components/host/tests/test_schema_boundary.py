"""Component schemas stay self-contained and are applied to actual inputs/outputs."""

import pytest
from slow_thinker_host import JsonObject, check_schema, validate_value


@pytest.mark.parametrize(
    "schema",
    [
        {"$ref": "https://untrusted.example/schema"},
        {"allOf": [{"$dynamicRef": "file:///private/data"}]},
        {"$ref": 1},
    ],
)
def test_external_references_are_rejected(schema: JsonObject) -> None:
    with pytest.raises(ValueError):
        check_schema(schema)


def test_local_references_are_validated() -> None:
    schema: JsonObject = {"$defs": {"number": {"type": "integer"}}, "$ref": "#/$defs/number"}
    check_schema(schema)
    validate_value(1, schema)
    with pytest.raises(ValueError):
        validate_value("1", schema)
