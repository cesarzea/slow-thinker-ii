"""Retain compact installation evidence and effective bindings without copying credential values."""

from hashlib import sha256

from pydantic import TypeAdapter

from slow_thinker_ii.accounting import Tariff
from slow_thinker_ii.adapters.catalog import InstalledPlan
from slow_thinker_ii.application import ModelBinding, PreparationRejected, workspace
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from ._host_profiles import HostProfile
from ._tariffs import SelectedTariff

TARIFF = TypeAdapter(Tariff)


def installation_evidence(value: str) -> JsonObject:
    record = json_object(decode_json(value))
    fingerprint = sha256(encode_json(record).encode()).hexdigest()
    files = record.pop("files")
    record["files_sha256"] = sha256(encode_json(files).encode()).hexdigest()
    record["record_sha256"] = fingerprint
    return record


def tariff_evidence(selected: SelectedTariff | workspace.ModelTariffSelection | None) -> JsonValue:
    if selected is None:
        return None
    revision = selected.revision
    return {
        "digest": revision.digest,
        "source": revision.source,
        "retrieved_at": revision.retrieved_at,
        "validated_at": selected.validated_at,
        "tariff": decode_json(TARIFF.dump_json(revision.tariff).decode()),
    }


def snapshot(
    installed: InstalledPlan, hosts: dict[str, HostProfile], tariff: SelectedTariff | None
) -> str:
    installations: JsonObject = {}
    instances: JsonObject = {}
    for item in installed.configurations:
        evidence = installation_evidence(item.description.installation_json)
        previous = installations.get(item.resolution_id)
        if previous is not None and previous != evidence:
            raise PreparationRejected("installation_changed_during_preparation")
        installations[item.resolution_id] = evidence
        instances[item.instance_id] = instance_evidence(item.instance_id, installed, hosts)
    return encode_json(
        {
            "schema_version": "1",
            "definition": decode_json(installed.plan.graph_json),
            "input": decode_json(installed.plan.input_json),
            "installations": installations,
            "instances": instances,
            "tariff": tariff_evidence(tariff),
        }
    )


def instance_evidence(
    identity: str, installed: InstalledPlan, hosts: dict[str, HostProfile]
) -> JsonObject:
    item = next(config for config in installed.configurations if config.instance_id == identity)
    host = hosts[identity]
    operations: list[JsonValue] = [
        {
            "name": operation.name,
            "input_schema": decode_json(operation.input_schema_json),
            "output_schema": decode_json(operation.output_schema_json),
        }
        for operation in item.description.operations
    ]
    return {
        "resolution_id": item.resolution_id,
        "descriptor": decode_json(item.descriptor_json),
        "config": decode_json(item.description.config_json),
        "operations": operations,
        "clients": decode_json(host.binding.clients_json),
        "models": model_evidence(host.models),
        "model_tariff": model_tariff_evidence(host.model_tariff),
        "credentials": "withheld" if host.binding.secrets else "none",
        "metered_operations": [name for name, _ in host.binding.pricing],
    }


def model_evidence(models: tuple[ModelBinding, ...]) -> list[JsonValue]:
    return [
        {
            "caller": model.caller,
            "alias": model.model_alias,
            "target": model.target.instance,
            "operation": model.target.operation,
        }
        for model in models
    ]


def model_tariff_evidence(selected: workspace.ModelTariffSelection | None) -> JsonValue:
    evidence = tariff_evidence(selected)
    if selected is None or selected.revision.tariff.profile != "deepseek.flash.direct.v1":
        return evidence
    source = json_object(decode_json(selected.revision.source_json))
    value = json_object(evidence)
    captured = source["captured_html"]
    if not isinstance(captured, str):
        raise PreparationRejected("invalid_tariff_source_capture")
    value["billing"] = source["normalized"]
    value["source_capture_sha256"] = sha256(captured.encode()).hexdigest()
    return value
