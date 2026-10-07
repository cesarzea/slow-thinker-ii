"""The Chat Completions request of a component: its shape, checked before any reservation."""

from dataclasses import dataclass

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

ROLES = frozenset({"system", "user", "assistant"})
MAX_MESSAGES = 100
_FIELDS = frozenset({"model", "messages", "response_format", "stream", "n"})
_SCHEMA_FORMAT = frozenset({"name", "schema", "strict"})


@dataclass(frozen=True)
class ChatRequest:
    document: JsonObject  # as received
    model: str
    messages: list[JsonValue]
    response_format: JsonValue  # None when absent
    parameters: JsonObject  # every field other than the four above

    def input_bytes(self) -> int:
        """UTF-8 bytes of the serialized messages and response format."""
        parts: list[JsonValue] = [self.messages, self.response_format]
        present = [part for part in parts if part is not None]
        return sum(len(encode_json(part).encode("utf-8")) for part in present)

    def dispatched(self, parameters: JsonObject) -> JsonObject:
        """The provider request: model, messages, response format and complete parameters."""
        request: JsonObject = {"model": self.model, "messages": list(self.messages)}
        if self.response_format is not None:
            request["response_format"] = self.response_format
        return json_object({**request, **parameters})


def parse_request(body: str, parameter_names: frozenset[str]) -> ChatRequest | str:
    """The request, or an English reason for `400 invalid_request`."""
    try:
        document = decode_json(body)
    except ValueError:
        return "The request body is not valid JSON."
    if not isinstance(document, dict):
        return "The request body must be a JSON object."
    unsupported = _unsupported(document, parameter_names)
    messages = _messages(document.get("messages"))
    model, response_format = document.get("model"), document.get("response_format")
    if unsupported is not None:
        return unsupported
    if isinstance(messages, str):
        return messages
    if not isinstance(model, str):
        return 'The field "model" must name a catalog entry.'
    if not _valid_format(response_format):
        return 'The field "response_format" is not supported in this form.'
    parameters = {key: value for key, value in document.items() if key not in _FIELDS}
    return ChatRequest(document, model, messages, response_format, parameters)


def _unsupported(document: JsonObject, parameter_names: frozenset[str]) -> str | None:
    for name, value in document.items():
        if name == "stream" and value is not False:
            return 'Streaming is not supported; send "stream": false or omit it.'
        if name == "n" and not (type(value) is int and value == 1):
            return 'Only one choice is supported; send "n": 1 or omit it.'
        if name not in _FIELDS and name not in parameter_names:
            return f'The field "{name}" is not supported.'
    return None


def _messages(value: JsonValue) -> list[JsonValue] | str:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_MESSAGES:
        return f'The field "messages" must list 1 to {MAX_MESSAGES} messages.'
    for index, message in enumerate(value):
        if not _valid_message(message):
            return (
                f"Message {index} must have only a role (system, user or assistant) "
                "and text content."
            )
    return value


def _valid_message(message: JsonValue) -> bool:
    if not isinstance(message, dict) or set(message) != {"role", "content"}:
        return False
    return message["role"] in ROLES and isinstance(message["content"], str)


def _valid_format(value: JsonValue) -> bool:
    if value is None:
        return True
    if not isinstance(value, dict):
        return False
    kind = value.get("type")
    if kind in ("text", "json_object"):
        return set(value) == {"type"}
    return kind == "json_schema" and set(value) == {"type", "json_schema"} and _schema(value)


def _schema(value: JsonObject) -> bool:
    schema = value["json_schema"]
    if not isinstance(schema, dict) or not set(schema) <= _SCHEMA_FORMAT:
        return False
    name, content, strict = schema.get("name"), schema.get("schema", {}), schema.get("strict")
    return isinstance(name, str) and isinstance(content, dict) and strict in (None, True, False)
