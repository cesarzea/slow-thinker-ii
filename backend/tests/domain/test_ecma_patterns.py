"""JSON Schema `pattern` follows ECMA-262: `$` matches only at the very end of a string."""

import pytest
from slow_thinker_ii.catalog import DeclarationError, parse_declaration
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .contract_fixtures import J1, changed, declaration_example, graph_example
from .graph_checks import messages

PATTERNED: JsonObject = {
    "format": "slow-thinker.component/1",
    "type": "patterned",
    "version": "1.0.0",
    "label": "Patterned",
    "description": "Configuration values constrained by patterns.",
    "icon": "component",
    "placements": ["node"],
    "state": "stateless",
    "ports": {"inputs": ["in"], "outputs": ["out"]},
    "uses": [],
    "config_schema": {
        "type": "object",
        "properties": {
            "word": {"type": "string", "pattern": "^[a-z]+$"},
            "price": {"type": "string", "pattern": "^\\$[0-9]+$"},
            "symbols": {"type": "string", "pattern": "^[]$]+$"},
            "answer": {"type": "string", "pattern": "^yes$|^no$"},
            "plain": {"type": "string", "pattern": "^[^$]*$"},
        },
    },
    "initial_config": {},
    "ui": {"card": [], "sections": []},
}


def declaration_issues(document: JsonObject) -> tuple[str, ...]:
    with pytest.raises(DeclarationError) as raised:
        parse_declaration(document)
    return raised.value.issues


@pytest.mark.parametrize(
    ("path", "value", "issue"),
    [
        (("type",), "llm-call\n", "/type: 'llm-call\\n' does not match '^[a-z][a-z0-9-]{0,63}$'"),
        (
            ("ports", "inputs", 0),
            "in\n",
            "/ports/inputs/0: 'in\\n' does not match '^[a-z][a-z0-9_]{0,31}$'",
        ),
        (
            ("version",),
            "1.0.0\n",
            r"/version: '1.0.0\n' does not match "
            r"'^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$'",
        ),
    ],
)
def test_declarations_reject_values_ending_in_a_newline(
    path: tuple[str | int, ...], value: str, issue: str
) -> None:
    assert declaration_issues(changed(declaration_example("llm-call"), path, value)) == (issue,)


@pytest.mark.parametrize(
    ("field", "value", "valid"),
    [
        ("word", "abc", True),
        ("word", "abc\n", False),
        ("price", "$12", True),
        ("price", "$12\n", False),
        ("price", "12", False),
        ("symbols", "$]$", True),
        ("symbols", "$\n", False),
        ("answer", "no", True),
        ("answer", "no\n", False),
        ("plain", "a\nb", True),
        ("plain", "a$", False),
    ],
)
def test_configuration_patterns(field: str, value: JsonValue, valid: bool) -> None:
    node: JsonObject = {
        "id": "proposer",
        "name": "Proposer",
        "component": "patterned@1.0.0",
        "config": {field: value},
    }
    document = changed(graph_example(J1), ("nodes", 1), node)
    expected = (
        []
        if valid
        else [(f"/nodes/1/config/{field}", f"{field.capitalize()} has an invalid format.")]
    )
    assert messages(document, "invalid_config", parse_declaration(PATTERNED)) == expected


def test_patterns_apply_only_to_strings() -> None:
    document = changed(declaration_example("llm-call"), ("type",), 5)
    assert declaration_issues(document) == ("/type: 5 is not of type 'string'",)
