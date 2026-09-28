"""Single model invocation with overridable functional message and validation hooks."""

from typing import cast

from openai import AsyncOpenAI
from openai.types.chat.completion_create_params import CompletionCreateParamsNonStreaming
from slow_thinker_host import (
    JsonObject,
    JsonValue,
    Operation,
    decode_json,
    encode_json,
    json_object,
    json_value,
)

from ._config import freeze, parse_config
from ._output import failure, schema_issue
from ._response import complete_text
from ._schemas import effective_operation
from ._types import (
    CallResult,
    JsonSuccess,
    LLMCallConfig,
    Message,
    ModelResponse,
    OutputIssue,
    OutputValidationError,
    TextSuccess,
)


class LLMCall:
    def __init__(self, config: LLMCallConfig, client: AsyncOpenAI, model: str) -> None:
        if not model or client.max_retries != 0:
            raise ValueError("LLMCall requires a bound model and no automatic retries")
        self._config = freeze(config)
        self._client, self._model = client, model

    @staticmethod
    def describe(config: JsonObject) -> tuple[Operation, ...]:
        return (effective_operation(parse_config(config)),)

    async def generate(self, arguments: JsonObject) -> CallResult:
        isolated = json_object(arguments)
        issue = schema_issue(isolated, json_object(decode_json(self._config.input_schema)))
        if issue is not None:
            raise ValueError(f"Invalid input at {issue.path}: {issue.message}")
        messages = self.build_messages(json_object(isolated))
        request = json_object(decode_json(self._config.parameters))
        request.update(
            model=self._model,
            n=1,
            stream=False,
            messages=[{"role": item.role, "content": item.content} for item in messages],
        )
        response = await self._client.chat.completions.create(
            **cast(CompletionCreateParamsNonStreaming, request)
        )
        return self._interpret(complete_text(response), isolated)

    def build_messages(self, arguments: JsonObject) -> list[Message]:
        messages = [Message("system", self._config.instructions)]
        if self._config.output_schema is not None:
            messages.append(
                Message(
                    "system",
                    "Return exactly one JSON value conforming to this schema, "
                    "with no surrounding text:\n" + self._config.output_schema,
                )
            )
        return [*messages, Message("user", encode_json(arguments))]

    def parse_response(self, response: ModelResponse) -> JsonValue:
        return decode_json(response.text) if self._config.format == "json" else response.text

    def validate_result(self, value: JsonValue, arguments: JsonObject) -> None:
        del value, arguments

    def _interpret(self, response: ModelResponse, arguments: JsonObject) -> CallResult:
        try:
            value = json_value(self.parse_response(response))
        except ValueError as error:
            return failure("invalid_json", response.text, (OutputIssue("", str(error)),))
        schema = self._config.output_schema
        if schema is not None:
            issue = schema_issue(value, json_object(decode_json(schema)))
            if issue is not None:
                return failure("output_schema_mismatch", response.text, (issue,))
        try:
            self.validate_result(json_value(value), json_object(arguments))
        except OutputValidationError as error:
            return failure("output_validation_failed", response.text, error.issues)
        if self._config.format == "text":
            if not isinstance(value, str):
                raise TypeError("Text parsing must return a string")
            return TextSuccess(status="ok", format="text", value=value)
        return JsonSuccess(status="ok", format="json", value=value)
