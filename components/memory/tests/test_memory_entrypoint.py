"""`python -m slow_thinker_memory` checks its bootstrap before serving or stops in English."""

import json
import runpy
import sys
from pathlib import Path

import pytest
from memory_fakes import bootstrap_document
from slow_thinker_host import Bootstrap, JsonObject, MemoryHandler
from slow_thinker_memory import Memory, main


def write(tmp_path: Path, document: JsonObject) -> str:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


def test_main_serves_a_stateful_memory(tmp_path: Path) -> None:
    served: list[tuple[Bootstrap, MemoryHandler, bool]] = []

    def serve(bootstrap: Bootstrap, *, memory: MemoryHandler, stateful: bool) -> None:
        served.append((bootstrap, memory, stateful))

    main([write(tmp_path, bootstrap_document())], serve=serve)
    ((bootstrap, memory, stateful),) = served
    assert (bootstrap.position, stateful) == ("memory", True)
    assert isinstance(memory, Memory)


@pytest.mark.parametrize(
    ("document", "reason"),
    [
        (bootstrap_document("node"), "cannot be placed at position node"),
        (bootstrap_document(max_exchanges=0), "configuration"),
        (bootstrap_document(max_exchanges=True), "configuration"),
        ({**bootstrap_document(), "component": "memory@2.0.0"}, "not memory@1.0.0"),
    ],
)
def test_startup_failures_print_why_and_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], document: JsonObject, reason: str
) -> None:
    with pytest.raises(SystemExit) as stopped:
        main([write(tmp_path, document)])
    assert stopped.value.code == 1
    error = capsys.readouterr().err
    assert error.startswith("Memory startup failed: ") and reason in error


@pytest.mark.parametrize("arguments", [[], ["a.json", "b.json"], ["/missing/bootstrap.json"]])
def test_a_missing_bootstrap_stops_the_host(
    capsys: pytest.CaptureFixture[str], arguments: list[str]
) -> None:
    with pytest.raises(SystemExit) as stopped:
        main(arguments)
    assert stopped.value.code == 1
    assert capsys.readouterr().err.startswith("Memory startup failed: ")


def test_module_entry_point_reads_its_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["slow_thinker_memory"])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("slow_thinker_memory", run_name="__main__")
    assert stopped.value.code == 1
