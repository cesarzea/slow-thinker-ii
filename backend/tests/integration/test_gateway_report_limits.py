"""Optional reported evidence is bounded and recording failures close authority."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import RecordingError
from slow_thinker_ii.contracts import encode_json
from support.mcp_gateway import mcp_case

REPORT = '{"kind":"state","schema_version":"1","value":null}'


def test_report_size_and_count_limits_are_recorded(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    with pytest.raises(ValueError, match="report_size_limit"):
        case.service.report(case.native.parent.token, '"' + "x" * 524_288 + '"')
    for _ in range(100):
        case.service.report(case.native.parent.token, REPORT)
    with pytest.raises(ValueError, match="report_count_limit"):
        case.service.report(case.native.parent.token, REPORT)
    with case.native.run.store.begin() as transaction:
        events = transaction.events("run")
        assert sum(event.event == "component.reported" for event in events) == 100
        assert sum(event.event == "call.rejected" for event in events) == 2


@pytest.mark.parametrize("timestamp", [True, None, "yesterday"])
def test_report_timestamp_rejects_nonfinite_or_non_numeric(
    tmp_path: Path, timestamp: str | bool | None
) -> None:
    case = mcp_case(tmp_path)
    report = encode_json(
        {
            "kind": "state",
            "schema_version": "1",
            "value": None,
            "source_occurred_at": timestamp,
        }
    )
    with pytest.raises(ValueError, match="invalid_report_timestamp"):
        case.service.report(case.native.parent.token, report)


def test_report_recording_failure_revokes_authority(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    with case.native.run.database.transaction() as db:
        db.execute(
            "CREATE TRIGGER fail_report BEFORE INSERT ON run_events "
            "WHEN NEW.event='component.reported' BEGIN SELECT RAISE(ABORT,'disk'); END"
        )
    with pytest.raises(RecordingError):
        case.service.report(case.native.parent.token, REPORT)
    with pytest.raises(AccessDenied):
        case.service.tools(case.native.parent.token)
    with case.native.run.store.begin() as transaction:
        assert not any(event.event == "component.reported" for event in transaction.events("run"))


def test_closed_run_rejects_reports_without_fabricated_evidence(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    with case.native.run.store.begin() as transaction:
        transaction.stop("run", "operator_stop")
    with pytest.raises(AccessDenied, match="run_closed"):
        case.service.report(case.native.parent.token, REPORT)


def test_repeated_denials_have_a_bounded_durable_tail(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    for _ in range(101):
        case.service.reject(case.native.parent.token, "guessed", "operation_denied")
    with case.native.run.store.begin() as transaction:
        assert sum(e.event == "call.rejected" for e in transaction.events("run")) == 99
        assert transaction.run("run").reason == "gateway_rejection_limit"
    with pytest.raises(AccessDenied):
        case.service.tools(case.native.parent.token)
