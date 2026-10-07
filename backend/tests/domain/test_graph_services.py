"""Service selections: nothing selected, unknown entries and parameters outside their schema."""

import pytest
from slow_thinker_ii.catalog import ComponentDeclaration, parse_declaration
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .contract_fixtures import J1, J2, changed, declaration_example, graph_example, without
from .graph_checks import found, messages

MODEL = "/nodes/1/config/model"


def with_model(value: JsonValue) -> JsonObject:
    return changed(graph_example(J1), ("nodes", 1, "config", "model"), value)


def with_judge_parameters(parameters: JsonObject) -> JsonObject:
    path = ("nodes", 1, "config", "model", "parameters")
    return changed(graph_example(J2), path, parameters)


def strict_llm_call() -> ComponentDeclaration:
    """An LLM Call variant whose schema itself rejects `null` at its declared use."""
    path = ("config_schema", "properties", "model", "type")
    document = changed(declaration_example("llm-call"), path, "object")
    return parse_declaration(changed(document, ("version",), "1.1.0"))


def test_nothing_selected() -> None:
    assert found(with_model(None)) == [
        ("service_not_selected", MODEL, "Select a model.", "proposer")
    ]
    missing = without(graph_example(J1), ("nodes", 1, "config", "model"))
    assert found(missing) == [("service_not_selected", MODEL, "Select a model.", "proposer")]


def test_an_unselected_value_is_not_also_invalid_configuration() -> None:
    document = changed(with_model(None), ("nodes", 1, "component"), "llm-call@1.1.0")
    assert found(document, strict_llm_call()) == [
        ("service_not_selected", MODEL, "Select a model.", "proposer")
    ]


def test_unknown_entries() -> None:
    document = with_model({"llm": "openai/gpt-5", "parameters": {}})
    message = "Model “openai/gpt-5” is not available; select another model."
    assert found(document) == [("unknown_service_entry", f"{MODEL}/llm", message, "proposer")]


@pytest.mark.parametrize(
    "value",
    [{"llm": "openai/gpt-6-luna"}, {"llm": 5, "parameters": {}}, {"llm": "x", "parameters": []}],
)
def test_malformed_selections(value: JsonValue) -> None:
    assert found(with_model(value)) == [("invalid_config", MODEL, "LLM is invalid.", "proposer")]


def test_selections_rejected_by_the_schema_are_reported_once() -> None:
    assert found(with_model("gpt-6")) == [
        ("invalid_config", MODEL, "LLM has the wrong type.", "proposer")
    ]


@pytest.mark.parametrize(
    ("parameters", "expected"),
    [
        (
            {"max_completion_tokens": 0},
            [("/max_completion_tokens", "Max output tokens must be at least 1.")],
        ),
        (
            {"max_completion_tokens": 128_001},
            [("/max_completion_tokens", "Max output tokens must be at most 128000.")],
        ),
        ({}, [("/max_completion_tokens", "Max output tokens is required.")]),
        (
            {"max_completion_tokens": 1, "temperature": 1},
            [("/temperature", "Temperature is invalid.")],
        ),
    ],
)
def test_luna_parameters(parameters: JsonObject, expected: list[tuple[str, str]]) -> None:
    document = with_model({"llm": "openai/gpt-6-luna", "parameters": parameters})
    prefixed = [(f"{MODEL}/parameters{path}", message) for path, message in expected]
    assert messages(document, "invalid_service_parameters") == prefixed


@pytest.mark.parametrize(
    ("parameters", "expected"),
    [
        (
            {"reasoning_effort": "high", "temperature": 0.5, "max_completion_tokens": 50},
            [("/temperature", "Temperature is invalid.")],
        ),
        (
            {"reasoning_effort": "turbo", "max_completion_tokens": 50},
            [("/reasoning_effort", 'Reasoning must be one of "none", "low", "high", "max".')],
        ),
        (
            {"temperature": 3, "max_completion_tokens": 50},
            [("/temperature", "Temperature must be at most 2.")],
        ),
        ({"top_p": 1, "max_completion_tokens": 50}, [("/top_p", "Top p is invalid.")]),
        ({"reasoning_effort": "low", "max_completion_tokens": 50}, []),
    ],
)
def test_deepseek_parameters(parameters: JsonObject, expected: list[tuple[str, str]]) -> None:
    prefixed = [(f"{MODEL}/parameters{path}", message) for path, message in expected]
    assert messages(with_judge_parameters(parameters), "invalid_service_parameters") == prefixed
