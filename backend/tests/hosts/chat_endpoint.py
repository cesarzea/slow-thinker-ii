"""A local fake of the platform's Chat Completions endpoint for real LLM Call hosts."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from slow_thinker_ii.contracts import JsonObject, json_object
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


class ChatEndpoint:
    """Answers every request with `reply` as the assistant's content; keeps what it received."""

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.base_url = ""
        self.requests: list[tuple[JsonObject, str]] = []

    async def complete(self, request: Request) -> Response:
        body = json_object(await request.json())
        self.requests.append((body, request.headers.get("authorization", "")))
        message = {"role": "assistant", "content": self.reply}
        choice = {"index": 0, "finish_reason": "stop", "message": message}
        completion = {
            "id": "chatcmpl-1",
            "object": "chat.completion",
            "created": 1,
            "model": body["model"],
            "choices": [choice],
        }
        return JSONResponse(completion)


@asynccontextmanager
async def chat_endpoint(reply: str) -> AsyncGenerator[ChatEndpoint]:
    """Serves the endpoint on a free loopback port while the context is open."""
    endpoint = ChatEndpoint(reply)
    app = Starlette(routes=[Route("/v1/chat/completions", endpoint.complete, methods=["POST"])])
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning", ws="none")
    )
    serving = asyncio.create_task(server.serve())
    while not server.started:
        if serving.done() or server.should_exit:
            raise RuntimeError("The fake Chat Completions endpoint did not start")
        await asyncio.sleep(0.005)
    endpoint.base_url = f"http://127.0.0.1:{server.servers[0].sockets[0].getsockname()[1]}/v1"
    try:
        yield endpoint
    finally:
        server.should_exit = True
        await asyncio.wait_for(serving, timeout=10)
