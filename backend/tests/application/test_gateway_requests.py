"""Gateway checks before any reservation: grant, request shape, selected entry, parameters."""

import pytest
from slow_thinker_ii.contracts import JsonValue, decode_json, encode_json
from support.examples import FLASH, J2, LUNA
from support.platform import Platform

from .held import body, calls, error_code, held_call, stopped

NUMBERED = encode_json({"model": 1, "messages": [{"role": "user", "content": "Hi"}]})


async def test_unknown_and_expired_grants_are_rejected_without_a_record() -> None:
    platform = Platform()
    context = await held_call(platform)
    unknown = await platform.gateway.complete("not-a-grant", body())
    assert error_code(unknown) == (401, "invalid_grant")
    assert unknown.body["error"] == {
        "code": "invalid_grant",
        "message": "The grant is missing, unknown or expired.",
        "type": "authentication_error",
    }
    platform.clock.advance(300)
    expired = await platform.gateway.complete(context.grant, body())
    assert error_code(expired) == (401, "invalid_grant")
    assert calls(platform, context) == []
    await stopped(platform, context)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("{", "The request body is not valid JSON."),
        ("[]", "The request body must be a JSON object."),
        (body(stream=True), 'Streaming is not supported; send "stream": false or omit it.'),
        (body(n=2), 'Only one choice is supported; send "n": 1 or omit it.'),
        (body(n=True), 'Only one choice is supported; send "n": 1 or omit it.'),
        (body(tools=[]), 'The field "tools" is not supported.'),
        (body(messages=[]), 'The field "messages" must list 1 to 100 messages.'),
        (body(messages=[{"role": "user", "content": "Hi"} for _ in range(101)]), "1 to 100"),
        (body(messages=[{"role": "tool", "content": "Hi"}]), "Message 0 must have only a role"),
        (body(messages=[{"role": "user", "content": ["Hi"]}]), "Message 0 must have only a role"),
        (body(messages=[{"role": "user", "content": "Hi", "name": "a"}]), "Message 0 must"),
        (NUMBERED, 'The field "model" must name a catalog entry.'),
        (body(response_format={"type": "xml"}), '"response_format" is not supported'),
        (body(response_format="text"), '"response_format" is not supported'),
        (body(response_format={"type": "text", "x": 1}), '"response_format" is not supported'),
        (body(response_format={"type": "json_schema", "json_schema": []}), "response_format"),
        (body(response_format={"type": "json_schema", "json_schema": {"x": 1}}), "response_"),
        (body(response_format={"type": "json_schema", "json_schema": {}}), "response_format"),
    ],
)
async def test_malformed_requests_are_invalid(text: str, message: str) -> None:
    platform = Platform()
    context = await held_call(platform)
    reply = await platform.gateway.complete(context.grant, text)
    assert error_code(reply) == (400, "invalid_request")
    error = reply.body["error"]
    assert isinstance(error, dict) and isinstance(error["message"], str)
    assert message in error["message"]
    assert error["type"] == "invalid_request_error"
    [recorded] = calls(platform, context)
    assert (recorded["status"], recorded["request"], recorded["llm"]) == (400, text, None)
    assert (recorded["reserved_usd"], recorded["cost_usd"]) == ("0.000000000", "0.000000000")
    assert platform.provider.requests == [] and platform.ledger.rows == {}
    await stopped(platform, context)


@pytest.mark.parametrize("model", [FLASH, "openai/unknown"])
async def test_only_the_selected_entry_may_be_called(model: str) -> None:
    platform = Platform()
    context = await held_call(platform)
    reply = await platform.gateway.complete(context.grant, body(model))
    assert error_code(reply) == (403, "model_not_allowed")
    error = reply.body["error"]
    assert isinstance(error, dict) and error["type"] == "permission_error"
    assert error["message"] == (
        f"The model “{model}” is not selected in this component's configuration."
    )
    [recorded] = calls(platform, context)
    assert (recorded["llm"], recorded["provider_model"], recorded["status"]) == (model, None, 403)
    await stopped(platform, context)


@pytest.mark.parametrize(
    ("fields", "problem"),
    [
        ({"max_completion_tokens": 200_000}, "Max output tokens must be at most 128000."),
        ({"max_completion_tokens": 0}, "Max output tokens must be at least 1."),
        ({"max_completion_tokens": "300"}, "Max output tokens has the wrong type."),
        ({"temperature": 0.5}, "Temperature is invalid."),
    ],
)
async def test_parameters_outside_the_entry_schema_are_invalid(
    fields: dict[str, JsonValue], problem: str
) -> None:
    platform = Platform()
    context = await held_call(platform)
    reply = await platform.gateway.complete(context.grant, body(**fields))
    assert error_code(reply) == (400, "invalid_request")
    error = reply.body["error"]
    assert isinstance(error, dict) and isinstance(error["message"], str)
    assert error["message"] == f"Invalid parameters: {problem}"
    assert platform.provider.requests == []
    await stopped(platform, context)


async def test_defaults_fill_missing_parameters_unless_a_condition_forbids_them() -> None:
    platform = Platform()
    context = await held_call(platform, J2)
    replies = [
        await platform.gateway.complete(context.grant, body(FLASH, **fields))
        for fields in ({}, {"reasoning_effort": "high"}, {"stream": False, "n": 1})
    ]
    assert [reply.status for reply in replies] == [200, 200, 200]
    sent = [request.request for request in platform.provider.requests]
    parameters = [
        {key: value for key, value in request.items() if key not in ("model", "messages")}
        for request in sent
    ]
    assert parameters == [
        {"reasoning_effort": "none", "temperature": 1, "max_completion_tokens": 1024},
        {"reasoning_effort": "high", "max_completion_tokens": 1024},
        {"reasoning_effort": "none", "temperature": 1, "max_completion_tokens": 1024},
    ]
    content = decode_json(body(FLASH))
    assert isinstance(content, dict)
    assert [entry["request"] for entry in calls(platform, context)][0] == {
        **content,
        **parameters[0],
    }
    await stopped(platform, context)


async def test_a_luna_request_receives_its_default_output_limit() -> None:
    platform = Platform()
    context = await held_call(platform)
    response_format: JsonValue = {
        "type": "json_schema",
        "json_schema": {"name": "x", "strict": True},
    }
    reply = await platform.gateway.complete(context.grant, body(response_format=response_format))
    assert reply.status == 200
    request = platform.provider.requests[0].request
    assert (request["model"], request["max_completion_tokens"]) == (LUNA, 1024)
    assert request["response_format"] == response_format
    await stopped(platform, context)
