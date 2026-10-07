"""Configuration problems are plain sentences that start with the field's interface label."""

from dataclasses import replace

import pytest
from slow_thinker_ii.catalog import ComponentDeclaration, parse_declaration
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .contract_fixtures import J1, J2, changed, graph_example
from .graph_checks import found_with, messages

FIELDS: list[JsonValue] = [
    {"path": "/title", "control": "text", "label": "Title"},
    {"path": "/count", "control": "number", "label": "Count"},
    {"path": "/code", "control": "code", "label": "Code", "language": "text"},
    {"path": "/tags", "control": "list", "label": "Tags"},
    {
        "path": "/mode",
        "control": "choice",
        "label": "Mode",
        "options": [{"value": "fast", "label": "Fast"}, {"value": "slow", "label": "Slow"}],
    },
]
PROBE: JsonObject = {
    "format": "slow-thinker.component/1",
    "type": "probe",
    "version": "1.0.0",
    "label": "Probe",
    "description": "Exercises configuration messages.",
    "icon": "component",
    "placements": ["node"],
    "state": "stateless",
    "ports": {"inputs": ["in"], "outputs": ["out"]},
    "uses": [],
    "config_schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["title", "count", "mode"],
        "properties": {
            "title": {"type": "string", "minLength": 1, "maxLength": 5},
            "count": {"type": "integer", "minimum": 1, "maximum": 3},
            "mode": {"enum": ["fast", "slow"]},
            "code": {"type": "string", "minLength": 2, "pattern": "^[a-z]+$"},
            "tags": {"type": "array", "maxItems": 2, "items": {"type": "string"}},
            "nested": {"type": "object", "required": ["inner"]},
            "ratio": {"type": "number", "exclusiveMaximum": 1},
            "level": {"const": "a", "not": {"const": "b"}},
        },
    },
    "initial_config": {"title": "", "count": 1, "mode": "fast"},
    "ui": {"card": [], "sections": [{"id": "main", "title": "Main", "fields": FIELDS}]},
}
VALID: JsonObject = {"title": "Hi", "count": 2, "mode": "fast"}


def probe() -> ComponentDeclaration:
    return parse_declaration(PROBE)


def probe_graph(config: JsonValue) -> JsonObject:
    node = {"id": "proposer", "name": "Probe", "component": "probe@1.0.0", "config": config}
    return changed(graph_example(J1), ("nodes", 1), node)


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"title": ""}, [("/title", "Title is required.")]),
        ({"title": "toolong"}, [("/title", "Title is too long.")]),
        ({"title": 5}, [("/title", "Title has the wrong type.")]),
        ({"count": 0}, [("/count", "Count must be at least 1.")]),
        ({"count": 4}, [("/count", "Count must be at most 3.")]),
        ({"mode": "x"}, [("/mode", 'Mode must be one of "fast", "slow".')]),
        ({"code": "AB"}, [("/code", "Code has an invalid format.")]),
        ({"code": "abc\n"}, [("/code", "Code has an invalid format.")]),
        ({"code": "a"}, [("/code", "Code is invalid.")]),
        ({"tags": ["a", "b", "c"]}, [("/tags", "Tags is too long.")]),
        ({"tags": [1]}, [("/tags/0", "Tags has the wrong type.")]),
        ({"nested": {}}, [("/nested/inner", "Inner is required.")]),
        ({"ratio": 1}, [("/ratio", "Ratio is invalid.")]),
        ({"colour_name": 1}, [("/colour_name", "Colour name is invalid.")]),
    ],
)
def test_keyword_sentences(change: JsonObject, expected: list[tuple[str, str]]) -> None:
    document = probe_graph(VALID | change)
    prefixed = [(f"/nodes/1/config{path}", message) for path, message in expected]
    assert messages(document, "invalid_config", probe()) == prefixed


def test_missing_members_are_reported_once_each() -> None:
    assert messages(probe_graph({"mode": "fast"}), "invalid_config", probe()) == [
        ("/nodes/1/config/count", "Count is required."),
        ("/nodes/1/config/title", "Title is required."),
    ]


def test_identical_messages_for_one_value_appear_once() -> None:
    assert messages(probe_graph(VALID | {"level": "b"}), "invalid_config", probe()) == [
        ("/nodes/1/config/level", "Level is invalid.")
    ]


def test_conditional_requirements_and_unlabelled_values() -> None:
    llm_json = changed(graph_example(J1), ("nodes", 1, "config", "output_format"), {"type": "json"})
    assert messages(llm_json, "invalid_config") == [
        ("/nodes/1/config/output_format/schema", "JSON schema is required.")
    ]
    llm_text = changed(graph_example(J1), ("nodes", 1, "config", "output_format"), "text")
    assert messages(llm_text, "invalid_config") == [
        ("/nodes/1/config/output_format", "Output format has the wrong type.")
    ]


def test_platform_and_embedded_component_labels() -> None:
    long_message = changed(graph_example(J1), ("nodes", 0, "config", "message"), "x" * 100_001)
    assert found_with(long_message, "invalid_config") == [
        (
            "invalid_config",
            "/nodes/0/config/message",
            "Message sent when the run starts is too long.",
            "story",
        )
    ]
    script = ("nodes", 1, "embedded", 0, "config", "script")
    assert messages(changed(graph_example(J2), script, ""), "invalid_config") == [
        ("/nodes/1/embedded/0/config/script", "route(received, node_input) is required.")
    ]


def test_schemas_with_unresolvable_references_cannot_be_checked() -> None:
    unresolvable: JsonObject = {"$ref": "https://example.com/never-fetched.json"}
    declaration = replace(probe(), config_schema=unresolvable)
    assert messages(probe_graph(VALID), "invalid_config", declaration) == [
        ("/nodes/1/config", "Configuration is invalid.")
    ]
