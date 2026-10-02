"""Strict JSON, local schemas, literal compatibility and bounded safe diagnostics."""

import pytest
from slow_thinker_ii.adapters.catalog import GraphDefinitionValidator
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonValue, encode_json
from support.personal_experiments.definitions import set_field
from support.sequence_plans import graph_value


@pytest.mark.parametrize(
    "parent,name,replacement",
    [
        ("/components/proposer/config", "input_schema", {"type": "object", "required": [7]}),
        (
            "/components/proposer/config",
            "input_schema",
            {"type": "object", "$ref": "https://secret.example/token"},
        ),
        (
            "/components/proposer/config",
            "input_schema",
            {"type": "object", "$ref": "urn:slow-thinker-ii:contracts:graph:0.1-draft"},
        ),
        (
            "/components/proposer/config",
            "input_schema",
            {"type": "object", "$ref": "#/$defs/missing"},
        ),
        (
            "/components/proposer/config",
            "output",
            {"format": "json", "schema": {"type": "incorrect"}},
        ),
        ("/nodes/draft/inputs", "problem", {"source": "literal", "value": 3}),
        ("/nodes/draft", "inputs", {}),
        ("/nodes/draft/inputs", "extra", {"source": "run_input", "pointer": "/problem"}),
    ],
)
def test_invalid_declared_schemas_and_literal_inputs_fail(
    validator: GraphDefinitionValidator, parent: str, name: str, replacement: JsonValue
) -> None:
    value = graph_value("single-agent")
    set_field(value, parent, name, replacement)
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(encode_json(value))
    assert error.value.code == "invalid_definition"
    assert all("secret.example" not in issue.message for issue in error.value.issues)


@pytest.mark.parametrize(
    "parameter",
    [
        "model",
        "messages",
        "stream",
        "response_format",
        "n",
        "base_url",
        "api_key",
        "timeout",
        "max_retries",
    ],
)
def test_public_reserved_parameters_are_rejected_without_echo(
    validator: GraphDefinitionValidator, parameter: str
) -> None:
    value = graph_value("single-agent")
    set_field(value, "/components/proposer/config", "parameters", {parameter: "sensitive-value"})
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(encode_json(value))
    assert error.value.code == "invalid_definition"
    assert error.value.issues[0].pointer == "/components/proposer/config/parameters"
    assert "sensitive-value" not in str(error.value.issues)


def mixed_schema_reference_graph(reference_schema: JsonValue) -> str:
    value = graph_value("single-agent")
    schema: JsonValue = {
        "type": "object",
        "$defs": {"literal": reference_schema},
        "properties": {"problem": {"type": "string"}, "extra": {"$ref": "#/$defs/literal"}},
        "required": ["problem", "extra"],
        "additionalProperties": False,
    }
    set_field(value, "/components/proposer/config", "input_schema", schema)
    set_field(
        value, "/nodes/draft/inputs", "extra", {"source": "literal", "value": "valid literal"}
    )
    return encode_json(value)


def test_local_fragment_schema_validates_mixed_literal_and_runtime_bindings(
    validator: GraphDefinitionValidator,
) -> None:
    validator.validate(mixed_schema_reference_graph({"type": "string", "minLength": 1}))
    with pytest.raises(library.DefinitionError):
        validator.validate(mixed_schema_reference_graph({"type": "integer"}))
    validator.validate(mixed_schema_reference_graph(True))


@pytest.mark.parametrize("keyword", ["$ref", "allOf"])
@pytest.mark.parametrize("allows", [True, False])
@pytest.mark.parametrize("literal", [True, False])
def test_boolean_schema_contracts_apply_with_runtime_or_literal_bindings(
    validator: GraphDefinitionValidator, keyword: str, allows: bool, literal: bool
) -> None:
    value = graph_value("single-agent")
    schema: JsonValue = (
        {"type": "object", "$defs": {"anything": allows}, "$ref": "#/$defs/anything"}
        if keyword == "$ref"
        else {"type": "object", "allOf": [allows]}
    )
    set_field(value, "/components/proposer/config", "input_schema", schema)
    if literal:
        set_field(value, "/nodes/draft/inputs", "problem", {"source": "literal", "value": "valid"})
    if allows:
        validator.validate(encode_json(value))
    else:
        with pytest.raises(library.DefinitionError) as error:
            validator.validate(encode_json(value))
        assert error.value.code == "invalid_definition"
        assert error.value.issues[0].pointer == "/nodes/draft/inputs"
