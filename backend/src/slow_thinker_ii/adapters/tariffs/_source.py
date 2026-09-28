"""Bounded public catalogue download; no API keys or model calls are involved."""

import asyncio

import httpx

from slow_thinker_ii.accounting import TariffRevision

from ._validation import SOURCE_URL, parse_catalog

MAX_CATALOG_BYTES = 4 * 1024 * 1024


class VercelTariffSource:
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport

    async def fetch(self, now: int) -> TariffRevision:
        try:
            async with asyncio.timeout(20):
                payload = await self._download()
        except httpx.HTTPError as error:
            raise OSError("Catalogue download failed") from error
        return parse_catalog(payload, now)

    async def _download(self) -> bytes:
        async with (
            httpx.AsyncClient(
                timeout=10, follow_redirects=False, trust_env=False, transport=self._transport
            ) as client,
            client.stream("GET", SOURCE_URL, headers={"Accept": "application/json"}) as reply,
        ):
            reply.raise_for_status()
            content = bytearray()
            async for part in reply.aiter_bytes():
                if len(content) + len(part) > MAX_CATALOG_BYTES:
                    raise ValueError("Catalogue exceeds the configured download limit")
                content.extend(part)
            return bytes(content)
