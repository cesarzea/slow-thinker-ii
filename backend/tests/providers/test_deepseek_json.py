"""DeepSeek's JSON output supports only `json_object`: a JSON Schema becomes an instruction.

OpenAI keeps `json_schema` unchanged (see `test_requests.py`).
"""

import copy

import httpx
import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue
from support.examples import FLASH

from .fixtures import chat, completion, http_provider, model

INSTRUCTION = "Answer with one JSON object that conforms to this JSON Schema: "
SCORE_TEXT = (
    '{"properties":{"score":{"maximum":10,"minimum":1,"type":"integer"}},'
    '"required":["score"],"type":"object"}'
)


def answer(request: httpx.Request) -> httpx.Response:
    del request
    return httpx.Response(200, json=completion())


def schema_format(schema: JsonValue) -> JsonObject:
    definition: JsonObject = {"name": "output", "schema": schema, "strict": False}
    return {"type": "json_schema", "json_schema": definition}


def score_format() -> JsonObject:
    score: JsonObject = {"type": "integer", "minimum": 1, "maximum": 10}
    return schema_format({"type": "object", "required": ["score"], "properties": {"score": score}})


async def sent(request: JsonObject) -> JsonObject:
    """What the DeepSeek adapter sends for `request`, which stays as the gateway recorded it."""
    original = copy.deepcopy(request)
    provider, exchanges = http_provider(answer)
    reply = await provider.complete(model(FLASH), request, 30)
    assert reply.status == 200 and request == original
    return exchanges.sent()


async def test_the_instruction_follows_a_leading_system_message() -> None:
    messages: list[JsonValue] = [
        {"role": "system", "content": "Rate how funny this story is."},
        {"role": "user", "content": "A cat tried to learn to fly."},
    ]
    request = chat(FLASH, messages=messages, response_format=score_format())
    native = await sent({**request, "reasoning_effort": "none"})
    assert native["response_format"] == {"type": "json_object"}
    assert native["messages"] == [
        {
            "role": "system",
            "content": f"Rate how funny this story is.\n\n{INSTRUCTION}{SCORE_TEXT}",
        },
        messages[1],
    ]
    assert (native["max_tokens"], native["thinking"]) == (64, {"type": "disabled"})


async def test_without_a_leading_system_message_the_instruction_comes_first() -> None:
    messages: list[JsonValue] = [
        {"role": "user", "content": "A cat tried to learn to fly."},
        {"role": "system", "content": "A later system message."},
    ]
    native = await sent(chat(FLASH, messages=messages, response_format=score_format()))
    assert native["response_format"] == {"type": "json_object"}
    assert native["messages"] == [
        {"role": "system", "content": INSTRUCTION + SCORE_TEXT},
        *messages,
    ]


@pytest.mark.parametrize(
    ("response_format", "schema_text"),
    [
        (
            schema_format(
                {
                    "type": "object",
                    "description": "Puntuación «graciosa»",
                    "properties": {"b": {"type": "string"}, "a": {"enum": [2, 1]}},
                }
            ),
            '{"description":"Puntuación «graciosa»",'
            '"properties":{"a":{"enum":[2,1]},"b":{"type":"string"}},"type":"object"}',
        ),
        ({"type": "json_schema", "json_schema": {"name": "output"}}, "{}"),
        ({"type": "json_schema"}, "{}"),
    ],
)
async def test_the_schema_is_named_as_canonical_json(
    response_format: JsonObject, schema_text: str
) -> None:
    native = await sent(chat(FLASH, response_format=response_format))
    assert native["response_format"] == {"type": "json_object"}
    assert native["messages"] == [
        {"role": "system", "content": INSTRUCTION + schema_text},
        {"role": "user", "content": "Hi"},
    ]


@pytest.mark.parametrize("response_format", [None, {"type": "text"}, {"type": "json_object"}])
async def test_other_formats_and_their_messages_are_unchanged(response_format: JsonValue) -> None:
    fields: JsonObject = {} if response_format is None else {"response_format": response_format}
    request = chat(FLASH, **fields)
    native = await sent(request)
    assert native.get("response_format") == response_format
    assert native["messages"] == request["messages"]
