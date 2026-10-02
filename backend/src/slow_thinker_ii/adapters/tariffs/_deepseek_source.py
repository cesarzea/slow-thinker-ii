"""One bounded TLS pricing-page fetch uses the existing daily tariff source port."""

import asyncio

import httpx

from slow_thinker_ii.accounting import TariffRevision

from ._deepseek_validation import DEEPSEEK_SOURCE_URL, MAX_PRICING_BYTES, parse_deepseek_pricing


class DeepSeekTariffSource:
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport

    async def fetch(self, now: int) -> TariffRevision:
        try:
            async with asyncio.timeout(20):
                payload = await self._download()
        except httpx.HTTPError as error:
            raise OSError("Direct pricing download failed") from error
        return parse_deepseek_pricing(payload, now)

    async def _download(self) -> bytes:
        async with (
            httpx.AsyncClient(
                timeout=10, follow_redirects=False, trust_env=False, transport=self._transport
            ) as client,
            client.stream(
                "GET",
                DEEPSEEK_SOURCE_URL,
                headers={"Accept": "text/html", "Accept-Encoding": "identity"},
            ) as reply,
        ):
            reply.raise_for_status()
            content_type = reply.headers.get("content-type", "").split(";", 1)[0].lower()
            if content_type != "text/html":
                raise ValueError("Expected the official HTML pricing representation")
            content = bytearray()
            async for part in reply.aiter_bytes(chunk_size=16_384):
                if len(content) + len(part) > MAX_PRICING_BYTES:
                    raise ValueError("Pricing page exceeds its capture bound")
                content.extend(part)
            return bytes(content)
