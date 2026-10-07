"""Launch: bootstrap documents, the isolated command line, readiness records, concurrency."""

import json
from pathlib import Path

import pytest
from slow_thinker_ii.contracts import json_object
from slow_thinker_ii.engine import Emission
from support.log import RecordingLog

from .owned_process import host_pids, is_running
from .plans import fixture_plan
from .process_fixture import RUN, Targets, context, launched, launcher, settings


async def test_a_launched_host_answers_and_is_stopped_by_close(tmp_path: Path) -> None:
    log, host_settings = RecordingLog(), settings(tmp_path)
    run_directory = host_settings.workspace / RUN
    async with launched(
        fixture_plan("serve"), host_settings, Targets(launcher(tmp_path)), log
    ) as hosts:
        reply = await hosts.activate(context(), "A cat.")
        pids = host_pids(run_directory)
        document = json.loads((run_directory / "w1.node.json").read_text())
    assert reply == (Emission("out", "A cat."),)
    assert document == {
        "format": "slow-thinker.bootstrap/1",
        "component": "fixture@1.0.0",
        "node": {"id": "w1", "name": "Worker 1"},
        "position": "node",
        "config": {"mode": "serve", "outputs": ["out"]},
        "platform": {"llm_base_url": "http://127.0.0.1:9/v1", "mcp_url": "http://127.0.0.1:9/mcp"},
        "limits": {"max_concurrent_invocations": 4},
    }
    (ready,) = log.of("host.ready")
    assert ready.node_id == "w1" and ready.data["position"] == "node"
    assert ready.data["component"] == "fixture@1.0.0" and isinstance(ready.data["startup_ms"], int)
    assert not run_directory.exists() and not is_running(pids["w1.node"])


async def test_hosts_run_isolated_in_their_own_session_with_only_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SLOW_THINKER_TEST_SECRET", "must-not-leak")
    plan, targets = fixture_plan("serve"), Targets(launcher(tmp_path))
    async with launched(plan, settings(tmp_path), targets, RecordingLog()) as hosts:
        reply = await hosts.activate(context(), {"facts": True})
    assert isinstance(reply, tuple)
    facts = json_object(reply[0].payload)
    environment = json_object(facts["environment"])
    assert environment["PATH"] == str(tmp_path)
    assert set(environment) <= {"PATH", "LC_CTYPE", "__CF_USER_TEXT_ENCODING"}
    run_directory = tmp_path / "workspace" / RUN
    assert facts["directory"] == str(run_directory.resolve()) and facts["session_leader"] is True
    assert facts["arguments"] == ["-B", "-I", "-m", "fixture", str(run_directory / "w1.node.json")]


async def test_every_host_of_a_run_starts_at_once(tmp_path: Path) -> None:
    log, host_settings = RecordingLog(), settings(tmp_path)
    plan = fixture_plan("slow", "slow", "slow", embedded="slow")
    async with launched(plan, host_settings, Targets(launcher(tmp_path)), log):
        run_directory = host_settings.workspace / RUN
        starts = [float(path.read_text()) for path in run_directory.glob("*.started")]
    assert len(starts) == 4 and max(starts) - min(starts) < 1.5
    keys = sorted((event.node_id, event.data["position"]) for event in log.of("host.ready"))
    assert keys == [("w1", "node"), ("w2", "node"), ("w3", "node"), ("w3", "output")]
