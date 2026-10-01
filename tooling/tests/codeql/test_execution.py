"""Reject missing tooling, failed commands and unsafe inventory."""

import pytest

from tooling.quality.codeql import CodeQLFailure, verify_codeql

from .conftest import Gate


@pytest.mark.parametrize("languages", [(), ("ruby",), ("python", "python")])
def test_invalid_languages_fail_before_commands(gate: Gate, languages: tuple[str, ...]) -> None:
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, languages)
    assert gate.cli.commands == []


@pytest.mark.parametrize("root_kind", ["missing", "file"])
def test_invalid_repository_root(gate: Gate, root_kind: str) -> None:
    root = gate.root / root_kind
    if root_kind == "file":
        root.write_text("not a directory")
    with pytest.raises(CodeQLFailure):
        verify_codeql(root, gate.executable)
    assert gate.cli.commands == []


@pytest.mark.parametrize("version", ['{"version":"0.0.0"}', "[]", "malformed"])
def test_invalid_cli_version_retains_diagnostics(gate: Gate, version: str) -> None:
    gate.cli.version = version
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable)
    evidence = gate.evidence()[0]
    assert version in (evidence / "version.log").read_text()
    assert gate.scratch() == ()


def test_missing_bundled_suite_fails(gate: Gate) -> None:
    suite = next(gate.executable.parent.rglob("python-security-and-quality.qls"))
    suite.unlink()
    with pytest.raises(CodeQLFailure, match="Missing bundled python query suite"):
        verify_codeql(gate.root, gate.executable)
    assert gate.scratch() == ()


@pytest.mark.parametrize("stage", ["version", "ls-files", "create", "analyze"])
@pytest.mark.parametrize(
    "error", [None, FileNotFoundError("missing CLI"), UnicodeError("bad bytes")]
)
def test_command_failure_retains_logs_and_cleans(
    gate: Gate, stage: str, error: Exception | None
) -> None:
    gate.cli.failed_stage = stage
    gate.cli.exception = error
    with pytest.raises(CodeQLFailure) as failure:
        verify_codeql(gate.root, gate.executable, ("python",))
    assert "log:" in str(failure.value) and "retained evidence:" in str(failure.value)
    assert gate.scratch() == ()
    logs = tuple(gate.evidence()[0].glob("*.log"))
    assert any(
        "failure" in path.read_text() or "could not complete" in path.read_text() for path in logs
    )


@pytest.mark.parametrize(
    "inventory", ["source.py", "/source.py\0", "../source.py\0", "folder\\source.py\0", "\0"]
)
def test_invalid_or_empty_git_inventory(gate: Gate, inventory: str) -> None:
    gate.cli.inventory = inventory
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert gate.scratch() == ()


def test_nonregular_inventory_file_fails(gate: Gate) -> None:
    (gate.root / "directory.py").mkdir()
    gate.cli.inventory = "source.py\0directory.py\0"
    with pytest.raises(CodeQLFailure, match="not a regular file"):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert gate.scratch() == ()


@pytest.mark.parametrize(
    "name",
    [
        ".local",
        ".local/verification",
        ".local/verification/codeql",
        ".local/verification/codeql/scratch",
        ".local/verification/codeql/reports",
    ],
)
def test_workspace_symlink_is_rejected(gate: Gate, name: str) -> None:
    link = gate.root / name
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(gate.root.parent, target_is_directory=True)
    with pytest.raises(CodeQLFailure, match="Verification directory cannot be a symlink"):
        verify_codeql(gate.root, gate.executable)
    assert gate.cli.commands == []


def test_requested_language_needs_current_source(gate: Gate) -> None:
    (gate.root / "frontend/main.ts").unlink()
    with pytest.raises(CodeQLFailure, match="No current owned javascript"):
        verify_codeql(gate.root, gate.executable)
    assert gate.scratch() == ()
