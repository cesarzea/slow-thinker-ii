"""Deterministic native provider evidence and trusted resource configuration."""

import time

import httpx2
from slow_thinker_host import Invocation, JsonObject
from slow_thinker_model_provider import (
    ModelProviderConfig,
    ModelProviderHost,
    ProviderEndpoint,
    ProviderTransport,
    effective_operation,
    parse_config,
)

SECRET = "synthetic-model-provider-key"


def record(provider: str = "deepseek") -> JsonObject:
    return {
        "provider": provider,
        "model": "deepseek-flash" if provider == "deepseek" else "gpt-6-luna",
        "model_alias": "bound-model",
        "default_output_tokens": 8,
        "maximum_output_tokens": 32,
        "reasoning_efforts": ["none", "low", "high", "max"] if provider == "deepseek" else ["none"],
    }


def config(provider: str = "deepseek") -> ModelProviderConfig:
    return parse_config(record(provider))


def arguments() -> JsonObject:
    return {"request": {"model": "bound-model", "messages": [{"role": "user", "content": "hello"}]}}


def invocation(seconds: float = 5) -> Invocation:
    return Invocation("scoped-model-grant", time.monotonic() + seconds)


def host(transport: httpx2.AsyncBaseTransport, limit: int = 524_288) -> ModelProviderHost:
    selected = config()
    endpoint = ProviderEndpoint(
        "deepseek", "https://api.deepseek.com", SECRET, max_response_bytes=limit
    )
    return ModelProviderHost(
        selected, effective_operation(selected), ProviderTransport(endpoint, transport)
    )


def response() -> JsonObject:
    return {
        "id": "completion-fixture",
        "model": "deepseek-flash",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "answer",
                    "reasoning_content": "native reasoning",
                }
            }
        ],
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 3,
            "total_tokens": 15,
            "prompt_cache_hit_tokens": 4,
            "prompt_cache_miss_tokens": 8,
        },
        "future_field": {"retained": True},
    }
