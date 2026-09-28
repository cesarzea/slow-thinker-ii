"""The initial adapter rejects unsupported native settings before authorizing spending."""

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from support.native_model import profile


def request() -> JsonObject:
    return {"model": "bound-model", "messages": [{"role": "developer", "content": "hello"}]}


def test_missing_settings_receive_explicit_frozen_defaults() -> None:
    wire = profile().request(encode_json({"request": request()}))
    assert wire == {
        "model": "gpt-6-luna",
        "messages": [{"role": "developer", "content": "hello"}],
        "reasoning_effort": "none",
        "stream": False,
        "n": 1,
        "store": False,
        "service_tier": "default",
        "max_completion_tokens": 8,
    }


UNSUPPORTED: tuple[tuple[str, JsonValue], ...] = (
    ("temperature", 0),
    ("max_tokens", 3),
    ("tools", []),
    ("stream", True),
    ("n", True),
    ("n", 2),
    ("store", True),
    ("reasoning_effort", "high"),
    ("service_tier", "flex"),
    ("max_completion_tokens", 0),
    ("max_completion_tokens", True),
    ("max_completion_tokens", 33),
    ("model", "unbound"),
    ("messages", []),
    ("messages", [{"role": "tool", "content": "x"}]),
    ("messages", [{"role": "user", "content": []}]),
    ("messages", [{"role": "user", "content": "x", "name": "y"}]),
)


@pytest.mark.parametrize("key,value", UNSUPPORTED)
def test_unsupported_native_options_are_not_silently_dropped(key: str, value: JsonValue) -> None:
    body = request()
    body[key] = value
    with pytest.raises(ValueError):
        profile().request(encode_json({"request": body}))
