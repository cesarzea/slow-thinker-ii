"""Definition structure keeps distinct control, permission and resource identities."""

import pytest
from slow_thinker_ii.contracts import JsonValue, json_object
from slow_thinker_ii.definitions import graph_detail
from support.composition_installations import change_object
from support.sequence_plans import graph_value


def test_finite_sequence_edges_keep_order_and_terminal_destination() -> None:
    graph = graph_value("review-cycle")
    detail = graph_detail(graph, {"proposer": ("agent",), "model": ("resource",)})
    structure = json_object(detail["structure"])
    edges, components = structure["edges"], structure["components"]
    assert isinstance(edges, list) and isinstance(components, list)
    control = [json_object(edge) for edge in edges if json_object(edge)["kind"] == "control"]
    steps = change_object(graph, "/components/sequence/config")["steps"]
    assert isinstance(steps, list)
    assert [edge["source"] for edge in control] == steps
    assert [edge["target"] for edge in control] == [*steps[1:], None]
    assert len({str(json_object(edge)["id"]) for edge in edges}) == len(edges)
    proposer = next(
        json_object(item) for item in components if json_object(item)["id"] == "proposer"
    )
    assert proposer["roles"] == ["agent"] and proposer["contained_by"] is None


@pytest.mark.parametrize(
    "pointer,key,value,reason",
    [
        ("", "permissions", {}, "Permissions must"),
        ("/permissions/0", "operations", {}, "Permission operations must"),
        ("/components/sequence/config", "steps", {}, "Sequence steps must"),
    ],
)
def test_structure_rejects_malformed_collections(
    pointer: str, key: str, value: JsonValue, reason: str
) -> None:
    graph = graph_value("review-cycle")
    change_object(graph, pointer)[key] = value
    with pytest.raises(ValueError, match=reason):
        graph_detail(graph, {})
