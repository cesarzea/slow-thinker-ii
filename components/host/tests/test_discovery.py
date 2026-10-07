"""Discovery advertises the pinned protocol and only tools; negotiating clients are served."""

from host_fixtures import Recorder, bootstrap, connect, meta
from mcp import Client, types
from slow_thinker_host import PROTOCOL_VERSION, create_server


async def test_discovery_advertises_the_protocol_and_only_tools() -> None:
    async with connect(create_server(bootstrap(), node=Recorder())) as client:
        discovered = await client.session.send_request(
            types.DiscoverRequest(), types.DiscoverResult
        )
    assert PROTOCOL_VERSION in discovered.supported_versions
    assert set(discovered.capabilities.model_dump(exclude_none=True)) == {"tools"}


async def test_an_auto_negotiating_client_uses_the_pinned_protocol() -> None:
    async with Client(create_server(bootstrap(), node=Recorder()), mode="auto") as client:
        version = client.protocol_version
        listed = await client.list_tools()
        result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert version == PROTOCOL_VERSION and [tool.name for tool in listed.tools] == ["activate"]
    assert result.structured_content == {"emissions": [{"port": "out", "payload": 1}]}
