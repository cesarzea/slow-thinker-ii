"""Verification must run real commands and stop at the first rejected gate."""

import json
import sys
from pathlib import Path

import pytest

from tooling.quality import verify


def prepare_root(root: Path) -> None:
    (root / "tooling").mkdir()
    manifest = {"roots": [], "files": [], "excluded": ["mutants"], "extensions": [".py"]}
    (root / "tooling/locations.json").write_text(json.dumps(manifest))
    (root / "coverage").mkdir()
    (root / "coverage/python.json").write_text(
        json.dumps(
            {
                "totals": {
                    "covered_lines": 10,
                    "num_statements": 10,
                    "covered_branches": 2,
                    "num_branches": 2,
                }
            }
        )
    )


def test_stops_on_command_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_root(tmp_path)
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setattr(verify, "COMMANDS", ((sys.executable, "-c", "raise SystemExit(7)"),))
    assert verify.main() == 7


def test_rejects_source_before_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_root(tmp_path)
    (tmp_path / "misplaced.py").write_text("")
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setattr(verify, "COMMANDS", (("must-not-execute",),))
    assert verify.main() == 1


def test_success_checks_coverage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prepare_root(tmp_path)
    stats = tmp_path / "backend/mutants/mutmut-stats.json"
    stale = tmp_path / "backend/mutants/tests/unit/test_removed_api.py"
    stale.parent.mkdir(parents=True)
    stats.write_text("stale test mapping")
    stale.write_text("from removed import api")
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setattr(verify, "COMMANDS", ((sys.executable, "-c", "pass"),))
    assert verify.main() == 0
    assert not stats.exists()
    assert not stale.exists()
    (tmp_path / "coverage/python.json").write_text("{}")
    with pytest.raises(ValueError, match="coverage totals"):
        verify.main()
