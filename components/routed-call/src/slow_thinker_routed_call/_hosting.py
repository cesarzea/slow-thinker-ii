"""Expose composition schemas without adding custom worker reasoning."""

from slow_thinker_host import (
    Invocation,
    JsonObject,
    McpEndpoint,
    Operation,
    ToolReply,
    decode_json,
    json_object,
)

from ._component import RoutedCall
from ._config import parse_config
from ._types import RoutedCallConfig


def effective_operation(config: RoutedCallConfig) -> Operation:
    worker_schema = json_object(decode_json(config.worker_output_schema_json))
    worker_schema.setdefault("$id", "urn:slow-thinker-ii:routed-worker-output")
    return Operation(
        "invoke",
        json_object(decode_json(config.input_schema_json)),
        {
            "type": "object",
            "properties": {
                "status": {"const": "succeeded"},
                "port": {"enum": list(config.outputs)},
                "value": worker_schema,
            },
            "required": ["status", "port", "value"],
            "additionalProperties": False,
        },
    )


class RoutedCallHost:
    def __init__(self, config: JsonObject, operation: Operation, endpoint: McpEndpoint) -> None:
        settings = parse_config(config)
        self._operation = effective_operation(settings)
        if operation != self._operation:
            raise ValueError("Configured RoutedCall operation schemas do not match")
        self._component = RoutedCall(settings, endpoint)

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        return (effective_operation(parse_config(config)),)

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        if name != "invoke":
            raise ValueError("Unsupported RoutedCall operation")
        return await self._component.invoke(arguments, context)
