"""Every declaration rule has a failing example with its issue text."""

import pytest
from slow_thinker_ii.catalog import DeclarationError, parse_declaration
from slow_thinker_ii.contracts import JsonObject

from .contract_fixtures import changed, declaration_example, without

DRAFT = "https://json-schema.org/draft/2020-12/schema"
UNRESOLVED_REFERENCE = "is not a local reference that resolves"


def llm_call() -> JsonObject:
    return declaration_example("llm-call")


def router() -> JsonObject:
    return declaration_example("router")


def issues_of(document: JsonObject) -> tuple[str, ...]:
    with pytest.raises(DeclarationError) as raised:
        parse_declaration(document)
    assert str(raised.value) == "Invalid component declaration: " + "; ".join(raised.value.issues)
    return raised.value.issues


def test_the_declaration_format_is_checked_first() -> None:
    issues = issues_of(changed(llm_call(), ("format",), "slow-thinker.component/2"))
    assert len(issues) == 1 and issues[0].startswith("/format: ")
    assert issues_of(without(llm_call(), ("ui",))) == ("declaration: 'ui' is a required property",)
    assert issues_of(changed(llm_call(), ("label",), "<b>LLM</b>"))[0].startswith("/label: ")


def test_config_schema_must_be_a_valid_draft_2020_12_schema() -> None:
    wrong_type = changed(llm_call(), ("config_schema", "properties", "prompt", "type"), "strin")
    assert issues_of(wrong_type)[0].startswith("/config_schema/properties/prompt/type: ")
    bad_regex = changed(router(), ("config_schema", "properties", "script", "pattern"), "(")
    assert issues_of(bad_regex) == (
        "/config_schema/properties/script/pattern: '(' is not a 'regex'",
    )
    draft_7 = changed(
        llm_call(), ("config_schema", "$schema"), "http://json-schema.org/draft-07/schema#"
    )
    assert issues_of(draft_7) == (f'/config_schema/$schema: must be "{DRAFT}"',)


@pytest.mark.parametrize(
    "reference", ["https://example.com/format.json", "#/$defs/missing", "#defs"]
)
def test_references_must_be_local_and_resolve(reference: str) -> None:
    document = changed(
        llm_call(), ("config_schema", "properties", "input_format"), {"$ref": reference}
    )
    location = "/config_schema/properties/input_format/$ref"
    assert issues_of(document) == (f'{location}: "{reference}" {UNRESOLVED_REFERENCE}',)


def test_use_pointers_must_resolve() -> None:
    assert issues_of(changed(llm_call(), ("uses", 0, "pointer"), "/modle")) == (
        '/uses/0/pointer: "/modle" does not resolve in config_schema',
        '/ui/sections/1/fields/0: service "llm" at "/model" is not declared in uses',
    )


def test_interface_pointers_must_resolve() -> None:
    card = changed(llm_call(), ("ui", "card", 1), "/nope")
    assert issues_of(card) == ('/ui/card/1: "/nope" does not resolve in config_schema',)
    field = changed(llm_call(), ("ui", "sections", 0, "fields", 0, "path"), "/nope")
    assert issues_of(field) == (
        '/ui/sections/0/fields/0/path: "/nope" does not resolve in config_schema',
    )
    when = ("ui", "sections", 3, "fields", 1, "when", "path")
    location = "/ui/sections/3/fields/1/when/path"
    assert issues_of(changed(llm_call(), when, "/output_format/kind")) == (
        f'{location}: "/output_format/kind" does not resolve in config_schema',
    )


def test_service_fields_must_match_a_declared_use() -> None:
    assert issues_of(changed(llm_call(), ("uses",), [])) == (
        '/ui/sections/1/fields/0: service "llm" at "/model" is not declared in uses',
    )


def test_output_placement_requires_outputs_from() -> None:
    document = changed(llm_call(), ("placements",), ["node", "output"])
    assert issues_of(document) == ('/ports: placement "output" requires outputs_from',)


@pytest.mark.parametrize("pointer", ["/script", "/nothing"])
def test_outputs_from_must_resolve_to_an_array_of_strings(pointer: str) -> None:
    document = changed(router(), ("ports", "outputs_from"), pointer)
    assert issues_of(document) == (
        f'/ports/outputs_from: "{pointer}" must resolve to an array of strings',
    )


def test_outputs_from_items_must_be_strings() -> None:
    items = ("config_schema", "properties", "outputs", "items")
    document = changed(router(), items, {"type": "integer"})
    assert issues_of(document) == (
        '/ports/outputs_from: "/outputs" must resolve to an array of strings',
    )


def test_section_ids_are_unique() -> None:
    document = changed(router(), ("ui", "sections", 1, "id"), "outputs")
    assert issues_of(document) == (
        '/ui/sections/1/id: "outputs" is already used by another section',
    )


def test_all_problems_are_collected_into_one_error() -> None:
    document = changed(router(), ("ui", "sections", 1, "id"), "outputs")
    document = changed(document, ("ui", "card", 0), "/nope")
    document = changed(document, ("ports", "outputs_from"), "/script")
    assert len(issues_of(document)) == 3


def test_pointers_resolve_through_items_and_local_references() -> None:
    schema: JsonObject = {
        "$schema": f"{DRAFT}#",
        "type": "object",
        "properties": {"routes": {"$ref": "#/$defs/route%20names"}, "script": {"type": "string"}},
        "$defs": {
            "route names": {"type": "array", "items": {"$ref": "#/$defs/name"}},
            "name": {"type": "string"},
        },
    }
    document = changed(router(), ("config_schema",), schema)
    document = changed(document, ("ports", "outputs_from"), "/routes")
    document = changed(document, ("ui", "card"), ["/routes/0"])
    document = changed(document, ("ui", "sections", 0, "fields", 0, "path"), "/routes")
    declaration = parse_declaration(document)
    assert declaration.output_ports({"routes": ["a", "b"]}) == ("a", "b")


def test_recursive_references_are_followed_a_bounded_number_of_times() -> None:
    document = changed(llm_call(), ("config_schema", "$ref"), "#")
    issues = issues_of(changed(document, ("ui", "card", 0), "/missing"))
    assert issues == ('/ui/card/0: "/missing" does not resolve in config_schema',)
