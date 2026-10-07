"""The HTTP app over `support.platform.Platform`, an operator client and held model calls."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import httpx
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import HttpServices, HttpSettings, create_http_app
from slow_thinker_ii.application import RunSettings
from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext
from starlette.types import ASGIApp, Receive, Scope, Send
from support.examples import J1
from support.hosts import ScriptedHosts, hang
from support.platform import Platform
from support.waiting import until

TOKEN = "http-tests-operator-token-0123456789abcdef"
HOST = "127.0.0.1:8000"
ORIGIN = "http://127.0.0.1:5173"
BASE = f"http://{HOST}"


def http_settings(
    *, token: str | None = TOKEN, limit: int = 1_048_576, static: Path | None = None
) -> HttpSettings:
    return HttpSettings(token, (HOST, "localhost:8000"), (ORIGIN,), limit, static)


def services(platform: Platform, catalog: Callable[[], Catalog] | None = None) -> HttpServices:
    return HttpServices(
        catalog=catalog or (lambda: platform.catalog),
        graphs=platform.library,
        runs=platform.runs,
        gateway=platform.gateway,
        reports=platform.reports,
        usage=platform.usage,
    )


@dataclass(frozen=True)
class Api:
    platform: Platform
    app: FastAPI
    http: httpx.AsyncClient  # sends requests to the allowed host, with the token by default


@asynccontextmanager
async def operator_api(
    platform: Platform | None = None,
    *,
    settings: HttpSettings | None = None,
    http_services: HttpServices | None = None,
    raise_errors: bool = True,
    authorized: bool = True,
    peer: str | None = "127.0.0.1",
) -> AsyncGenerator[Api]:
    """Serves the app in this event loop; every run is stopped and cleaned up afterwards.

    With `authorized`, every request carries the operator token unless it sets its own.
    Requests come from the `peer` address, or over a connection without one when `None`.
    """
    platform = platform or Platform()
    app = create_http_app(http_services or services(platform), settings or http_settings())
    transport = httpx.ASGITransport(app=seen_from(app, peer), raise_app_exceptions=raise_errors)
    headers = {"authorization": f"Bearer {TOKEN}"} if authorized else {}
    try:
        async with httpx.AsyncClient(transport=transport, base_url=BASE, headers=headers) as http:
            yield Api(platform, app, http)
    finally:
        await platform.runs.shutdown()


def seen_from(app: FastAPI, peer: str | None) -> ASGIApp:
    """The app as reached from `peer`, or from a connection without a client address."""

    async def serve(scope: Scope, receive: Receive, send: Send) -> None:
        await app({**scope, "client": None if peer is None else (peer, 50_000)}, receive, send)

    return serve


def held_platform(settings: RunSettings | None = None) -> tuple[Platform, ScriptedHosts]:
    """A platform whose Proposer activations never answer until their run stops."""
    hosts = ScriptedHosts({"proposer": hang()})
    return Platform(hosts=lambda _plan: hosts, settings=settings), hosts


async def held_call(api: Api, hosts: ScriptedHosts, message: JsonValue = None) -> CallContext:
    """Runs J1 (saved once) and returns the context of its held Proposer activation."""
    if not api.platform.library.graphs():
        api.platform.saved(J1)
    known = len(hosts.calls)
    await api.platform.runs.start("funny-story", 1, message)
    await until(lambda: len(hosts.calls) > known)
    return hosts.calls[known]


def error(response: httpx.Response) -> tuple[int, str]:
    """The status and error code of an operator or component error reply."""
    body = response.json()
    assert set(body) == {"error"}
    return response.status_code, body["error"]["code"]
