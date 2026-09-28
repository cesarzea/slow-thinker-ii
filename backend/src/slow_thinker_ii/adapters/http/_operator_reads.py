"""Read projections without replaying commands or acquiring invocation authority."""

import asyncio
from collections.abc import Callable

from fastapi import Request, Response

from slow_thinker_ii.application import OperatorQueries, OperatorSessions
from slow_thinker_ii.contracts import encode_json

from ._operator_auth import OperatorAccess
from ._operator_errors import OperatorError, operator_error
from ._operator_replies import receipt_data, representation


class OperatorReads:
    def __init__(
        self,
        queries: OperatorQueries,
        sessions: OperatorSessions,
        access: OperatorAccess,
        limit: int,
    ) -> None:
        self._queries, self._sessions, self._access, self._limit = queries, sessions, access, limit

    async def _read(self, request: Request, query: Callable[[], str | None]) -> Response:
        try:
            self._access.require(request)
            return representation(request, await asyncio.to_thread(query), self._limit)
        except Exception as error:
            return operator_error(error)

    async def workspace(self, request: Request) -> Response:
        return await self._read(request, lambda: self._queries.workspace(cursor(request)))

    async def run(self, request: Request, run_id: str) -> Response:
        return await self._read(request, lambda: self._queries.run(run_id))

    async def result(self, request: Request, run_id: str) -> Response:
        return await self._read(request, lambda: self._queries.result(run_id))

    async def events(self, request: Request, run_id: str) -> Response:
        return await self._read(request, lambda: self._queries.events(run_id, cursor(request)))

    async def call(self, request: Request, run_id: str, call_id: str) -> Response:
        return await self._read(
            request, lambda: self._queries.call(run_id, call_id, cursor(request))
        )

    async def payload(self, request: Request, run_id: str, payload_id: str) -> Response:
        return await self._read(request, lambda: self._queries.payload(run_id, payload_id))

    async def activation(self, request: Request, run_id: str, activation_id: str) -> Response:
        return await self._read(
            request, lambda: self._queries.activation(run_id, activation_id, cursor(request))
        )

    async def definition(self, request: Request, run_id: str) -> Response:
        return await self._read(request, lambda: self._queries.definition(run_id))

    async def session_runs(self, request: Request, session_id: str) -> Response:
        return await self._read(
            request, lambda: self._queries.session_runs(session_id, cursor(request))
        )

    async def command(self, request: Request, command_id: str) -> Response:
        def query() -> str | None:
            receipt = self._sessions.command(command_id)
            return None if receipt is None else encode_json(receipt_data(receipt))

        return await self._read(request, query)


def cursor(request: Request) -> str | None:
    if set(request.query_params) - {"cursor"} or len(request.query_params.getlist("cursor")) > 1:
        raise OperatorError("invalid_query", 400)
    return request.query_params.get("cursor")
