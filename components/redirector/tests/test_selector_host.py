"""Trusted selector discovery rejects unsupported code before exposing an operation."""

import sys
from collections.abc import AsyncIterator
from types import ModuleType

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    GRANT_META,
    PROTOCOL_VERSION,
    Invocation,
    JsonObject,
    Operation,
    create_server,
)
from slow_thinker_redirector import RedirectorHost

CONFIG: JsonObject = {
    "outputs": ["accept", "revise"],
    "selector": "example_grounded_review:choose",
    "input_schema": {"type": "object"},
}


async def coroutine(value: object) -> str:
    del value
    return "accept"


async def generator(value: object) -> AsyncIterator[str]:
    del value
    yield "accept"


class AsyncCallable:
    async def __call__(self, value: object) -> str:
        del value
        return "accept"


def wrong_signature() -> str:
    return "accept"


@pytest.mark.parametrize("selector", [coroutine, generator, AsyncCallable(), 3, wrong_signature])
def test_unsupported_selector_is_rejected_at_description(
    monkeypatch: pytest.MonkeyPatch, selector: object
) -> None:
    module = ModuleType("authored_selector")
    monkeypatch.setattr(module, "choose", selector, raising=False)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    with pytest.raises((ValueError, TypeError)):
        RedirectorHost.describe({**CONFIG, "selector": "authored_selector:choose"})


async def test_host_publishes_ports_and_preserves_selector_failure() -> None:
    (operation,) = RedirectorHost.describe(CONFIG)
    host = RedirectorHost(CONFIG, operation)
    async with Client(create_server(host, "redirector", "0.1.0"), mode=PROTOCOL_VERSION) as client:
        reply = await client.call_tool(
            "route", {"value": {"accepted": True}}, meta={GRANT_META: "a"}
        )
        assert reply.structured_content == {"port": "accept"}
        with pytest.raises(MCPError) as captured:
            await client.call_tool("route", {"value": {}}, meta={GRANT_META: "b"})
    assert captured.value.code == -32603
    assert captured.value.data == {
        "stage": "selector",
        "reason": "A validated review with accepted is required",
    }


async def test_host_rejects_wrong_operation_and_shape() -> None:
    (operation,) = RedirectorHost.describe(CONFIG)
    with pytest.raises(ValueError, match="schemas"):
        RedirectorHost(CONFIG, Operation("route", {}, {}))
    host = RedirectorHost(CONFIG, operation)
    invalid: list[tuple[str, JsonObject]] = [("other", {"value": {}}), ("route", {})]
    for name, arguments in invalid:
        with pytest.raises(ValueError, match="invocation"):
            await host.invoke(name, arguments, Invocation("a"))
