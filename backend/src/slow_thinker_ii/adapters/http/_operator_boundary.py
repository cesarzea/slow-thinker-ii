"""Every `/api/v2` request is authorized before routing; no operator reply is cached."""

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ._operator_auth import OperatorAccess
from ._operator_errors import operator_error, operator_path


class OperatorBoundary:
    """ASGI middleware: refuses unauthorized operator requests before any body is read and
    marks every operator response, refusals and failures included, `Cache-Control: no-store`."""

    def __init__(self, app: ASGIApp, access: OperatorAccess) -> None:
        self._app = app
        self._access = access

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not operator_path(str(scope["path"])):
            await self._app(scope, receive, send)
            return

        async def no_store(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["cache-control"] = "no-store"
            await send(message)

        denial = self._access.denial(scope)
        if denial is None:
            await self._app(scope, receive, no_store)
        else:
            await operator_error(denial)(scope, receive, no_store)
