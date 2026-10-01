"""Optional reports require a durable boolean receipt under invocation authority."""

import pytest
from slow_thinker_host import Invocation, JsonObject, McpEndpoint, ToolReply, report_component

from tooling.tests.mcp_gateway_fixture import GatewayFixture

ENDPOINT = McpEndpoint("http://127.0.0.1:8000/mcp", 2, 1)
REPORT: JsonObject = {"kind": "state", "schema_version": "1", "value": {"stage": "reviewing"}}


@pytest.mark.parametrize("kind", ["state", "progress", "explanation", "reasoning"])
async def test_report_uses_reserved_tool_and_preserves_optional_timestamp(
    monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    fixture = GatewayFixture()
    fixture.add("platform.report", ToolReply({"recorded": True}))
    fixture.install(monkeypatch)
    value = {**REPORT, "kind": kind, "source_occurred_at": 123.5}
    assert await report_component(ENDPOINT, Invocation("g"), value) == {"recorded": True}
    assert fixture.calls == [("platform.report", value, "Bearer g")]


@pytest.mark.parametrize(
    "report",
    [
        {},
        {**REPORT, "extra": 1},
        {**REPORT, "kind": "unknown"},
        {**REPORT, "schema_version": "2"},
        {**REPORT, "source_occurred_at": True},
        {**REPORT, "source_occurred_at": "now"},
    ],
)
async def test_invalid_report_never_dispatches(
    monkeypatch: pytest.MonkeyPatch, report: JsonObject
) -> None:
    fixture = GatewayFixture()
    fixture.install(monkeypatch)
    with pytest.raises(ValueError):
        await report_component(ENDPOINT, Invocation("g"), report)
    assert not fixture.clients


@pytest.mark.parametrize(
    "reply",
    [
        ToolReply({"recorded": False}),
        ToolReply({"recorded": 1}),
        ToolReply({"recorded": True, "extra": 1}),
        ToolReply({"error": "refused"}, True),
    ],
)
async def test_non_durable_report_reply_is_not_success(
    monkeypatch: pytest.MonkeyPatch, reply: ToolReply
) -> None:
    fixture = GatewayFixture()
    fixture.add("platform.report", reply)
    fixture.install(monkeypatch)
    with pytest.raises(ValueError):
        await report_component(ENDPOINT, Invocation("g"), REPORT)
    assert len(fixture.calls) == 1
