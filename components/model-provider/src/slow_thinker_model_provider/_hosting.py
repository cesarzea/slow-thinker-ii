"""A provider-neutral resource keeps functional request policy separate from one native attempt."""

from slow_thinker_host import Invocation, JsonObject, Operation, ToolReply, validate_value

from ._config import ModelProviderConfig, parse_config
from ._requests import normalized_request
from ._schemas import effective_operation
from ._transport import ProviderTransport


class ModelProviderHost:
    def __init__(
        self, config: ModelProviderConfig, operation: Operation, transport: ProviderTransport
    ) -> None:
        if operation != effective_operation(config):
            raise ValueError("Configured native operation schemas do not match")
        self._config, self._transport = config, transport

    @staticmethod
    def describe(config: JsonObject) -> tuple[Operation, ...]:
        return (effective_operation(parse_config(config)),)

    def operations(self) -> tuple[Operation, ...]:
        return (effective_operation(self._config),)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        if name != "complete":
            raise ValueError("Unsupported model operation")
        validate_value(arguments, effective_operation(self._config).input_schema)
        return await self._transport.complete(normalized_request(self._config, arguments), context)
