"""All three independent package entrypoints bind reviewed operations before serving."""

import runpy
import sys
from pathlib import Path

import pytest
from slow_thinker_bounded_flow import BoundedFlowHost
from slow_thinker_host import HostedComponent, JsonObject, Operation, encode_json
from slow_thinker_redirector import RedirectorHost
from slow_thinker_routed_call import RoutedCallHost

CONFIGS: dict[str, JsonObject] = {
    "redirector": {
        "outputs": ["accept", "revise"],
        "selector": "example_grounded_review:choose",
        "input_schema": {},
    },
    "bounded_flow": {"entry": "only", "routes": {"only": {"done": None}}, "max_activations": 1},
    "routed_call": {
        "input_schema": {"type": "object"},
        "worker_operation": "work",
        "worker_output_schema": {"type": "object"},
        "router_input_pointer": "",
        "outputs": ["done"],
    },
}


def operation(name: str, config: JsonObject) -> Operation:
    if name == "redirector":
        return RedirectorHost.describe(config)[0]
    if name == "bounded_flow":
        return BoundedFlowHost.describe(config)[0]
    return RoutedCallHost.describe(config)[0]


def bootstrap(name: str) -> JsonObject:
    configured = CONFIGS[name]
    op = operation(name, configured)
    clients: JsonObject = {}
    if name == "routed_call":
        clients["mcp"] = {
            "url": "http://127.0.0.1:8000/mcp",
            "timeout_seconds": 3,
            "close_seconds": 1,
            "resources": {"worker": {"work": "worker"}, "router": {"route": "router"}},
        }
    return {
        "config": configured,
        "operations": [
            {"name": op.name, "input_schema": op.input_schema, "output_schema": op.output_schema}
        ],
        "clients": clients,
    }


@pytest.mark.parametrize("name", CONFIGS)
def test_missing_bootstrap_is_rejected(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [name])
    with pytest.raises(ValueError, match="one trusted bootstrap"):
        runpy.run_module("slow_thinker_" + name, run_name="__main__")


@pytest.mark.parametrize("name", CONFIGS)
@pytest.mark.parametrize("valid", [True, False])
def test_entrypoint_validates_then_serves(
    name: str, valid: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = bootstrap(name)
    if not valid:
        record["operations"] = []
    path = tmp_path / "bootstrap.json"
    path.write_text(encode_json(record))
    monkeypatch.setattr(sys, "argv", [name, str(path)])
    served: list[str] = []

    def serve(component: HostedComponent, label: str, version: str) -> None:
        assert version == "0.1.0" and len(component.operations()) == 1
        served.append(label)

    monkeypatch.setattr("slow_thinker_host.run_stdio", serve)
    if valid:
        runpy.run_module("slow_thinker_" + name, run_name="__main__")
        assert served == [name.replace("_", "-")]
    else:
        with pytest.raises(ValueError, match="one operation"):
            runpy.run_module("slow_thinker_" + name, run_name="__main__")
        assert not served
