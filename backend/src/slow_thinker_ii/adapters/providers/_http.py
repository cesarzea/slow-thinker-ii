"""The OpenAI and DeepSeek adapters: one bounded HTTP attempt per call to a reviewed origin."""

import asyncio
from collections.abc import Mapping

import httpx

from slow_thinker_ii.application import LlmModel, LlmProvider, ProviderReply
from slow_thinker_ii.contracts import JsonObject, encode_json

from ._capture import CaptureLimit, read_body
from ._endpoint import ProviderEndpoint
from ._replies import error_reply, response_reply, utc_now
from ._requests import native_request


class HttpProvider(LlmProvider):
    """Calls the endpoint of the model's provider: no retries, redirects or proxy settings.

    `endpoints` is keyed by provider name; `transport` replaces the network in tests.
    """

    def __init__(
        self,
        endpoints: Mapping[str, ProviderEndpoint],
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        for name, endpoint in endpoints.items():
            if name != endpoint.provider:
                raise ValueError(
                    f"The endpoint configured as “{name}” is a {endpoint.provider} one."
                )
        self._endpoints = dict(endpoints)
        self._transport = transport

    async def complete(
        self, model: LlmModel, request: JsonObject, timeout_s: float
    ) -> ProviderReply:
        """One attempt within the smaller of `timeout_s` and the endpoint's timeout.

        Expected failures are replies (502 `provider_error`, 504 `provider_timeout`); a
        cancellation propagates after the connection is closed.
        """
        started = utc_now()
        name = model.settings.provider
        endpoint = self._endpoints.get(name)
        if endpoint is None:
            return error_reply(502, f"No provider endpoint is configured for “{name}”.", started)
        native = native_request(endpoint.provider, model, request)
        if isinstance(native, str):
            return error_reply(502, native, started)
        seconds = min(timeout_s, endpoint.timeout_seconds)
        if not seconds > 0:
            return error_reply(504, "No time was left for the provider call.", started)
        return await self._attempt(endpoint, native, seconds)

    async def _attempt(
        self, endpoint: ProviderEndpoint, native: JsonObject, seconds: float
    ) -> ProviderReply:
        started = utc_now()
        try:
            async with asyncio.timeout(seconds):
                status, raw = await self._exchange(endpoint, native, seconds)
        except CaptureLimit:
            limit = endpoint.max_response_bytes
            return error_reply(502, f"The provider's response exceeds {limit} bytes.", started)
        except (TimeoutError, httpx.TimeoutException):
            message = f"The provider did not answer within {seconds:g} seconds."
            return error_reply(504, message, started)
        except httpx.HTTPError as error:  # the error's text may quote the request: not kept
            message = f"The connection to the provider failed ({type(error).__name__})."
            return error_reply(502, message, started)
        return response_reply(endpoint, status, raw, started)

    async def _exchange(
        self, endpoint: ProviderEndpoint, native: JsonObject, seconds: float
    ) -> tuple[int, bytes]:
        client = httpx.AsyncClient(
            timeout=seconds, trust_env=False, follow_redirects=False, transport=self._transport
        )
        content = encode_json(native).encode("utf-8")
        headers = _headers(endpoint.api_key)
        try:
            async with client.stream(
                "POST", endpoint.url, content=content, headers=headers
            ) as reply:
                return reply.status_code, await read_body(reply, endpoint.max_response_bytes)
        finally:  # also on cancellation: the response, then the connection, are closed
            await client.aclose()


def _headers(api_key: str) -> dict[str, str]:
    return {
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json",
        "accept": "application/json",
        "accept-encoding": "identity",
    }
