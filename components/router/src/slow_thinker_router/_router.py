"""The Router: `route(received, node_input)` chooses the output and the content to send."""

from collections.abc import Sequence
from typing import cast

from slow_thinker_host import Context, Emission, HandlerError, JsonValue, json_value

from ._config import RouterConfig
from ._script import Route, raised
from ._thread import call_route


class Router:
    """Node handler (`route(message, message)`) and output handler of one configured script."""

    def __init__(self, config: RouterConfig, route: Route) -> None:
        self._outputs = config.outputs
        self._route = route

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        return [await self._decide(message, message, context)]

    async def select_output(
        self, received: JsonValue, node_input: JsonValue, context: Context
    ) -> Emission:
        return await self._decide(received, node_input, context)

    async def _decide(
        self, received: JsonValue, node_input: JsonValue, context: Context
    ) -> Emission:
        outcome = await call_route(self._route, json_value(received), json_value(node_input))
        if outcome.error is not None:
            raise HandlerError("script_error", f"The script raised {raised(outcome.error)}.")
        emission = self._emission(outcome.value)
        await context.report("step", f"route returned {emission.port}")
        return emission

    def _emission(self, result: object) -> Emission:
        if not isinstance(result, tuple | list) or len(cast(Sequence[object], result)) != 2:
            message = "The script must return a pair: an output name and the content to send."
            raise HandlerError("invalid_result", message)
        output, payload = cast(Sequence[object], result)
        if not isinstance(output, str):
            message = f"The script returned an output name of type {type(output).__name__}."
            raise HandlerError("invalid_result", message)
        if output not in self._outputs:
            message = f'The script returned the undeclared output "{output}".'
            raise HandlerError("undeclared_output", message)
        try:
            return Emission(output, json_value(payload))
        except ValueError as error:
            message = f'The content for output "{output}" is not a JSON value.'
            raise HandlerError("invalid_result", message) from error
