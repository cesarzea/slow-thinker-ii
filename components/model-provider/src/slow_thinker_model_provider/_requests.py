"""Normalize a reviewed text request without discarding an unsupported native option."""

from collections.abc import Mapping

from slow_thinker_host import JsonObject, JsonValue, json_object

from ._config import ModelProviderConfig

COMMON: dict[str, bool | int | str] = {"stream": False, "n": 1}
OPENAI: dict[str, bool | int | str] = {"store": False, "service_tier": "default"}


def text_messages(value: JsonValue, roles: tuple[str, ...]) -> list[JsonValue]:
    if not isinstance(value, list) or not value:
        raise ValueError("Text messages are required")
    for item in value:
        message = json_object(item)
        if (
            set(message) != {"role", "content"}
            or message["role"] not in roles
            or not isinstance(message["content"], str)
        ):
            raise ValueError("Only reviewed text messages are supported")
    return value


def fixed(request: JsonObject, fields: Mapping[str, bool | int | str]) -> JsonObject:
    for name, expected in fields.items():
        if name in request and (
            type(request[name]) is not type(expected) or request[name] != expected
        ):
            raise ValueError("Unsupported fixed generation setting")
    return {name: value for name, value in fields.items()}


def normalized_request(config: ModelProviderConfig, arguments: JsonObject) -> JsonObject:
    if set(arguments) != {"request"}:
        raise ValueError("Unsupported native operation envelope")
    request = json_object(arguments["request"])
    allowed = {"model", "messages", "max_completion_tokens", "reasoning_effort", *COMMON}
    allowed.update(OPENAI if config.provider == "openai" else {"temperature"})
    if set(request) - allowed or request.get("model") != config.model_alias:
        raise ValueError("Unsupported model or generation option")
    cap = request.get("max_completion_tokens", config.default_output_tokens)
    effort = request.get("reasoning_effort", "none")
    if type(cap) is not int or not 1 <= cap <= config.maximum_output_tokens:
        raise ValueError("Output cap exceeds the reviewed profile")
    if not isinstance(effort, str) or effort not in config.reasoning_efforts:
        raise ValueError("Unsupported reasoning effort")
    common = fixed(request, COMMON)
    result: JsonObject = {
        **common,
        "model": config.model,
        "messages": text_messages(request.get("messages"), message_roles(config)),
    }
    if config.provider == "openai":
        return {
            **result,
            **fixed(request, OPENAI),
            "reasoning_effort": effort,
            "max_completion_tokens": cap,
        }
    return {**result, **deepseek_options(request, effort), "max_tokens": cap}


def message_roles(config: ModelProviderConfig) -> tuple[str, ...]:
    common = ("system", "user", "assistant")
    return (*common, "developer") if config.provider == "openai" else common


def deepseek_options(request: JsonObject, effort: str) -> JsonObject:
    options: JsonObject = {"thinking": {"type": "disabled" if effort == "none" else "enabled"}}
    if effort != "none":
        options["reasoning_effort"] = effort
    if "temperature" in request:
        value = request["temperature"]
        if (
            effort != "none"
            or (not isinstance(value, (int, float)) or isinstance(value, bool))
            or not 0 <= value <= 2
        ):
            raise ValueError("Temperature is unsupported for the selected reasoning mode")
        options["temperature"] = value
    return options
