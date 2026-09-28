"""A high combined percentage cannot hide insufficient branch coverage."""

import json
from pathlib import Path

import pytest

from tooling.quality.coverage_gate import require_coverage


@pytest.mark.parametrize("lines, branches", [(89, 100), (100, 89)])
def test_rejects_hidden_coverage_gap(tmp_path: Path, lines: int, branches: int) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(
        json.dumps(
            {
                "totals": {
                    "covered_lines": lines,
                    "num_statements": 100,
                    "covered_branches": branches,
                    "num_branches": 100,
                }
            }
        )
    )
    with pytest.raises(ValueError, match="90% independently"):
        require_coverage(path)


def test_accepts_exact_boundary(tmp_path: Path) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(
        json.dumps(
            {
                "totals": {
                    "covered_lines": 90,
                    "num_statements": 100,
                    "covered_branches": 90,
                    "num_branches": 100,
                }
            }
        )
    )
    require_coverage(path)


@pytest.mark.parametrize("data", [[], {}, {"totals": {}}, {"totals": {"num_statements": 0}}])
def test_missing_coverage_is_not_success(tmp_path: Path, data: object) -> None:
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        require_coverage(path)
