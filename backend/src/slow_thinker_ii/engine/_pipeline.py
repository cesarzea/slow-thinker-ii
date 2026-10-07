"""A package activation: memory, the host's `activate`, then the embedded output component."""

from slow_thinker_ii.graphs import PlanComponent

from ._calls import ComponentCalls
from ._ports import CallFailure, Emission
from ._state import Activation


class Pipeline:
    def __init__(self, calls: ComponentCalls) -> None:
        self._calls = calls

    async def run(self, activation: Activation) -> tuple[Emission, ...] | CallFailure:
        """The node's emissions, each on one of its effective outputs, or the first failure."""
        memory = activation.node.embedded_memory
        message = (
            activation.message if memory is None else await self._calls.recall(activation, memory)
        )
        if isinstance(message, CallFailure):
            return message
        emitted = await self._calls.activate(activation, message)
        if isinstance(emitted, CallFailure):
            return emitted
        if memory is not None:
            for emission in emitted:
                kept = await self._calls.remember(activation, memory, emission.payload)
                if isinstance(kept, CallFailure):
                    return kept
        host = activation.node.host
        declared = host.declaration.output_ports(host.config)
        undeclared = next((item.port for item in emitted if item.port not in declared), None)
        if undeclared is not None:
            message = f'The component emitted on the undeclared output "{undeclared}".'
            return CallFailure("undeclared_port", message)
        embedded = activation.node.embedded_output
        return emitted if embedded is None else await self._select(activation, embedded, emitted)

    async def _select(
        self, activation: Activation, embedded: PlanComponent, emitted: tuple[Emission, ...]
    ) -> tuple[Emission, ...] | CallFailure:
        selected: list[Emission] = []
        for emission in emitted:
            choice = await self._calls.select_output(activation, embedded, emission.payload)
            if isinstance(choice, CallFailure):
                return choice
            if choice.port not in activation.node.outputs:
                message = f'The output component selected the undeclared output "{choice.port}".'
                return CallFailure("undeclared_port", message)
            selected.append(choice)
        return tuple(selected)
