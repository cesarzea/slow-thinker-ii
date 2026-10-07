"""`POST /mcp`: each request owns a stateless MCP exchange bound to its invocation grant."""

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.types import Receive, Scope, Send

from slow_thinker_ii.application import ReportService, RunService

from ._mcp_tools import report_server
from ._native_errors import INVALID_GRANT, GatewayRefusal, refusal_reply
from ._native_input import invocation_grant

PROTOCOL = "2026-07-28"


class ReportEndpoint:
    """ASGI endpoint. The grant must name an active call before the MCP SDK sees the request,
    so unknown, expired and revoked grants get a real `401 invalid_grant`."""

    def __init__(self, runs: RunService, reports: ReportService, limit: int) -> None:
        self._runs = runs
        self._reports = reports
        self._limit = limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            grant = self._admitted(Request(scope, receive))
        except GatewayRefusal as refusal:
            await refusal_reply(refusal)(scope, receive, send)
            return
        manager = StreamableHTTPSessionManager(
            report_server(self._reports, grant),
            stateless=True,
            json_response=True,
            max_request_body_size=self._limit,
            # Browser origins are refused above and the grant authenticates the caller;
            # component endpoints must not assume loopback hosts (ADR 0023).
            security_settings=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        )
        async with manager.run():
            await manager.handle_request(scope, receive, send)

    def _admitted(self, request: Request) -> str:
        grant = invocation_grant(request)
        if self._runs.active_call(grant) is None:
            raise GatewayRefusal(401, "invalid_grant", INVALID_GRANT)
        if request.headers.getlist("mcp-protocol-version") != [PROTOCOL]:
            message = f"Use MCP protocol revision {PROTOCOL}."
            raise GatewayRefusal(400, "unsupported_protocol", message)
        return grant
