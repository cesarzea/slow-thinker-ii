"""End to end: the installed entry point runs as a process and serves MCP over stdio."""

import json
import sys
from pathlib import Path

from llm_call_fakes import SCORE, config
from llm_call_platform import fake_platform
from mcp import Client, StdioServerParameters
from slow_thinker_host import PROTOCOL_VERSION, JsonObject, tool_schemas


def bootstrap_file(tmp_path: Path, base: str) -> str:
    document: JsonObject = {
        "format": "slow-thinker.bootstrap/1",
        "component": "llm-call@1.0.0",
        "node": {"id": "reviewer", "name": "Reviewer"},
        "position": "node",
        "config": config(output_format={"type": "json", "schema": SCORE}),
        "platform": {"llm_base_url": f"{base}/v1", "mcp_url": f"{base}/mcp"},
        "limits": {"max_concurrent_invocations": 4},
    }
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


def host(path: str) -> StdioServerParameters:
    """The platform's launch line: isolated, without bytecode, as a module."""
    arguments = ["-B", "-I", "-m", "slow_thinker_llm_call", path]
    return StdioServerParameters(command=sys.executable, args=arguments)


async def test_llm_call_process_lists_and_serves_activate(tmp_path: Path) -> None:
    async with fake_platform('{"score": 8}') as platform:
        process = host(bootstrap_file(tmp_path, platform.base))
        async with Client(process, mode=PROTOCOL_VERSION) as client:
            listed = await client.list_tools()
            result = await client.call_tool(
                "activate",
                {"message": "Whiskers studied pigeons."},
                meta={
                    "slow-thinker/grant": "grant-e2e",
                    "slow-thinker/budget-ms": 10000,
                    "slow-thinker/activation-id": "a1",
                },
            )
    name, input_schema, output_schema = tool_schemas("node")
    assert [(tool.name, tool.input_schema, tool.output_schema) for tool in listed.tools] == [
        (name, input_schema, output_schema)
    ]
    assert result.structured_content == {"emissions": [{"port": "out", "payload": {"score": 8}}]}
    ((request, authorization),) = platform.chats
    assert authorization == "Bearer grant-e2e" and request["model"] == "openai/gpt-6-luna"
    assert [report for report, _ in platform.reports] == [
        {"kind": "step", "content": "messages built: 2 messages"},
        {"kind": "step", "content": "model replied: 12 characters"},
        {"kind": "step", "content": "reply validated"},
    ]
    assert {grant for _, grant in platform.reports} == {"Bearer grant-e2e"}
