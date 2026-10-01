"""Validate retained SARIF before accepting a language analysis."""

from pathlib import Path

from ._descriptors import descriptors
from ._notifications import extraction_evidence, require_coverage
from ._rules import result_severity
from ._shapes import object_value, objects, read_object
from ._types import AnalysisResult, CodeQLFailure


def validate_report(
    report: Path, language: str, version: str, owned: frozenset[str]
) -> AnalysisResult:
    document = read_object(report)
    if document.get("version") != "2.1.0":
        raise CodeQLFailure(f"Expected SARIF 2.1.0: {report}")
    runs = objects(document.get("runs"), "SARIF runs")
    if not runs:
        raise CodeQLFailure(f"SARIF contains no analysis runs: {report}")
    counts = {"none": 0, "note": 0, "warning": 0, "error": 0}
    evidence: tuple[set[str], set[str]] = (set(), set())
    for run in runs:
        _validate_run(run, language, version, counts, evidence)
    require_coverage(evidence, owned, language)
    result = AnalysisResult(language, counts["note"], counts["warning"], counts["error"], report)
    if result.warnings or result.errors:
        raise CodeQLFailure(
            f"CodeQL {language}: {result.errors} errors, {result.warnings} warnings, "
            f"{result.notes} notes; report: {report}"
        )
    return result


def _validate_run(
    run: dict[str, object],
    language: str,
    version: str,
    counts: dict[str, int],
    evidence: tuple[set[str], set[str]],
) -> None:
    driver = object_value(object_value(run.get("tool"), "SARIF tool").get("driver"), "SARIF driver")
    _validate_tool(driver, version)
    rules = descriptors(driver.get("rules"), "SARIF rules")
    if not rules:
        raise CodeQLFailure("SARIF contains no analyzed query rules")
    current = extraction_evidence(run, driver, language)
    for aggregate, present in zip(evidence, current, strict=True):
        aggregate.update(present)
    for result in objects(run.get("results"), "SARIF results"):
        counts[result_severity(result, rules)] += 1


def _validate_tool(driver: dict[str, object], version: str) -> None:
    if driver.get("name") != "CodeQL":
        raise CodeQLFailure("SARIF must identify the CodeQL driver")
    reported = [driver[key] for key in ("semanticVersion", "version") if key in driver]
    if not reported or any(value != version for value in reported):
        raise CodeQLFailure(f"SARIF CodeQL version must be {version}")
