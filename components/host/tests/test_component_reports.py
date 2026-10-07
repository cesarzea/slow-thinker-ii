"""Reports reach `platform.report` under the call's grant; failures never fail the call."""

from collections.abc import Sequence
from dataclasses import replace

import pytest
from host_fixtures import bootstrap, connect, meta
from host_platform import fake_platform
from slow_thinker_host import Context, Emission, JsonValue, create_server


class Reporter:
    def __init__(self, kind: str, content: JsonValue) -> None:
        self.kind, self.content = kind, content

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        await context.report(self.kind, self.content)
        return [Emission("out", message)]


@pytest.mark.parametrize("kind", ["step", "progress", "state", "explanation", "reasoning"])
async def test_reports_are_sent_with_the_call_grant(kind: str) -> None:
    async with fake_platform() as platform:
        host = replace(bootstrap(), mcp_url=platform.mcp_url)
        reporter = Reporter(kind, {"messages": 2})
        async with connect(create_server(host, node=reporter)) as client:
            result = await client.call_tool("activate", {"message": 1}, meta=meta(grant="g-7"))
    assert not result.is_error
    assert platform.reports == [({"kind": kind, "content": {"messages": 2}}, "Bearer g-7")]


async def test_a_rejected_report_is_swallowed_after_one_attempt(
    capsys: pytest.CaptureFixture[str],
) -> None:
    async with fake_platform() as platform:
        platform.reject_reports = True
        host = replace(bootstrap(), mcp_url=platform.mcp_url)
        async with connect(create_server(host, node=Reporter("step", "built"))) as client:
            result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert result.structured_content == {"emissions": [{"port": "out", "payload": 1}]}
    assert len(platform.reports) == 1
    assert "Node echo: report not recorded: ValueError" in capsys.readouterr().err


async def test_an_unreachable_platform_does_not_fail_the_call() -> None:
    async with fake_platform() as platform:
        unreachable = platform.mcp_url
    host = replace(bootstrap(), mcp_url=unreachable)
    async with connect(create_server(host, node=Reporter("step", "built"))) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert not result.is_error


@pytest.mark.parametrize(
    ("kind", "content", "reason"),
    [
        ("debug", "text", "ValueError: unsupported kind 'debug'"),
        ("step", float("inf"), "ValueError: Expected a finite JSON value"),
    ],
)
async def test_invalid_reports_are_logged_and_never_sent(
    capsys: pytest.CaptureFixture[str], kind: str, content: JsonValue, reason: str
) -> None:
    async with fake_platform() as platform:
        host = replace(bootstrap(), mcp_url=platform.mcp_url)
        async with connect(create_server(host, node=Reporter(kind, content))) as client:
            result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert not result.is_error and not platform.reports
    assert f"Node echo: report not recorded: {reason}" in capsys.readouterr().err
