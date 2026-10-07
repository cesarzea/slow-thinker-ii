"""A host that speaks raw JSON-RPC lines to break the protocol on purpose; for adapter tests.

Run as `protocol_fixture.py <bootstrap> <launch arguments as JSON>`. The configuration's
`mode` names the violation; without one it follows the protocol.
"""

import json
import os
import sys
import time
from pathlib import Path

from slow_thinker_host import tool_schemas

CACHE = {"ttlMs": 0, "cacheScope": "private", "resultType": "complete"}


def result(request: dict[str, object], value: object) -> str:
    return json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": value})


def discovery(mode: str, request: dict[str, object]) -> str:
    if mode == "discover_error":
        error = {"code": -32601, "message": "Method not found"}
        return json.dumps({"jsonrpc": "2.0", "id": request["id"], "error": error})
    if mode == "huge_hello":
        return result(request, {"padding": "x" * 100_000})
    versions = ["2025-11-25"] if mode == "old_protocol" else ["2026-07-28"]
    capabilities: dict[str, object] = {"tools": {}}
    if mode == "extra_capability":
        capabilities["prompts"] = {}
    return result(request, {"supportedVersions": versions, "capabilities": capabilities, **CACHE})


def listing(mode: str, position: str, request: dict[str, object]) -> str:
    name, input_schema, output_schema = tool_schemas("node" if position == "node" else "output")
    tool = {
        "name": "other" if mode == "wrong_tools" else name,
        "inputSchema": {"type": "object"} if mode == "bad_schemas" else input_schema,
        "outputSchema": output_schema,
    }
    return result(request, {"tools": [tool], **CACHE})


def called(mode: str, request: dict[str, object]) -> str:
    text = [{"type": "text", "text": "plain failure"}]
    replies: dict[str, dict[str, object]] = {
        "bad_result": {
            "content": text,
            "structuredContent": {"emissions": "none"},
            "isError": False,
        },
        "bad_error": {"content": text, "isError": True},
        "bad_reply": {"content": "not a list of content blocks"},
        "nan_payload": {
            "content": text,
            "structuredContent": {"emissions": [{"port": "out", "payload": float("nan")}]},
        },
    }
    reply = replies.get(mode, {"content": text, "structuredContent": {"emissions": []}})
    return result(request, {**CACHE, **reply})


def main() -> None:
    bootstrap = json.loads(Path(sys.argv[1]).read_text())
    mode, position = bootstrap["config"].get("mode", ""), bootstrap["position"]
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            continue
        method = request["method"]
        if method == "server/discover":
            answer = discovery(mode, request)
        elif method == "tools/list":
            answer = listing(mode, position, request)
        elif mode == "silent_call":
            continue
        else:
            answer = called(mode, request)
        sys.stdout.write(answer + "\n")
        sys.stdout.flush()
        if mode == "deaf" and method == "tools/list":
            os.close(sys.stdin.fileno())
            time.sleep(60)


if __name__ == "__main__":
    main()
