"""Interpret complete native responses before exposing text to functional hooks."""

from openai.types.chat import ChatCompletion
from slow_thinker_host import JsonObject, json_object

from ._types import ModelOperationError, ModelResponse


def _choice(response: object) -> JsonObject:
    if not isinstance(response, ChatCompletion):
        raise ValueError("Expected a native Chat Completion")
    value = json_object(response.model_dump(mode="json", warnings=False))
    identity = (value.get("id"), value.get("model"))
    if value.get("object") != "chat.completion" or any(
        not isinstance(item, str) or not item for item in identity
    ):
        raise ValueError("Invalid response identity")
    choices = value.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError("Expected exactly one choice")
    choice = json_object(choices[0])
    if type(choice.get("index")) is not int or choice["index"] != 0:
        raise ValueError("Unexpected choice identity")
    if json_object(choice.get("message")).get("role") != "assistant":
        raise ValueError("Unexpected response role")
    return choice


def complete_text(response: object) -> ModelResponse:
    try:
        choice = _choice(response)
    except (ValueError, TypeError) as error:
        raise ModelOperationError("provider_response_invalid") from error
    message = json_object(choice["message"])
    reason = choice.get("finish_reason")
    if message.get("refusal") is not None or reason == "content_filter":
        raise ModelOperationError("provider_refusal")
    if reason == "length":
        raise ModelOperationError("incomplete_response")
    if reason != "stop" or message.get("tool_calls") or message.get("function_call"):
        raise ModelOperationError("unsupported_response")
    content = message.get("content")
    if not isinstance(content, str):
        raise ModelOperationError("missing_text")
    return ModelResponse(content)
