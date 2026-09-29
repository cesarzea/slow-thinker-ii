"""Stateless history validation and bounded next-activation selection."""

from ._config import validated_config
from ._types import BoundedFlowConfig, CompletedStep, FlowDecision


class BoundedFlow:
    def __init__(self, config: BoundedFlowConfig) -> None:
        self.config = validated_config(config)
        self._routes = {(item.node, item.port): item.target for item in self.config.routes}

    def next(self, completed: tuple[CompletedStep, ...]) -> FlowDecision:
        if len(completed) > self.config.max_activations:
            raise ValueError("Completed history exceeds the configured activation bound")
        expected: str | None = self.config.entry
        for step in completed:
            if expected is None or step.node != expected:
                raise ValueError("Completed history does not follow the declared topology")
            route = (step.node, step.port)
            if route not in self._routes:
                raise ValueError("Completed history selects an undeclared port")
            expected = self._routes[route]
        if expected is None:
            return FlowDecision("complete")
        if len(completed) == self.config.max_activations:
            return FlowDecision("exhausted", reason="activation_limit_reached")
        return FlowDecision("activate", node=expected)
