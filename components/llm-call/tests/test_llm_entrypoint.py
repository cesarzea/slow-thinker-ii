"""`python -m slow_thinker_llm_call` checks its bootstrap before serving and fails in English."""

import json
import runpy
import sys
from pathlib import Path

import pytest
from llm_call_fakes import config
from slow_thinker_host import Bootstrap, JsonObject, JsonValue, NodeHandler
from slow_thinker_llm_call import LLMCall, main


def bootstrap_document(**changes: JsonValue) -> JsonObject:
    document: JsonObject = {
        "format": "slow-thinker.bootstrap/1",
        "component": "llm-call@1.0.0",
        "node": {"id": "proposer", "name": "Proposer"},
        "position": "node",
        "config": config(),
        "platform": {
            "llm_base_url": "http://127.0.0.1:8000/v1",
            "mcp_url": "http://127.0.0.1:8000/mcp",
        },
        "limits": {"max_concurrent_invocations": 4},
    }
    return {**document, **changes}


def write(tmp_path: Path, document: JsonObject) -> str:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


def test_main_serves_the_configured_node(tmp_path: Path) -> None:
    served: list[tuple[Bootstrap, NodeHandler]] = []

    def serve(bootstrap: Bootstrap, *, node: NodeHandler) -> None:
        served.append((bootstrap, node))

    main([write(tmp_path, bootstrap_document())], serve=serve)
    ((bootstrap, node),) = served
    assert bootstrap.node_name == "Proposer"
    assert isinstance(node, LLMCall) and node.config.llm == "openai/gpt-6-luna"


@pytest.mark.parametrize(
    ("document", "reason"),
    [
        (bootstrap_document(component="router@1.0.0"), "names router@1.0.0, not llm-call@1.0.0"),
        (bootstrap_document(position="output"), "cannot be placed at position output"),
        (bootstrap_document(config=config(model=None)), "No LLM is selected"),
        (bootstrap_document(config=config(prompt="")), "configuration is invalid"),
        (bootstrap_document(format="other"), "Unsupported bootstrap format"),
    ],
)
def test_invalid_bootstraps_stop_the_host_before_readiness(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], document: JsonObject, reason: str
) -> None:
    with pytest.raises(SystemExit) as stopped:
        main([write(tmp_path, document)])
    assert stopped.value.code == 1
    error = capsys.readouterr().err
    assert error.startswith("LLM Call startup failed: ") and reason in error


@pytest.mark.parametrize("arguments", [[], ["a.json", "b.json"], ["/missing/bootstrap.json"]])
def test_a_missing_bootstrap_stops_the_host(
    capsys: pytest.CaptureFixture[str], arguments: list[str]
) -> None:
    with pytest.raises(SystemExit) as stopped:
        main(arguments)
    assert stopped.value.code == 1
    assert capsys.readouterr().err.startswith("LLM Call startup failed: ")


def test_module_entry_point_reads_its_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["slow_thinker_llm_call"])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("slow_thinker_llm_call", run_name="__main__")
    assert stopped.value.code == 1
