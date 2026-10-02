"""Ordinary SDK and LangChain share managed transport and accounting."""

import time
from pathlib import Path

import pytest
from langchain_openai import ChatOpenAI
from openai import APIStatusError
from openai.types.chat import ChatCompletionMessageParam
from pydantic import SecretStr
from slow_thinker_ii.contracts import JsonObject, json_object
from support.native_gateway import sdk_client
from support.native_server import gateway_app, serve
from support.run_admission import outstanding

from models.fixtures import utc
from models.mediation_assertions import assert_managed, assert_provider_selection
from models.mediation_fixture import model_case


async def test_two_bound_providers_preserve_native_identity_and_shared_accounting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(time, "time", lambda: utc("2026-06-22T02:00:00"))
    case = model_case(tmp_path, separate_agents=True)
    async with (
        serve(gateway_app(case.gateway)) as port,
        sdk_client(port, case.parent.token) as sdk,
        sdk_client(port, case.deepseek_parent.token) as second,
    ):
        openai = await sdk.chat.completions.create(
            model="openai", messages=[{"role": "user", "content": "first"}]
        )
        deepseek = await second.chat.completions.with_raw_response.create(
            model="deepseek",
            messages=[{"role": "user", "content": "second"}],
            reasoning_effort="high",
        )
        assert openai.model == "gpt-6-luna" and deepseek.parse().model == "deepseek-flash"
        assert deepseek.headers["x-request-id"] == "req-bound-model"
        assert deepseek.parse().choices[0].message.model_extra == {
            "reasoning_content": "native reasoning"
        }
    assert_provider_selection(case)
    assert_managed(case, 8414, 2)
    await case.calls.close(1)


async def test_langchain_uses_same_reasoning_authority_and_price_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(time, "time", lambda: utc("2026-06-22T02:00:00"))
    case = model_case(tmp_path)
    async with serve(gateway_app(case.gateway)) as port:
        model = ChatOpenAI(
            model="deepseek",
            reasoning_effort="low",
            api_key=SecretStr(case.parent.token),
            base_url=f"http://127.0.0.1:{port}/v1",
            max_retries=0,
            timeout=5,
            use_responses_api=False,
            stream_usage=False,
        )
        try:
            assert (await model.ainvoke("normal invocation")).content == "answer"
        finally:
            await model.root_async_client.close()
            model.root_client.close()
    assert case.deepseek.native_requests[0]["reasoning_effort"] == "low"
    assert_managed(case, 6024, 1)
    await case.calls.close(1)


@pytest.mark.parametrize("fault", ["reasoning", "developer", "budget", "permission"])
async def test_invalid_request_or_authority_never_reaches_native_provider(
    tmp_path: Path, fault: str
) -> None:
    case = model_case(
        tmp_path, permitted=fault != "permission", cap=1000 if fault == "budget" else 1_000_000_000
    )
    async with serve(gateway_app(case.gateway)) as port, sdk_client(port, case.parent.token) as sdk:
        with pytest.raises(APIStatusError):
            await sdk.chat.completions.create(
                model="deepseek",
                reasoning_effort="medium" if fault == "reasoning" else "none",
                messages=invalid_messages(fault),
            )
    assert not case.deepseek.native_requests and not case.openai.native_requests
    assert outstanding(case.run) == (0, 0, 0)
    await case.calls.close(1)


async def test_native_error_is_single_attempt_and_preserves_unsettled_exposure(
    tmp_path: Path,
) -> None:
    case = model_case(tmp_path)
    case.deepseek.status = 429
    error: JsonObject = {
        "error": {"message": "rate limited", "type": "rate_limit", "code": "limited"}
    }
    case.deepseek.body = error
    async with serve(gateway_app(case.gateway)) as port, sdk_client(port, case.parent.token) as sdk:
        with pytest.raises(APIStatusError) as caught:
            await sdk.chat.completions.create(
                model="deepseek", messages=[{"role": "user", "content": "x"}]
            )
    assert caught.value.status_code == 429 and caught.value.request_id == "req-bound-model"
    assert json_object(caught.value.body)["code"] == "limited"
    assert len(case.deepseek.native_requests) == 1
    assert outstanding(case.run) == (300_009_600,) * 3
    await case.calls.close(1)


def invalid_messages(fault: str) -> list[ChatCompletionMessageParam]:
    return (
        [{"role": "developer", "content": "x"}]
        if fault == "developer"
        else [{"role": "user", "content": "x"}]
    )
