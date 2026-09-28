"""The model resource owns provider access; the platform owns authorization and settlement."""

from slow_thinker_host import Invocation, JsonObject, Operation, ToolReply

from ._config import ModelConfig, parse_config
from ._schemas import effective_operation, native_request
from ._transport import ProviderTransport


class OpenAIModelHost:
    def __init__(
        self, config: ModelConfig, operation: Operation, transport: ProviderTransport
    ) -> None:
        if operation != effective_operation(config):
            raise ValueError("Configured model operation schemas do not match")
        self._config, self._transport = config, transport

    @staticmethod
    def describe(config: JsonObject) -> tuple[Operation, ...]:
        return (effective_operation(parse_config(config)),)

    def operations(self) -> tuple[Operation, ...]:
        return (effective_operation(self._config),)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        if name != "complete":
            raise ValueError("Unsupported model operation")
        return await self._transport.complete(native_request(self._config, arguments), context)
