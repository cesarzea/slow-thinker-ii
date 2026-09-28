"""Ordinary OpenAI clients cross the HTTP gateway into authorized, metered child calls."""

from pathlib import Path

import pytest
from openai import APIStatusError, RateLimitError
from slow_thinker_ii.contracts import JsonObject, OperationResult, encode_json
from support.native_gateway import assert_recorded, native_case, sdk_client
from support.native_server import gateway_app, serve
from support.run_admission import outstanding


async def test_native_sdk_response_and_usage_survive_the_managed_route(tmp_path: Path) -> None:
    case = native_case(tmp_path)
    async with serve(gateway_app(case.gateway)) as port, sdk_client(port, case.parent.token) as sdk:
        raw = await sdk.chat.completions.with_raw_response.create(
            model="bound-model", messages=[{"role": "user", "content": "x"}]
        )
        result = raw.parse()
        assert result.choices[0].message.content == "success"
        assert result.model_extra == {"future_field": {"kept": True}}
        assert raw.headers["x-request-id"] == "req_fixture"
    assert len(case.model.calls) == 1 and case.model.calls[0]["model"] == "gpt-6-luna"
    assert_recorded(case)
    await case.calls.close(1)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500, 503])
async def test_native_sdk_receives_original_provider_errors(tmp_path: Path, status: int) -> None:
    case = native_case(tmp_path)
    error: JsonObject = {
        "error": {"message": "provider fixture", "type": "provider_type", "code": "provider_code"}
    }
    payload: JsonObject = {
        "error": {"origin": "provider", "status": status, "body": error, "request_id": "req_error"}
    }
    case.model.result = OperationResult(encode_json(payload), True)
    async with serve(gateway_app(case.gateway)) as port, sdk_client(port, case.parent.token) as sdk:
        with pytest.raises(APIStatusError) as caught:
            await sdk.chat.completions.create(
                model="bound-model", messages=[{"role": "user", "content": "x"}]
            )
    assert caught.value.status_code == status and caught.value.request_id == "req_error"
    assert caught.value.body == error["error"]
    assert len(case.model.calls) == 1 and outstanding(case.run) == (262_506_000,) * 3
    await case.calls.close(1)


async def test_budget_denial_never_invokes_the_model_and_is_not_a_provider_error(
    tmp_path: Path,
) -> None:
    case = native_case(tmp_path, cap=1000)
    async with serve(gateway_app(case.gateway)) as port, sdk_client(port, case.parent.token) as sdk:
        with pytest.raises(RateLimitError) as caught:
            await sdk.chat.completions.create(
                model="bound-model", messages=[{"role": "user", "content": "x"}]
            )
    assert caught.value.code == "budget_denied" and "platform" in str(caught.value.body)
    assert not case.model.calls and outstanding(case.run) == (0, 0, 0)
    with case.run.store.begin() as transaction:
        assert transaction.run("run").reason == "budget_denied"
