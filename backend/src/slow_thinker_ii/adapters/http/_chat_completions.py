"""`POST /v1/chat/completions`: the LLM service for components, answered by the gateway."""

from fastapi import Request, Response

from slow_thinker_ii.application import LlmGateway
from slow_thinker_ii.contracts import encode_json

from ._native_errors import GatewayRefusal, refusal_reply
from ._native_input import invocation_grant, request_body


class ChatCompletions:
    def __init__(self, gateway: LlmGateway, limit: int) -> None:
        self._gateway = gateway
        self._limit = limit

    async def complete(self, request: Request) -> Response:
        """The gateway's status and body, unchanged; adapter refusals use the same body shape."""
        try:
            grant = invocation_grant(request)
            body = await request_body(request, self._limit)
        except GatewayRefusal as refusal:
            return refusal_reply(refusal)
        reply = await self._gateway.complete(grant, body)
        return Response(encode_json(reply.body), reply.status, media_type="application/json")
