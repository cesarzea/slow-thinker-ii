"""Shared JSON values: strict decoding, canonical encoding and validated copies."""

import json

import pytest
from slow_thinker_ii.contracts import (
    decode_json,
    encode_json,
    json_object,
    json_value,
)


@pytest.mark.parametrize("source", ['{"a": 1, "a": 2}', "NaN", "[Infinity]", "{", ""])
def test_ambiguous_or_invalid_json_is_rejected(source: str) -> None:
    with pytest.raises(ValueError):
        decode_json(source)


def test_values_round_trip_canonically() -> None:
    value = json_object(decode_json('{"~a/b": [true, null, 1.5, "é"], "": 0, "b": {"c": -1}}'))
    encoded = encode_json(value)
    assert encoded == '{"":0,"b":{"c":-1},"~a/b":[true,null,1.5,"é"]}'
    assert decode_json(encoded) == value


def test_conversions_copy_and_validate() -> None:
    original: dict[str, object] = {"items": [1, {"x": None}]}
    copied = json_object(original)
    assert copied == original
    assert copied["items"] is not original["items"]
    assert json_value("text") == "text"


@pytest.mark.parametrize(
    "value", [{1: "key"}, (1, 2), {"x": float("nan")}, [float("inf")], {"s": {1}}, object()]
)
def test_non_json_values_are_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="^Expected a finite JSON value$"):
        json_value(value)


@pytest.mark.parametrize("value", [[], "text", 1, None])
def test_objects_are_required(value: object) -> None:
    with pytest.raises(ValueError, match="^Expected a JSON object$"):
        json_object(value)


def test_encoding_rejects_non_finite_numbers() -> None:
    with pytest.raises(ValueError):
        encode_json(float("nan"))
    assert json.loads(encode_json({"z": 1, "a": [2]})) == {"a": [2], "z": 1}
