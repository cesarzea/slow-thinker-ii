"""Repeated MCP calls receive fresh objects, grants and clients, even after failure."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from openai import AsyncOpenAI
from slow_thinker_host import GRANT_META, PROTOCOL_VERSION, Invocation, Operation, create_server
from slow_thinker_llm_call import JsonObject, LLMCall, LLMCallHost, Message, effective_operation
from support.openai_calls import ModelStub, completion, config


class Clients:
    def __init__(self, stub: ModelStub) -> None:
        self.stub = stub
        self.created: list[AsyncOpenAI] = []

    @asynccontextmanager
    async def open(self, context: Invocation) -> AsyncGenerator[AsyncOpenAI]:
        async with self.stub.client(context.grant) as client:
            self.created.append(client)
            yield client


class SingleUse(LLMCall):
    def build_messages(self, arguments: JsonObject) -> list[Message]:
        assert not getattr(self, "_used", False)
        self._used = True
        return super().build_messages(arguments)


async def test_fresh_instances_clients_and_grants_after_output_failure() -> None:
    clients = Clients(ModelStub(completion("not-json")))
    settings = config({"type": "integer"})
    host = LLMCallHost(settings, effective_operation(settings), clients.open, "model", SingleUse)
    async with Client(create_server(host, "llm-call", "1"), mode=PROTOCOL_VERSION) as client:
        failed = await client.call_tool("generate", {}, meta={GRANT_META: "first"})
        assert failed.is_error
        assert failed.structured_content is not None
        assert failed.structured_content["status"] == "error"
        clients.stub.response = completion("7")
        result = await client.call_tool("generate", {}, meta={GRANT_META: "second"})
        assert result.structured_content == {"status": "ok", "format": "json", "value": 7}
    assert clients.stub.authority == ["Bearer first", "Bearer second"]
    assert len(clients.created) == 2 and clients.created[0] is not clients.created[1]
    assert all(client.is_closed() for client in clients.created)


@pytest.mark.parametrize("status", [200, 500])
async def test_provider_errors_close_the_client_without_returning_functional_failure(
    status: int,
) -> None:
    clients = Clients(ModelStub(completion("partial", "length"), status))
    settings = config()
    host = LLMCallHost(settings, effective_operation(settings), clients.open, "model")
    expected = "incomplete_response" if status == 200 else "model_request_failed"
    with pytest.raises(MCPError, match=expected):
        await host.invoke("generate", {}, Invocation("grant"))
    assert clients.created[0].is_closed()
    assert len(clients.stub.requests) == 1


async def test_host_rejects_wrong_operation_and_schema() -> None:
    clients = Clients(ModelStub(completion("unused")))
    settings = config()
    with pytest.raises(ValueError, match="schemas"):
        LLMCallHost(settings, Operation("generate", {}, {}), clients.open, "model")
    host = LLMCallHost(settings, effective_operation(settings), clients.open, "model")
    with pytest.raises(ValueError, match="Unsupported"):
        await host.invoke("unknown", {}, Invocation("grant"))
    assert not clients.created
