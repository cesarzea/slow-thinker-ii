"""Presentation attributes of sections and fields: accepted, kept as declared, refused."""

import pytest
from slow_thinker_ii.catalog import DeclarationError, parse_declaration
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .contract_fixtures import appended, changed, declaration_example

PRESENTATION = ("columns", "label_position", "align", "width", "format")
SECTION = ("ui", "sections", 0)
FIELD = ("ui", "sections", 0, "fields", 0)


def with_number_field(attributes: JsonObject) -> JsonObject:
    """The Router declaration with a numeric `limit` field in a third section."""
    limit: JsonObject = {"type": "integer", "minimum": 1}
    document = changed(
        declaration_example("router"), ("config_schema", "properties", "limit"), limit
    )
    field: JsonObject = {"path": "/limit", "control": "number", "label": "Limit"} | attributes
    section: JsonObject = {"id": "limits", "title": "Limits", "fields": [field]}
    return appended(document, ("ui", "sections"), section)


def issues_of(document: JsonObject) -> tuple[str, ...]:
    with pytest.raises(DeclarationError) as raised:
        parse_declaration(document)
    return raised.value.issues


@pytest.mark.parametrize(
    ("path", "value"),
    [
        ((*SECTION, "columns"), 1),
        ((*SECTION, "columns"), 2),
        *[((*FIELD, "label_position"), value) for value in ("top", "start")],
        *[((*FIELD, "align"), value) for value in ("start", "end", "center")],
        *[((*FIELD, "width"), value) for value in ("xs", "sm", "md", "lg", "full")],
    ],
)
def test_section_and_field_attributes_are_kept_as_declared(
    path: tuple[str | int, ...], value: JsonValue
) -> None:
    document = changed(declaration_example("router"), path, value)
    assert parse_declaration(document).document == document


@pytest.mark.parametrize(
    "number_format",
    [
        {},
        {"decimals": 0},
        {"decimals": 6},
        {"grouping": False},
        {"prefix": "$"},
        {"suffix": "tokens"},
        {"decimals": 2, "grouping": True, "prefix": "US $", "suffix": "/ call"},
    ],
)
def test_number_fields_accept_a_format(number_format: JsonObject) -> None:
    document = with_number_field({"format": number_format, "align": "end", "width": "sm"})
    assert parse_declaration(document).document == document


def test_absent_attributes_stay_absent() -> None:
    example = declaration_example("llm-call")
    document = parse_declaration(example).document
    assert document == example
    sections = document["ui"]
    assert isinstance(sections, dict) and isinstance(sections["sections"], list)
    for section in sections["sections"]:
        assert isinstance(section, dict) and isinstance(section["fields"], list)
        assert not set(PRESENTATION) & set(section)
        assert all(
            isinstance(field, dict) and not set(PRESENTATION) & set(field)
            for field in section["fields"]
        )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        *[((*SECTION, "columns"), value) for value in (0, 3, 1.5, "2", True)],
        ((*FIELD, "label_position"), "left"),
        ((*FIELD, "align"), "right"),
        ((*FIELD, "width"), "xl"),
    ],
)
def test_attribute_values_outside_the_contract_are_refused(
    path: tuple[str | int, ...], value: JsonValue
) -> None:
    issues = issues_of(changed(declaration_example("router"), path, value))
    pointer = "".join(f"/{token}" for token in path)
    assert len(issues) == 1 and issues[0].startswith(f"{pointer}: ")


@pytest.mark.parametrize(
    ("number_format", "member"),
    [
        ("2dp", ""),
        ({"unit": "s"}, ""),
        ({"decimals": 7}, "/decimals"),
        ({"decimals": -1}, "/decimals"),
        ({"decimals": 1.5}, "/decimals"),
        ({"grouping": "yes"}, "/grouping"),
        ({"prefix": ""}, "/prefix"),
        ({"prefix": "dollars!!"}, "/prefix"),
        ({"suffix": "<b>"}, "/suffix"),
    ],
)
def test_malformed_formats_are_refused(number_format: JsonValue, member: str) -> None:
    issues = issues_of(with_number_field({"format": number_format}))
    assert len(issues) == 1 and issues[0].startswith(f"/ui/sections/2/fields/0/format{member}: ")


@pytest.mark.parametrize(("name", "control"), [("router", "list"), ("llm-call", "multiline")])
def test_only_number_fields_accept_a_format(name: str, control: str) -> None:
    document = changed(declaration_example(name), (*FIELD, "format"), {"decimals": 0})
    expected = (
        f'/ui/sections/0/fields/0/format: only number fields accept format, not "{control}" fields'
    )
    assert issues_of(document) == (expected,)
