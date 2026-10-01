"""Validate finding references, effective severity and immutable public results."""

from dataclasses import FrozenInstanceError

import pytest

from tooling.quality.codeql import AnalysisResult, CodeQLFailure, verify_codeql

from .conftest import Gate
from .paths import DRIVER, RESULT, RUN
from .reports import FieldPath, remove, replace


@pytest.mark.parametrize(
    "path,value",
    [
        ((*RESULT, "level"), "unknown"),
        ((*RESULT, "level"), None),
        ((*RESULT, "level"), "warning"),
        ((*RESULT, "level"), "error"),
        ((*RESULT, "ruleId"), "unknown/rule"),
        ((*RESULT, "ruleIndex"), True),
        ((*RESULT, "ruleIndex"), -1),
        ((*RESULT, "ruleIndex"), 99),
        ((*RESULT, "rule"), {"id": "different/rule"}),
        ((*RESULT, "rule"), {"index": 1}),
        ((*RESULT, "rule"), {"toolComponent": {"name": "external"}}),
        ((*RESULT, "rule"), []),
        ((*RESULT, "suppressions"), [{"kind": "inSource"}]),
        ((*RESULT, "suppressions"), {}),
        ((*DRIVER, "rules"), [{"id": "owned/rule"}, {"id": "owned/rule"}]),
    ],
)
def test_invalid_and_actionable_findings_fail(gate: Gate, path: FieldPath, value: object) -> None:
    replace(gate.cli.python_report(), path, value)
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert gate.scratch() == ()
    assert (gate.evidence()[0] / "python.sarif").is_file()


@pytest.mark.parametrize("level", [None, "unknown", "warning", "error"])
def test_rule_default_severity_is_validated(gate: Gate, level: object) -> None:
    document = gate.cli.python_report()
    remove(document, (*RESULT, "level"))
    replace(document, (*DRIVER, "rules", 0, "defaultConfiguration", "level"), level)
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))


@pytest.mark.parametrize(
    "removed", [(*RESULT, "ruleId"), (*RESULT, "ruleIndex"), (*RESULT, "level")]
)
def test_index_id_and_default_severity_are_supported(gate: Gate, removed: FieldPath) -> None:
    remove(gate.cli.python_report(), removed)
    result = verify_codeql(gate.root, gate.executable, ("python",))[0]
    assert isinstance(result, AnalysisResult)
    assert (result.language, result.notes, result.warnings, result.errors) == ("python", 1, 0, 0)
    attribute = "notes"
    with pytest.raises(FrozenInstanceError):
        setattr(result, attribute, 99)


def test_none_results_and_empty_findings_are_clean(gate: Gate) -> None:
    replace(gate.cli.python_report(), (*RESULT, "level"), "none")
    first = verify_codeql(gate.root, gate.executable, ("python",))[0]
    replace(gate.cli.python_report(), (*RUN, "results"), [])
    second = verify_codeql(gate.root, gate.executable, ("python",))[0]
    assert first.notes == second.notes == 0
    assert first.report.is_file() and second.report.is_file()


@pytest.mark.parametrize(
    "missing", [(*RESULT, "level"), (*RESULT, "ruleId"), (*DRIVER, "semanticVersion")]
)
def test_absent_rule_severity_and_version_fail(gate: Gate, missing: FieldPath) -> None:
    document = gate.cli.python_report()
    remove(document, missing)
    if missing == (*RESULT, "level"):
        remove(document, (*DRIVER, "rules", 0, "defaultConfiguration"))
    if missing == (*RESULT, "ruleId"):
        remove(document, (*RESULT, "ruleIndex"))
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))


def test_disagreeing_rule_id_and_index_fail(gate: Gate) -> None:
    replace(
        gate.cli.python_report(), (*DRIVER, "rules"), [{"id": "owned/rule"}, {"id": "second/rule"}]
    )
    replace(gate.cli.python_report(), (*RESULT, "ruleIndex"), 1)
    with pytest.raises(CodeQLFailure, match="ID disagrees with its index"):
        verify_codeql(gate.root, gate.executable, ("python",))


def test_nested_rule_reference_is_supported(gate: Gate) -> None:
    replace(
        gate.cli.python_report(),
        RESULT,
        {"rule": {"id": "owned/rule", "index": 0}, "level": "note"},
    )
    result = verify_codeql(gate.root, gate.executable, ("python",))[0]
    assert result.notes == 1
