"""Standard Chat Completions calls enter the same managed invocation path as MCP."""

import asyncio

from fastapi import APIRouter, Request, Response

from slow_thinker_ii.application import NativeModelService

from ._native_errors import platform_error
from ._native_input import invocation_grant, request_body


class NativeEndpoint:
    def __init__(self, gateway: NativeModelService, max_body_bytes: int) -> None:
        if type(max_body_bytes) is not int or max_body_bytes <= 0:
            raise ValueError("A positive request byte limit is required")
        self._gateway, self._limit = gateway, max_body_bytes

    async def create(self, request: Request) -> Response:
        try:
            grant = invocation_grant(request)
            async with asyncio.timeout_at(self._gateway.deadline(grant)):
                body = await request_body(request, self._limit)
                result = await self._gateway.complete(grant, body)
            headers = {} if result.request_id is None else {"x-request-id": result.request_id}
            if result.retry_after is not None:
                headers["retry-after"] = result.retry_after
            return Response(
                result.payload_json,
                status_code=result.status,
                media_type="application/json",
                headers=headers,
            )
        except Exception as error:
            return platform_error(error)


def openai_router(gateway: NativeModelService, max_body_bytes: int = 1_048_576) -> APIRouter:
    endpoint = NativeEndpoint(gateway, max_body_bytes)
    router = APIRouter()
    router.add_api_route("/v1/chat/completions", endpoint.create, methods=["POST"])
    return router
