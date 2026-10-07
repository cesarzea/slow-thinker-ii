"""Each adapter sends the reviewed model name and maps fields as the contract's table states."""

import httpx
import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue
from support.examples import FLASH, LUNA

from .fixtures import chat, completion, error_of, http_provider, model

SCHEMA_FORMAT: JsonObject = {
    "type": "json_schema",
    "json_schema": {"name": "output", "schema": {"type": "object"}, "strict": False},
}


def answer(request: httpx.Request) -> httpx.Response:
    del request
    return httpx.Response(200, json=completion())


async def test_openai_keeps_every_field_and_adds_the_reviewed_settings() -> None:
    provider, exchanges = http_provider(answer)
    request = chat(LUNA, response_format=SCHEMA_FORMAT)
    reply = await provider.complete(model(LUNA), request, 30)
    assert reply.status == 200
    assert exchanges.sent() == {
        **request,
        "model": "gpt-6-luna",
        "reasoning_effort": "none",
        "store": False,
        "service_tier": "default",
    }


async def test_openai_keeps_a_requested_reasoning_effort() -> None:
    provider, exchanges = http_provider(answer)
    choices = model(LUNA, reasoning_efforts=("none", "low"))
    await provider.complete(choices, chat(LUNA, reasoning_effort="low", temperature=0.5), 30)
    sent = exchanges.sent()
    assert (sent["reasoning_effort"], sent["temperature"]) == ("low", 0.5)


@pytest.mark.parametrize("identifier", [LUNA, FLASH])
async def test_a_model_without_reviewed_efforts_sends_no_reasoning(identifier: str) -> None:
    provider, exchanges = http_provider(answer)
    await provider.complete(model(identifier, reasoning_efforts=()), chat(identifier), 30)
    sent = exchanges.sent()
    assert "reasoning_effort" not in sent and "thinking" not in sent


@pytest.mark.parametrize("effort", ["none", "low", "high", "max"])
async def test_deepseek_maps_the_output_limit_and_thinking(effort: str) -> None:
    provider, exchanges = http_provider(answer)
    request = chat(FLASH, reasoning_effort=effort, max_completion_tokens=17)
    await provider.complete(model(FLASH), request, 30)
    sent = exchanges.sent()
    assert sent["model"] == "deepseek-flash" and sent["max_tokens"] == 17
    assert "max_completion_tokens" not in sent and "store" not in sent
    assert sent["thinking"] == {"type": "disabled" if effort == "none" else "enabled"}
    assert sent.get("reasoning_effort") == (None if effort == "none" else effort)


async def test_deepseek_passes_temperature_format_and_text_roles_unchanged() -> None:
    provider, exchanges = http_provider(answer)
    messages: list[JsonValue] = [
        {"role": role, "content": "x"} for role in ("system", "user", "assistant", "user")
    ]
    fields: JsonObject = {"temperature": 0.25, "response_format": {"type": "json_object"}}
    request = chat(FLASH, messages=messages, reasoning_effort="none", **fields)
    await provider.complete(model(FLASH), request, 30)
    assert exchanges.sent() == {
        "model": "deepseek-flash",
        "messages": messages,
        "max_tokens": 64,
        "thinking": {"type": "disabled"},
        **fields,
    }


async def test_deepseek_adds_no_output_limit_that_was_not_requested() -> None:
    provider, exchanges = http_provider(answer)
    request: JsonObject = {"model": FLASH, "messages": [{"role": "user", "content": "x"}]}
    await provider.complete(model(FLASH), request, 30)
    sent = exchanges.sent()
    assert "max_tokens" not in sent and "max_completion_tokens" not in sent


@pytest.mark.parametrize(
    ("efforts", "thinking"), [(("none", "low"), "disabled"), (("high",), "enabled")]
)
async def test_deepseek_without_an_effort_uses_the_reviewed_default(
    efforts: tuple[str, ...], thinking: str
) -> None:
    provider, exchanges = http_provider(answer)
    await provider.complete(model(FLASH, reasoning_efforts=efforts), chat(FLASH), 30)
    sent = exchanges.sent()
    assert sent["thinking"] == {"type": thinking}
    assert sent.get("reasoning_effort") == (None if efforts[0] == "none" else efforts[0])


@pytest.mark.parametrize("role", ["developer", "tool"])
async def test_deepseek_refuses_other_roles_without_contacting_the_provider(role: str) -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"A {request.method} request must not be sent")

    provider, exchanges = http_provider(refuse)
    request = chat(FLASH, messages=[{"role": role, "content": "x"}])
    reply = await provider.complete(model(FLASH), request, 30)
    assert reply.status == 502 and not exchanges.requests
    assert error_of(reply) == {
        "code": "provider_error",
        "message": "DeepSeek accepts only system, user and assistant messages.",
        "type": "provider_error",
    }
