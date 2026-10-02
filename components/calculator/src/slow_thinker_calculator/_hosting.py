"""Explicit nonbillable calculator schemas and standard MCP failures."""

from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, JsonObject, Operation, ToolReply, validate_value

from ._calculator import Calculator
from ._config import Settings, settings


def operation(limits: Settings) -> Operation:
    expression: JsonObject = {
        "type": "string",
        "minLength": 1,
        "maxLength": limits.max_expression_bytes,
    }
    return Operation(
        "calculate",
        {
            "type": "object",
            "properties": {"expression": expression},
            "required": ["expression"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "expression": expression,
                "value": {"type": "string", "minLength": 1, "maxLength": limits.max_result_bytes},
            },
            "required": ["expression", "value"],
            "additionalProperties": False,
        },
    )


class CalculatorHost:
    def __init__(self, config: JsonObject, operations: tuple[Operation, ...]) -> None:
        limits = settings(config)
        self._operation = operation(limits)
        if operations != (self._operation,):
            raise ValueError("Configured Calculator operation schemas do not match")
        self._calculator = Calculator(
            max_expression_bytes=limits.max_expression_bytes,
            max_nodes=limits.max_nodes,
            max_exponent=limits.max_exponent,
            max_result_bytes=limits.max_result_bytes,
        )

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        return (operation(settings(config)),)

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del context
        try:
            if name != "calculate":
                raise ValueError("Unsupported Calculator operation")
            validate_value(arguments, self._operation.input_schema)
            expression = arguments["expression"]
            if not isinstance(expression, str):
                raise ValueError("Calculator expression must be a string")
            return ToolReply(self._calculator.calculate(expression))
        except ValueError as error:
            raise MCPError(
                code=-32602, message="calculator_failed", data={"reason": str(error)}
            ) from error
