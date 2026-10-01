"""Fresh standard clients carry invocation grants only to the local platform endpoint."""

import asyncio
import math
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx2
from openai import AsyncOpenAI
from slow_thinker_host import Invocation, JsonObject


@dataclass(frozen=True)
class OpenAIEndpoint:
    base_url: str
    model: str
    timeout_seconds: float
    close_seconds: float

    def __post_init__(self) -> None:
        url = urlsplit(self.base_url)
        if url.scheme != "http" or url.hostname not in {"127.0.0.1", "::1"}:
            raise ValueError("The initial host requires a local platform endpoint")
        if (
            url.port == 0
            or url.username
            or url.password
            or url.query
            or url.fragment
            or not self.model
        ):
            raise ValueError("Invalid platform client binding")
        for seconds in (self.timeout_seconds, self.close_seconds):
            if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError("Client timeouts must be finite and positive")

    @asynccontextmanager
    async def client(self, invocation: Invocation) -> AsyncGenerator[AsyncOpenAI]:
        if not invocation.grant:
            raise ValueError("Invocation authority is required")
        timeout = self.timeout_seconds
        if invocation.deadline is not None:
            timeout = min(timeout, invocation.deadline - time.monotonic())
        if timeout <= 0:
            raise TimeoutError("Invocation deadline expired before client creation")
        client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=invocation.grant,
            max_retries=0,
            timeout=timeout,
            http_client=httpx2.AsyncClient(
                timeout=timeout, trust_env=False, follow_redirects=False
            ),
        )
        try:
            yield client
        finally:
            async with asyncio.timeout(self.close_seconds):
                await client.close()


def endpoint_from_record(record: JsonObject) -> OpenAIEndpoint:
    if set(record) != {"base_url", "model", "timeout_seconds", "close_seconds"}:
        raise ValueError("Unsupported platform client fields")
    url, model = record["base_url"], record["model"]
    timeout, close = record["timeout_seconds"], record["close_seconds"]
    if not isinstance(url, str) or not isinstance(model, str):
        raise ValueError("Invalid platform endpoint identity")
    if not isinstance(timeout, int | float) or not isinstance(close, int | float):
        raise ValueError("Invalid platform endpoint timeouts")
    return OpenAIEndpoint(url, model, timeout, close)
