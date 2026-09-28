"""An execution-enabled application protects every operator route, including catalogue reads."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ._operator_auth import OperatorAccess
from ._operator_errors import OperatorError, operator_error


class OperatorBoundary(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, access: OperatorAccess) -> None:
        super().__init__(app, dispatch=self._dispatch)
        self._access = access

    async def _dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith("/api/v1/"):
            try:
                self._access.require(request)
            except OperatorError as error:
                return operator_error(error)
        response = await call_next(request)
        if request.url.path.startswith("/api/v1/"):
            response.headers["cache-control"] = "no-store"
        return response
