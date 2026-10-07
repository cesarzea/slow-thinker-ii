"""Per-call wire data: `_meta` entries, handler results and the tool replies."""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from mcp import types

from ._json import JsonObject, encode_json, json_value
from ._protocol import ACTIVATION_META, BUDGET_META, GRANT_META, Emission, HandlerError


@dataclass(frozen=True)
class CallMeta:
    grant: str
    budget_seconds: float
    activation_id: str


def call_meta(meta: Mapping[str, object] | None) -> CallMeta:
    """Read the grant, the relative budget in milliseconds and the activation id."""
    entries: Mapping[str, object] = meta or {}
    grant, budget = entries.get(GRANT_META), entries.get(BUDGET_META)
    activation = entries.get(ACTIVATION_META)
    if not isinstance(grant, str) or not grant:
        raise HandlerError("invalid_request", "The call carries no invocation grant.")
    if isinstance(budget, bool) or not isinstance(budget, int | float):
        raise HandlerError("invalid_request", "The call carries no time budget.")
    if not math.isfinite(budget) or budget < 0:
        raise HandlerError("invalid_request", "The call's time budget is not a valid duration.")
    if not isinstance(activation, str) or not activation:
        raise HandlerError("invalid_request", "The call carries no activation identifier.")
    return CallMeta(grant, budget / 1000, activation)


def emission_record(item: object) -> JsonObject:
    """The JSON form of one emission; the tool's output schema then checks its shape."""
    if not isinstance(item, Emission):
        raise HandlerError("invalid_result", "The component returned no emission.")
    try:
        return {"port": json_value(item.port), "payload": json_value(item.payload)}
    except ValueError as error:
        message = f"The emission on output {item.port!r} is not JSON."
        raise HandlerError("invalid_result", message) from error


def emissions_record(items: object) -> JsonObject:
    if isinstance(items, str) or not isinstance(items, Sequence):
        raise HandlerError("invalid_result", "The component returned no sequence of emissions.")
    emissions = cast(Sequence[object], items)
    return {"emissions": [emission_record(item) for item in emissions]}


def describe(error: Exception) -> str:
    """A short English description of an unexpected exception."""
    name, detail = type(error).__name__, str(error)
    if not detail:
        return f"The component raised {name}."
    if len(detail) > 300:
        detail = detail[:300] + "…"
    return f"The component raised {name}: {detail}"


def tool_error(code: str, message: str) -> types.CallToolResult:
    text = encode_json({"code": code, "message": message})
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)], is_error=True)


def tool_result(value: JsonObject) -> types.CallToolResult:
    text = encode_json(value)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)], structured_content=value
    )
