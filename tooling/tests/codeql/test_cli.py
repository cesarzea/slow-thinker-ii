"""Exercise the public module CLI and documented executable resolution order."""

import shutil
from pathlib import Path

import pytest

from tooling.quality.codeql import AnalysisResult, CodeQLFailure
from tooling.quality.codeql import __main__ as cli

from .conftest import Gate, write_file


def select_root(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "__file__", str(root / "tooling/quality/codeql/__main__.py"))


def prepare_resolution(gate: Gate, monkeypatch: pytest.MonkeyPatch, source: str) -> Path:
    select_root(gate.root, monkeypatch)
    monkeypatch.delenv("CODEQL_EXECUTABLE", raising=False)
    cached = gate.root / ".cache/codeql-bundle/2.27.1/codeql/codeql"
    if source in {"environment", "cache"}:
        write_file(gate.root, str(cached.relative_to(gate.root)))
    if source == "environment":
        monkeypatch.setenv("CODEQL_EXECUTABLE", str(gate.executable))
    available = None if source == "missing" else str(gate.executable)

    def find_cli(_command: str) -> str | None:
        return available

    monkeypatch.setattr(shutil, "which", find_cli)
    return cached if source == "cache" else gate.executable


@pytest.mark.parametrize("source", ["environment", "cache", "path", "missing"])
def test_cli_resolution_precedence_and_missing_tool(
    gate: Gate, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], source: str
) -> None:
    expected = prepare_resolution(gate, monkeypatch, source)
    captured: list[tuple[Path, Path]] = []

    def verify(root: Path, executable: Path) -> tuple[AnalysisResult, ...]:
        captured.append((root, executable))
        return (AnalysisResult("python", 2, 0, 0, root / "report.sarif"),)

    monkeypatch.setattr(cli, "verify_codeql", verify)
    status = cli.main()
    output = capsys.readouterr()
    assert status == (1 if source == "missing" else 0)
    assert captured == ([] if source == "missing" else [(gate.root, expected.resolve())])
    assert (
        "CodeQL is missing" in output.err
        if source == "missing"
        else "2 notes; report:" in output.out
    )


def test_cli_runs_both_languages_and_prints_retained_reports(
    gate: Gate, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    select_root(gate.root, monkeypatch)
    monkeypatch.setenv("CODEQL_EXECUTABLE", str(gate.executable))
    status = cli.main()
    output = capsys.readouterr()
    assert status == 0
    assert "CodeQL python: 1 notes; report:" in output.out
    assert "CodeQL javascript: 1 notes; report:" in output.out
    assert str(gate.evidence()[0]) in output.out
    assert output.err == ""


@pytest.mark.parametrize(
    "error", [CodeQLFailure("incomplete analysis"), OSError("unavailable evidence")]
)
def test_cli_api_failure_prints_useful_error(
    gate: Gate,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: Exception,
) -> None:
    select_root(gate.root, monkeypatch)
    monkeypatch.setenv("CODEQL_EXECUTABLE", str(gate.executable))

    def fail(_root: Path, _executable: Path) -> tuple[AnalysisResult, ...]:
        raise error

    monkeypatch.setattr(cli, "verify_codeql", fail)
    status = cli.main()
    output = capsys.readouterr()
    assert status == 1
    assert str(error) in output.err
    assert output.out == ""


def test_cli_real_public_failure_identifies_retained_evidence(
    gate: Gate, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    select_root(gate.root, monkeypatch)
    monkeypatch.setenv("CODEQL_EXECUTABLE", str(gate.executable))
    gate.cli.failed_stage = "create"
    status = cli.main()
    output = capsys.readouterr()
    assert status == 1
    assert str(gate.evidence()[0]) in output.err
    assert gate.scratch() == ()
