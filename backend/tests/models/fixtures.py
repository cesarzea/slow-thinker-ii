"""Public immutable model policies and deterministic native usage/timing evidence."""

from datetime import UTC, datetime

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.adapters.models import ModelPricePolicy, ModelProfile
from slow_thinker_ii.adapters.tariffs import parse_catalog, parse_deepseek_pricing
from slow_thinker_ii.contracts import JsonObject, OperationResult, encode_json
from support.catalog import PAYLOAD
from support.openai_calls import completion
from support.preparation import NOW
from support.workspace_tariffs import DEEPSEEK_PAYLOAD


def revision(provider: str = "deepseek") -> TariffRevision:
    return (
        parse_catalog(PAYLOAD, NOW)
        if provider == "openai"
        else parse_deepseek_pricing(DEEPSEEK_PAYLOAD, NOW)
    )


def profile(provider: str = "deepseek") -> ModelProfile:
    name = "openai" if provider == "openai" else "deepseek"
    selected = revision(name)
    return ModelProfile(selected, name, "bound-model", 8, 32, (selected.tariff.model,))


def policy(provider: str = "deepseek") -> ModelPricePolicy:
    return ModelPricePolicy(profile(provider))


def arguments(**options: object) -> str:
    value: JsonObject = {"model": "bound-model", "messages": [{"role": "user", "content": "hello"}]}
    for key, item in options.items():
        if isinstance(item, str | int | float | bool) or item is None:
            value[key] = item
        else:
            raise ValueError("Fixture generation options must be scalar")
    return encode_json({"request": value})


def utc(value: str) -> float:
    return datetime.fromisoformat(value).replace(tzinfo=UTC).timestamp()


def native_response() -> JsonObject:
    body = completion("answer")
    body.update(model="deepseek-flash", created=int(utc("2026-06-22T02:00:00")))
    body["usage"] = {
        "prompt_tokens": 12,
        "completion_tokens": 3,
        "total_tokens": 15,
        "prompt_cache_hit_tokens": 4,
        "prompt_cache_miss_tokens": 8,
        "completion_tokens_details": {"reasoning_tokens": 2},
    }
    body["choices"] = [
        {
            "index": 0,
            "finish_reason": "stop",
            "message": {
                "role": "assistant",
                "content": "answer",
                "reasoning_content": "native reasoning",
            },
        }
    ]
    return body


def payload(start: str = "2026-06-22T02:00:00", finish: str | None = None) -> JsonObject:
    first = utc(start)
    last = first + 0.1 if finish is None else utc(finish)
    body = native_response()
    body["created"] = int(first)
    return {
        "response": body,
        "transport": {"request_started_at": first, "response_finished_at": last},
    }


def result(value: JsonObject, *, error: bool = False) -> OperationResult:
    return OperationResult(encode_json(value), error)
