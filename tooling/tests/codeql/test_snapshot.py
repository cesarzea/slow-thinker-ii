"""Verify current source, privacy exclusions and retained evidence publicly."""

import pytest

from tooling.quality.codeql import CodeQLFailure, verify_codeql

from .conftest import Gate, git, write_file
from .reports import report


def test_current_edits_untracked_and_deleted_files(gate: Gate) -> None:
    deleted = write_file(gate.root, "deleted.py")
    git(gate.root, "add", "deleted.py")
    deleted.unlink()
    write_file(gate.root, "source.py", "value = 'current unstaged edit'\n")
    write_file(gate.root, "new source.py", "value = 'untracked source'\n")
    write_file(gate.root, "ignored/dependency.py", "ignored content\n")
    gate.cli.documents["python"] = report("python", ("source.py", "new source.py"))
    results = verify_codeql(gate.root, gate.executable)
    assert isinstance(results, tuple)
    assert [result.language for result in results] == ["python", "javascript"]
    copied = gate.cli.snapshots[0]
    assert copied["source.py"] == "value = 'current unstaged edit'\n"
    assert copied["new source.py"] == "value = 'untracked source'\n"
    assert "deleted.py" not in copied
    assert "ignored/dependency.py" not in copied
    assert gate.scratch() == ()
    for result in results:
        assert result.report.is_file()
        assert result.notes == 1 and result.warnings == 0 and result.errors == 0


@pytest.mark.parametrize(
    "names",
    [
        (
            ".cache",
            ".local",
            ".venv",
            "node_modules",
            "site-packages",
            "vendor",
            "bower_components",
        ),
        ("__pycache__", "dist", "build", "coverage", "mutants", ".idea", ".vscode", ".aws", ".ssh"),
        ("venv", "env", "packages", "bin", "obj", "target", "private", "secrets", "credentials"),
        (
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            ".import_linter_cache",
            ".jbeval",
            ".gnupg",
        ),
        (
            "ext",
            "extjs",
            "ext-framework",
            "sencha",
            "jquery-plugin",
            "bootstrap-theme",
            ".hg",
            ".svn",
        ),
    ],
)
def test_excludes_nested_private_dependency_and_build_directories(
    gate: Gate, names: tuple[str, ...]
) -> None:
    for name in names:
        write_file(gate.root, f"nested/{name}/must-not-copy.py", "private fixture\n")
    git(gate.root, "add", ".")
    verify_codeql(gate.root, gate.executable, ("python",))
    assert set(gate.cli.snapshots[0]) == {"source.py", "frontend/main.ts", ".gitignore"}


@pytest.mark.parametrize(
    "names",
    [
        (".env", ".env.local", "project.env", "slow-thinker.keys.json", "service.credentials.json"),
        (
            "private.pem",
            "private.key",
            "private.p12",
            "private.pfx",
            "private.jks",
            "private.keystore",
        ),
        (".envrc", ".npmrc", ".netrc", ".pypirc", ".git-credentials", "id_rsa", "id_ed25519"),
        ("credentials.json", "credentials.yaml", "credentials.yml", "id_dsa", "id_ecdsa"),
        ("library.min.js", "prior.sarif", "prior.bqrs", "jquery.js", "bootstrap.css"),
    ],
)
def test_excludes_credential_names_and_prior_analysis(gate: Gate, names: tuple[str, ...]) -> None:
    for name in names:
        write_file(gate.root, name, "synthetic private fixture\n")
    git(gate.root, "add", ".")
    verify_codeql(gate.root, gate.executable, ("python",))
    assert set(gate.cli.snapshots[0]) == {"source.py", "frontend/main.ts", ".gitignore"}


def test_all_javascript_extensions_are_required(gate: Gate) -> None:
    names = tuple(f"module{extension}" for extension in (".js", ".cjs", ".mjs", ".ts", ".tsx"))
    for name in names:
        write_file(gate.root, name, "export const value = 1;\n")
    gate.cli.documents["javascript"] = report("javascript", ("frontend/main.ts", *names))
    results = verify_codeql(gate.root, gate.executable, ("javascript",))
    assert results[0].language == "javascript"
    assert all(name in gate.cli.snapshots[0] for name in names)


def test_each_invocation_retains_fresh_evidence_and_cleans_scratch(gate: Gate) -> None:
    first = verify_codeql(gate.root, gate.executable, ("python",))[0]
    second = verify_codeql(gate.root, gate.executable, ("python",))[0]
    assert first.report.parent != second.report.parent
    assert first.report.is_file() and second.report.is_file()
    assert len(gate.evidence()) == 2
    assert gate.scratch() == ()
    logs = {path.name for path in first.report.parent.iterdir()}
    assert logs == {
        "version.log",
        "source-inventory.log",
        "python-create.log",
        "python-analyze.log",
        "python.sarif",
    }
    create = next(command for command in gate.cli.commands if "create" in command)
    analyze = next(command for command in gate.cli.commands if "analyze" in command)
    assert {"--build-mode=none", "--threads=2", "--ram=4096"}.issubset(create)
    assert {"--format=sarifv2.1.0", "--no-download", "--no-sarif-group-rules-by-pack"}.issubset(
        analyze
    )
    assert "python-queries/1.8.11/codeql-suites/python-security-and-quality.qls" in analyze[4]


@pytest.mark.parametrize("directory", [False, True])
def test_source_symlinks_fail_and_cleanup(gate: Gate, directory: bool) -> None:
    target = gate.root.parent / "outside"
    target.mkdir()
    write_file(target, "linked.py")
    link = gate.root / ("linked" if directory else "linked.py")
    link.symlink_to(target if directory else target / "linked.py", target_is_directory=directory)
    gate.cli.inventory = "source.py\0linked/linked.py\0" if directory else "source.py\0linked.py\0"
    with pytest.raises(CodeQLFailure, match="Source symlinks are forbidden") as failure:
        verify_codeql(gate.root, gate.executable, ("python",))
    assert "retained evidence:" in str(failure.value)
    assert gate.scratch() == ()
    assert len(gate.evidence()) == 1
