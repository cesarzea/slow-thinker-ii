"""Graph startup seals host bootstraps and rejects incomplete billing before starting work."""

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.catalog import InstalledPlan
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.adapters.process import (
    HostBinding,
    HostLimits,
    InstalledGraphEnvironment,
    ProcessFleet,
)
from slow_thinker_ii.application import OperationPort
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.installations import new_catalog
from support.installed_graphs import compiler, types
from support.native_model import profile
from support.sequence_plans import graph_value


def bindings() -> dict[str, HostBinding]:
    return {
        "proposer": HostBinding(),
        "sequence": HostBinding(),
        "model": HostBinding(pricing=(("complete", OpenAIPricePolicy(profile())),)),
    }


async def test_environment_freezes_config_and_is_single_use(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    installed = compiler(tmp_path, types(tmp_path)).compile(
        encode_json(graph_value("single-agent")), '{"problem":"p"}'
    )

    @asynccontextmanager
    async def controlled(
        fleet: ProcessFleet, deadline: float
    ) -> AsyncGenerator[Mapping[OperationAddress, OperationPort]]:
        assert deadline > 0 and "not_started" in fleet.report()
        yield {}

    monkeypatch.setattr(ProcessFleet, "open", controlled)
    workspace = tmp_path / "run"
    environment = InstalledGraphEnvironment(
        new_catalog(tmp_path), installed, workspace, bindings(), HostLimits(5, 3, 1_048_576)
    )
    assert environment.report() == "[]"
    async with environment.open(float("inf")):
        for config in installed.configurations:
            record = json_object(
                decode_json((workspace / config.instance_id / "bootstrap.json").read_text())
            )
            assert record["config"] == decode_json(config.description.config_json)
    assert "not_started" in environment.report()
    with pytest.raises(RuntimeError, match="cannot be reused"):
        async with environment.open(float("inf")):
            pytest.fail("A graph environment cannot start twice")


@pytest.mark.parametrize(
    "fault",
    [
        "missing_host",
        "missing_price",
        "extra_price",
        "duplicate_charge",
        "relative",
        "path",
        "duplicate",
        "mismatch",
    ],
)
def test_invalid_host_configuration_never_creates_a_workspace(tmp_path: Path, fault: str) -> None:
    installed = compiler(tmp_path, types(tmp_path)).compile(
        encode_json(graph_value("single-agent")), '{"problem":"p"}'
    )
    supplied = bindings()
    workspace = tmp_path / "run"
    if fault == "missing_host":
        del supplied["proposer"]
    elif fault == "missing_price":
        supplied["model"] = HostBinding()
    elif fault in {"extra_price", "duplicate_charge"}:
        supplied["proposer" if fault == "duplicate_charge" else "model"] = HostBinding(
            pricing=(("generate", OpenAIPricePolicy(profile())),)
        )
    elif fault == "relative":
        workspace = Path("relative")
    installed = invalid_plan(installed, fault)
    with pytest.raises(ValueError):
        InstalledGraphEnvironment(
            new_catalog(tmp_path), installed, workspace, supplied, HostLimits(5, 3, 1024)
        )
    assert not (tmp_path / "run").exists()


def invalid_plan(installed: InstalledPlan, fault: str) -> InstalledPlan:
    if fault == "path":
        installed = replace(
            installed,
            configurations=(replace(installed.configurations[0], instance_id="../escape"),),
        )
    elif fault == "duplicate":
        installed = replace(
            installed, configurations=(*installed.configurations, installed.configurations[0])
        )
    elif fault == "mismatch":
        installed = replace(installed, configurations=installed.configurations[:1])
    return installed


async def test_changed_installation_record_prevents_process_launch(tmp_path: Path) -> None:
    installed = compiler(tmp_path, types(tmp_path)).compile(
        encode_json(graph_value("single-agent")), '{"problem":"p"}'
    )
    config = installed.configurations[0]
    path = tmp_path / "installations/catalog" / f"{config.resolution_id}.json"
    record = json_object(decode_json(path.read_text()))
    record["provenance"] = {"changed": "after preflight"}
    path.write_text(encode_json(record))
    environment = InstalledGraphEnvironment(
        new_catalog(tmp_path), installed, tmp_path / "run", bindings(), HostLimits(5, 3, 1024)
    )
    with pytest.raises(ValueError, match="changed after graph preflight"):
        async with environment.open(float("inf")):
            pytest.fail("Changed installation evidence must prevent all process launches")
    assert environment.report() == "[]"
