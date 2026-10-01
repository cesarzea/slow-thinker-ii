"""A bounded real loopback HTTP server exercises ordinary clients without a provider key."""

import asyncio
import socket
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slow_thinker_ii.adapters.http import openai_router
from slow_thinker_ii.application import NativeModelService


def gateway_app(gateway: NativeModelService, *, limit: int = 1_048_576) -> FastAPI:
    app = FastAPI()
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    app.include_router(openai_router(gateway, limit))
    return app


@asynccontextmanager
async def serve(app: FastAPI) -> AsyncGenerator[int]:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    listener.setblocking(False)
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            log_level="critical",
            access_log=False,
            lifespan="off",
            ws="none",
            timeout_graceful_shutdown=1,
        )
    )
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        async with asyncio.timeout(5):
            while not server.started:
                if task.done():
                    await task
                    raise RuntimeError("Fixture HTTP server did not become ready")
                await asyncio.sleep(0.01)
        yield listener.getsockname()[1]
    finally:
        if not server.should_exit:
            server.should_exit = True
        await asyncio.wait_for(task, 3)
        listener.close()
