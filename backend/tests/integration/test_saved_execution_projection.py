"""Saved definitions and page continuations do not drift as live evidence changes."""

from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteOperatorQueries
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object
from support.conditional_runtime import conditional_case
from support.coordinator import eventually


async def test_definition_preserves_admitted_graph_with_explicit_layers(tmp_path: Path) -> None:
    case, _ = conditional_case(tmp_path)
    receipt = await case.coordinator.start("start", case.base.prepared().intent)
    run = receipt.receipt.target_id
    assert run is not None
    await eventually(lambda: not case.coordinator.pending().runs)
    queries = SqliteOperatorQueries(case.base.database, b"k" * 32)
    saved = json_object(decode_json(queries.definition(run) or "{}"))
    assert saved["definition"] == json_object(saved["execution"])["definition"]
    assert saved["graph_id"] == "bounded-review"
    assert saved["input_schema"] == json_object(saved["definition"])["input_schema"]
    components = json_object(saved["structure"])["components"]
    assert isinstance(components, list) and len(components) == 7
    await case.coordinator.close()


async def test_paging_retains_active_state_after_the_run_finishes(tmp_path: Path) -> None:
    case, environment = conditional_case(tmp_path, "wait")
    receipt = await case.coordinator.start("start", case.base.prepared().intent)
    run = receipt.receipt.target_id
    assert run is not None
    await environment.proposer.started.wait()
    queries = SqliteOperatorQueries(case.base.database, b"k" * 32, page_size=1)
    page = json_object(decode_json(queries.execution(run) or "{}"))
    through = page["through_sequence"]
    environment.proposer.release.set()
    await eventually(lambda: not case.coordinator.pending().runs)
    activations: list[JsonObject] = []
    while isinstance(cursor := page["next_cursor"], str):
        page = json_object(decode_json(queries.execution(run, cursor) or "{}"))
        assert page["through_sequence"] == through
        nodes = page["activations"]
        assert isinstance(nodes, list)
        activations.extend(json_object(item) for item in nodes)
    assert len(activations) == 1 and activations[0]["state"] == "dispatched"
    assert activations[0]["selected_port"] is None
    await case.coordinator.close()
