"""Each HTTP request owns its pinned SDK transport and invocation-bound handlers."""

import asyncio

from fastapi import APIRouter, Request
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.routing import Route
from starlette.types import Message, Receive, Scope, Send

from slow_thinker_ii.application import GatewayError, ManagedGatewayService

from ._mcp_tools import PROTOCOL, gateway_server
from ._native_errors import platform_error
from ._native_input import invocation_grant


class GatewayHTTP:
    def __init__(self, service: ManagedGatewayService, limit: int) -> None:
        self._service, self._limit = service, limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)
        tracked = ResponseProgress(send)
        try:
            grant = invocation_grant(request)
            deadline = self._service.deadline(grant)
            version = request.headers.get("mcp-protocol-version")
            if version is not None and version != PROTOCOL:
                self._service.reject(grant, "protocol", "unsupported_protocol")
                raise GatewayError("unsupported_protocol", 400)
            manager = StreamableHTTPSessionManager(
                gateway_server(self._service, grant),
                stateless=True,
                json_response=False,
                max_request_body_size=self._limit,
                security_settings=TransportSecuritySettings(
                    allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*"]
                ),
            )
            async with asyncio.timeout_at(deadline), manager.run():
                await manager.handle_request(scope, receive, tracked.send)
        except Exception as error:
            if not tracked.started:
                await platform_error(error)(scope, receive, send)


def mcp_router(service: ManagedGatewayService, max_body_bytes: int = 1_048_576) -> APIRouter:
    router = APIRouter()
    router.routes.append(
        Route("/mcp", GatewayHTTP(service, max_body_bytes), methods=["GET", "POST", "DELETE"])
    )
    return router


class ResponseProgress:
    def __init__(self, send: Send) -> None:
        self._send, self.started = send, False

    async def send(self, message: Message) -> None:
        if message["type"] == "http.response.start":
            self.started = True
        await self._send(message)
