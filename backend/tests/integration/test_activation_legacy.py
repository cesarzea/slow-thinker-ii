"""Older run records retain explicit absence rather than fabricated binding input."""

from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteOperatorQueries
from slow_thinker_ii.contracts import decode_json, json_object
from support.run_admission import run_case


def test_known_run_without_saved_input_differs_from_an_unknown_run(tmp_path: Path) -> None:
    case = run_case(tmp_path / "legacy.sqlite")
    queries = SqliteOperatorQueries(case.database, b"k" * 32)
    response = queries.payload("run", "run-input:run")
    assert response is not None
    value = json_object(decode_json(response))
    assert value["status"] == "unavailable" and value["reason"] == "not_recorded"
    assert queries.payload("unknown", "run-input:unknown") is None
