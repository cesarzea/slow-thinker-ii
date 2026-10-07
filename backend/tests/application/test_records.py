"""JSON shapes of the records, views and pages that adapters serve."""

from datetime import UTC, datetime, timedelta, timezone
from types import MappingProxyType

import pytest
from slow_thinker_ii.application import (
    BranchSummary,
    ChangeRecord,
    ChangeSummary,
    EventPage,
    GraphRecord,
    GraphSummary,
    RecordedEvent,
    RunRecord,
    RunView,
    VersionRecord,
    VersionSummary,
    rfc3339,
)
from slow_thinker_ii.contracts import JsonObject

AT = datetime(2026, 10, 5, 12, 0, 1, 123_456, tzinfo=UTC)
STAMP = "2026-10-05T12:00:01.123Z"


def test_times_are_utc_with_milliseconds() -> None:
    assert rfc3339(AT) == STAMP
    assert rfc3339(AT.astimezone(timezone(timedelta(hours=2)))) == STAMP
    with pytest.raises(ValueError, match="timezone-aware"):
        rfc3339(datetime(2026, 10, 5))


def test_run_records_serialize_as_run_summaries() -> None:
    running = RunRecord("r1", "funny-story", 1, 1, "running", None, "", "Hi", AT, None, None)
    assert running.to_json() == {
        "run_id": "r1",
        "graph_id": "funny-story",
        "version": 1,
        "change": 1,
        "status": "running",
        "reason": None,
        "detail": "",
        "created_at": STAMP,
        "ended_at": None,
        "totals": None,
    }
    totals: JsonObject = {"activations": 3}
    ended = RunRecord("r1", "funny-story", 1, 1, "completed", None, "", "Hi", AT, AT, totals)
    document = ended.to_json()
    assert (document["ended_at"], document["totals"]) == (STAMP, totals)


def test_events_views_and_pages_follow_the_contracts() -> None:
    data: JsonObject = {"name": "Funny story", "message_id": "m2", "payload": "Hi"}
    event = RecordedEvent("r1", 7, AT, 1500, "run.result", "observed", "result", "a3", data)
    envelope = event.to_json()
    assert envelope == {
        "run_id": "r1",
        "seq": 7,
        "at": STAMP,
        "elapsed_ms": 1500,
        "kind": "run.result",
        "evidence": "observed",
        "node_id": "result",
        "activation_id": "a3",
        "data": data,
    }
    assert EventPage((event,), 7, True).to_json() == {
        "events": [envelope],
        "last_seq": 7,
        "finished": True,
    }
    summary = RunRecord("r1", "funny-story", 1, 1, "completed", None, "", "Hi", AT, AT, {})
    result: JsonObject = {"node_id": "result", "name": "Funny story", "payload": "Hi", "at": STAMP}
    counts = MappingProxyType({"result": 1})
    view = RunView(summary, (result,), counts, MappingProxyType({"a.out -> b.in": 2}))
    document = view.to_json()
    assert document["results"] == [result]
    assert document["activations_by_node"] == {"result": 1}
    assert document["messages_by_connection"] == {"a.out -> b.in": 2}
    assert document["run_id"] == "r1"


def test_graph_records_serialize_as_the_operator_api() -> None:
    versions = (VersionSummary(1, "main", None, 2, "Funny story", AT),)
    branches = (BranchSummary("main", AT, None, None, 3, 1),)
    assert GraphRecord("funny-story", "Funny story", 1, 3, branches, versions).to_json() == {
        "id": "funny-story",
        "name": "Funny story",
        "active_version": 1,
        "latest_change": 3,
        "branches": [
            {
                "name": "main",
                "created_at": STAMP,
                "from_version": None,
                "from_change": None,
                "latest_change": 3,
                "head_version": 1,
            }
        ],
        "versions": [
            {
                "version": 1,
                "branch": "main",
                "parent": None,
                "change": 2,
                "name": "Funny story",
                "created_at": STAMP,
            }
        ],
    }


def test_version_records_serialize_as_the_operator_api() -> None:
    document: JsonObject = {"format": "slow-thinker.graph/1"}
    assert VersionRecord("funny-story", 1, "main", None, 2, AT, document).to_json() == {
        "graph_id": "funny-story",
        "version": 1,
        "branch": "main",
        "parent": None,
        "change": 2,
        "created_at": STAMP,
        "document": document,
    }


def test_summaries_and_changes_serialize_as_the_operator_api() -> None:
    summary = GraphSummary("funny-story", "Funny story", None, 1, AT)
    assert summary.to_json()["active_version"] is None
    document: JsonObject = {"format": "slow-thinker.graph/1"}
    assert ChangeSummary(3, "main", AT, "Funny story", None).to_json() == {
        "change": 3,
        "branch": "main",
        "at": STAMP,
        "name": "Funny story",
        "version": None,
    }
    assert ChangeRecord("funny-story", 2, "main", AT, document, 1).to_json() == {
        "graph_id": "funny-story",
        "change": 2,
        "branch": "main",
        "at": STAMP,
        "document": document,
        "version": 1,
    }
