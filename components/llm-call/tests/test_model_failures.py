"""Every LLM Call failure code, with exactly one model request and no repair attempt."""

import httpx2
import pytest
from llm_call_fakes import SCORE, FakeContext, completion, config, platform_error
from slow_thinker_host import HandlerError, JsonObject, JsonValue
from slow_thinker_llm_call import LLMCall, parse_config

JSON_OUTPUT: JsonValue = {"type": "json", "schema": SCORE}


async def failure(context: FakeContext, settings: JsonObject, message: JsonValue) -> HandlerError:
    with pytest.raises(HandlerError) as caught:
        await LLMCall(parse_config(settings)).activate(message, context)
    return caught.value


async def test_input_format_mismatch_fails_before_any_model_call() -> None:
    context = FakeContext()
    settings = config(input_format={"type": "object", "required": ["story"]})
    error = await failure(context, settings, "plain text")
    assert error.code == "input_format_mismatch"
    assert error.message == (
        "The received message does not match the input format: 'plain text' is not of type 'object'"
    )
    assert not context.requests and not context.reports


@pytest.mark.parametrize("reply", ["Sure! " + "x" * 300, '{"score": 1, "score": 2}', "NaN", ""])
async def test_invalid_json_keeps_the_start_of_the_reply(reply: str) -> None:
    context = FakeContext(completion(reply))
    error = await failure(context, config(output_format=JSON_OUTPUT), "story")
    assert error.code == "invalid_json"
    assert error.message.startswith("The reply is not valid JSON (")
    assert error.message.endswith(f"Reply: {reply[:200]}")
    assert len(context.requests) == 1
    assert context.steps()[-1] == "reply failed validation: invalid_json"


async def test_schema_mismatch_names_the_violation_and_keeps_the_reply() -> None:
    context = FakeContext(completion('{"score": 11}'))
    error = await failure(context, config(output_format=JSON_OUTPUT), "story")
    assert error.code == "schema_mismatch"
    assert error.message == (
        "The reply does not match the output schema: /score: 11 is greater than the maximum "
        'of 10. Reply: {"score": 11}'
    )
    assert len(context.requests) == 1
    assert context.steps()[-1] == "reply failed validation: schema_mismatch"


@pytest.mark.parametrize(
    ("status", "code", "text"),
    [
        (402, "budget_exhausted", "The run budget is exhausted."),
        (403, "model_not_allowed", "The entry is not selected in the caller's configuration."),
        (502, "provider_error", "The provider failed."),
        (504, "provider_timeout", "No complete response within the time budget."),
    ],
)
async def test_platform_errors_keep_their_code_and_message(
    status: int, code: str, text: str
) -> None:
    context = FakeContext(platform_error(code, text), status)
    error = await failure(context, config(), "story")
    assert error.code == "model_call_failed"
    assert error.message == f"The model call failed with {code}: {text}"
    assert len(context.requests) == 1
    assert context.steps() == ["messages built: 2 messages"]


async def test_an_error_without_a_platform_body_names_the_status() -> None:
    context = FakeContext({"detail": "gateway"}, 503)
    error = await failure(context, config(), "story")
    assert error.message == "The model call failed with HTTP status 503."


async def test_an_unreachable_endpoint_fails_the_call_without_retry() -> None:
    context = FakeContext()
    context.failure = httpx2.ConnectError("connection refused")
    error = await failure(context, config(), "story")
    assert error.code == "model_call_failed"
    assert error.message == "The model call failed: Connection error."
    assert len(context.requests) == 1


async def test_a_client_timeout_is_the_budget_expiring() -> None:
    context = FakeContext()
    context.failure = httpx2.ReadTimeout("no reply")
    error = await failure(context, config(), "story")
    assert (error.code, error.message) == (
        "timeout",
        "The model call did not finish within the call's time budget.",
    )
    assert len(context.requests) == 1


@pytest.mark.parametrize("reply", [completion(None), {**completion("unused"), "choices": []}])
async def test_a_reply_without_text_fails_the_call(reply: JsonObject) -> None:
    error = await failure(FakeContext(reply), config(), "story")
    assert (error.code, error.message) == (
        "model_call_failed",
        "The model reply contains no text.",
    )
