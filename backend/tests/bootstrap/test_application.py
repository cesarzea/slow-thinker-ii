"""An application built from the example configuration: operator API, ownership and recovery."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slow_thinker_ii.accounting import Scope
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteGraphStore,
    SqliteLedger,
    SqliteRunStore,
)
from slow_thinker_ii.application import RunRecord
from slow_thinker_ii.bootstrap import (
    AppOverrides,
    ServerConfiguration,
    create_app,
    load_configuration,
)
from slow_thinker_ii.contracts import JsonValue
from support.examples import FLASH, J1, LUNA, graph_document

from .configurations import (
    TOKEN,
    DevelopmentTargets,
    local,
    package_declarations,
    simulated,
    written,
)

AT = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)
OPERATOR = {"Authorization": f"Bearer {TOKEN}"}
OVERRIDES = AppOverrides(components=package_declarations(), launch_targets=DevelopmentTargets())


def configured(directory: Path) -> ServerConfiguration:
    """The example served by the simulated provider, with its state under `directory`."""
    return load_configuration(written(directory, simulated(local(directory))))


def client_of(configuration: ServerConfiguration) -> TestClient:
    environment = {"SLOW_THINKER_OPERATOR_TOKEN": TOKEN}
    app = create_app(configuration, environment, OVERRIDES)
    return TestClient(app, base_url="http://127.0.0.1:8000")


def activate(client: TestClient, graph_id: str, change: int) -> tuple[int, JsonValue]:
    """Activates a change of the working copy as the graph's next version: status and body."""
    body = {"change": change}
    reply = client.post(f"/api/v2/graphs/{graph_id}/versions", json=body, headers=OPERATOR)
    answer: JsonValue = reply.json()
    return reply.status_code, answer


def test_the_example_configuration_serves_the_operator_api(tmp_path: Path) -> None:
    with client_of(configured(tmp_path)) as client:
        assert client.get("/api/v2/catalog").status_code == 401
        catalog = client.get("/api/v2/catalog", headers=OPERATOR).json()
        components = [(item["type"], item["origin"]) for item in catalog["components"]]
        assert components == [
            ("trigger", "platform"),
            ("output", "platform"),
            ("llm-call", "package"),
            ("router", "package"),
        ]
        assert [entry["id"] for entry in catalog["llms"]] == [LUNA, FLASH]
        document = graph_document(J1)
        created = client.post("/api/v2/graphs", json={"document": document}, headers=OPERATOR)
        identity = {"id": "funny-story", "branch": "main", "change": 1}
        assert (created.status_code, created.json()) == (201, identity)
        activated = {"version": 1, "branch": "main", "change": 1}
        assert activate(client, "funny-story", 1) == (201, activated)
        version = client.get("/api/v2/graphs/funny-story/versions/1", headers=OPERATOR).json()
        assert (version["change"], version["document"]) == (1, document)
        usage = client.get("/api/v2/usage", headers=OPERATOR).json()
        assert (usage["day"]["limit_usd"], usage["month"]["limit_usd"]) == (
            "1.000000000",
            "5.000000000",
        )
    assert (tmp_path / "runs").is_dir()


def started_twice(configuration: ServerConfiguration) -> None:
    """Starts a second application on the database while a first one serves it."""
    with client_of(configuration), client_of(configuration):
        pass


def test_one_backend_owns_the_database(tmp_path: Path) -> None:
    configuration = configured(tmp_path)
    with pytest.raises(RuntimeError, match="Another backend owns"):
        started_twice(configuration)
    with client_of(configuration) as client:
        assert client.get("/api/v2/graphs", headers=OPERATOR).json() == {"graphs": []}


def test_startup_finishes_interrupted_runs_and_settles_their_reservations(tmp_path: Path) -> None:
    configuration = configured(tmp_path)
    database = SqliteDatabase(configuration.database)
    database.initialize()
    graphs = SqliteGraphStore(database)
    graphs.create("funny-story", "Funny story", graph_document(J1), AT)
    graphs.add_version("funny-story", 1, None, AT)
    record = RunRecord("r1", "funny-story", 1, 1, "starting", None, "", "Hi", AT, None, None)
    SqliteRunStore(database).create(record)
    scopes = [Scope("run", "r1", 1_000, 0), Scope("day", "2026-10-05", 10_000, 0)]
    assert SqliteLedger(database).reserve("c1", "r1", scopes, 400, AT) is None
    with client_of(configuration) as client:
        run = client.get("/api/v2/runs/r1", headers=OPERATOR).json()
        events = client.get("/api/v2/runs/r1/events", headers=OPERATOR).json()
    assert (run["status"], run["reason"]) == ("failed", "interrupted")
    assert run["detail"] == "The backend restarted before the run finished."
    assert [event["kind"] for event in events["events"]] == ["run.finished"]
    assert events["finished"] is True
    with database.transaction() as connection:
        row = connection.execute("SELECT charge, estimated FROM ledger").fetchone()
    assert tuple(row) == (400, 1)


def test_shutdown_cancels_active_runs_and_closes_their_hosts(tmp_path: Path) -> None:
    configuration = configured(tmp_path)
    with client_of(configuration) as client:
        document = {"document": graph_document(J1)}
        assert client.post("/api/v2/graphs", json=document, headers=OPERATOR).status_code == 201
        assert activate(client, "funny-story", 1)[0] == 201
        start = {"graph_id": "funny-story", "version": 1}
        run_id = client.post("/api/v2/runs", json=start, headers=OPERATOR).json()["run_id"]
    record = SqliteRunStore(SqliteDatabase(configuration.database)).run(run_id)
    assert record is not None and record.status == "cancelled"
    assert record.detail == "The platform shut down before the run finished."
    assert not (tmp_path / "runs" / run_id).exists()
