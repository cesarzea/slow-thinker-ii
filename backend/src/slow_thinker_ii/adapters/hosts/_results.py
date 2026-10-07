"""Tool results of the protocol's operations, read into the engine's values."""

import re

from mcp import types

from slow_thinker_ii.contracts import JsonValue, decode_json, json_value
from slow_thinker_ii.engine import CallFailure, Emission

CODE = re.compile(r"[a-z][a-z0-9_]{0,63}")


def activation(result: types.CallToolResult) -> tuple[Emission, ...] | CallFailure:
    """The emissions of an `activate` result, or the failure it reports."""
    if result.is_error:
        return failure(result)
    record = _record(result.structured_content, {"emissions"})
    items = record["emissions"] if record is not None else None
    if not isinstance(items, list):
        return _invalid("activate")
    emissions = [_emission(item) for item in items]
    valid = [item for item in emissions if item is not None]
    return tuple(valid) if len(valid) == len(emissions) else _invalid("activate")


def selection(result: types.CallToolResult) -> Emission | CallFailure:
    """The emission chosen by a `select_output` result, or the failure it reports."""
    if result.is_error:
        return failure(result)
    chosen = _emission(_structured(result.structured_content))
    return chosen if chosen is not None else _invalid("select_output")


def recalled(result: types.CallToolResult) -> JsonValue | CallFailure:
    """The message a `recall` result gives the node, or the failure it reports."""
    if result.is_error:
        return failure(result)
    record = _record(result.structured_content, {"message"})
    return _invalid("recall") if record is None else record["message"]


def remembered(result: types.CallToolResult) -> None | CallFailure:
    """Nothing for a `remember` result, or the failure it reports."""
    return failure(result) if result.is_error else None


def failure(result: types.CallToolResult) -> CallFailure:
    """A tool error carries the text `{"code", "message"}`."""
    texts = [block.text for block in result.content if isinstance(block, types.TextContent)]
    try:
        record = _record(decode_json(texts[0]) if texts else None, {"code", "message"})
    except ValueError:
        record = None
    code, message = (record["code"], record["message"]) if record is not None else (None, None)
    if isinstance(code, str) and CODE.fullmatch(code) and isinstance(message, str) and message:
        return CallFailure(code, message)
    return CallFailure(
        "invalid_result", "The component reported an error without a code and a message."
    )


def _emission(value: JsonValue) -> Emission | None:
    record = _record(value, {"port", "payload"})
    if record is None or not isinstance(record["port"], str):
        return None
    return Emission(record["port"], record["payload"])


def _record(value: object, keys: set[str]) -> dict[str, JsonValue] | None:
    """`value` as a JSON object with exactly `keys`, or None."""
    structured = _structured(value)
    if not isinstance(structured, dict) or set(structured) != keys:
        return None
    return structured


def _structured(value: object) -> JsonValue:
    try:
        return json_value(value)
    except ValueError:
        return None


def _invalid(tool: str) -> CallFailure:
    return CallFailure(
        "invalid_result", f"The component's result does not match the {tool} schema."
    )
