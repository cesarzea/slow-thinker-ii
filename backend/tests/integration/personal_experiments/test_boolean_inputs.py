"""Unconditionally impossible property schemas reject bindings without requiring runtime values."""

import pytest
from slow_thinker_ii.adapters.catalog import GraphDefinitionValidator
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from support.personal_experiments.definitions import set_field
from support.sequence_plans import graph_value


@pytest.mark.parametrize("with_identity", [False, True])
@pytest.mark.parametrize("keyword", ["direct", "$ref", "allOf"])
@pytest.mark.parametrize("allows", [True, False])
@pytest.mark.parametrize("literal", [True, False])
def test_boolean_property_contract_applies_to_unknown_values(
    validator: GraphDefinitionValidator,
    keyword: str,
    allows: bool,
    literal: bool,
    with_identity: bool,
) -> None:
    value = graph_value("single-agent")
    set_field(
        value,
        "/components/proposer/config",
        "input_schema",
        property_contract(keyword, allows, with_identity),
    )
    if literal:
        set_field(value, "/nodes/draft/inputs", "problem", {"source": "literal", "value": "valid"})
    if allows:
        validator.validate(encode_json(value))
    else:
        with pytest.raises(library.DefinitionError) as error:
            validator.validate(encode_json(value))
        assert error.value.code == "invalid_definition"


@pytest.mark.parametrize("keyword", ["anyOf", "oneOf"])
def test_boolean_alternative_does_not_make_unknown_binding_impossible(
    validator: GraphDefinitionValidator, keyword: str
) -> None:
    value = graph_value("single-agent")
    schema: JsonObject = {
        "type": "object",
        "properties": {"problem": {keyword: [False, {"type": "string"}]}},
        "required": ["problem"],
        "additionalProperties": False,
    }
    set_field(value, "/components/proposer/config", "input_schema", schema)
    validator.validate(encode_json(value))


def property_contract(keyword: str, allows: bool, with_identity: bool) -> JsonObject:
    child: JsonValue = allows
    if keyword == "$ref":
        child = {"$ref": "#/$defs/allowed"}
    if keyword == "allOf":
        child = {"allOf": [allows]}
    schema: JsonObject = {
        "type": "object",
        "$defs": {"allowed": allows},
        "properties": {"problem": child},
        "required": ["problem"],
        "additionalProperties": False,
    }
    if with_identity:
        schema["$id"] = "urn:test:personal-input"
    return schema
