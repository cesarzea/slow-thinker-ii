"""LLM entries check call parameters with plain sentences and fill in schema defaults."""

import pytest
from slow_thinker_ii.catalog import LlmEntry, llm_entry
from slow_thinker_ii.contracts import JsonObject

from .contract_fixtures import model_settings

LUNA_ID, FLASH_ID = "openai/gpt-6-luna", "deepseek/deepseek-flash"
REASONING = 'Reasoning must be one of "none", "low", "high", "max".'
CUSTOM: JsonObject = {
    "type": "object",
    "properties": {
        "stop": {"type": "string", "title": "Stop", "pattern": "^[a-z]+$"},
        "name": {"type": "string", "title": "Name", "minLength": 1},
        "count": {"type": "integer", "minimum": 5, "default": 1},
        "flag": True,
        "note": {"default": None},
        "tags": {"type": "array", "items": {"type": "string"}, "default": ["a"]},
    },
}
CASES: list[tuple[str, JsonObject, tuple[str, ...]]] = [
    (LUNA_ID, {"max_completion_tokens": 300}, ()),
    (LUNA_ID, {"max_completion_tokens": 0}, ("Max output tokens must be at least 1.",)),
    (LUNA_ID, {"max_completion_tokens": 128_001}, ("Max output tokens must be at most 128000.",)),
    (LUNA_ID, {}, ("Max output tokens is required.",)),
    (LUNA_ID, {"max_completion_tokens": "1"}, ("Max output tokens has the wrong type.",)),
    (
        LUNA_ID,
        {"max_completion_tokens": 1, "top_p": 1, "temperature": 1},
        ("Temperature is invalid.", "Top p is invalid."),
    ),
    (FLASH_ID, {"reasoning_effort": "none", "temperature": 0.2, "max_completion_tokens": 50}, ()),
    (
        FLASH_ID,
        {"reasoning_effort": "high", "temperature": 0.5, "max_completion_tokens": 50},
        ("Temperature is invalid.",),
    ),
    (FLASH_ID, {"reasoning_effort": "turbo", "max_completion_tokens": 50}, (REASONING,)),
    (
        FLASH_ID,
        {"temperature": 3, "max_completion_tokens": 0},
        ("Max output tokens must be at least 1.", "Temperature must be at most 2."),
    ),
]


def entry(entry_id: str) -> LlmEntry:
    return next(llm_entry(item) for item in model_settings() if item.id == entry_id)


def custom() -> LlmEntry:
    return LlmEntry("test/custom", "Custom", "simulated", CUSTOM)


@pytest.mark.parametrize(("entry_id", "parameters", "expected"), CASES)
def test_parameter_problems(
    entry_id: str, parameters: JsonObject, expected: tuple[str, ...]
) -> None:
    assert entry(entry_id).parameter_problems(parameters) == expected


def test_custom_schemas_use_the_same_validator() -> None:
    assert custom().parameter_problems({"stop": "end", "name": "x", "tags": ["a"]}) == ()
    assert custom().parameter_problems({"stop": "end\n", "name": "", "tags": [1]}) == (
        "Name is required.",
        "Stop has an invalid format.",
        "Tags has the wrong type.",
    )


def test_unresolvable_schemas_report_the_parameters() -> None:
    unresolvable = LlmEntry("test/x", "X", "simulated", {"$ref": "https://example.com/x.json"})
    assert unresolvable.parameter_problems({}) == ("Parameters is invalid.",)
    assert unresolvable.with_defaults({"a": 1}) == {"a": 1}


def test_defaults_fill_missing_properties() -> None:
    assert entry(LUNA_ID).with_defaults({}) == {"max_completion_tokens": 1024}
    full = {"reasoning_effort": "none", "temperature": 1, "max_completion_tokens": 1024}
    assert entry(FLASH_ID).with_defaults({}) == full
    chosen: JsonObject = {"reasoning_effort": "none", "temperature": 0.2}
    assert entry(FLASH_ID).with_defaults(chosen) == chosen | {"max_completion_tokens": 1024}


def test_defaults_that_would_add_a_problem_are_left_out() -> None:
    reasoning: JsonObject = {"reasoning_effort": "high"}
    assert entry(FLASH_ID).with_defaults(reasoning) == reasoning | {"max_completion_tokens": 1024}
    assert custom().with_defaults({}) == {"note": None, "tags": ["a"]}


def test_existing_values_are_never_changed_and_results_are_copies() -> None:
    parameters: JsonObject = {"max_completion_tokens": 0}
    result = entry(LUNA_ID).with_defaults(parameters)
    assert result == {"max_completion_tokens": 0} and result is not parameters
    tags = custom().with_defaults({})["tags"]
    assert isinstance(tags, list)
    tags.append("b")
    assert custom().with_defaults({})["tags"] == ["a"]
