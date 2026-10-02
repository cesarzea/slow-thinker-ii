"""Describe the configured ordinary operation without opening clients."""

from slow_thinker_host import (
    Invocation,
    JsonObject,
    McpEndpoint,
    Operation,
    ToolReply,
    decode_json,
    json_object,
)

from ._component import ContextualCall
from ._config import settings


def operation(config: JsonObject) -> Operation:
    frozen = settings(config)
    return Operation(
        "invoke",
        json_object(decode_json(frozen.input_schema)),
        json_object(decode_json(frozen.output_schema)),
    )


class ContextualCallHost:
    def __init__(self, config: JsonObject, declared: Operation, endpoint: McpEndpoint) -> None:
        self._operation = operation(config)
        if declared != self._operation:
            raise ValueError("Configured ContextualCall operation schemas do not match")
        self._component = ContextualCall(config, endpoint)

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        return (operation(config),)

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        if name != "invoke":
            raise ValueError("Unsupported ContextualCall operation")
        return await self._component.invoke(arguments, context)
