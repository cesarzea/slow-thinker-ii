"""Ordinary pinned clients discover filtered operations and retain the true parent identity."""

from pathlib import Path

import pytest
from mcp import MCPError, types
from slow_thinker_host import JsonObject, managed_mcp_client, report_component
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.adapters.sqlite import SqliteOperatorQueries
from slow_thinker_ii.contracts import decode_json, json_object
from support.mcp_gateway import mcp_case
from support.native_gateway import assert_recorded
from support.native_server import serve


async def test_pinned_mcp_discovery_and_real_nested_call(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    async with (
        serve(case.app) as port,
        managed_mcp_client(case.endpoint(port), case.invocation()) as client,
    ):
        discovery = await client.session.send_request(types.DiscoverRequest(), types.DiscoverResult)
        assert discovery.supported_versions == ["2026-07-28"]
        tools = (await client.list_tools()).tools
        assert len(tools) == 2 and tools[1].name == "platform.report"
        assert tools[0].input_schema["required"] == ["request"]
        result = await client.call_tool(
            tools[0].name,
            {
                "request": {
                    "model": "bound-model",
                    "messages": [{"role": "user", "content": "hello"}],
                }
            },
        )
        assert not result.is_error and result.structured_content is not None
    assert_recorded(case.native)
    await case.native.calls.close(1)


async def test_denied_alias_is_recorded_without_child_dispatch(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    async with (
        serve(case.app) as port,
        managed_mcp_client(case.endpoint(port), case.invocation()) as client,
    ):
        with pytest.raises(MCPError):
            await client.call_tool("guessed-alias", {})
    assert not case.native.model.calls
    with case.native.run.store.begin() as transaction:
        rejected = [event for event in transaction.events("run") if event.event == "call.rejected"]
    assert len(rejected) == 1 and "operation_denied" in rejected[0].payload_json
    assert rejected[0].call_id == case.native.parent.context.call_id
    await case.native.calls.close(1)


async def test_reports_are_durable_redacted_and_scoped(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    report: JsonObject = {
        "kind": "reasoning",
        "schema_version": "1",
        "value": {"authorization": "secret", "summary": "because"},
        "source_occurred_at": 42.0,
    }
    async with serve(case.app) as port:
        await report_component(case.endpoint(port), case.invocation(), report)
    queries = SqliteOperatorQueries(case.native.run.database, b"k" * 32)
    call = json_object(decode_json(queries.call("run", case.native.parent.context.call_id) or "{}"))
    reports = call["reports"]
    assert isinstance(reports, list) and len(reports) == 1
    record = json_object(reports[0])
    payload = json_object(decode_json(queries.payload("run", str(record["payload_id"])) or "{}"))
    assert record["evidence"] == "reported" and record["source_occurred_at"] == 42
    assert payload["status"] == "redacted" and "secret" not in str(payload)
    assert not case.native.model.calls
    case.native.run.authority.revoke(case.native.parent.context.call_id)
    with pytest.raises(AccessDenied):
        case.service.report(
            case.native.parent.token, '{"kind":"state","schema_version":"1","value":null}'
        )
    await case.native.calls.close(1)


@pytest.mark.parametrize(
    "report",
    [
        "{}",
        '{"kind":"unknown","schema_version":"1","value":null}',
        '{"kind":"state","schema_version":"1","value":null,"extra":true}',
    ],
)
def test_invalid_reports_are_recorded_without_payload(tmp_path: Path, report: str) -> None:
    case = mcp_case(tmp_path)
    with pytest.raises(ValueError):
        case.service.report(case.native.parent.token, report)
    with case.native.run.store.begin() as transaction:
        assert any(event.event == "call.rejected" for event in transaction.events("run"))
        assert not any(event.event == "component.reported" for event in transaction.events("run"))
