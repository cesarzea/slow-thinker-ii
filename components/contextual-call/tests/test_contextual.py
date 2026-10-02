"""Enabled stages preserve exact context and worker results without retries."""

import asyncio
import time

import pytest
from context_case import CONFIG, ENDPOINT, gateway
from mcp.shared.exceptions import MCPError
from slow_thinker_contextual_call import ContextualCall
from slow_thinker_host import Invocation, JsonObject, ToolReply


async def test_all_stages_preserve_inputs_order_grants_deadline_and_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = gateway(monkeypatch)
    arguments: JsonObject = {"expression": "1+2", "task": "work"}
    deadline = time.monotonic() + 2
    result = await ContextualCall(CONFIG, ENDPOINT).invoke(arguments, Invocation("grant", deadline))
    assert result == fixture.replies["worker-work"]
    assert arguments == {"expression": "1+2", "task": "work"}
    assert [call[0] for call in fixture.calls] == [
        "memory-get",
        "calculator-calculate",
        "worker-work",
        "memory-put",
    ]
    assert fixture.calls[2][1] == {**arguments, "memory": {"remembered": 1}, "calculation": "3"}
    assert fixture.calls[3][1] == {"key": "context", "value": {"n": 9007199254740993}}
    assert all(call[2] == "Bearer grant" for call in fixture.calls)
    assert all(str(request.url) == ENDPOINT.url for request in fixture.requests)
    assert all(client.is_closed for client in fixture.clients)


async def test_disabled_bindings_do_not_inject_context(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    config = {**CONFIG, "memory_read": False, "memory_write": False, "calculation_enabled": False}
    assert (
        await ContextualCall(config, ENDPOINT).invoke({}, Invocation("g"))
        == fixture.replies["worker-work"]
    )
    assert [item[0] for item in fixture.calls] == ["worker-work"]


@pytest.mark.parametrize(
    "alias,reply,stage",
    [
        ("memory-get", ToolReply({"error": "denied"}, True), "memory_get"),
        ("memory-get", ToolReply({"found": True, "value": 1, "version": None}), "memory_get"),
        ("memory-get", ToolReply({"found": False, "value": 1, "version": None}), "memory_get"),
        ("memory-get", ToolReply({"found": "yes"}), "memory_get"),
        ("calculator-calculate", ToolReply({"expression": "wrong", "value": "3"}), "calculate"),
        ("calculator-calculate", ToolReply({"expression": "1+2", "value": False}), "calculate"),
        ("worker-work", ToolReply({"status": "error"}), "worker"),
        ("worker-work", ToolReply({"error": "budget"}, True), "worker"),
        ("memory-put", ToolReply({"version": 0}), "memory_put"),
        ("memory-put", ToolReply({"error": "conflict"}, True), "memory_put"),
    ],
)
async def test_failed_stage_stops_and_never_repeats_worker(
    monkeypatch: pytest.MonkeyPatch, alias: str, reply: ToolReply, stage: str
) -> None:
    fixture = gateway(monkeypatch)
    fixture.replies[alias] = reply
    with pytest.raises(MCPError) as caught:
        await ContextualCall(CONFIG, ENDPOINT).invoke({"expression": "1+2"}, Invocation("g"))
    assert caught.value.data["stage"] == stage
    assert [item[0] for item in fixture.calls].count("worker-work") <= 1
    assert fixture.calls[-1][0] == alias


async def test_missing_memory_injects_null(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    fixture.replies["memory-get"] = ToolReply({"found": False, "value": None, "version": None})
    await ContextualCall(CONFIG, ENDPOINT).invoke({"expression": "1+2"}, Invocation("g"))
    assert fixture.calls[2][1]["memory"] is None


async def test_cancelled_call_is_closed_and_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    fixture.block = True
    task = asyncio.create_task(ContextualCall(CONFIG, ENDPOINT).invoke({}, Invocation("g")))
    await asyncio.wait_for(fixture.started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 2)
    assert [item[0] for item in fixture.calls] == ["memory-get"]
    assert all(client.is_closed for client in fixture.clients)


async def test_expired_deadline_has_no_child_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    with pytest.raises(MCPError):
        await ContextualCall(CONFIG, ENDPOINT).invoke({}, Invocation("g", time.monotonic() - 1))
    assert not fixture.calls
