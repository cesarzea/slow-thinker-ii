"""A RoutedCall can use only explicitly permitted resources with matching effective schemas."""

import pytest
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import ConditionalPlan
from support.composition_installations import (
    CompositionInstallation,
    change_object,
    effective_descriptions,
    prepare_composition,
)
from support.sequence_plans import graph_value


@pytest.fixture(scope="module")
def composition_installation(tmp_path_factory: pytest.TempPathFactory) -> CompositionInstallation:
    directory = tmp_path_factory.mktemp("composition-contracts")
    return prepare_composition(directory)


def test_matching_effective_worker_and_router_contracts_are_admitted(
    composition_installation: CompositionInstallation,
) -> None:
    installed = composition_installation.compiler().compile(
        encode_json(graph_value("bounded-review")),
        '{"problem":"inspect contracts"}',
        effective_descriptions(),
    )
    assert isinstance(installed.plan, ConditionalPlan)
    assert {item.instance_id for item in installed.configurations} >= {
        "reviewer",
        "review-worker",
        "review-router",
    }


@pytest.mark.parametrize(
    "side,field,expected",
    [
        ("review-worker", "incoming", "input schema"),
        ("review-worker", "outgoing", "output schema"),
        ("review-router", "outgoing", "outputs differ"),
    ],
)
def test_incompatible_installed_schema_is_rejected(
    composition_installation: CompositionInstallation, side: str, field: str, expected: str
) -> None:
    descriptions = effective_descriptions()
    value = json_object(decode_json(descriptions[side]))
    value[field] = (
        {"type": "object", "properties": {"port": {"enum": ["accept", "wrong"]}}}
        if side == "review-router"
        else {"type": "string"}
    )
    descriptions[side] = encode_json(value)
    with pytest.raises(ValueError, match=expected):
        composition_installation.compiler().compile(
            encode_json(graph_value("bounded-review")),
            '{"problem":"inspect contracts"}',
            descriptions,
        )


@pytest.mark.parametrize("resource", ["review-worker", "review-router"])
def test_composition_requires_permission_even_if_descriptor_does_not(
    composition_installation: CompositionInstallation,
    resource: str,
) -> None:
    graph = graph_value("bounded-review")
    permissions = graph["permissions"]
    assert isinstance(permissions, list)
    graph["permissions"] = [rule for rule in permissions if json_object(rule)["target"] != resource]
    with pytest.raises(ValueError, match="explicit effective operation permissions"):
        composition_installation.compiler().compile(
            encode_json(graph), '{"problem":"x"}', effective_descriptions()
        )


@pytest.mark.parametrize("field", ["worker", "router", "worker_operation"])
def test_weak_metadata_cannot_omit_required_composition_identity(
    composition_installation: CompositionInstallation,
    field: str,
) -> None:
    graph = graph_value("bounded-review")
    path = "config" if field == "worker_operation" else "resources"
    change_object(graph, f"/components/reviewer/{path}").pop(field)
    with pytest.raises(ValueError, match="worker and router resource bindings"):
        composition_installation.compiler().compile(
            encode_json(graph), '{"problem":"x"}', effective_descriptions()
        )
