"""The resource consumes a dedicated launch secret before serving its declared contract."""

import os
import runpy
import sys
from pathlib import Path

import pytest
import slow_thinker_host
from slow_thinker_host import HostedComponent, encode_json
from slow_thinker_openai_model import ModelConfig, effective_operation
from support.provider_process import SECRET, bootstrap_record


def test_resource_entrypoint_requires_a_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["resource"])
    with pytest.raises(ValueError, match="one trusted bootstrap"):
        runpy.run_module("slow_thinker_openai_model", run_name="__main__")


@pytest.mark.parametrize("fault", ["none", "binding", "credential", "operation"])
def test_resource_startup_consumes_secret_and_checks_readiness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    config = ModelConfig("bound-model", "gpt-6-luna", 8, 32)
    record = bootstrap_record(config, effective_operation(config), 123)
    if fault == "binding":
        record["clients"] = {}
    elif fault == "operation":
        record["operations"] = [{"name": "other", "input_schema": {}, "output_schema": {}}]
    path = tmp_path / "bootstrap.json"
    path.write_text(encode_json(record))
    monkeypatch.setattr(sys, "argv", ["resource", str(path)])
    monkeypatch.setenv("SLOW_THINKER_SECRET_OPENAI", "" if fault == "credential" else SECRET)
    served: list[str] = []

    def serve(component: HostedComponent, name: str, version: str) -> None:
        assert component.operations()[0].name == "complete" and version == "0.1.0.dev1"
        assert "SLOW_THINKER_SECRET_OPENAI" not in os.environ
        served.append(name)

    monkeypatch.setattr(slow_thinker_host, "run_stdio", serve)
    if fault == "none":
        runpy.run_module("slow_thinker_openai_model", run_name="__main__")
        assert served == ["openai-model"]
    else:
        with pytest.raises(ValueError) as caught:
            runpy.run_module("slow_thinker_openai_model", run_name="__main__")
        assert not served and SECRET not in str(caught.value)
