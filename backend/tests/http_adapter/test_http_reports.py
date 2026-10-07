"""`platform.report` records reported evidence for the activation of the request's grant."""

import json

import pytest
from slow_thinker_ii.contracts import JsonObject

from .http_harness import held_call, held_platform, operator_api
from .http_mcp import REPORT_TOOL, call, raw_call, raw_headers, report_client, tool_error

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"enum": ["step", "progress", "state", "explanation", "reasoning"]},
        "content": {},
    },
    "required": ["kind", "content"],
    "additionalProperties": False,
}


async def test_the_report_tool_is_the_only_tool() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        async with report_client(api.app, context.grant) as client:
            [tool] = (await client.list_tools()).tools
        assert (tool.name, tool.input_schema) == (REPORT_TOOL, INPUT_SCHEMA)


async def test_reports_are_recorded_for_the_activation_of_the_grant() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        async with report_client(api.app, context.grant) as client:
            result = await call(client, {"kind": "step", "content": {"text": "Messages built."}})
            await call(client, {"kind": "reasoning", "content": "x" * 65_534})
        assert not result.is_error and result.structured_content == {"recorded": True}
        first, second = api.platform.run_store.of(context.run_id, "report")
        assert (first.evidence, first.node_id) == ("reported", "proposer")
        assert first.activation_id == context.activation_id
        assert first.data == {"kind": "step", "content": {"text": "Messages built."}}
        assert second.data["kind"] == "reasoning"


@pytest.mark.parametrize(
    ("name", "arguments", "code"),
    [
        (REPORT_TOOL, {"kind": "diary", "content": 1}, "invalid_report"),
        (REPORT_TOOL, {"kind": "state", "content": "x" * 65_535}, "invalid_report"),
        (REPORT_TOOL, {"kind": "state"}, "invalid_arguments"),
        (REPORT_TOOL, {"kind": 1, "content": 1}, "invalid_arguments"),
        (REPORT_TOOL, {"kind": "state", "content": 1, "extra": 2}, "invalid_arguments"),
        ("platform.write", {"kind": "state", "content": 1}, "unknown_tool"),
    ],
)
async def test_refused_reports_are_tool_errors(name: str, arguments: JsonObject, code: str) -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        async with report_client(api.app, context.grant) as client:
            result = await call(client, arguments, name)
        assert tool_error(result) == code
        assert api.platform.run_store.of(context.run_id, "report") == []


async def test_non_finite_content_is_refused_as_invalid_arguments() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        content = raw_call('{"kind": "state", "content": NaN}')
        response = await api.http.post("/mcp", content=content, headers=raw_headers(context.grant))
        result = response.json()["result"]
        assert response.status_code == 200 and result["isError"] is True
        assert json.loads(result["content"][0]["text"])["code"] == "invalid_arguments"
        assert api.platform.run_store.of(context.run_id, "report") == []
