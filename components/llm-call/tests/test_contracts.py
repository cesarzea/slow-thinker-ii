"""The packaged declaration is the contract example; configurations are checked against it."""

import json
from pathlib import Path

import pytest
from llm_call_fakes import SCORE, config
from slow_thinker_host import JsonValue, read_declaration
from slow_thinker_llm_call import LLMCallConfig, parse_config

EXAMPLE = Path(__file__).resolve().parents[3] / "docs/contracts/examples/llm-call.component.json"


def test_packaged_declaration_equals_the_contract_example() -> None:
    assert read_declaration("slow_thinker_llm_call") == json.loads(EXAMPLE.read_text("utf-8"))


def test_configuration_is_read_into_its_fields() -> None:
    settings = parse_config(
        config(
            input_format={"type": "string"},
            output_format={"type": "json", "schema": SCORE},
        )
    )
    assert settings == LLMCallConfig(
        prompt="Rewrite this story so that it is funny. Keep it under 80 words.",
        llm="openai/gpt-6-luna",
        parameters={"max_completion_tokens": 300},
        input_format={"type": "string"},
        output_schema=SCORE,
    )


def test_missing_parameters_are_left_to_the_platform_defaults() -> None:
    assert parse_config(config(model={"llm": "openai/gpt-6-luna"})).parameters == {}


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("model", None, "No LLM is selected"),
        ("model", {"parameters": {}}, "must name a catalog entry"),
        ("model", {"llm": "", "parameters": {}}, "must name a catalog entry"),
        ("model", {"llm": "openai/x", "parameters": []}, "must name a catalog entry"),
        ("prompt", "", "configuration is invalid"),
        ("output_format", {"type": "json"}, "configuration is invalid"),
        ("output_format", {"type": "yaml"}, "configuration is invalid"),
        ("extra", True, "configuration is invalid"),
        ("input_format", {"type": "unknown"}, "Invalid JSON Schema"),
        ("output_format", {"type": "json", "schema": {"$ref": "https://x.test/s"}}, "local"),
    ],
)
def test_unrunnable_configurations_are_rejected(field: str, value: JsonValue, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        parse_config(config(**{field: value}))
