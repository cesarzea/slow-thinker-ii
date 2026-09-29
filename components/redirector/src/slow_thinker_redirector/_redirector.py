"""One validated selector execution, with no fallback route or retry."""

from collections.abc import Callable

from slow_thinker_host import JsonValue, decode_json, json_object, json_value, validate_value

from ._config import parse_config
from ._types import RedirectorConfig


class Redirector:
    def __init__(self, config: RedirectorConfig, selector: Callable[[JsonValue], str]) -> None:
        self.config = parse_config(
            {
                "outputs": list(config.outputs),
                "selector": config.selector,
                "input_schema": decode_json(config.input_schema_json),
            }
        )
        if not callable(selector):
            raise ValueError("Redirector requires a callable selector")
        self._selector: Callable[[JsonValue], object] = selector

    def route(self, value: JsonValue) -> str:
        isolated = json_value(value)
        validate_value(isolated, json_object(decode_json(self.config.input_schema_json)))
        port: object = self._selector(isolated)
        if not isinstance(port, str) or port not in self.config.outputs:
            raise ValueError("Selector returned an undeclared output port")
        return port
