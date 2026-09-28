"""External values cannot silently acquire duplicate keys or non-finite numbers."""

import pytest
from slow_thinker_host import decode_json, encode_json, json_object, json_value


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', "NaN", "Infinity", "1e9999", "{} {}"])
def test_ambiguous_json_is_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        decode_json(text)


@pytest.mark.parametrize("value", [object(), {1: "bad"}, float("inf"), (1, 2)])
def test_non_json_python_values_are_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        json_value(value)


def test_json_values_roundtrip_without_mutable_aliases() -> None:
    value = {"z": [1, 0.25, True, None], "a": "ñ"}
    encoded = encode_json(json_value(value))
    assert encoded == '{"a":"ñ","z":[1,0.25,true,null]}'
    assert decode_json(encoded) == value
    assert json_object(value) is not value
    with pytest.raises(ValueError):
        json_object([])
