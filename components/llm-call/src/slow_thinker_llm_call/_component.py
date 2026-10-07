"""One LLM call per activation: the prompt as system message, the received message as user."""

from collections.abc import Sequence

from slow_thinker_host import (
    Context,
    Emission,
    HandlerError,
    JsonValue,
    decode_json,
    encode_json,
    validate_value,
)

from ._config import LLMCallConfig
from ._model import Message, complete, request_body


class LLMCall:
    """The LLM Call node handler. Subclasses may override the three public hooks."""

    def __init__(self, config: LLMCallConfig) -> None:
        self.config = config

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        self._check_input(message)
        messages = self.build_messages(message)
        await context.report("step", f"messages built: {len(messages)} messages")
        reply = await complete(context.llm_client(), request_body(self.config, messages))
        await context.report("step", f"model replied: {len(reply)} characters")
        try:
            value = self.parse_response(reply)
            self.validate_result(value, reply)
        except HandlerError as error:
            await context.report("step", f"reply failed validation: {error.code}")
            raise
        json_output = self.config.output_schema is not None
        await context.report("step", "reply validated" if json_output else "reply returned as text")
        return [Emission("out", value)]

    def build_messages(self, message: JsonValue) -> list[Message]:
        """The prompt, then the message itself if it is text, else its canonical JSON."""
        text = message if isinstance(message, str) else encode_json(message)
        return [Message("system", self.config.prompt), Message("user", text)]

    def parse_response(self, reply: str) -> JsonValue:
        """The reply text for text output; the parsed reply for JSON output."""
        if self.config.output_schema is None:
            return reply
        try:
            return decode_json(reply)
        except ValueError as error:
            message = f"The reply is not valid JSON ({error}). Reply: {reply[:200]}"
            raise HandlerError("invalid_json", message) from error

    def validate_result(self, value: JsonValue, reply: str) -> None:
        """Check a JSON reply against the output schema; text output is not checked."""
        if self.config.output_schema is None:
            return
        try:
            validate_value(value, self.config.output_schema)
        except ValueError as error:
            message = f"The reply does not match the output schema: {error}. Reply: {reply[:200]}"
            raise HandlerError("schema_mismatch", message) from error

    def _check_input(self, message: JsonValue) -> None:
        if self.config.input_format is None:
            return
        try:
            validate_value(message, self.config.input_format)
        except ValueError as error:
            text = f"The received message does not match the input format: {error}"
            raise HandlerError("input_format_mismatch", text) from error
