"""Configured models, reviewed endpoints and recorded mock HTTP exchanges for adapter tests."""

import dataclasses
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

import httpx
from slow_thinker_ii.adapters.providers import HttpProvider, ProviderEndpoint
from slow_thinker_ii.application import LlmModel, ProviderReply
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object
from support.configuration import llm_models
from support.examples import LUNA

SECRET = "synthetic-provider-key"
OPENAI_URL, DEEPSEEK_URL = "https://api.openai.com/v1", "https://api.deepseek.com"

type Handler = Callable[[httpx.Request], httpx.Response | Awaitable[httpx.Response]]


class Exchanges:
    """A mock provider: `handler` answers and every request is kept."""

    def __init__(self, handler: Handler) -> None:
        self.requests: list[httpx.Request] = []
        self._handler = handler

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self._handle)

    def sent(self) -> JsonObject:
        """The JSON body of the only request."""
        [request] = self.requests
        return json_object(decode_json(request.content.decode("utf-8")))

    async def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        answer = self._handler(request)
        return answer if isinstance(answer, httpx.Response) else await answer


def http_provider(
    handler: Handler, *, timeout: float = 120, limit: int = 524_288
) -> tuple[HttpProvider, Exchanges]:
    """Both reviewed endpoints over a mock transport answering with `handler`."""
    exchanges = Exchanges(handler)
    endpoints = {
        "openai": ProviderEndpoint("openai", OPENAI_URL, SECRET, timeout, limit),
        "deepseek": ProviderEndpoint("deepseek", DEEPSEEK_URL, SECRET, timeout, limit),
    }
    return HttpProvider(endpoints, exchanges.transport()), exchanges


def model(identifier: str = LUNA, **settings: object) -> LlmModel:
    """A model of the step 1 configuration example, with `settings` replaced."""
    configured = next(item for item in llm_models() if item.settings.id == identifier)
    changed = dataclasses.replace(configured.settings, **settings)
    return dataclasses.replace(configured, settings=changed)


def chat(identifier: str = LUNA, **fields: JsonValue) -> JsonObject:
    """A request as the gateway dispatches it: the entry id, one user message and `fields`."""
    request: JsonObject = {
        "model": identifier,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_completion_tokens": 64,
    }
    return {**request, **fields}


def completion(**fields: JsonValue) -> JsonObject:
    """A Chat Completions response; `fields` add or replace members such as `usage`."""
    message: JsonObject = {"role": "assistant", "content": "Hello.", "reasoning_content": "Hm."}
    body: JsonObject = {
        "id": "chatcmpl-fixture",
        "object": "chat.completion",
        "created": 1790918959,
        "model": "gpt-6-luna",
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
    }
    return {**body, **fields}


def openai_usage() -> JsonObject:
    details: JsonObject = {"audio_tokens": 0, "cache_write_tokens": 2, "cached_tokens": 4}
    return {
        "completion_tokens": 165,
        "prompt_tokens": 135,
        "prompt_tokens_details": details,
        "total_tokens": 300,
    }


def deepseek_usage() -> JsonObject:
    return {
        "completion_tokens": 215,
        "prompt_cache_hit_tokens": 64,
        "prompt_cache_miss_tokens": 430,
        "prompt_tokens": 494,
        "prompt_tokens_details": {"cached_tokens": 64},
        "total_tokens": 709,
    }


def error_of(reply: ProviderReply) -> JsonObject:
    return json_object(reply.body["error"])


def text_of(reply: ProviderReply) -> str:
    """The content of the reply's first choice."""
    choices = reply.body["choices"]
    assert isinstance(choices, list)
    content = json_object(json_object(choices[0])["message"])["content"]
    assert isinstance(content, str)
    return content


def assert_timed(reply: ProviderReply, before: datetime) -> None:
    """Aware UTC start and end times, in order, within the test's own interval."""
    assert reply.started_at.tzinfo is UTC and reply.ended_at.tzinfo is UTC
    assert before <= reply.started_at <= reply.ended_at <= datetime.now(UTC)
