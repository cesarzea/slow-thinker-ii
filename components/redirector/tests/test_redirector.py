"""Deterministic selectors execute once and cannot select undeclared routes."""

from collections.abc import Callable

import pytest
from slow_thinker_host import JsonObject, JsonValue, decode_json
from slow_thinker_redirector import Redirector, parse_config

CONFIG: JsonObject = {
    "outputs": ["accept", "revise"],
    "selector": "example_grounded_review:choose",
    "input_schema": {
        "type": "object",
        "properties": {"accepted": {"type": "boolean"}},
        "required": ["accepted"],
        "additionalProperties": False,
    },
}


@pytest.mark.parametrize("accepted,port", [(True, "accept"), (False, "revise")])
def test_selector_receives_validated_input_once(accepted: bool, port: str) -> None:
    calls: list[JsonValue] = []

    def choose(value: JsonValue) -> str:
        calls.append(value)
        return port

    config = parse_config(CONFIG)
    component = Redirector(config, choose)
    value: JsonObject = {"accepted": accepted}
    assert component.route(value) == port
    assert calls == [value] and calls[0] is not value
    assert decode_json(config.input_schema_json) == CONFIG["input_schema"]


@pytest.mark.parametrize("value", [{}, {"accepted": "true"}, {"accepted": True, "extra": 1}])
def test_invalid_input_never_calls_selector(value: JsonObject) -> None:
    def forbidden(selected: JsonValue) -> str:
        del selected
        pytest.fail("Invalid inputs must not reach authored code")

    with pytest.raises(ValueError):
        Redirector(parse_config(CONFIG), forbidden).route(value)


@pytest.mark.parametrize("result", [None, 1, True, [], "unknown"])
def test_invalid_selector_output_fails_once(result: object) -> None:
    calls: list[JsonValue] = []

    def choose(value: JsonValue) -> object:
        calls.append(value)
        return result

    from typing import cast

    with pytest.raises(ValueError, match="undeclared"):
        Redirector(parse_config(CONFIG), cast(Callable[[JsonValue], str], choose)).route(
            {"accepted": True}
        )
    assert len(calls) == 1


def test_selector_exception_is_not_retried() -> None:
    calls: list[JsonValue] = []

    def fail(value: JsonValue) -> str:
        calls.append(value)
        raise RuntimeError("authored failure")

    with pytest.raises(RuntimeError, match="authored failure"):
        Redirector(parse_config(CONFIG), fail).route({"accepted": False})
    assert len(calls) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("extra", True),
        ("outputs", []),
        ("outputs", "accept"),
        ("outputs", [" "]),
        ("outputs", ["accept", "accept"]),
        ("outputs", [1]),
        ("selector", "path/to.py"),
        ("selector", "module:"),
        ("selector", 3),
        ("input_schema", {"$ref": "https://example.test/a"}),
    ],
)
def test_invalid_configuration_is_rejected(field: str, value: JsonValue) -> None:
    with pytest.raises(ValueError):
        parse_config({**CONFIG, field: value})
