"""The simulated provider: deterministic replies and usage, without any network access."""

from collections.abc import Mapping, Sequence

from slow_thinker_ii.accounting import Usage
from slow_thinker_ii.application import LlmModel, LlmProvider, ProviderReply
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json

from ._replies import utc_now
from ._schema_instance import smallest_instance

ECHO_CHARACTERS = 200


class SimulatedProvider(LlmProvider):
    """Answers every model at once, whatever its provider.

    A model id with configured replies cycles through them in call order, shared by every run
    of the process; an empty sequence counts as none. Otherwise the reply derives from the
    request: the smallest instance of a requested JSON Schema, `{}` for JSON object output,
    else `Simulated reply to: <first 200 characters of the last user message>`.
    """

    def __init__(self, replies: Mapping[str, Sequence[str]] | None = None) -> None:
        configured = (replies or {}).items()
        self._replies = {model: tuple(texts) for model, texts in configured if texts}
        self._next: dict[str, int] = {}

    async def complete(
        self, model: LlmModel, request: JsonObject, timeout_s: float
    ) -> ProviderReply:
        """A 200 reply with usage of request bytes ÷ 4 and reply bytes ÷ 4, rounded up."""
        del timeout_s  # answered at once
        started = utc_now()
        content = self._scripted(model.settings.id)
        if content is None:
            content = derived_reply(request)
        usage = Usage(_quarter(encode_json(request)), 0, 0, _quarter(content))
        return ProviderReply(200, _completion(model, content, usage), usage, started, utc_now())

    def _scripted(self, model_id: str) -> str | None:
        texts = self._replies.get(model_id)
        if texts is None:
            return None
        index = self._next.get(model_id, 0)
        self._next[model_id] = (index + 1) % len(texts)
        return texts[index]


def derived_reply(request: JsonObject) -> str:
    output = request.get("response_format")
    if isinstance(output, dict) and output.get("type") in ("json_schema", "json_object"):
        definition = output.get("json_schema")
        schema: JsonValue = definition.get("schema", {}) if isinstance(definition, dict) else {}
        return encode_json(smallest_instance(schema))
    return f"Simulated reply to: {_last_user_message(request)[:ECHO_CHARACTERS]}"


def _last_user_message(request: JsonObject) -> str:
    """The content of the last `user` message; empty when there is none."""
    messages = request.get("messages")
    for message in reversed(messages if isinstance(messages, list) else []):
        if isinstance(message, dict) and message.get("role") == "user":
            content = message.get("content")
            return content if isinstance(content, str) else ""
    return ""


def _quarter(text: str) -> int:
    """UTF-8 bytes ÷ 4, rounded up."""
    return -(-len(text.encode("utf-8")) // 4)


def _completion(model: LlmModel, content: str, usage: Usage) -> JsonObject:
    """A Chat Completions response; fixed `id` and `created` keep it deterministic."""
    message: JsonObject = {"role": "assistant", "content": content}
    return {
        "id": "chatcmpl-simulated",
        "object": "chat.completion",
        "created": 0,
        "model": model.settings.model,
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": usage.input,
            "completion_tokens": usage.output,
            "total_tokens": usage.input + usage.output,
        },
    }
