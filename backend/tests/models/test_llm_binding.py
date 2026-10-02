"""Existing LLMCall prompts and result envelopes work with managed DeepSeek reasoning."""

import time
from pathlib import Path

import pytest
from slow_thinker_llm_call import LLMCall
from support.native_gateway import sdk_client
from support.native_server import gateway_app, serve
from support.openai_calls import config

from models.fixtures import utc
from models.mediation_assertions import assert_managed
from models.mediation_fixture import model_case


async def test_plain_llm_call_forwards_reasoning_and_preserves_one_call_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(time, "time", lambda: utc("2026-06-22T02:00:00"))
    case = model_case(tmp_path)
    settings = config()
    settings["parameters"] = {"reasoning_effort": "max"}
    async with (
        serve(gateway_app(case.gateway)) as port,
        sdk_client(port, case.parent.token) as client,
    ):
        result = await LLMCall(settings, client, "deepseek").generate(
            {"problem": "managed reasoning"}
        )
    assert result == {"status": "ok", "format": "text", "value": "answer"}
    assert len(case.deepseek.native_requests) == 1
    native = case.deepseek.native_requests[0]
    assert native["reasoning_effort"] == "max" and native["thinking"] == {"type": "enabled"}
    assert native["messages"] == [
        {"role": "system", "content": "Review the supplied input."},
        {"role": "user", "content": '{"problem":"managed reasoning"}'},
    ]
    assert_managed(case, 6024, 1)
    await case.calls.close(1)
