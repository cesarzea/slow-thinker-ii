"""Extraction descriptors and source locations must prove complete analysis."""

from typing import cast

import pytest

from tooling.quality.codeql import CodeQLFailure, verify_codeql

from .conftest import Gate, write_file
from .paths import DRIVER, EXPECTED, EXTRACTED, INVOCATION, LOCATION, NOTIFICATIONS, RUN
from .reports import FieldPath, JsonObject, field, remove, replace, report


@pytest.mark.parametrize(
    "path,value",
    [
        ((*EXPECTED, "level"), "warning"),
        ((*EXPECTED, "level"), "error"),
        ((*EXPECTED, "level"), "unknown"),
        ((*EXPECTED, "level"), None),
        ((*EXPECTED, "descriptor"), []),
        ((*EXPECTED, "descriptor"), {}),
        ((*EXPECTED, "descriptor", "id"), "unknown"),
        ((*EXPECTED, "descriptor", "index"), 1),
        ((*EXPECTED, "descriptor", "index"), True),
        ((*EXPECTED, "descriptor", "index"), 99),
        ((*EXPECTED, "locations"), []),
        ((*EXPECTED, "locations"), {}),
        ((*EXPECTED, "locations", 0, "physicalLocation"), None),
        (LOCATION, []),
        ((*LOCATION, "index"), -1),
        ((*LOCATION, "index"), True),
        ((*LOCATION, "index"), 99),
        ((*RUN, "artifacts", 0, "location"), []),
        ((*RUN, "artifacts", 0, "location", "uri"), None),
        ((*LOCATION, "uri"), "different.py"),
        ((*DRIVER, "notifications"), [{"id": "same"}, {"id": "same"}]),
    ],
)
def test_invalid_extraction_evidence_fails(gate: Gate, path: FieldPath, value: object) -> None:
    replace(gate.cli.python_report(), path, value)
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))
    assert gate.scratch() == ()


@pytest.mark.parametrize(
    "uri",
    [
        "",
        "/source.py",
        "../source.py",
        "https://example/source.py",
        "//host/source.py",
        "source.py?q=x",
        "source.py#fragment",
        "folder\\source.py",
        "%FF.py",
    ],
)
def test_invalid_source_relative_uris_fail(gate: Gate, uri: str) -> None:
    replace(gate.cli.python_report(), (*LOCATION, "uri"), uri)
    with pytest.raises(CodeQLFailure):
        verify_codeql(gate.root, gate.executable, ("python",))


@pytest.mark.parametrize("missing", [0, 1])
def test_baseline_and_successful_extraction_are_independently_required(
    gate: Gate, missing: int
) -> None:
    remove(gate.cli.python_report(), (*NOTIFICATIONS, missing))
    with pytest.raises(CodeQLFailure, match="Incomplete python"):
        verify_codeql(gate.root, gate.executable, ("python",))


def test_untracked_source_cannot_be_omitted_from_extraction(gate: Gate) -> None:
    write_file(gate.root, "missing.py", "value = 'must be analyzed'\n")
    with pytest.raises(CodeQLFailure, match="missing.py"):
        verify_codeql(gate.root, gate.executable, ("python",))


@pytest.mark.parametrize("removed", ["uri", "index"])
def test_artifact_uri_or_index_can_resolve_source(gate: Gate, removed: str) -> None:
    remove(gate.cli.python_report(), (*LOCATION, removed))
    results = verify_codeql(gate.root, gate.executable, ("python",))
    assert results[0].notes == 1


def test_percent_decoded_paths_and_inline_notification_ids(gate: Gate) -> None:
    document = gate.cli.python_report()
    replace(document, (*LOCATION, "uri"), "source%2Epy")
    remove(document, (*DRIVER, "notifications"))
    remove(document, (*EXPECTED, "descriptor", "index"))
    remove(document, (*EXTRACTED, "descriptor", "index"))
    results = verify_codeql(gate.root, gate.executable, ("python",))
    assert results[0].notes == 1


@pytest.mark.parametrize(
    "descriptor", [{}, {"id": "py/baseline/expected-extracted-files", "index": 0}]
)
def test_unresolvable_inline_notification_fails(gate: Gate, descriptor: JsonObject) -> None:
    remove(gate.cli.python_report(), (*DRIVER, "notifications"))
    replace(gate.cli.python_report(), (*EXPECTED, "descriptor"), descriptor)
    with pytest.raises(CodeQLFailure, match="cannot be resolved"):
        verify_codeql(gate.root, gate.executable, ("python",))


def test_configuration_notifications_and_auxiliary_notes_are_supported(gate: Gate) -> None:
    document = gate.cli.python_report()
    notifications = cast(list[object], field(document, NOTIFICATIONS))
    replace(
        document,
        (*INVOCATION, "toolConfigurationNotifications"),
        [*notifications, {"level": "note"}],
    )
    remove(document, NOTIFICATIONS)
    result = verify_codeql(gate.root, gate.executable, ("python",))[0]
    assert result.notes == 1


def test_multiple_runs_aggregate_extraction_evidence(gate: Gate) -> None:
    write_file(gate.root, "additional.py", "value = 2\n")
    additional = report("python", ("additional.py",))
    runs = cast(list[object], field(gate.cli.python_report(), ("runs",)))
    runs.append(field(additional, RUN))
    results = verify_codeql(gate.root, gate.executable, ("python",))
    assert results[0].notes == 2
