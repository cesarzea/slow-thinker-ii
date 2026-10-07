"""JSON Pointers follow RFC 6901 escaping and resolve without raising."""

import pytest
from slow_thinker_ii.contracts import JsonValue, format_pointer, parse_pointer, value_at_pointer

DOCUMENT: JsonValue = {
    "a/b": {"~c": [10, 20, {"d": None}]},
    "": "empty key",
    "list": [],
}


@pytest.mark.parametrize(
    ("pointer", "tokens"),
    [
        ("", ()),
        ("/", ("",)),
        ("/a~1b/~0c/2", ("a/b", "~c", "2")),
        ("/~01", ("~1",)),
        ("/x/", ("x", "")),
    ],
)
def test_parse_and_format_round_trip(pointer: str, tokens: tuple[str, ...]) -> None:
    assert parse_pointer(pointer) == tokens
    assert format_pointer(tokens) == pointer


@pytest.mark.parametrize("pointer", ["a", "a/b"])
def test_pointers_start_with_a_slash(pointer: str) -> None:
    with pytest.raises(ValueError, match="^A JSON Pointer must be empty or start with '/'$"):
        parse_pointer(pointer)


@pytest.mark.parametrize("pointer", ["/~", "/~2", "/a~", "/~~1"])
def test_invalid_escapes(pointer: str) -> None:
    with pytest.raises(ValueError, match="invalid '~' escape"):
        parse_pointer(pointer)


def test_format_accepts_indices() -> None:
    assert format_pointer(("nodes", 3, "config")) == "/nodes/3/config"
    assert format_pointer(()) == ""


@pytest.mark.parametrize(
    ("tokens", "expected"),
    [
        ((), DOCUMENT),
        (("",), "empty key"),
        (("a/b", "~c", "1"), 20),
        (("a/b", "~c", 2, "d"), None),
        (("a/b", "~c", "3"), None),
        (("a/b", "~c", "01"), None),
        (("a/b", "~c", "-"), None),
        (("list", "0"), None),
        (("missing", "x"), None),
        (("", "x"), None),
    ],
)
def test_lookup(tokens: tuple[str | int, ...], expected: JsonValue) -> None:
    assert value_at_pointer(DOCUMENT, tokens) == expected
