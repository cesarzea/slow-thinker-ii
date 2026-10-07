"""The HTTP application: operator API, model endpoint, report endpoint and the interface."""

from fastapi import FastAPI
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.types import Lifespan

from ._chat_completions import ChatCompletions
from ._mcp_gateway import ReportEndpoint
from ._operator_auth import OperatorAccess
from ._operator_boundary import OperatorBoundary
from ._operator_errors import OPERATOR_ERRORS, internal_error, operator_reply
from ._operator_routes import operator_router, unknown_routes
from ._settings import HttpServices, HttpSettings


def create_http_app(
    services: HttpServices, settings: HttpSettings, lifespan: Lifespan[FastAPI] | None = None
) -> FastAPI:
    """Every handler is `async` and calls the use cases on the event-loop thread.

    Raises `ValueError` when `settings.static_directory` is not a directory.
    """
    static = settings.static_directory
    if static is not None and not static.is_dir():
        raise ValueError(f"The interface directory “{static}” does not exist.")
    app = FastAPI(
        title="Slow Thinker II", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
    )
    access = OperatorAccess(settings)
    app.add_middleware(OperatorBoundary, access=access)
    for kind in OPERATOR_ERRORS:
        app.add_exception_handler(kind, operator_reply)
    app.add_exception_handler(Exception, internal_error)
    limit = settings.max_body_bytes
    app.include_router(operator_router(services, limit, access.authentication))
    completions = ChatCompletions(services.gateway, limit)
    app.add_api_route("/v1/chat/completions", completions.complete, methods=["POST"])
    reports = ReportEndpoint(services.runs, services.reports, limit)
    app.router.routes.extend((Route("/mcp", reports, methods=["POST"]), *unknown_routes()))
    if static is not None:
        app.mount("/", StaticFiles(directory=static, html=True))
    return app
