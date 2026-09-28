"""Expose managed operation calls without leaking protocol SDK objects upstream."""

import asyncio
import math
import time
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager

from jsonschema import Draft202012Validator, validate
from mcp import Client, types
from pydantic import JsonValue
from referencing import Registry

from slow_thinker_ii.contracts import OperationContract, OperationResult

from ._launch import ProcessLaunch
from ._owned import OwnedProcess, ProcessOutcome
from ._readiness import DEADLINE_META, GRANT_META, JSON_OBJECT, PROTOCOL_VERSION, require_ready
from ._transport import transport


def _call_deadline(timeout: float, deadline: float | None) -> float:
    if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Invalid managed component invocation")
    end = time.monotonic() + timeout
    if deadline is not None:
        if isinstance(deadline, bool) or not math.isfinite(deadline):
            raise ValueError("Invalid managed deadline")
        end = min(end, deadline)
    return end


class ComponentConnection:
    def __init__(self, client: Client, operations: tuple[OperationContract, ...]) -> None:
        self._client = client
        self._operations = {item.name: item for item in operations}

    def operation_names(self) -> tuple[str, ...]:
        return tuple(self._operations)

    def prepare(self, name: str, arguments_json: str) -> str:
        operation = self._operations.get(name)
        if operation is None:
            raise ValueError("Unknown managed component operation")
        arguments = JSON_OBJECT.validate_json(arguments_json)
        schema = JSON_OBJECT.validate_json(operation.input_schema_json)
        validate(arguments, schema, cls=Draft202012Validator, registry=Registry[JsonValue]())
        return JSON_OBJECT.dump_json(arguments).decode()

    async def call(
        self,
        name: str,
        arguments_json: str,
        grant: str,
        timeout: float,
        *,
        deadline: float | None = None,
    ) -> OperationResult:
        operation = self._operations.get(name)
        if operation is None or not grant:
            raise ValueError("Invalid managed component invocation")
        end = _call_deadline(timeout, deadline)
        arguments = JSON_OBJECT.validate_json(self.prepare(name, arguments_json))
        if time.monotonic() >= end:
            raise TimeoutError("Managed component deadline expired before dispatch")
        async with asyncio.timeout_at(end):
            reply = await self._client.call_tool(
                name, arguments, meta={GRANT_META: grant, DEADLINE_META: end}
            )
        value = JSON_OBJECT.validate_python(reply.structured_content)
        validate(
            value,
            JSON_OBJECT.validate_json(operation.output_schema_json),
            cls=Draft202012Validator,
            registry=Registry[JsonValue](),
        )
        return OperationResult(JSON_OBJECT.dump_json(value).decode(), reply.is_error)


class ComponentProcess:
    def __init__(self, launch: ProcessLaunch, operations: tuple[OperationContract, ...]) -> None:
        self._launch = launch
        self._operations = operations
        self._owner = OwnedProcess(launch)

    def outcome(self) -> ProcessOutcome | None:
        return self._owner.outcome()

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[ComponentConnection]:
        client = Client(
            transport(self._owner, self._launch),
            mode=PROTOCOL_VERSION,
            client_info=types.Implementation(name="Slow Thinker II", version="0.1.0.dev1"),
        )
        try:
            async with AsyncExitStack() as stack:
                async with asyncio.timeout(self._launch.startup_seconds):
                    await stack.enter_async_context(client)
                    await require_ready(client, self._operations)
                yield ComponentConnection(client, self._operations)
        except ExceptionGroup as group:
            error: BaseException = group
            while isinstance(error, BaseExceptionGroup) and len(error.exceptions) == 1:
                error = error.exceptions[0]
            raise error from None
