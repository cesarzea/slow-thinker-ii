"""An independent MCP component calls a real loopback endpoint through the native SDK."""

import asyncio
from pathlib import Path

from slow_thinker_host import decode_json
from support.llm_process import ModelEndpoint, llm_process
from support.process_fixture import assert_reaped


async def test_llm_subprocess_routes_each_invocation_and_exits_cleanly(tmp_path: Path) -> None:
    endpoint = ModelEndpoint()
    async with await asyncio.start_server(endpoint.handle, "127.0.0.1", 0) as server:
        process = llm_process(tmp_path, server.sockets[0].getsockname()[1])
        async with process.connect() as connection:
            for grant in ("first", "second"):
                result = await connection.call("generate", '{"question":"test"}', grant, 5)
                assert not result.is_error
                assert decode_json(result.payload_json) == {
                    "status": "ok",
                    "format": "text",
                    "value": "success",
                }
        assert_reaped(process, forced=False)
    assert endpoint.authority == [b"bearer first", b"bearer second"]
    assert len(endpoint.requests) == 2
    assert endpoint.requests[0] == endpoint.requests[1]
    assert endpoint.requests[0]["model"] == "bound-model"
