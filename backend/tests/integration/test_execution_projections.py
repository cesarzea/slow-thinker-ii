"""Projection pages freeze state and retain separate repeated activation identities."""

from pathlib import Path

from slow_thinker_ii.adapters.catalog import BundledDefinitionStore
from slow_thinker_ii.adapters.sqlite import SqliteOperatorQueries
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object
from support.conditional_runtime import conditional_case
from support.coordinator import eventually
from support.sequence_plans import EXAMPLES


def test_catalog_detail_declares_inputs_layers_and_containment() -> None:
    store = BundledDefinitionStore(EXAMPLES)
    summary = next(item for item in store.summaries() if item.graph_id == "bounded-review")
    detail = json_object(decode_json(store.detail(summary.graph_id, summary.revision)))
    structure = json_object(detail["structure"])
    assert detail["input_schema"] == json_object(detail["definition"])["input_schema"]
    edges, components = structure["edges"], structure["components"]
    assert isinstance(edges, list) and isinstance(components, list)
    assert {str(json_object(item)["kind"]) for item in edges} == {
        "control",
        "permission",
        "binding",
    }
    assert any(json_object(item)["contained_by"] == "reviewer" for item in components)


async def test_execution_pages_cover_all_entries_without_duplicates(tmp_path: Path) -> None:
    case, _ = conditional_case(tmp_path)
    receipt = await case.coordinator.start("start", case.base.prepared().intent)
    run = receipt.receipt.target_id
    assert run is not None
    await eventually(lambda: not case.coordinator.pending().runs)
    queries = SqliteOperatorQueries(case.base.database, b"k" * 32, page_size=2)
    activations, calls, boundaries = pages(queries, run)
    assert len(boundaries) == 1 and len(activations) == 4 and len(calls) == 9
    assert len({str(item["id"]) for item in activations}) == 4
    assert [json_object(item)["selected_port"] for item in activations] == [
        "next",
        "revise",
        "next",
        "accept",
    ]
    await case.coordinator.close()


def pages(
    queries: SqliteOperatorQueries, run: str
) -> tuple[list[JsonObject], list[JsonObject], set[int]]:
    cursor: str | None = None
    activations: list[JsonObject] = []
    calls: list[JsonObject] = []
    boundaries: set[int] = set()
    while True:
        page = json_object(decode_json(queries.execution(run, cursor) or "{}"))
        boundary, nodes, managed, next_cursor = (
            page["through_sequence"],
            page["activations"],
            page["calls"],
            page["next_cursor"],
        )
        assert isinstance(boundary, int) and isinstance(nodes, list) and isinstance(managed, list)
        assert next_cursor is None or isinstance(next_cursor, str)
        cursor = next_cursor
        boundaries.add(boundary)
        activations.extend(json_object(item) for item in nodes)
        calls.extend(json_object(item) for item in managed)
        if cursor is None:
            return activations, calls, boundaries
