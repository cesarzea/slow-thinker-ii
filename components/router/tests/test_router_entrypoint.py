"""`python -m slow_thinker_router` loads its script before readiness or stops in English."""

import json
import runpy
import sys
from pathlib import Path

import pytest
from router_fakes import bootstrap_document
from slow_thinker_host import Bootstrap, JsonObject, NodeHandler, OutputHandler
from slow_thinker_router import Router, main


def write(tmp_path: Path, document: JsonObject) -> str:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize("position", ["node", "output"])
def test_main_serves_the_router_for_both_operations(tmp_path: Path, position: str) -> None:
    served: list[tuple[Bootstrap, NodeHandler, OutputHandler]] = []

    def serve(bootstrap: Bootstrap, *, node: NodeHandler, output: OutputHandler) -> None:
        served.append((bootstrap, node, output))

    main([write(tmp_path, bootstrap_document(position))], serve=serve)
    ((bootstrap, node, output),) = served
    assert bootstrap.position == position
    assert isinstance(node, Router) and node is output


@pytest.mark.parametrize(
    ("document", "reason"),
    [
        (
            bootstrap_document(script="def route(received, node_input)\n    pass\n"),
            "The script has a syntax error at line 1: expected ':'",
        ),
        (bootstrap_document(script="x = 1\n"), "does not define a function named route"),
        ({**bootstrap_document(), "component": "router@2.0.0"}, "not router@1.0.0"),
        ({**bootstrap_document(), "config": {"outputs": []}}, "configuration is invalid"),
    ],
)
def test_startup_failures_print_why_and_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], document: JsonObject, reason: str
) -> None:
    with pytest.raises(SystemExit) as stopped:
        main([write(tmp_path, document)])
    assert stopped.value.code == 1
    error = capsys.readouterr().err
    assert error.startswith("Router startup failed: ") and reason in error


@pytest.mark.parametrize("arguments", [[], ["a.json", "b.json"], ["/missing/bootstrap.json"]])
def test_a_missing_bootstrap_stops_the_host(
    capsys: pytest.CaptureFixture[str], arguments: list[str]
) -> None:
    with pytest.raises(SystemExit) as stopped:
        main(arguments)
    assert stopped.value.code == 1
    assert capsys.readouterr().err.startswith("Router startup failed: ")


def test_module_entry_point_reads_its_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["slow_thinker_router"])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("slow_thinker_router", run_name="__main__")
    assert stopped.value.code == 1
