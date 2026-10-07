"""The operator API, version 2: every route, plus an enveloped 404 for anything else."""

from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Request, Response
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

from ._change_routes import ChangeRoutes
from ._graph_routes import GraphRoutes
from ._operator_errors import ACCESS, PREFIX, OperatorError
from ._operator_input import query, reply
from ._run_routes import RunRoutes
from ._settings import HttpServices

type Endpoint = Callable[..., Awaitable[Response]]


def operator_router(services: HttpServices, limit: int, authentication: str) -> APIRouter:
    graphs, changes = GraphRoutes(services, limit), ChangeRoutes(services, limit)
    runs = RunRoutes(services, limit)
    routes: tuple[tuple[str, str, Endpoint], ...] = (
        ("GET", ACCESS, AccessRoute(authentication).access),
        ("GET", "/catalog", graphs.catalog),
        ("POST", "/graphs/validate", graphs.validate),
        ("GET", "/graphs", graphs.graphs),
        ("POST", "/graphs", graphs.create),
        ("GET", "/graphs/{graph_id}/branches", changes.branches),
        ("POST", "/graphs/{graph_id}/branches", changes.create_branch),
        ("POST", "/graphs/{graph_id}/changes", changes.record),
        ("GET", "/graphs/{graph_id}/changes", changes.changes),
        ("GET", "/graphs/{graph_id}/changes/{change}", changes.change),
        ("POST", "/graphs/{graph_id}/versions", changes.activate),
        ("GET", "/graphs/{graph_id}", graphs.graph),
        ("GET", "/graphs/{graph_id}/versions/{version}", graphs.version),
        ("POST", "/runs", runs.start),
        ("GET", "/runs", runs.runs),
        ("GET", "/runs/{run_id}", runs.run),
        ("GET", "/runs/{run_id}/events", runs.events),
        ("POST", "/runs/{run_id}/stop", runs.stop),
        ("GET", "/usage", runs.usage),
    )
    router = APIRouter(prefix=PREFIX)
    for method, path, endpoint in routes:
        router.add_api_route(path, endpoint, methods=[method])
    return router


class AccessRoute:
    def __init__(self, authentication: str) -> None:
        self._authentication = authentication

    async def access(self, request: Request) -> Response:
        """`{"authentication": "token" | "none"}`; the boundary lets it through without a token."""
        query(request)
        return reply({"authentication": self._authentication})


def unknown_routes() -> tuple[Route, ...]:
    """Every method on every other operator path; added after the routes, before any mount."""
    return (Route(PREFIX, Unknown()), Route(f"{PREFIX}/{{path:path}}", Unknown()))


class Unknown:
    """ASGI endpoint, so that it matches any method: unknown paths, and known paths with
    another method, are not operator resources."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        del scope, receive, send
        raise OperatorError(404, "not_found", "No operator API resource matches this request.")
