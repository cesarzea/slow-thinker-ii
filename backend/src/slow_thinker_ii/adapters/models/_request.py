"""The direct DeepSeek policy validates SDK options before dispatch authorization."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object


def text_messages(value: JsonValue) -> list[JsonValue]:
    if not isinstance(value, list) or not value:
        raise ValueError("Text messages are required")
    for item in value:
        message = json_object(item)
        if (
            set(message) != {"role", "content"}
            or message["role"] not in ("system", "user", "assistant")
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


def deepseek_request(arguments_json: str, alias: str, default: int, maximum: int) -> JsonObject:
    envelope = json_object(decode_json(arguments_json))
    if set(envelope) != {"request"}:
        raise ValueError("Unsupported native operation envelope")
    request = json_object(envelope["request"])
    allowed = {
        "model",
        "messages",
        "max_completion_tokens",
        "reasoning_effort",
        "stream",
        "n",
        "temperature",
    }
    if set(request) - allowed or request.get("model") != alias:
        raise ValueError("Unsupported model or generation option")
    cap, effort = generation(request, default, maximum)
    common = fixed(request, {"stream": False, "n": 1})
    return {
        **common,
        "model": "deepseek-flash",
        "messages": text_messages(request.get("messages")),
        **deepseek_options(request, effort),
        "max_tokens": cap,
    }


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


def generation(request: JsonObject, default: int, maximum: int) -> tuple[int, str]:
    cap, effort = (
        request.get("max_completion_tokens", default),
        request.get("reasoning_effort", "none"),
    )
    if type(cap) is not int or not 1 <= cap <= maximum:
        raise ValueError("Output cap exceeds the reviewed profile")
    if not isinstance(effort, str) or effort not in ("none", "low", "high", "max"):
        raise ValueError("Unsupported reasoning effort")
    return cap, effort
