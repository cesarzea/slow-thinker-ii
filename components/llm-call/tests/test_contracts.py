"""Configuration and advertised results cannot bypass the functional contract."""

import pytest
from slow_thinker_host import JsonObject, json_object, validate_value
from slow_thinker_llm_call import (
    LLMCall,
    OutputIssue,
    OutputValidationError,
    effective_operation,
    parse_config,
)
from support.openai_calls import ModelStub, completion, config


@pytest.mark.parametrize(
    "parameter",
    [
        "model",
        "messages",
        "n",
        "stream",
        "response_format",
        "extra_body",
        "extra_headers",
        "extra_query",
        "timeout",
        "api_key",
        "base_url",
        "max_retries",
        "unknown",
    ],
)
def test_routing_and_lifecycle_parameters_are_reserved(parameter: str) -> None:
    settings = config()
    settings["parameters"] = {parameter: "override"}
    with pytest.raises(ValueError, match="parameters"):
        parse_config(settings)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("extra", True),
        ("instructions", ""),
        ("input_schema", {"type": "array"}),
        ("output", {"format": "yaml"}),
        ("output", {"format": "text", "schema": {}}),
        ("output", {"format": "json", "schema": {"$ref": "https://example.com/schema"}}),
    ],
)
def test_invalid_configuration(field: str, value: object) -> None:
    settings: dict[str, object] = dict(config())
    settings[field] = value
    with pytest.raises(ValueError):
        parse_config(settings)


async def test_standard_parameters_pass_through_and_schema_refs_keep_their_root() -> None:
    schema: JsonObject = {"$defs": {"integer": {"type": "integer"}}, "$ref": "#/$defs/integer"}
    settings = config(schema)
    settings["parameters"] = {"max_completion_tokens": 20, "reasoning_effort": "none"}
    operation = effective_operation(settings)
    stub = ModelStub(completion("7"))
    async with stub.client() as client:
        result = await LLMCall(settings, client, "model").generate({})
    validate_value(json_object(result), operation.output_schema)
    assert stub.requests[0]["max_completion_tokens"] == 20
    assert stub.requests[0]["reasoning_effort"] == "none"
    with pytest.raises(ValueError):
        validate_value({"status": "ok", "format": "json", "value": "7"}, operation.output_schema)


@pytest.mark.parametrize("path", ["not/a/pointer", "/bad~2", "/bad~"])
def test_output_issues_require_valid_json_pointers(path: str) -> None:
    with pytest.raises(ValueError):
        OutputIssue(path, "Invalid result")


def test_output_issues_and_validation_errors_cannot_be_empty() -> None:
    with pytest.raises(ValueError):
        OutputIssue("", "")
    with pytest.raises(ValueError):
        OutputValidationError(())


async def test_client_must_disable_automatic_retries() -> None:
    stub = ModelStub(completion("unused"))
    async with stub.client() as client:
        client.max_retries = 1
        with pytest.raises(ValueError, match="no automatic retries"):
            LLMCall(config(), client, "model")
    assert not stub.requests
