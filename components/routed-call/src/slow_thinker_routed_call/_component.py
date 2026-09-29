"""Ordinary worker plus one redirector, both called through platform MCP aliases."""

from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    Invocation,
    JsonObject,
    JsonValue,
    McpEndpoint,
    ToolReply,
    decode_json,
    json_object,
    managed_mcp_client,
    validate_value,
)

from ._config import parse_config
from ._pointer import extract
from ._types import RoutedCallConfig


class RoutedCall:
    def __init__(self, config: RoutedCallConfig, endpoint: McpEndpoint) -> None:
        self.config = parse_config(
            {
                "input_schema": decode_json(config.input_schema_json),
                "worker_operation": config.worker_operation,
                "worker_output_schema": decode_json(config.worker_output_schema_json),
                "router_input_pointer": config.router_input_pointer,
                "outputs": list(config.outputs),
            }
        )
        self._endpoint = endpoint
        self._worker = endpoint.alias("worker", self.config.worker_operation)
        self._router = endpoint.alias("router", "route")

    async def invoke(self, arguments: JsonObject, invocation: Invocation) -> ToolReply:
        stage = "input"
        try:
            value = json_object(arguments)
            validate_value(value, json_object(decode_json(self.config.input_schema_json)))
            stage = "worker"
            async with managed_mcp_client(self._endpoint, invocation) as client:
                output = await self._worker_output(client, value)
                stage = "extraction"
                selected = extract(output, self.config.router_input_pointer)
                stage = "router"
                port = await self._router_port(client, selected)
            return ToolReply({"status": "succeeded", "port": port, "value": output})
        except Exception as error:
            raise MCPError(
                code=-32603,
                message="routed_call_failed",
                data={"stage": stage, "reason": str(error)},
            ) from error

    async def _worker_output(self, client: Client, value: JsonObject) -> JsonObject:
        worker = await client.call_tool(self._worker, value)
        if worker.is_error:
            raise ValueError("Worker returned an error")
        output = json_object(worker.structured_content)
        validate_value(output, json_object(decode_json(self.config.worker_output_schema_json)))
        return output

    async def _router_port(self, client: Client, selected: JsonValue) -> str:
        router = await client.call_tool(self._router, {"value": selected})
        if router.is_error:
            raise ValueError("Router returned an error")
        return self._port(json_object(router.structured_content))

    def _port(self, value: JsonObject) -> str:
        port = value.get("port")
        if set(value) != {"port"} or not isinstance(port, str) or port not in self.config.outputs:
            raise ValueError("Router did not return exactly one declared output port")
        return port
