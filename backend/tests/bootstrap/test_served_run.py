"""A journey through the served application: real component hosts and the simulated provider.

Hosts call the platform back on the configured public URL, so the application is served on a
loopback port of its own for this test.
"""

import signal
import socket
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI
from slow_thinker_ii.bootstrap import AppOverrides, create_app, load_configuration
from slow_thinker_ii.contracts import JsonObject, value_at_pointer
from support.examples import J1, graph_document

from .configurations import (
    TOKEN,
    DevelopmentTargets,
    local,
    package_declarations,
    simulated,
    written,
)

TERMINAL = ("completed", "stopped", "failed", "cancelled")


@contextmanager
def served(app_for: Callable[[str], FastAPI]) -> Generator[httpx.Client]:
    """The application of `app_for(origin)`, served on a free loopback port until the block ends."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    origin = f"http://127.0.0.1:{listener.getsockname()[1]}"
    config = uvicorn.Config(app_for(origin), log_level="warning", ws="none", lifespan="on")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]})
    thread.start()
    try:
        _wait(lambda: server.started or not thread.is_alive(), 10)
        assert server.started, "The application did not start"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        with httpx.Client(base_url=origin, headers=headers, timeout=10) as client:
            yield client
    finally:
        server.handle_exit(signal.SIGTERM, None)
        thread.join(15)
        listener.close()


def finished(client: httpx.Client, run_id: str) -> JsonObject:
    """The run once terminal; polls its summary for at most 30 seconds."""
    seen: list[JsonObject] = []

    def terminal() -> bool:
        seen.append(client.get(f"/api/v2/runs/{run_id}").json())
        return seen[-1]["status"] in TERMINAL

    _wait(terminal, 30)
    return seen[-1]


def _wait(condition: Callable[[], bool], seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while not condition():
        assert time.monotonic() < deadline, "The awaited condition did not hold in time"
        time.sleep(0.05)


def test_a_journey_runs_through_hosts_that_call_the_platform_back(tmp_path: Path) -> None:
    def app_for(origin: str) -> FastAPI:
        document = simulated(local(tmp_path, origin))
        overrides = AppOverrides(package_declarations(), DevelopmentTargets())
        configuration = load_configuration(written(tmp_path, document))
        return create_app(configuration, {"SLOW_THINKER_OPERATOR_TOKEN": TOKEN}, overrides)

    with served(app_for) as client:
        story = graph_document(J1)
        assert client.post("/api/v2/graphs", json={"document": story}).status_code == 201
        activated = client.post("/api/v2/graphs/funny-story/versions", json={"change": 1})
        assert activated.json() == {"version": 1, "branch": "main", "change": 1}
        started = client.post("/api/v2/runs", json={"graph_id": "funny-story", "version": 1})
        run_id = started.json()["run_id"]
        run = finished(client, run_id)
        events = client.get(f"/api/v2/runs/{run_id}/events").json()["events"]
        usage = client.get("/api/v2/usage").json()
    assert (run["status"], run["reason"]) == ("completed", None), run["detail"]
    results = run["results"]
    assert isinstance(results, list) and len(results) == 1
    payload = value_at_pointer(results, (0, "payload"))
    assert payload == "Simulated reply to: A cat tried to learn to fly."
    kinds = [event["kind"] for event in events]
    assert kinds[0] == "run.started" and kinds[-1] == "run.finished"
    assert {"host.ready", "llm.called", "run.result"} <= set(kinds)
    assert usage["day"]["used_usd"] != "0.000000000"
