"""Materialize one immutable bootstrap and bind its approved installed implementation."""

from pathlib import Path

from slow_thinker_ii.adapters.catalog import ConfiguredInstance
from slow_thinker_ii.adapters.installations import InstallationCatalog, Resolution
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from ._fleet import ProcessHost
from ._graph_bindings import HostBinding, HostLimits
from ._installed import HostSettings, InstalledProcess


def bootstrap_record(config: ConfiguredInstance, binding: HostBinding) -> JsonObject:
    operations: list[JsonValue] = [
        {
            "name": item.name,
            "input_schema": decode_json(item.input_schema_json),
            "output_schema": decode_json(item.output_schema_json),
        }
        for item in config.description.operations
    ]
    return {
        "config": decode_json(config.description.config_json),
        "operations": operations,
        "clients": json_object(decode_json(binding.clients_json)),
    }


def validate_billing(config: ConfiguredInstance, binding: HostBinding) -> None:
    names = {item.name for item in config.description.operations}
    priced = {name for name, _ in binding.pricing}
    billing = json_object(decode_json(config.descriptor_json))["billing"]
    if billing not in {"none", "mediated", "metered"}:
        raise ValueError("Unsupported component billing declaration")
    if priced - names or (billing == "metered" and priced != names):
        raise ValueError("Every metered operation needs its approved price policy")
    if billing != "metered" and priced:
        raise ValueError("Mediated or unmetered components cannot duplicate model charges")


def build_host(
    catalog: InstallationCatalog,
    config: ConfiguredInstance,
    binding: HostBinding,
    workspace: Path,
    limits: HostLimits,
) -> ProcessHost:
    settings = host_settings(config, binding, workspace, limits)
    registration = Resolution.model_validate_json(config.description.installation_json).registration
    process = InstalledProcess(
        catalog,
        config.resolution_id,
        registration.type_id,
        registration.type_version,
        settings,
        config.description.operations,
    )
    if process.installation_json() != config.description.installation_json:
        raise ValueError("Installation changed after graph preflight")
    pricing = dict(binding.pricing)
    return ProcessHost(
        config.instance_id,
        process,
        tuple((item.name, pricing.get(item.name)) for item in config.description.operations),
    )


def write_bootstrap(
    config: ConfiguredInstance, binding: HostBinding, workspace: Path
) -> tuple[Path, Path]:
    directory = workspace / config.instance_id
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    path = directory / "bootstrap.json"
    with path.open("x") as stream:
        stream.write(encode_json(bootstrap_record(config, binding)))
    return directory, path


def host_settings(
    config: ConfiguredInstance, binding: HostBinding, workspace: Path, limits: HostLimits
) -> HostSettings:
    directory, path = write_bootstrap(config, binding, workspace)
    return HostSettings(
        path,
        directory,
        limits.startup_seconds,
        limits.shutdown_seconds,
        limits.max_message_bytes,
        binding.secrets,
    )
