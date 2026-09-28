"""Deliberate violations establish that placement and size gates reject code."""

from pathlib import Path

import pytest

from tooling.quality.inventory import Locations, approved_path, source_files
from tooling.quality.source_rules import check_source, python_sizes


@pytest.fixture
def locations() -> Locations:
    return Locations(("src",), ("entry.py",), frozenset({".venv"}), frozenset({".py"}))


@pytest.mark.parametrize(
    "path, expected", [("src/a.py", True), ("src_extra/a.py", False), ("entry.py", True)]
)
def test_location_boundary(path: str, expected: bool, locations: Locations) -> None:
    assert approved_path(path, locations) is expected


def test_excludes_dependencies(tmp_path: Path, locations: Locations) -> None:
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv/third_party.py").write_text("invalid dependency source")
    (tmp_path / "entry.py").write_text("")
    assert source_files(tmp_path, locations) == [tmp_path / "entry.py"]


def test_rejects_long_misplaced_source(tmp_path: Path, locations: Locations) -> None:
    (tmp_path / "loose.py").write_text("# line\n" * 151)
    issues = check_source(tmp_path, locations)
    assert len(issues) == 2
    assert "outside declared" in issues[0]
    assert "150 physical" in issues[1]


@pytest.mark.parametrize("prefix", ["def", "async def"])
def test_function_boundary(prefix: str) -> None:
    accepted = f"{prefix} f():\n" + "    pass\n" * 29
    assert python_sizes("example.py", accepted) == []
    assert "30 physical" in python_sizes("example.py", accepted + "    pass\n")[0]


def test_accepts_small_source(tmp_path: Path, locations: Locations) -> None:
    (tmp_path / "entry.py").write_text("def f():\n    return 1\n")
    assert check_source(tmp_path, locations) == []
