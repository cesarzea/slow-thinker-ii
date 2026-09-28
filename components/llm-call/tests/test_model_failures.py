"""HTTP success is not proof of a usable completion; retries remain explicit."""

import pytest
from openai import APIStatusError, APITimeoutError
from slow_thinker_host import JsonObject
from slow_thinker_llm_call import LLMCall, ModelOperationError
from support.openai_calls import ModelStub, completion, config


@pytest.mark.parametrize(
    "reason,expected",
    [
        ("length", "incomplete_response"),
        ("content_filter", "provider_refusal"),
        ("tool_calls", "unsupported_response"),
        ("function_call", "unsupported_response"),
        ("future_reason", "unsupported_response"),
    ],
)
async def test_unusable_finish_reason_never_exposes_valid_json(reason: str, expected: str) -> None:
    stub = ModelStub(completion("{}", reason))
    async with stub.client() as client:
        with pytest.raises(ModelOperationError) as caught:
            await LLMCall(config({}), client, "model").generate({})
    assert caught.value.code == expected and len(stub.requests) == 1


@pytest.mark.parametrize(
    "change,expected",
    [
        ({"refusal": ""}, "provider_refusal"),
        ({"content": None}, "missing_text"),
        ({"content": 7}, "missing_text"),
        ({"role": "user"}, "provider_response_invalid"),
        (
            {
                "tool_calls": [
                    {
                        "id": "tool",
                        "type": "function",
                        "function": {"name": "test", "arguments": "{}"},
                    }
                ]
            },
            "unsupported_response",
        ),
    ],
)
async def test_message_failures_are_distinct(change: JsonObject, expected: str) -> None:
    response = completion("text")
    response["choices"] = [
        {
            "index": 0,
            "finish_reason": "stop",
            "message": {"role": "assistant", "content": "text", **change},
        }
    ]
    stub = ModelStub(response)
    async with stub.client() as client:
        with pytest.raises(ModelOperationError) as caught:
            await LLMCall(config(), client, "model").generate({})
    assert caught.value.code == expected


@pytest.mark.parametrize("status", [429, 500, 503])
async def test_sdk_status_errors_are_not_retried(status: int) -> None:
    stub = ModelStub({"error": {"message": "fixture failure", "type": "fixture"}}, status)
    async with stub.client() as client:
        with pytest.raises(APIStatusError):
            await LLMCall(config(), client, "model").generate({})
    assert len(stub.requests) == 1


async def test_ambiguous_timeout_is_not_retried() -> None:
    stub = ModelStub(completion("unused"))
    stub.timeout = True
    async with stub.client() as client:
        with pytest.raises(APITimeoutError):
            await LLMCall(config(), client, "model").generate({})
    assert len(stub.requests) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"object": "wrong"},
        {"id": 7},
        {"model": ""},
        {"choices": []},
        {"choices": None},
        {
            "choices": [
                {
                    "index": 1,
                    "message": {"role": "assistant", "content": "text"},
                    "finish_reason": "stop",
                }
            ]
        },
    ],
)
async def test_invalid_native_response_is_rejected(change: JsonObject) -> None:
    response = completion("text")
    response.update(change)
    stub = ModelStub(response)
    async with stub.client() as client:
        with pytest.raises(ModelOperationError, match="provider_response_invalid"):
            await LLMCall(config(), client, "model").generate({})
