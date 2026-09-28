"""A reused host constructs a fresh implementation and client for every invocation."""

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from mcp.shared.exceptions import MCPError
from openai import APIError, AsyncOpenAI
from slow_thinker_host import (
    Invocation,
    JsonObject,
    Operation,
    ToolReply,
    decode_json,
    encode_json,
    json_object,
)

from ._component import LLMCall
from ._config import parse_config
from ._schemas import effective_operation
from ._types import LLMCallConfig, ModelOperationError

type ClientFactory = Callable[[Invocation], AbstractAsyncContextManager[AsyncOpenAI]]


class LLMCallHost:
    def __init__(
        self,
        config: LLMCallConfig,
        operation: Operation,
        client_factory: ClientFactory,
        model: str,
        implementation: type[LLMCall] = LLMCall,
    ) -> None:
        settings = parse_config(config)
        expected = effective_operation(settings)
        if operation != expected:
            raise ValueError("Configured LLMCall operation schemas do not match")
        self._config = encode_json(json_object(settings))
        self._operation = expected
        self._clients, self._model, self._implementation = client_factory, model, implementation

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        if name != "generate":
            raise ValueError("Unsupported LLMCall operation")
        try:
            async with self._clients(context) as client:
                component = self._implementation(
                    parse_config(decode_json(self._config)), client, self._model
                )
                result = await component.generate(json_object(arguments))
        except ModelOperationError as error:
            raise MCPError(
                code=-32603, message=error.code, data={"failure_code": error.code}
            ) from error
        except APIError as error:
            raise MCPError(code=-32603, message="model_request_failed") from error
        return ToolReply(json_object(result), is_error=result["status"] == "error")
