"""End to end: `python -m slow_thinker_router` serves MCP over stdio as its own process."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import Client, StdioServerParameters, types
from mcp.types import RequestParamsMeta
from router_fakes import bootstrap_document
from slow_thinker_host import PROTOCOL_VERSION, JsonObject, JsonValue, decode_json, tool_schemas

META: RequestParamsMeta = {
    "slow-thinker/grant": "grant-e2e",
    "slow-thinker/budget-ms": 10000,
    "slow-thinker/activation-id": "a2",
}


def bootstrap_file(tmp_path: Path, document: JsonObject) -> str:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


def launch(path: str) -> list[str]:
    """The platform's launch line: isolated, without bytecode, as a module."""
    return [sys.executable, "-B", "-I", "-m", "slow_thinker_router", path]


def host(path: str) -> StdioServerParameters:
    command, *arguments = launch(path)
    return StdioServerParameters(command=command, args=arguments)


def run_alone(path: str) -> subprocess.CompletedProcess[bytes]:
    """Run with standard input already closed and an environment of only PATH."""
    environment = {"PATH": os.environ["PATH"]}
    return subprocess.run(
        launch(path), input=b"", capture_output=True, env=environment, timeout=30, check=False
    )


def tool_error(result: types.CallToolResult) -> JsonValue:
    content = result.content[0]
    assert result.is_error and isinstance(content, types.TextContent)
    return decode_json(content.text)


async def test_output_position_serves_select_output(tmp_path: Path) -> None:
    path = bootstrap_file(tmp_path, bootstrap_document("output"))
    async with Client(host(path), mode=PROTOCOL_VERSION) as client:
        listed = await client.list_tools()
        accepted = await client.call_tool(
            "select_output", {"received": {"score": 8}, "node_input": "story"}, meta=META
        )
        failed = await client.call_tool(
            "select_output", {"received": {"grade": 8}, "node_input": "story"}, meta=META
        )
    name, input_schema, output_schema = tool_schemas("output")
    assert [(tool.name, tool.input_schema, tool.output_schema) for tool in listed.tools] == [
        (name, input_schema, output_schema)
    ]
    assert accepted.structured_content == {"port": "accepted", "payload": "story"}
    assert tool_error(failed) == {
        "code": "script_error",
        "message": "The script raised KeyError: 'score' at line 2.",
    }


async def test_node_position_serves_activate(tmp_path: Path) -> None:
    script = "def route(received, node_input):\n    return 'revise', received\n"
    path = bootstrap_file(tmp_path, bootstrap_document("node", script))
    async with Client(host(path), mode="auto") as client:
        listed = await client.list_tools()
        result = await client.call_tool("activate", {"message": "story"}, meta=META)
    assert [tool.name for tool in listed.tools] == ["activate"]
    assert result.structured_content == {"emissions": [{"port": "revise", "payload": "story"}]}


def test_the_host_exits_cleanly_when_stdin_closes(tmp_path: Path) -> None:
    finished = run_alone(bootstrap_file(tmp_path, bootstrap_document("output")))
    assert finished.returncode == 0 and finished.stdout == b""


@pytest.mark.parametrize(
    ("script", "message"),
    [
        ("def route(received, node_input):\n    return 'a' 'b' 1\n", "syntax error at line 2"),
        ("def choose(received, node_input):\n    pass\n", "does not define a function named route"),
    ],
)
def test_a_broken_script_stops_the_host_before_readiness(
    tmp_path: Path, script: str, message: str
) -> None:
    finished = run_alone(bootstrap_file(tmp_path, bootstrap_document("output", script)))
    assert finished.returncode == 1 and finished.stdout == b""
    assert finished.stderr.decode().startswith("Router startup failed: The script")
    assert message in finished.stderr.decode()
