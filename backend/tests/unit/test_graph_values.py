"""Strict JSON and pointer semantics retain nulls, escaped names and array boundaries."""

import pytest
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import read_pointer


@pytest.mark.parametrize("source", ['{"a":1,"a":2}', "NaN", "Infinity", "1e999", '{"a":NaN}'])
def test_nonfinite_or_ambiguous_json_is_rejected(source: str) -> None:
    with pytest.raises(ValueError):
        decode_json(source)


def test_finite_json_roundtrip_and_independent_object_values() -> None:
    value = json_object(decode_json('{"~a/b":[true,null,1.5],"":0}'))
    assert read_pointer(value, "/~0a~1b/1") is None
    assert read_pointer(value, "/") == 0
    assert read_pointer(value, "") == value
    assert decode_json(encode_json(value)) == value
    copied = json_object(value)
    copied["new"] = 1
    assert "new" not in value


@pytest.mark.parametrize(
    "pointer",
    ["invalid", "/~2", "/~", "/a/-", "/a/01", "/a/-1", "/a/١", "/a/3", "/missing", "/a/0/x"],
)
def test_missing_or_invalid_pointer_never_becomes_an_empty_input(pointer: str) -> None:
    with pytest.raises(ValueError):
        read_pointer({"a": [None]}, pointer)


@pytest.mark.parametrize("value", [[], {1: "value"}, object()])
def test_object_boundary_rejects_nonobjects_and_nonstring_keys(value: object) -> None:
    with pytest.raises(ValueError):
        json_object(value)
