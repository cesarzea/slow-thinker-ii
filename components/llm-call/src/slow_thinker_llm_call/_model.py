"""The Chat Completions request sent through the platform and the reading of its reply."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, cast

from openai import APIError, APIStatusError, APITimeoutError, AsyncOpenAI
from openai.types.chat.completion_create_params import CompletionCreateParamsNonStreaming
from slow_thinker_host import HandlerError, JsonObject, json_object

from ._config import LLMCallConfig


@dataclass(frozen=True)
class Message:
    """One chat message of the request."""

    role: Literal["system", "user", "assistant"]
    content: str


def request_body(config: LLMCallConfig, messages: Sequence[Message]) -> JsonObject:
    """The selected entry, the messages, every configured parameter and the JSON format."""
    body = json_object(config.parameters)
    body["model"] = config.llm
    body["messages"] = [{"role": item.role, "content": item.content} for item in messages]
    if config.output_schema is not None:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "output",
                "schema": json_object(config.output_schema),
                "strict": False,
            },
        }
    return body


async def complete(client: AsyncOpenAI, body: JsonObject) -> str:
    """One call, no retries; the client is closed afterwards. Returns the reply text.

    The client's timeout is the call's remaining budget, so its expiry is a `timeout`."""
    try:
        async with client:
            completion = await client.chat.completions.create(
                **cast(CompletionCreateParamsNonStreaming, body)
            )
    except APIStatusError as error:
        raise HandlerError("model_call_failed", _rejection(error)) from error
    except APITimeoutError as error:
        message = "The model call did not finish within the call's time budget."
        raise HandlerError("timeout", message) from error
    except APIError as error:
        message = f"The model call failed: {error.message}"
        raise HandlerError("model_call_failed", message) from error
    content = completion.choices[0].message.content if completion.choices else None
    if content is None:
        raise HandlerError("model_call_failed", "The model reply contains no text.")
    return content


def _rejection(error: APIStatusError) -> str:
    """The platform's error code and message, when its body carries them."""
    body: object = error.body
    message = cast(dict[str, object], body).get("message") if isinstance(body, dict) else None
    if error.code and isinstance(message, str):
        return f"The model call failed with {error.code}: {message}"
    return f"The model call failed with HTTP status {error.status_code}."
