"""Malformed location manifests cannot silently disable verification."""

import json
from pathlib import Path

import pytest

from tooling.quality.inventory import read_locations, source_files


@pytest.mark.parametrize("value", [[], {}, {"roots": [1]}, {"roots": "src"}])
def test_rejects_malformed_manifest(tmp_path: Path, value: object) -> None:
    (tmp_path / "tooling").mkdir()
    (tmp_path / "tooling/locations.json").write_text(json.dumps(value))
    with pytest.raises(ValueError):
        read_locations(tmp_path)


def test_loads_current_manifest() -> None:
    root = Path(__file__).resolve().parents[2]
    locations = read_locations(root)
    assert "backend/src/slow_thinker_ii/accounting" in locations.roots
    assert ".venv" in locations.excluded
    assert ".py" in locations.extensions


def test_managed_installations_are_not_repository_source(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    locations = read_locations(root)
    installed = tmp_path / ".local/components/environment/site-packages/dependency"
    installed.mkdir(parents=True)
    (installed / "external.py").write_text("This is deliberately not valid Python source")
    assert source_files(tmp_path, locations) == []
