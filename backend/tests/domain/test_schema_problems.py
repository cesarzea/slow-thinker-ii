"""Located schema problems in plain English, shared by catalog entries and graph validation."""

import pytest
from slow_thinker_ii.catalog import SchemaProblem, schema_problems
from slow_thinker_ii.contracts import JsonObject, JsonValue

SCHEMA: JsonObject = {
    "type": "object",
    "additionalProperties": False,
    "required": ["name", "count"],
    "properties": {
        "name": {"type": "string", "title": "Display name", "minLength": 1, "maxLength": 5},
        "count": {"type": "integer", "minimum": 1, "maximum": 3},
        "mode": {"enum": ["fast", "slow"]},
        "code": {"type": "string", "pattern": "^[a-z]+$"},
        "tags": {"type": "array", "maxItems": 2, "items": {"type": "string"}},
        "nested": {"type": "object", "properties": {"inner": {"type": "string", "title": "Inner"}}},
        "off": False,
    },
}
VALID: JsonObject = {"name": "Ada", "count": 2}


def problem(path: tuple[str, ...], keyword: str, phrase: str, label: str) -> SchemaProblem:
    return SchemaProblem(path, keyword, phrase, f"{label} {phrase}.")


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({}, ()),
        ({"name": ""}, (problem(("name",), "minLength", "is required", "Display name"),)),
        ({"name": "Grace!"}, (problem(("name",), "maxLength", "is too long", "Display name"),)),
        ({"count": 0}, (problem(("count",), "minimum", "must be at least 1", "Count"),)),
        ({"count": 4}, (problem(("count",), "maximum", "must be at most 3", "Count"),)),
        ({"count": "2"}, (problem(("count",), "type", "has the wrong type", "Count"),)),
        ({"mode": "x"}, (problem(("mode",), "enum", 'must be one of "fast", "slow"', "Mode"),)),
        ({"code": "abc\n"}, (problem(("code",), "pattern", "has an invalid format", "Code"),)),
        ({"tags": ["a", "b", "c"]}, (problem(("tags",), "maxItems", "is too long", "Tags"),)),
        ({"tags": [1]}, (problem(("tags", "0"), "type", "has the wrong type", "Tags"),)),
        (
            {"nested": {"inner": 5}},
            (problem(("nested", "inner"), "type", "has the wrong type", "Inner"),),
        ),
        (
            {"extra_field": 1},
            (problem(("extra_field",), "additionalProperties", "is invalid", "Extra field"),),
        ),
        ({"off": 1}, (problem(("off",), "", "is invalid", "Off"),)),
    ],
)
def test_problems_are_located_and_named_by_titles(
    change: JsonObject, expected: tuple[SchemaProblem, ...]
) -> None:
    assert schema_problems(SCHEMA, VALID | change) == expected


def test_missing_members_are_reported_once_each() -> None:
    assert set(schema_problems(SCHEMA, {})) == {
        problem(("name",), "required", "is required", "Display name"),
        problem(("count",), "required", "is required", "Count"),
    }


def test_given_labels_replace_titles_and_the_deepest_applies() -> None:
    labels = [(("name",), "Name"), (("tags",), "Tag list"), (("tags", "0"), "First tag")]
    found = schema_problems(SCHEMA, {"name": "", "count": 2, "tags": [1]}, labels)
    assert [item.sentence for item in found] == [
        "Name is required.",
        "First tag has the wrong type.",
    ]
    nested: JsonObject = {"nested": {"inner": 5}}
    untitled = schema_problems(SCHEMA, VALID | nested, labels=())
    assert [item.sentence for item in untitled] == ["Inner has the wrong type."]


@pytest.mark.parametrize(
    ("fallback", "sentence"),
    [
        ("Value", "Value has the wrong type."),
        ("Configuration", "Configuration has the wrong type."),
    ],
)
def test_problems_with_the_whole_value(fallback: str, sentence: str) -> None:
    assert schema_problems({"type": "object"}, 5, fallback=fallback) == (
        SchemaProblem((), "type", "has the wrong type", sentence),
    )


def test_unresolvable_references_are_never_fetched() -> None:
    schema: JsonObject = {"$ref": "https://example.com/never-fetched.json"}
    assert schema_problems(schema, {}) == (
        SchemaProblem((), "$ref", "is invalid", "Value is invalid."),
    )


@pytest.mark.parametrize(
    ("path", "labels", "fallback", "label"),
    [
        (("output_format",), [], "Value", "Output format"),
        (("outputs", "1"), [(("outputs",), "Output names")], "Value", "Output names"),
        (("top-p",), [(("other",), "Other")], "Value", "Top p"),
        (("0",), [], "Items", "Items"),
        (("_",), [], "Configuration", "Value"),
        ((), [], "Configuration", "Configuration"),
    ],
)
def test_labels(
    path: tuple[str, ...], labels: list[tuple[tuple[str, ...], str]], fallback: str, label: str
) -> None:
    assert SchemaProblem.label_of(path, labels, fallback) == label


def test_values_of_any_type_are_checked() -> None:
    value: JsonValue = ["a", 1]
    schema: JsonObject = {"type": "array", "items": {"type": "string"}}
    assert schema_problems(schema, value) == (
        problem(("1",), "type", "has the wrong type", "Value"),
    )


def test_names_refused_by_property_names_are_located_at_their_member() -> None:
    schema: JsonObject = {
        "propertyNames": {"maxLength": 3},
        "properties": {"propertyNames": {"type": "string"}},
    }
    assert schema_problems(schema, {"abcd": 1, "ab": 2}) == (
        problem(("abcd",), "maxLength", "is too long", "Abcd"),
    )
    named: JsonObject = {"properties": {"propertyNames": {"type": "string"}}}
    assert schema_problems(named, {"propertyNames": 5}) == (
        problem(("propertyNames",), "type", "has the wrong type", "PropertyNames"),
    )
