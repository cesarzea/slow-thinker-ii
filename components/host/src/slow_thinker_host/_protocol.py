"""Wire names, tool schemas and values of the component protocol (CORE-PROTOCOL-1)."""

import re
from dataclasses import dataclass
from typing import Final, Literal

from ._json import JsonObject, JsonValue

PROTOCOL_VERSION: Final = "2026-07-28"
BOOTSTRAP_FORMAT: Final = "slow-thinker.bootstrap/1"
GRANT_META: Final = "slow-thinker/grant"
BUDGET_META: Final = "slow-thinker/budget-ms"
ACTIVATION_META: Final = "slow-thinker/activation-id"
REPORT_TOOL: Final = "platform.report"
REPORT_KINDS: Final = frozenset({"step", "progress", "state", "explanation", "reasoning"})

type Position = Literal["node", "output", "memory"]
type ToolSchema = tuple[str, JsonObject, JsonObject]  # name, input schema, output schema


@dataclass(frozen=True)
class Emission:
    """A payload sent on one output port."""

    port: str
    payload: JsonValue


class HandlerError(Exception):
    """A failed operation, returned to the platform as the tool error `{code, message}`."""

    def __init__(self, code: str, message: str) -> None:
        if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", code) is None:
            raise ValueError(f"Invalid error code: {code!r}")
        if not message:
            raise ValueError("An error message is required")
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _closed(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _emission() -> JsonObject:
    return _closed({"port": {"type": "string"}, "payload": {}})


def tool_schemas(position: Position) -> tuple[str, JsonObject, JsonObject]:
    """The first tool a host exposes at `position`: name, input and output schema."""
    return position_tools(position)[0]


def position_tools(position: Position) -> tuple[ToolSchema, ...]:
    """Every tool a host exposes at `position`; a memory serves `recall` and `remember`."""
    if position == "node":
        emissions: JsonObject = {"type": "array", "items": _emission()}
        return (("activate", _closed({"message": {}}), _closed({"emissions": emissions})),)
    if position == "memory":
        return (
            ("recall", _closed({"message": {}}), _closed({"message": {}})),
            ("remember", _closed({"received": {}, "replied": {}}), _closed({})),
        )
    return (("select_output", _closed({"received": {}, "node_input": {}}), _emission()),)
