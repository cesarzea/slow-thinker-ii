"""Owned source whose directory names resemble third-party frameworks is still analysed."""

from tooling.quality.codeql import verify_codeql

from .conftest import Gate, git, write_file
from .reports import report

COMPOSITION_ROOT = "backend/src/application/bootstrap/__init__.py"
FRAMEWORK_COPY = "nested/bootstrap-theme/style.py"


def test_composition_root_named_bootstrap_is_copied(gate: Gate) -> None:
    write_file(gate.root, COMPOSITION_ROOT, "value = 1\n")
    write_file(gate.root, FRAMEWORK_COPY, "private fixture\n")
    git(gate.root, "add", ".")
    gate.cli.documents["python"] = report("python", ("source.py", COMPOSITION_ROOT))
    verify_codeql(gate.root, gate.executable, ("python",))
    copied = gate.cli.snapshots[0]
    assert COMPOSITION_ROOT in copied
    assert FRAMEWORK_COPY not in copied
