"""The HTTP boundary delegates execution ownership to the application coordinator."""

from fastapi import Request, Response

from slow_thinker_ii.application import ExecutionCoordinator, StartIntent
from slow_thinker_ii.contracts import encode_json

from ._operator_auth import OperatorAccess
from ._operator_errors import OperatorError, operator_error
from ._operator_input import CommandBody, SessionBody, StartBody, command_body
from ._operator_replies import command_reply


class OperatorCommands:
    def __init__(
        self,
        coordinator: ExecutionCoordinator,
        access: OperatorAccess,
        limit: int,
    ) -> None:
        self._coordinator, self._access, self._limit = coordinator, access, limit

    async def start(self, request: Request) -> Response:
        try:
            self._access.require(request)
            body = await command_body(request, StartBody, self._limit)
            intent = StartIntent(
                body.session_id,
                body.graph_id,
                body.graph_revision,
                body.configuration_revision,
                encode_json(body.input),
            )
            return command_reply(await self._coordinator.start(body.command_id, intent))
        except Exception as error:
            return operator_error(error)

    async def session(self, request: Request) -> Response:
        try:
            self._access.require(request)
            body = await command_body(request, SessionBody, self._limit)
            if not body.name.strip():
                raise OperatorError("invalid_session_name", 422)
            result = await self._coordinator.create_session(body.command_id, body.name)
            return command_reply(result)
        except Exception as error:
            return operator_error(error)

    async def stop(self, request: Request, run_id: str) -> Response:
        try:
            self._access.require(request)
            body = await command_body(request, CommandBody, self._limit)
            return command_reply(await self._coordinator.stop(body.command_id, run_id))
        except Exception as error:
            return operator_error(error)

    async def withdraw(self, request: Request, command_id: str) -> Response:
        try:
            self._access.require(request)
            body = await command_body(request, CommandBody, self._limit)
            if body.command_id != command_id:
                raise OperatorError("command_identity_mismatch", 422)
            return command_reply(await self._coordinator.withdraw(command_id))
        except Exception as error:
            return operator_error(error)
