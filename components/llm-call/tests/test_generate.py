"""Functional results use one standard SDK call and preserve exact model text."""

import pytest
from slow_thinker_llm_call import JsonObject, LLMCall
from support.openai_calls import ModelStub, completion, config


@pytest.mark.parametrize("text", ["  ñ\n", ""])
async def test_text_and_canonical_messages(text: str) -> None:
    stub = ModelStub(completion(text))
    async with stub.client() as client:
        result = await LLMCall(config(), client, "bound-model").generate({"z": 1, "a": "ñ"})
    assert result == {"status": "ok", "format": "text", "value": text}
    assert stub.requests == [
        {
            "model": "bound-model",
            "n": 1,
            "stream": False,
            "messages": [
                {"role": "system", "content": "Review the supplied input."},
                {"role": "user", "content": '{"a":"ñ","z":1}'},
            ],
        }
    ]


async def test_json_message_and_validated_value() -> None:
    stub = ModelStub(completion(" [1, 2] \n"))
    schema: JsonObject = {"type": "array", "items": {"type": "integer"}}
    async with stub.client() as client:
        result = await LLMCall(config(schema), client, "bound-model").generate({})
    assert result == {"status": "ok", "format": "json", "value": [1, 2]}
    assert stub.requests[0]["messages"] == [
        {"role": "system", "content": "Review the supplied input."},
        {
            "role": "system",
            "content": "Return exactly one JSON value conforming to this schema, "
            'with no surrounding text:\n{"items":{"type":"integer"},"type":"array"}',
        },
        {"role": "user", "content": "{}"},
    ]


@pytest.mark.parametrize(
    "raw", ['{"a":1,"a":2}', "NaN", "Infinity", "1e9999", "{} {}", "```json\n{}\n```", ""]
)
async def test_invalid_json_is_retained_without_another_call(raw: str) -> None:
    stub = ModelStub(completion(raw))
    async with stub.client() as client:
        result = await LLMCall(config({}), client, "model").generate({})
    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_json"
    assert result["error"]["raw_output"] == raw
    assert result["error"]["issues"][0]["path"] == ""
    assert len(stub.requests) == 1


async def test_schema_error_escapes_json_pointer() -> None:
    raw = '{"a/~b":"wrong"}'
    stub = ModelStub(completion(raw))
    schema: JsonObject = {"type": "object", "properties": {"a/~b": {"type": "integer"}}}
    async with stub.client() as client:
        result = await LLMCall(config(schema), client, "model").generate({})
    assert result["status"] == "error"
    assert result["error"]["code"] == "output_schema_mismatch"
    assert result["error"]["raw_output"] == raw
    assert result["error"]["issues"][0]["path"] == "/a~1~0b"


async def test_input_rejection_occurs_before_dispatch() -> None:
    stub = ModelStub(completion("unused"))
    settings = config()
    settings["input_schema"] = {"type": "object", "required": ["question"]}
    async with stub.client() as client:
        with pytest.raises(ValueError, match="Invalid input"):
            await LLMCall(settings, client, "model").generate({})
    assert not stub.requests


async def test_configuration_and_history_are_not_shared() -> None:
    stub = ModelStub(completion("1"))
    settings = config({"type": "integer"})
    async with stub.client() as client:
        component = LLMCall(settings, client, "model")
        settings["instructions"] = "Changed"
        settings["output"] = {"format": "text"}
        result = await component.generate({"first": 1})
        assert result["status"] == "ok"
        assert result["format"] == "json"
        await component.generate({"second": 2})
    assert stub.requests[1]["messages"] == [
        {"role": "system", "content": "Review the supplied input."},
        {
            "role": "system",
            "content": "Return exactly one JSON value conforming to this schema, "
            'with no surrounding text:\n{"type":"integer"}',
        },
        {"role": "user", "content": '{"second":2}'},
    ]
