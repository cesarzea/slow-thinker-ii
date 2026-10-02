"""Local descriptor and graph validation covers every registered execution profile."""

import pytest
from slow_thinker_ii.adapters.catalog import GraphDefinitionValidator
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonValue, decode_json, encode_json, json_object
from support.personal_experiments.definitions import set_field
from support.sequence_plans import graph_value


@pytest.mark.parametrize(
    "name", ["single-agent", "handoff", "review-cycle", "repeated-review", "bounded-review"]
)
def test_all_supported_bundled_definitions_validate_locally(
    validator: GraphDefinitionValidator, name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("Static definition validation attempted component startup")

    monkeypatch.setattr("subprocess.Popen", forbidden)
    value = graph_value(name)
    validated = validator.validate(encode_json(value))
    detail = json_object(decode_json(validator.detail(validated.definition_json)))
    assert detail["definition"] == value
    assert detail["graph_id"] == validated.reference.graph_id
    assert validated.summary.participant_count >= 1


@pytest.mark.parametrize(
    "parent,name,replacement",
    [
        ("/components/proposer", "type_version", "unknown-version"),
        ("/components/proposer", "type_id", "unregistered-type"),
        ("/components/proposer", "contained_by", "missing"),
        ("/components/proposer", "contained_by", "proposer"),
        ("/controller", "component", "missing"),
        ("/controller", "operation", "missing"),
        ("/controller", "component", "proposer"),
        ("/nodes/draft", "component", "missing"),
        ("/nodes/draft", "operation", "missing"),
        ("/nodes/review/inputs/proposal", "node", "review"),
        ("/nodes/review/inputs/proposal", "node", "revise"),
        ("/nodes/draft/inputs/problem", "pointer", "/bad~2pointer"),
        ("/nodes/draft/inputs/problem", "activation", "latest_completed"),
        ("/components/sequence/config", "steps", ["draft"]),
        ("/components/sequence/config", "steps", ["draft", "review", "review"]),
        ("/components/proposer", "resources", {}),
        ("/components/proposer/resources", "model", "missing"),
        ("/components/proposer/resources", "model", "sequence"),
        ("/components/proposer/resources", "unknown", "model"),
        ("", "permissions", []),
        ("", "permissions", [{"caller": "missing", "target": "model", "operations": ["complete"]}]),
        ("", "permissions", [{"caller": "proposer", "target": "model", "operations": ["missing"]}]),
        ("", "execution_profile", "future-profile"),
    ],
)
def test_invalid_references_and_profiles_are_rejected(
    validator: GraphDefinitionValidator, parent: str, name: str, replacement: JsonValue
) -> None:
    value = graph_value("review-cycle")
    set_field(value, parent, name, replacement)
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(encode_json(value))
    assert error.value.code == "invalid_definition"
    assert 1 <= len(error.value.issues) <= 10


@pytest.mark.parametrize(
    "parent,name,replacement",
    [
        ("/components/flow/config", "entry", "missing"),
        ("/components/flow/config", "routes", {"propose": {"next": None}}),
        ("/components/flow/config/routes/propose", "next", "missing"),
        ("/components/flow/config/routes", "propose", {"": None}),
        ("/nodes/propose", "output", {"constant": "unknown"}),
        ("/nodes/propose", "output", {"pointer": "invalid"}),
        ("/nodes/propose/inputs/proposal", "node", "missing"),
        ("/nodes/propose/inputs/proposal", "activation", None),
        ("", "result", {"source": "run_input", "pointer": "/problem"}),
        ("/result", "node", "missing"),
        ("/components/reviewer/config", "worker_operation", "missing"),
        ("/components/reviewer/config", "outputs", ["different"]),
        ("/components/reviewer/config", "input_schema", {"type": "object"}),
        ("/components/reviewer/config", "router_input_pointer", "invalid"),
    ],
)
def test_conditional_references_routes_and_compositions_are_rejected(
    validator: GraphDefinitionValidator, parent: str, name: str, replacement: JsonValue
) -> None:
    value = graph_value("bounded-review")
    set_field(value, parent, name, replacement)
    with pytest.raises(library.DefinitionError) as error:
        validator.validate(encode_json(value))
    assert error.value.code == "invalid_definition"


def test_containment_cycles_and_duplicate_permissions_are_rejected(
    validator: GraphDefinitionValidator,
) -> None:
    cycle = graph_value("single-agent")
    set_field(cycle, "/components/proposer", "contained_by", "model")
    set_field(cycle, "/components/model", "contained_by", "proposer")
    duplicates = graph_value("single-agent")
    permissions: list[JsonValue] = [
        {"caller": "proposer", "target": "model", "operations": ["complete"]}
    ] * 2
    duplicates["permissions"] = permissions
    for value in (cycle, duplicates):
        with pytest.raises(library.DefinitionError) as error:
            validator.validate(encode_json(value))
        assert error.value.code == "invalid_definition"
