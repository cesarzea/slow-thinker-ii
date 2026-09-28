"""Minimal hosting boundary; functional components need not inherit from an agent."""

from dataclasses import dataclass
from typing import Protocol

from ._json import JsonObject


@dataclass(frozen=True)
class Operation:
    name: str
    input_schema: JsonObject
    output_schema: JsonObject


@dataclass(frozen=True)
class Invocation:
    grant: str
    deadline: float | None = None


@dataclass(frozen=True)
class ToolReply:
    value: JsonObject
    is_error: bool = False


class HostedComponent(Protocol):
    def operations(self) -> tuple[Operation, ...]: ...

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply: ...
