"""Entry-point checks use ordinary public bootstrap and suppress only stdio serving."""

import runpy
import sys
from pathlib import Path

import pytest
from slow_thinker_host import HostedComponent, JsonObject, Operation, encode_json


def invoke_entry(
    module: str,
    config: JsonObject,
    operations: tuple[Operation, ...],
    clients: JsonObject,
    directory: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    path = directory / "bootstrap.json"
    write_bootstrap(path, config, operations, clients)
    observed: list[str] = []

    def serve(host: HostedComponent, name: str, version: str) -> None:
        assert host.operations() == operations and version == "0.1.0"
        observed.append(name)

    monkeypatch.setattr("slow_thinker_host.run_stdio", serve)
    monkeypatch.setattr(sys, "argv", [module, str(path)])
    runpy.run_module(module, run_name="__main__")
    return observed


def invalid_argv(module: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [module])
    with pytest.raises(ValueError, match="bootstrap path"):
        runpy.run_module(module, run_name="__main__")


def write_bootstrap(
    path: Path, config: JsonObject, operations: tuple[Operation, ...], clients: JsonObject
) -> None:
    path.write_text(
        encode_json(
            {
                "config": config,
                "operations": [
                    {
                        "name": item.name,
                        "input_schema": item.input_schema,
                        "output_schema": item.output_schema,
                    }
                    for item in operations
                ],
                "clients": clients,
            }
        )
    )
