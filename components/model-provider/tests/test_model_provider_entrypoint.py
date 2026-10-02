"""Startup consumes only the dedicated secret and serves the reviewed installed contract."""

import os
import runpy
import sys
from pathlib import Path

import pytest
import slow_thinker_host
from model_provider_fixture import SECRET, config, record
from slow_thinker_host import HostedComponent, JsonObject, encode_json
from slow_thinker_model_provider import effective_operation


def bootstrap() -> JsonObject:
    operation = effective_operation(config())
    return {
        "config": record(),
        "operations": [
            {
                "name": operation.name,
                "input_schema": operation.input_schema,
                "output_schema": operation.output_schema,
            }
        ],
        "clients": {
            "provider": {
                "base_url": "http://127.0.0.1:123/v1",
                "timeout_seconds": 5,
                "close_seconds": 1,
                "max_response_bytes": 524_288,
            }
        },
    }


@pytest.mark.parametrize("fault", ["none", "binding", "credential", "operation", "extra_client"])
def test_entrypoint_checks_readiness_without_native_io(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    value = bootstrap()
    if fault == "binding":
        value["clients"] = {}
    elif fault == "operation":
        value["operations"] = [{"name": "other", "input_schema": {}, "output_schema": {}}]
    elif fault == "extra_client":
        value["clients"] = {"provider": {}, "other": {}}
    path = tmp_path / "provider.json"
    path.write_text(encode_json(value))
    monkeypatch.setattr(sys, "argv", ["resource", str(path)])
    monkeypatch.setenv("SLOW_THINKER_SECRET_MODEL", "" if fault == "credential" else SECRET)
    served: list[str] = []

    def serve(component: HostedComponent, name: str, version: str) -> None:
        assert component.operations()[0].name == "complete" and version == "0.1.0"
        assert "SLOW_THINKER_SECRET_MODEL" not in os.environ
        served.append(name)

    monkeypatch.setattr(slow_thinker_host, "run_stdio", serve)
    if fault == "none":
        runpy.run_module("slow_thinker_model_provider", run_name="__main__")
        assert served == ["model-provider"]
    else:
        with pytest.raises(ValueError):
            runpy.run_module("slow_thinker_model_provider", run_name="__main__")
        assert not served


def test_entrypoint_requires_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["resource"])
    with pytest.raises(ValueError, match="one trusted bootstrap"):
        runpy.run_module("slow_thinker_model_provider", run_name="__main__")
