"""The optional view: connection style and curvature, for presentation only."""

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import compile_plan

from .contract_fixtures import J1, changed, graph_example, step_one_catalog
from .graph_checks import found

STYLE = 'Connection style must be one of "curved", "simple", "routed".'


def with_view(view: JsonValue) -> JsonObject:
    return changed(graph_example(J1), ("view",), view)


def test_documents_without_a_view() -> None:
    assert "view" not in graph_example(J1)
    assert found(graph_example(J1)) == []


VALID: list[JsonValue] = [
    {},
    {"connections": "curved"},
    {"connections": "simple"},
    {"connections": "routed"},
    {"curvature": 0},
    {"curvature": 1},
    {"connections": "curved", "curvature": 0.35},
]


@pytest.mark.parametrize("view", VALID)
def test_valid_views(view: JsonValue) -> None:
    assert found(with_view(view)) == []


def test_views_never_affect_execution() -> None:
    plain = compile_plan(graph_example(J1), step_one_catalog(), 1)
    viewed = compile_plan(
        with_view({"connections": "routed", "curvature": 0.5}), step_one_catalog(), 1
    )
    assert (viewed.nodes, viewed.routes, viewed.limits) == (plain.nodes, plain.routes, plain.limits)


INVALID: list[tuple[JsonValue, str, str]] = [
    ("curved", "/view", "View has the wrong type."),
    ({"connections": "straight"}, "/view/connections", STYLE),
    ({"connections": 1}, "/view/connections", STYLE),
    ({"curvature": -0.1}, "/view/curvature", "Curvature must be at least 0."),
    ({"curvature": 1.5}, "/view/curvature", "Curvature must be at most 1."),
    ({"curvature": "0.5"}, "/view/curvature", "Curvature has the wrong type."),
    ({"zoom": 2}, "/view/zoom", "Zoom is invalid."),
]


@pytest.mark.parametrize(("view", "path", "message"), INVALID)
def test_bad_shapes_and_values_are_errors(view: JsonValue, path: str, message: str) -> None:
    assert found(with_view(view)) == [("invalid_document", path, message, None)]
