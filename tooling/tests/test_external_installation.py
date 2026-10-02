"""A real authored package is independently built, installed and executed with mediated models."""

import hashlib
import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import InstallationCatalog, Resolution
from slow_thinker_ii.adapters.process import HostSettings, InstalledProcess, ProcessOperation
from slow_thinker_ii.contracts import OperationContract, encode_json
from slow_thinker_llm_call import effective_operation
from support.native_gateway import assert_recorded, native_case
from support.native_server import gateway_app, serve
from support.openai_calls import bootstrap_record, config

from tooling.components.bundle import BundleDescriptor, write_bundle
from tooling.components.external import external_target
from tooling.tests.test_external_support import ROOT, prepare_external_installation


@pytest.fixture(scope="module")
def external_installation(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Resolution]:
    return prepare_external_installation(tmp_path_factory.mktemp("external-component"))


def test_independent_environment_exact_closure_and_copied_bundle(
    external_installation: tuple[Path, Resolution],
) -> None:
    directory, resolution = external_installation
    assert resolution.inspection.packages["example-resource-agent"] == "0.1.0"
    assert resolution.inspection.base_entry_point == "slow_thinker_llm_call:LLMCall"
    assert resolution.inspection.packages["slow-thinker-host"] == "0.1.0.dev1"
    assert all(artifact.sha256 for artifact in resolution.artifacts)
    selected = external_target(
        ROOT,
        ROOT / "examples/resource-agent",
        ROOT / "examples/resource-agent/registration.json",
        ROOT / "examples/resource-agent/resource-agent.component.json",
    )
    manifest = write_bundle(
        directory,
        {"example.resource-agent": resolution},
        {
            "example.resource-agent": BundleDescriptor(
                selected.descriptor_name, selected.descriptor_json, selected.registration_json
            )
        },
    )
    path = manifest.parent / manifest.stem / "example.resource-agent" / selected.descriptor_name
    assert path.read_text().strip() == selected.descriptor_json
    assert hashlib.sha256(path.read_bytes()).hexdigest()
    assert (path.parent / "registration.json").exists()


async def test_installed_authored_component_executes_through_managed_gateway(
    tmp_path: Path,
    external_installation: tuple[Path, Resolution],
) -> None:
    directory, resolution = external_installation
    case = native_case(tmp_path)
    operation = effective_operation(config())
    contract = OperationContract(
        operation.name, encode_json(operation.input_schema), encode_json(operation.output_schema)
    )
    async with serve(gateway_app(case.gateway)) as port:
        bootstrap = tmp_path / "external.json"
        bootstrap.write_text(encode_json(bootstrap_record(f"http://127.0.0.1:{port}/v1")))
        host = installed_host(directory, resolution, bootstrap, tmp_path, contract)
        async with host.connect() as connection:
            reply = await ProcessOperation(connection, "generate", None).invoke(
                '{"question":"test","memory":"supplied"}',
                case.parent.token,
                case.parent.context.deadline,
            )
    assert not reply.result.is_error and "success" in reply.result.payload_json
    assert len(case.model.calls) == 1
    assert_recorded(case)


def installed_host(
    directory: Path,
    resolution: Resolution,
    bootstrap: Path,
    workspace: Path,
    contract: OperationContract,
) -> InstalledProcess:
    python = Path(sys.executable)
    catalog = InstallationCatalog(directory, python.with_name("uv"), python)
    return InstalledProcess(
        catalog,
        resolution.identity,
        "example.resource-agent",
        "0.1.0",
        HostSettings(bootstrap, workspace, 10, 3, 1048576),
        (contract,),
    )
