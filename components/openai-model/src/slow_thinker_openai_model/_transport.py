"""One bounded native HTTP attempt, with no redirects, proxy inheritance or retries."""

import asyncio
import math
import time

import httpx2
from slow_thinker_host import Invocation, JsonObject, ToolReply, encode_json

from ._capture import CaptureLimit, provider_reply, read_body, transport_failure
from ._endpoint import ProviderEndpoint


class ProviderTransport:
    def __init__(
        self, endpoint: ProviderEndpoint, transport: httpx2.AsyncBaseTransport | None = None
    ) -> None:
        self._endpoint, self._transport = endpoint, transport

    async def complete(self, request: JsonObject, context: Invocation) -> ToolReply:
        if not context.grant or context.deadline is None or not math.isfinite(context.deadline):
            raise ValueError("A managed invocation with an absolute deadline is required")
        seconds = min(self._endpoint.timeout_seconds, context.deadline - time.monotonic())
        if seconds <= 0:
            raise TimeoutError("Provider deadline expired before client creation")
        client = httpx2.AsyncClient(
            timeout=seconds, trust_env=False, follow_redirects=False, transport=self._transport
        )
        try:
            async with asyncio.timeout(seconds):
                return await self._send(client, request)
        except CaptureLimit:
            return transport_failure("provider_capture_limit")
        except (httpx2.RequestError, TimeoutError):
            return transport_failure("provider_outcome_unknown")
        finally:
            async with asyncio.timeout(self._endpoint.close_seconds):
                await client.aclose()

    async def _send(self, client: httpx2.AsyncClient, request: JsonObject) -> ToolReply:
        endpoint = self._endpoint
        headers = {
            "authorization": f"Bearer {endpoint.api_key}",
            "content-type": "application/json",
            "accept": "application/json",
            "accept-encoding": "identity",
        }
        async with client.stream(
            "POST",
            endpoint.base_url.rstrip("/") + "/chat/completions",
            content=encode_json(request).encode(),
            headers=headers,
        ) as response:
            raw = await read_body(response, endpoint.max_response_bytes)
            return provider_reply(response, raw, endpoint.api_key)
