"""Bootstrap input is data, with explicit fields and no executable selection."""

import json
from pathlib import Path

import pytest
from slow_thinker_host import JsonObject, read_bootstrap

INVALID_RECORDS: list[JsonObject] = [
    {},
    {"config": {}, "operations": [], "command": "untrusted"},
    {"config": {}, "operations": {}},
    {"config": {}, "operations": [{}]},
    {"config": {}, "operations": [{"name": "", "input_schema": {}, "output_schema": {}}]},
]


def test_bootstrap_accepts_only_declared_data(tmp_path: Path) -> None:
    path = tmp_path / "bootstrap.json"
    path.write_text(
        json.dumps(
            {
                "config": {},
                "operations": [
                    {
                        "name": "echo",
                        "input_schema": {"type": "object"},
                        "output_schema": {"type": "object"},
                    }
                ],
            }
        )
    )
    loaded = read_bootstrap(path)
    assert loaded.config == {}
    assert loaded.operations[0].name == "echo"


@pytest.mark.parametrize("record", INVALID_RECORDS)
def test_invalid_bootstrap(tmp_path: Path, record: object) -> None:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        read_bootstrap(path)
