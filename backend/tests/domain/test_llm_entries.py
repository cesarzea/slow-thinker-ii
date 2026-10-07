"""LLM catalog entries and their generated parameter schemas."""

from dataclasses import replace

import pytest
from slow_thinker_ii.catalog import LlmModelSettings, llm_entry
from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object

from .contract_fixtures import example, model_settings

LUNA_SETTINGS = LlmModelSettings(
    id="openai/gpt-6-luna",
    label="OpenAI · GPT-6 Luna",
    provider="openai",
    model="gpt-6-luna",
    max_output_tokens=128_000,
    default_output_tokens=1024,
    reasoning_efforts=("none",),
    temperature="unsupported",
)


def max_tokens(maximum: int = 128_000, default: int = 1024) -> JsonValue:
    return {
        "type": "integer",
        "title": "Max output tokens",
        "minimum": 1,
        "maximum": maximum,
        "default": default,
    }


def properties(settings: LlmModelSettings) -> JsonObject:
    return json_object(llm_entry(settings).parameters["properties"])


def test_the_catalog_example_equals_the_entries_of_the_step_one_settings() -> None:
    settings = model_settings()
    assert settings[0] == LUNA_SETTINGS
    assert settings[0].model == "gpt-6-luna"
    assert [llm_entry(item).document() for item in settings] == example("llm-catalog.json")


def test_entry_fields() -> None:
    entry = llm_entry(LUNA_SETTINGS)
    assert (entry.id, entry.label, entry.provider) == (
        "openai/gpt-6-luna",
        "OpenAI · GPT-6 Luna",
        "openai",
    )
    assert entry.parameters["required"] == ["max_completion_tokens"]
    assert entry.parameters["additionalProperties"] is False
    assert properties(LUNA_SETTINGS) == {"max_completion_tokens": max_tokens()}


def test_documents_are_copies() -> None:
    entry = llm_entry(LUNA_SETTINGS)
    parameters = json_object(entry.document()["parameters"])
    parameters["additionalProperties"] = True
    assert entry.parameters["additionalProperties"] is False


def test_supported_temperature_has_no_conditional_clause() -> None:
    settings = replace(LUNA_SETTINGS, reasoning_efforts=("low", "high"), temperature="supported")
    assert properties(settings) == {
        "reasoning_effort": {"title": "Reasoning", "enum": ["low", "high"], "default": "low"},
        "temperature": {
            "type": "number",
            "title": "Temperature",
            "minimum": 0,
            "maximum": 2,
            "default": 1,
        },
        "max_completion_tokens": max_tokens(),
    }
    parameters = llm_entry(settings).parameters
    assert "if" not in parameters and "else" not in parameters


def test_temperature_without_reasoning_adds_the_conditional_clause() -> None:
    settings = replace(LUNA_SETTINGS, temperature="without_reasoning")
    parameters = llm_entry(settings).parameters
    assert "reasoning_effort" not in properties(settings)
    assert parameters["if"] == {"properties": {"reasoning_effort": {"const": "none"}}}
    assert parameters["else"] == {"properties": {"temperature": False}}


@pytest.mark.parametrize(("maximum", "default"), [(100, 101), (100, 0), (0, 0)])
def test_default_output_tokens_must_be_within_the_maximum(maximum: int, default: int) -> None:
    settings = replace(LUNA_SETTINGS, max_output_tokens=maximum, default_output_tokens=default)
    with pytest.raises(ValueError, match="default_output_tokens must be from 1 to max_output"):
        llm_entry(settings)


def test_the_default_may_equal_the_maximum() -> None:
    settings = replace(LUNA_SETTINGS, max_output_tokens=100, default_output_tokens=100)
    assert properties(settings) == {"max_completion_tokens": max_tokens(100, 100)}
