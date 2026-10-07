"""Compose a component's handlers into an MCP server and serve it over standard I/O."""

import asyncio
from collections.abc import Sequence
from typing import Protocol

from mcp.server import Server
from mcp.server.stdio import stdio_server

from ._bootstrap import Bootstrap
from ._calls import emission_record, emissions_record
from ._context import Context
from ._json import JsonObject, JsonValue
from ._protocol import Emission
from ._server import HostServer, Invoke


class NodeHandler(Protocol):
    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]: ...


class OutputHandler(Protocol):
    async def select_output(
        self, received: JsonValue, node_input: JsonValue, context: Context
    ) -> Emission: ...


class MemoryHandler(Protocol):
    """A node's memory: what the node receives instead of a message, and what it replied."""

    async def recall(self, message: JsonValue, context: Context) -> JsonValue: ...

    async def remember(self, received: JsonValue, replied: JsonValue, context: Context) -> None: ...


def create_server(
    bootstrap: Bootstrap,
    *,
    node: NodeHandler | None = None,
    output: OutputHandler | None = None,
    memory: MemoryHandler | None = None,
    stateful: bool = False,
) -> Server[object]:
    """The MCP server of a host; it exposes exactly the tools of the bootstrap's position."""
    handlers = HostServer(bootstrap, _invokers(bootstrap, node, output, memory), stateful)
    name, _, version = bootstrap.component.partition("@")
    return Server[object](
        name, version=version, on_list_tools=handlers.list_tools, on_call_tool=handlers.call_tool
    )


def run_host(
    bootstrap: Bootstrap,
    *,
    node: NodeHandler | None = None,
    output: OutputHandler | None = None,
    memory: MemoryHandler | None = None,
    stateful: bool = False,
) -> None:
    """Serve MCP on standard input and output until standard input closes."""
    server = create_server(bootstrap, node=node, output=output, memory=memory, stateful=stateful)
    asyncio.run(_serve(server))


async def _serve(server: Server[object]) -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def _invokers(
    bootstrap: Bootstrap,
    node: NodeHandler | None,
    output: OutputHandler | None,
    memory: MemoryHandler | None,
) -> dict[str, Invoke]:
    if bootstrap.position == "node":
        if node is None:
            raise ValueError("A host at position node requires a node handler")
        return {"activate": _activate(node)}
    if bootstrap.position == "memory":
        if memory is None:
            raise ValueError("A host at position memory requires a memory handler")
        return {"recall": _recall(memory), "remember": _remember(memory)}
    if output is None:
        raise ValueError("A host at position output requires an output handler")
    return {"select_output": _select_output(output)}


def _recall(handler: MemoryHandler) -> Invoke:
    async def invoke(arguments: JsonObject, context: Context) -> JsonObject:
        return {"message": await handler.recall(arguments["message"], context)}

    return invoke


def _remember(handler: MemoryHandler) -> Invoke:
    async def invoke(arguments: JsonObject, context: Context) -> JsonObject:
        await handler.remember(arguments["received"], arguments["replied"], context)
        return {}

    return invoke


def _activate(handler: NodeHandler) -> Invoke:
    async def invoke(arguments: JsonObject, context: Context) -> JsonObject:
        return emissions_record(await handler.activate(arguments["message"], context))

    return invoke


def _select_output(handler: OutputHandler) -> Invoke:
    async def invoke(arguments: JsonObject, context: Context) -> JsonObject:
        emission = await handler.select_output(
            arguments["received"], arguments["node_input"], context
        )
        return emission_record(emission)

    return invoke
