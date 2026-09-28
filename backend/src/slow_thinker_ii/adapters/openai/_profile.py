"""The first native request profile is explicit; unsupported options never disappear silently."""

from dataclasses import dataclass

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

FIXED: tuple[tuple[str, JsonValue], ...] = (
    ("reasoning_effort", "none"),
    ("stream", False),
    ("n", 1),
    ("store", False),
    ("service_tier", "default"),
)
ROLES = frozenset({"system", "developer", "user", "assistant"})


@dataclass(frozen=True)
class OpenAIProfile:
    revision: TariffRevision
    model_alias: str
    default_output_tokens: int
    maximum_output_tokens: int
    returned_models: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.model_alias
            or not self.returned_models
            or any(not model for model in self.returned_models)
        ):
            raise ValueError("Model aliases and reviewed response identities are required")
        if any(
            type(value) is not int
            for value in (self.default_output_tokens, self.maximum_output_tokens)
        ):
            raise ValueError("Output token caps must be integers")
        if (
            not 1
            <= self.default_output_tokens
            <= self.maximum_output_tokens
            <= self.revision.tariff.output_capacity
        ):
            raise ValueError("Output caps must fit the reviewed model capacity")

    def request(self, arguments_json: str) -> JsonObject:
        envelope = json_object(decode_json(arguments_json))
        if set(envelope) != {"request"}:
            raise ValueError("Unsupported model operation arguments")
        request = json_object(envelope["request"])
        allowed = {"model", "messages", "max_completion_tokens", *(name for name, _ in FIXED)}
        if set(request) - allowed or request.get("model") != self.model_alias:
            raise ValueError("Unsupported model or generation option")
        messages = text_messages(request.get("messages"))
        cap = request.get("max_completion_tokens", self.default_output_tokens)
        if type(cap) is not int or not 1 <= cap <= self.maximum_output_tokens:
            raise ValueError("Output token cap exceeds the frozen request profile")
        return {
            **fixed_settings(request),
            "model": self.revision.tariff.model,
            "messages": messages,
            "max_completion_tokens": cap,
        }


def text_messages(value: JsonValue) -> list[JsonValue]:
    if not isinstance(value, list) or not value:
        raise ValueError("A model request requires text messages")
    for item in value:
        message = json_object(item)
        role = message.get("role")
        if set(message) != {"role", "content"} or not isinstance(role, str) or role not in ROLES:
            raise ValueError("Unsupported message role or field")
        if not isinstance(message["content"], str):
            raise ValueError("Only text message content is supported")
    return value


def fixed_settings(request: JsonObject) -> JsonObject:
    for key, expected in FIXED:
        if key in request and (
            type(request[key]) is not type(expected) or request[key] != expected
        ):
            raise ValueError("Unsupported fixed generation setting")
    return dict(FIXED)
