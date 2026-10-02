"""Strict JSON and bounded diagnostic evidence through the public validator."""

import pytest
from slow_thinker_ii.adapters.catalog import GraphDefinitionValidator
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import encode_json
from support.sequence_plans import graph_value


@pytest.mark.parametrize(
    "source",
    [
        '{"x":1,"x":2}',
        '{"value":NaN}',
        '{"value":Infinity}',
        '{"value":1e400}',
        '{"x":"\\ud800"}',
        "invalid",
        "\ufeff{}",
    ],
)
def test_strict_json_errors_are_distinct_and_safe(
    validator: GraphDefinitionValidator, source: str
) -> None:
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(source)
    assert error.value.code == "invalid_json" and not error.value.issues


def test_diagnostics_are_bounded_and_do_not_echo_submitted_values(
    validator: GraphDefinitionValidator,
) -> None:
    value = graph_value("single-agent")
    for index in range(20):
        value[f"sensitive-{index}"] = "sensitive-secret-value"
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(encode_json(value))
    assert 1 <= len(error.value.issues) <= 10
    assert all(
        len(issue.pointer) <= 160 and len(issue.message) <= 160 for issue in error.value.issues
    )
    assert "sensitive-secret-value" not in str(error.value.issues)


def test_oversized_pointer_falls_back_to_root(validator: GraphDefinitionValidator) -> None:
    value = graph_value("single-agent")
    components = value["components"]
    assert isinstance(components, dict)
    components["a" * 300] = {
        "type_id": "unregistered",
        "type_version": "1",
        "config": {},
        "resources": {},
    }
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(encode_json(value))
    assert error.value.issues[0].pointer == ""


@pytest.mark.parametrize("source", ["[]", "null", "3", '"scalar"', "true"])
def test_valid_json_requires_a_graph_object(
    validator: GraphDefinitionValidator, source: str
) -> None:
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(source)
    assert error.value.code == "invalid_definition"
    assert error.value.issues == (
        library.DefinitionIssue("", "Definition does not satisfy the supported graph contract."),
    )
