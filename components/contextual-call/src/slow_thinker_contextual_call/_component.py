"""Optional context stages around one ordinary worker, without retries or fallback."""

from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    Invocation,
    JsonObject,
    McpEndpoint,
    ToolReply,
    decode_json,
    json_object,
    managed_mcp_client,
    validate_value,
)

from ._config import settings
from ._pointer import extract, insert
from ._stages import calculate, memory_get, memory_put, stage, worker


class ContextualCall:
    def __init__(self, config: JsonObject, endpoint: McpEndpoint) -> None:
        self._config, self._endpoint = settings(config), endpoint
        if any(item.slot not in {"worker", "memory", "calculator"} for item in endpoint.resources):
            raise ValueError("Unsupported ContextualCall resource binding")
        endpoint.alias("worker", self._config.worker_operation)
        for enabled, slot, operation in (
            (self._config.memory_read, "memory", "get"),
            (self._config.calculation_enabled, "calculator", "calculate"),
            (self._config.memory_write, "memory", "put"),
        ):
            if enabled:
                endpoint.alias(slot, operation)

    async def invoke(self, arguments: JsonObject, invocation: Invocation) -> ToolReply:
        config = self._config
        try:
            value = json_object(arguments)
            validate_value(value, json_object(decode_json(config.input_schema)))
            async with managed_mcp_client(self._endpoint, invocation) as client:
                await stage("memory_get", self._memory_context(client, value))
                await stage("calculate", self._calculation_context(client, arguments, value))
                output = await stage(
                    "worker",
                    worker(
                        client,
                        self._endpoint,
                        config.worker_operation,
                        value,
                        json_object(decode_json(config.output_schema)),
                    ),
                )
                await stage("memory_put", self._store(client, output))
            return ToolReply(output)
        except MCPError:
            raise
        except Exception as error:
            raise MCPError(
                code=-32603,
                message="contextual_call_failed",
                data={"stage": "input", "reason": str(error)[:160]},
            ) from error

    async def _memory_context(self, client: Client, value: JsonObject) -> None:
        config = self._config
        if config.memory_read:
            insert(
                value,
                config.memory_field,
                await memory_get(client, self._endpoint, config.memory_key),
            )

    async def _calculation_context(
        self, client: Client, arguments: JsonObject, value: JsonObject
    ) -> None:
        config = self._config
        if config.calculation_enabled:
            expression = extract(arguments, config.expression_pointer)
            insert(
                value, config.calculation_field, await calculate(client, self._endpoint, expression)
            )

    async def _store(self, client: Client, output: JsonObject) -> None:
        config = self._config
        if config.memory_write:
            await memory_put(
                client, self._endpoint, config.memory_key, extract(output, config.result_pointer)
            )
