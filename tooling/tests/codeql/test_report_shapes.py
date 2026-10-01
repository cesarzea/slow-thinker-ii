"""Malformed or unsuccessful SARIF is rejected even when the CLI exits zero."""

import pytest

from tooling.quality.codeql import CodeQLFailure, verify_codeql

from .conftest import Gate
from .paths import DRIVER, EXPECTED, INVOCATION, NOTIFICATIONS, RESULT, RUN
from .reports import FieldPath, replace


@pytest.mark.parametrize(
    "path,value",
    [
        (("version",), "2.0.0"),
        (("runs",), []),
        (("runs",), {}),
        (RUN, "invalid run"),
        ((*RUN, "tool"), None),
        (DRIVER, []),
        ((*DRIVER, "name"), "Other analyzer"),
        ((*DRIVER, "semanticVersion"), "2.27.0"),
        ((*DRIVER, "version"), "2.27.0"),
        ((*DRIVER, "rules"), []),
        ((*DRIVER, "rules"), {}),
        ((*DRIVER, "rules", 0), "invalid rule"),
        ((*DRIVER, "rules", 0, "id"), ""),
        ((*DRIVER, "rules", 0, "id"), 3),
        ((*RUN, "results"), None),
        (RESULT, False),
        ((*RUN, "invocations"), []),
        ((*RUN, "invocations"), {}),
        (INVOCATION, None),
        ((*INVOCATION, "executionSuccessful"), False),
        ((*INVOCATION, "executionSuccessful"), 1),
        (NOTIFICATIONS, None),
        (EXPECTED, "invalid notification"),
        ((*DRIVER, "notifications"), {}),
        ((*RUN, "artifacts"), {}),
        ((*INVOCATION, "toolConfigurationNotifications"), {}),
    ],
)
def test_rejects_invalid_sarif_shapes(gate: Gate, path: FieldPath, value: object) -> None:
    replace(gate.cli.python_report(), path, value)
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert gate.scratch() == ()
    assert (gate.evidence()[0] / "python.sarif").is_file()


@pytest.mark.parametrize("raw", ["not JSON", "[]", "null", "42"])
def test_rejects_unreadable_or_nonobject_json(gate: Gate, raw: str) -> None:
    gate.cli.raw_report = raw
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert (gate.evidence()[0] / "python.sarif").read_text() == raw
    assert gate.scratch() == ()


def test_cli_success_without_a_report_is_failure(gate: Gate) -> None:
    gate.cli.write_report = False
    with pytest.raises(CodeQLFailure, match="Cannot read JSON evidence"):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert (gate.evidence()[0] / "python-analyze.log").is_file()
    assert gate.scratch() == ()
