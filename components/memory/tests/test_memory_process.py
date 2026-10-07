"""End to end: `python -m slow_thinker_memory` serves recall and remember as its own process."""

import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.types import RequestParamsMeta
from memory_fakes import bootstrap_document
from slow_thinker_host import PROTOCOL_VERSION, position_tools

META: RequestParamsMeta = {
    "slow-thinker/grant": "grant-e2e",
    "slow-thinker/budget-ms": 10000,
    "slow-thinker/activation-id": "a2",
}


def host(tmp_path: Path) -> StdioServerParameters:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(bootstrap_document()), encoding="utf-8")
    return StdioServerParameters(
        command=sys.executable, args=["-B", "-I", "-m", "slow_thinker_memory", str(path)]
    )


async def test_memory_position_serves_recall_and_remember(tmp_path: Path) -> None:
    async with Client(host(tmp_path), mode=PROTOCOL_VERSION) as client:
        listed = await client.list_tools()
        first = await client.call_tool("recall", {"message": "Hi"}, meta=META)
        kept = await client.call_tool("remember", {"received": "Hi", "replied": "Hello"}, meta=META)
        second = await client.call_tool("recall", {"message": "Again"}, meta=META)
    assert [(tool.name, tool.input_schema, tool.output_schema) for tool in listed.tools] == list(
        position_tools("memory")
    )
    assert first.structured_content == {"message": "Hi"}
    assert kept.structured_content == {} and not kept.is_error
    transcript = "Conversation so far:\nYou received: Hi\nYou replied: Hello\n\n"
    assert second.structured_content == {"message": f"{transcript}New message:\nAgain"}
