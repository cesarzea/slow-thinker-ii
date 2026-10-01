"""Independent MCP host for one installed deterministic selector."""

from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, JsonObject, Operation, ToolReply, decode_json, json_object

from ._config import load_selector, parse_config
from ._redirector import Redirector
from ._types import RedirectorConfig


def effective_operation(config: RedirectorConfig) -> Operation:
    value_schema = json_object(decode_json(config.input_schema_json))
    value_schema.setdefault("$id", "urn:slow-thinker-ii:redirector-input")
    return Operation(
        "route",
        {
            "type": "object",
            "properties": {"value": value_schema},
            "required": ["value"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {"port": {"enum": list(config.outputs)}},
            "required": ["port"],
            "additionalProperties": False,
        },
    )


class RedirectorHost:
    def __init__(self, config: JsonObject, operation: Operation) -> None:
        settings = parse_config(config)
        self._operation = effective_operation(settings)
        if operation != self._operation:
            raise ValueError("Configured Redirector operation schemas do not match")
        self._redirector = Redirector(settings, load_selector(settings.selector))

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        settings = parse_config(config)
        load_selector(settings.selector)
        return (effective_operation(settings),)

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del context
        if name != "route" or set(arguments) != {"value"}:
            raise ValueError("Unsupported Redirector invocation")
        try:
            return ToolReply({"port": self._redirector.route(arguments["value"])})
        except Exception as error:
            raise MCPError(
                code=-32603,
                message="selector_failed",
                data={
                    "stage": "selector",
                    "reason": str(error),
                },
            ) from error
