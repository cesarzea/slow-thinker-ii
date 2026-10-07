"""The provider's native request: the reviewed model name and each adapter's field mapping.

The gateway has already validated the request against the entry's parameter schema; the
adapter only maps it, as the LLM service contract's adapter table states. The received
request, which the gateway records, is never changed: mappings build new values.
"""

from slow_thinker_ii.application import LlmModel
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json

DEEPSEEK_ROLES = frozenset({"system", "user", "assistant"})
SCHEMA_INSTRUCTION = "Answer with one JSON object that conforms to this JSON Schema: "


def native_request(provider: str, model: LlmModel, request: JsonObject) -> JsonObject | str:
    """The request to send, or an English reason why it cannot be sent."""
    native: JsonObject = {**request, "model": model.settings.model}
    effort = _effort(model, native.pop("reasoning_effort", None))
    if provider == "openai":
        reasoning: JsonObject = {} if effort is None else {"reasoning_effort": effort}
        return {**native, **reasoning, "store": False, "service_tier": "default"}
    return _deepseek(native, effort)


def _effort(model: LlmModel, requested: JsonValue) -> str | None:
    """The requested effort, else the reviewed default (the first), else none at all."""
    if isinstance(requested, str):
        return requested
    return next(iter(model.settings.reasoning_efforts), None)


def _deepseek(native: JsonObject, effort: str | None) -> JsonObject | str:
    messages = native.get("messages")
    if not isinstance(messages, list) or not all(_deepseek_message(item) for item in messages):
        return "DeepSeek accepts only system, user and assistant messages."
    if "max_completion_tokens" in native:
        native["max_tokens"] = native.pop("max_completion_tokens")
    if effort is not None:
        native["thinking"] = {"type": "disabled" if effort == "none" else "enabled"}
    if effort not in (None, "none"):
        native["reasoning_effort"] = effort
    instruction = _schema_instruction(native.get("response_format"))
    if instruction is not None:  # DeepSeek's JSON output supports only `json_object`
        native["response_format"] = {"type": "json_object"}
        native["messages"] = _instructed(messages, instruction)
    return native


def _deepseek_message(message: JsonValue) -> bool:
    return isinstance(message, dict) and message.get("role") in DEEPSEEK_ROLES


def _schema_instruction(output: JsonValue) -> str | None:
    """For a `json_schema` format, the instruction naming its schema as canonical JSON."""
    if not isinstance(output, dict) or output.get("type") != "json_schema":
        return None
    definition = output.get("json_schema")
    schema: JsonValue = definition.get("schema", {}) if isinstance(definition, dict) else {}
    return SCHEMA_INSTRUCTION + encode_json(schema)


def _instructed(messages: list[JsonValue], instruction: str) -> list[JsonValue]:
    """`instruction` after a blank line in a leading system message, else as a new first one."""
    first = messages[0] if messages else None
    if isinstance(first, dict) and first.get("role") == "system":
        content = first.get("content")
        return [{**first, "content": f"{content}\n\n{instruction}"}, *messages[1:]]
    return [{"role": "system", "content": instruction}, *messages]
