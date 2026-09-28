"""Bind the functional controller to reviewed schemas without backend imports."""

from slow_thinker_host import Invocation, JsonObject, JsonValue, Operation, ToolReply

from ._schema import sequence_operation
from ._sequence import Sequence


def names(value: JsonValue) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("Expected an array of node identities")
    return tuple(str(item) for item in value)


class SequenceHost:
    def __init__(self, config: JsonObject, operation: Operation) -> None:
        if set(config) != {"steps"} or operation.name != "next":
            raise ValueError("Unsupported sequence binding")
        self._controller = Sequence(names(config["steps"]))
        self._operation = operation

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        return cls(config, sequence_operation()).operations()

    def operations(self) -> tuple[Operation, ...]:
        return (self._operation,)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del context
        if name != "next" or set(arguments) != {"completed_nodes"}:
            raise ValueError("Unsupported sequence invocation")
        decision = self._controller.next(names(arguments["completed_nodes"]))
        return ToolReply({"action": decision.action, "nodes": list(decision.nodes)})
