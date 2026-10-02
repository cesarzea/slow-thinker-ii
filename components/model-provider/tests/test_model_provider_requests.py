"""SDK options map explicitly to native requests, without silently discarding values."""

import pytest
from model_provider_fixture import arguments, config
from slow_thinker_host import JsonObject, JsonValue, json_object, validate_value
from slow_thinker_model_provider import effective_operation, normalized_request


@pytest.mark.parametrize("effort", ["none", "low", "high", "max"])
def test_deepseek_reasoning_and_output_are_native(effort: str) -> None:
    request = json_object(arguments()["request"])
    request.update(reasoning_effort=effort, max_completion_tokens=17)
    native = normalized_request(config(), {"request": request})
    assert native["model"] == "deepseek-flash" and native["max_tokens"] == 17
    assert "max_completion_tokens" not in native
    assert native["thinking"] == {"type": "disabled" if effort == "none" else "enabled"}
    assert native.get("reasoning_effort") == (None if effort == "none" else effort)


def test_openai_retains_fixed_settings_and_developer_role() -> None:
    request: JsonObject = {
        "model": "bound-model",
        "messages": [{"role": "developer", "content": "x"}],
    }
    native = normalized_request(config("openai"), {"request": request})
    assert native["reasoning_effort"] == "none" and native["max_completion_tokens"] == 8
    assert native["store"] is False and native["service_tier"] == "default"


@pytest.mark.parametrize(
    "field,value",
    [
        ("model", "other"),
        ("unknown", 1),
        ("tools", list[JsonValue]()),
        ("stream", True),
        ("n", 2),
        ("n", True),
        ("max_completion_tokens", 0),
        ("max_completion_tokens", 33),
        ("max_completion_tokens", True),
        ("reasoning_effort", "medium"),
        ("reasoning_effort", False),
        ("temperature", True),
        ("temperature", -1),
        ("temperature", 3),
        ("temperature", "1"),
        ("temperature", float("nan")),
        ("messages", list[JsonValue]()),
        ("messages", "text"),
        ("messages", [{"role": "developer", "content": "x"}]),
        ("messages", [{"role": "tool", "content": "x"}]),
        ("messages", [{"role": "user", "content": list[JsonValue](), "extra": 1}]),
    ],
)
def test_unsupported_deepseek_options_fail_before_native_transport(
    field: str, value: JsonValue
) -> None:
    request = json_object(arguments()["request"])
    with pytest.raises(ValueError):
        normalized_request(config(), {"request": {**request, field: value}})


@pytest.mark.parametrize("effort", ["low", "high", "max"])
def test_temperature_conflict_is_rejected_by_policy_and_effective_schema(effort: str) -> None:
    request = json_object(arguments()["request"])
    payload: JsonObject = {"request": {**request, "reasoning_effort": effort, "temperature": 1}}
    with pytest.raises(ValueError):
        normalized_request(config(), payload)
    with pytest.raises(ValueError):
        validate_value(payload, effective_operation(config()).input_schema)


def test_none_temperature_and_text_roles_are_supported() -> None:
    request = json_object(arguments()["request"])
    request["temperature"] = 0.25
    request["messages"] = [
        {"role": role, "content": "x"} for role in ("system", "user", "assistant")
    ]
    payload: JsonObject = {"request": request}
    validate_value(payload, effective_operation(config()).input_schema)
    assert normalized_request(config(), payload)["temperature"] == 0.25
    with pytest.raises(ValueError):
        normalized_request(config(), {**payload, "extra": 1})
    with pytest.raises(ValueError):
        normalized_request(config("openai"), {"request": {**request, "store": True}})
