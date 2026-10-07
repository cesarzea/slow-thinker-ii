"""The handler's view of one call: time remaining, reports and the platform's LLM service."""

import asyncio
import sys
from contextlib import suppress
from typing import Protocol

import httpx2
from openai import AsyncOpenAI

from ._bootstrap import Bootstrap
from ._calls import CallMeta
from ._json import JsonObject, JsonValue, json_value
from ._protocol import REPORT_KINDS
from ._report import send_report


class Context(Protocol):
    """Services for one call; valid only while the handler runs."""

    @property
    def activation_id(self) -> str: ...

    def remaining_seconds(self) -> float: ...

    async def report(self, kind: str, content: JsonValue) -> None: ...

    def llm_client(self) -> AsyncOpenAI: ...


class InvocationContext:
    """Binds one call's grant and budget to the platform endpoints of the bootstrap."""

    def __init__(self, bootstrap: Bootstrap, call: CallMeta, deadline: float) -> None:
        self._bootstrap = bootstrap
        self._call = call
        self._deadline = deadline
        self._clients: list[AsyncOpenAI] = []

    @property
    def activation_id(self) -> str:
        return self._call.activation_id

    def remaining_seconds(self) -> float:
        return max(0.0, self._deadline - asyncio.get_running_loop().time())

    async def report(self, kind: str, content: JsonValue) -> None:
        """Record reported evidence in one attempt. Any failure, an invalid report included,
        is logged to standard error and never raised or retried."""
        try:
            if kind not in REPORT_KINDS:
                raise ValueError(f"unsupported kind {kind!r}")
            arguments: JsonObject = {"kind": kind, "content": json_value(content)}
            seconds = self.remaining_seconds()
            await send_report(self._bootstrap.mcp_url, self._call.grant, arguments, seconds)
        except Exception as error:
            node = self._bootstrap.node_id
            sys.stderr.write(f"Node {node}: report not recorded: {type(error).__name__}: {error}\n")

    def llm_client(self) -> AsyncOpenAI:
        """A client of the platform's Chat Completions endpoint, without retries."""
        seconds = self.remaining_seconds()
        client = AsyncOpenAI(
            base_url=self._bootstrap.llm_base_url,
            api_key=self._call.grant,
            max_retries=0,
            timeout=seconds,
            http_client=httpx2.AsyncClient(
                timeout=seconds, trust_env=False, follow_redirects=False
            ),
        )
        self._clients.append(client)
        return client

    async def close(self) -> None:
        for client in self._clients:
            with suppress(Exception):
                await client.close()
