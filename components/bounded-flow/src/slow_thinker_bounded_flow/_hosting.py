"""Publish exact bounded-control decisions through the optional MCP host."""

from slow_thinker_host import Invocation, JsonObject, JsonValue, Operation, ToolReply, json_object

from ._config import parse_config
from ._flow import BoundedFlow
from ._types import BoundedFlowConfig, CompletedStep


def _object(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def effective_operation(config: BoundedFlowConfig) -> Operation:
    step = _object({"node": {"type": "string"}, "port": {"type": "string"}})
    activate = _object(
        {
            "action": {"const": "activate"},
            "nodes": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1,
                "items": json_object({"enum": sorted({route.node for route in config.routes})}),
            },
        }
    )
    complete = _object({"action": {"const": "complete"}})
    exhausted = _object(
        {
            "action": {"const": "exhausted"},
            "reason": {"const": "activation_limit_reached"},
        }
    )
    return Operation(
        "next",
        _object({"completed": {"type": "array", "items": step}}),
        {"type": "object", "oneOf": [activate, complete, exhausted]},
    )


def _completed(value: JsonValue) -> tuple[CompletedStep, ...]:
    if not isinstance(value, list):
        raise ValueError("Completed history must be an array")
    steps: list[CompletedStep] = []
    for item in value:
        record = json_object(item)
        if set(record) != {"node", "port"}:
            raise ValueError("Unsupported completed history fields")
        node, port = record["node"], record["port"]
        if not isinstance(node, str) or not isinstance(port, str):
            raise ValueError("History node and port must be strings")
        steps.append(CompletedStep(node, port))
    return tuple(steps)


class BoundedFlowHost:
    def __init__(self, config: JsonObject, operation: Operation) -> None:
        settings = parse_config(config)
        self._operation = effective_operation(settings)
        if operation != self._operation:
            raise ValueError("Configured BoundedFlow operation schemas do not match")
        self._controller = BoundedFlow(settings)

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        return (effective_operation(parse_config(config)),)

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del context
        if name != "next" or set(arguments) != {"completed"}:
            raise ValueError("Unsupported BoundedFlow invocation")
        decision = self._controller.next(_completed(arguments["completed"]))
        value: JsonObject = {"action": decision.action}
        if decision.node is not None:
            value["nodes"] = [decision.node]
        if decision.reason is not None:
            value["reason"] = decision.reason
        return ToolReply(value)
