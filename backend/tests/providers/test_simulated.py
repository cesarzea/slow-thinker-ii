"""The simulated provider: scripted replies cycle per model; other replies derive from requests."""

from datetime import UTC, datetime

import pytest
from slow_thinker_ii.accounting import Usage
from slow_thinker_ii.adapters.providers import SimulatedProvider
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from support.examples import FLASH, LUNA

from .fixtures import assert_timed, chat, model, text_of

SCORE_FORMAT: JsonObject = {
    "type": "json_schema",
    "json_schema": {
        "name": "output",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score"],
            "properties": {"score": {"type": "integer", "minimum": 1, "maximum": 10}},
        },
        "strict": False,
    },
}


async def answers(provider: SimulatedProvider, identifier: str, count: int) -> list[str]:
    """The contents of `count` calls, each with a different request."""
    replies = [
        await provider.complete(model(identifier), chat(identifier, seed=index), 30)
        for index in range(count)
    ]
    return [text_of(reply) for reply in replies]


async def test_a_reply_is_a_chat_completion_with_deterministic_usage() -> None:
    request = chat(FLASH, messages=[{"role": "user", "content": "Ünïcode story"}])
    before = datetime.now(UTC)
    reply = await SimulatedProvider().complete(model(FLASH), request, 30)
    text = "Simulated reply to: Ünïcode story"
    sent, replied = len(encode_json(request).encode()), len(text.encode())
    usage = Usage(-(-sent // 4), 0, 0, -(-replied // 4))
    assert (reply.status, reply.usage) == (200, usage)
    assert reply.body == {
        "id": "chatcmpl-simulated",
        "object": "chat.completion",
        "created": 0,
        "model": "deepseek-flash",
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
        ],
        "usage": {
            "prompt_tokens": usage.input,
            "completion_tokens": usage.output,
            "total_tokens": usage.input + usage.output,
        },
    }
    assert_timed(reply, before)


async def test_the_same_request_gets_the_same_reply() -> None:
    request = chat(LUNA, response_format=SCORE_FORMAT)
    first = await SimulatedProvider().complete(model(LUNA), request, 30)
    second = await SimulatedProvider().complete(model(LUNA), request, 30)
    assert (first.status, first.body, first.usage) == (second.status, second.body, second.usage)


@pytest.mark.parametrize(
    ("messages", "echoed"),
    [
        (
            [
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": "Earlier."},
                {"role": "user", "content": "A" * 300},
                {"role": "assistant", "content": "Later."},
            ],
            "A" * 200,
        ),
        ([{"role": "system", "content": "Only a system prompt."}], ""),
        ([{"role": "user", "content": None}], ""),
        (None, ""),
    ],
)
async def test_the_default_reply_echoes_the_last_user_message(
    messages: JsonValue, echoed: str
) -> None:
    reply = await SimulatedProvider().complete(model(LUNA), chat(LUNA, messages=messages), 30)
    assert text_of(reply) == f"Simulated reply to: {echoed}"


async def test_scripted_replies_cycle_per_model_across_requests() -> None:
    provider = SimulatedProvider({FLASH: ('{"score": 5}', '{"score": 8}', "third"), LUNA: ()})
    assert await answers(provider, FLASH, 4) == ['{"score": 5}', '{"score": 8}', "third"] + [
        '{"score": 5}'
    ]
    assert await answers(provider, LUNA, 1) == ["Simulated reply to: Hi"]
    assert await answers(provider, FLASH, 1) == ['{"score": 8}']


async def test_scripted_replies_take_precedence_over_a_requested_schema() -> None:
    provider = SimulatedProvider({FLASH: ("not JSON at all",)})
    reply = await provider.complete(model(FLASH), chat(FLASH, response_format=SCORE_FORMAT), 30)
    assert text_of(reply) == "not JSON at all"


@pytest.mark.parametrize(
    ("response_format", "expected"),
    [
        (SCORE_FORMAT, '{"score":10}'),
        ({"type": "json_schema", "json_schema": {"name": "output"}}, "{}"),
        ({"type": "json_schema"}, "{}"),
        ({"type": "json_object"}, "{}"),
        ({"type": "text"}, "Simulated reply to: Hi"),
        ("json", "Simulated reply to: Hi"),
    ],
)
async def test_json_output_is_the_smallest_instance(
    response_format: JsonValue, expected: str
) -> None:
    request = chat(FLASH, response_format=response_format)
    reply = await SimulatedProvider().complete(model(FLASH), request, 30)
    assert text_of(reply) == expected
