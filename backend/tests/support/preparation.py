"""Explicit resource configuration with synthetic credentials and local installation evidence."""

from dataclasses import dataclass, field, replace
from pathlib import Path

from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, TypeInstallation
from slow_thinker_ii.adapters.preparation import (
    HostAdapter,
    InstalledWorkflowPreparer,
    ServiceEndpoints,
    standard_host_adapters,
)
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteTariffStore
from slow_thinker_ii.adapters.tariffs import parse_catalog
from slow_thinker_ii.application import ExecutionConfiguration, LimitsProfile, StartIntent
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from .catalog import PAYLOAD
from .installations import new_catalog
from .operator_commands import Clock
from .sequence_plans import EXAMPLES, SCHEMAS

NOW = 1_790_553_600


@dataclass
class SyntheticSecrets:
    requested: list[str] = field(default_factory=list[str])

    def resolve(self, reference: str) -> str:
        self.requested.append(reference)
        return "synthetic-preparation-key"


def resource_settings(selected: tuple[TypeInstallation, ...]) -> JsonObject:
    names = {
        "llm-call": "openai-client",
        "example.sequence": "mcp",
        "example.model-resource": "openai-model",
        "example.grounded-review": "openai-client",
    }
    installations: list[JsonValue] = []
    for item in selected:
        manifest = json_object(decode_json(item.descriptor_json))
        installations.append(
            {
                "type_id": manifest["type_id"],
                "type_version": manifest["type_version"],
                "resolution_id": item.resolution_id,
                "host_adapter": names[str(manifest["type_id"])],
            }
        )
    return {
        "schema_version": "1",
        "installations": installations,
        "providers": {"illustrative-provider": provider_settings()},
    }


def provider_settings() -> JsonObject:
    return {
        "model": "gpt-6-luna",
        "returned_models": ["gpt-6-luna"],
        "credential_ref": "test-provider",
        "default_output_tokens": 8,
        "maximum_output_tokens": 8,
        "review_expires_at": NOW + 3600,
        "maximum_tariff_age_seconds": 86400,
    }


class PreparationCase:
    def __init__(self, directory: Path, installed: Path, selected: tuple[TypeInstallation, ...]):
        self.directory, self.installed, self.selected = directory, installed, selected
        self.database = SqliteDatabase(directory / "preparation.sqlite")
        self.database.initialize()
        self.tariffs = SqliteTariffStore(self.database)
        self.tariffs.publish(parse_catalog(PAYLOAD, NOW))
        self.settings = resource_settings(selected)
        limits = LimitsProfile(
            "illustrative-limits",
            90,
            20,
            20,
            5,
            100,
            8,
            1_048_576,
            1_000_000_000,
            2_000_000_000,
            3_000_000_000,
        )
        self.configuration: ExecutionConfiguration | None = ExecutionConfiguration(
            "resources-1", limits, encode_json(self.settings)
        )
        self.clock, self.secrets = Clock(NOW), SyntheticSecrets()
        self.definitions = BundledDefinitionStore(EXAMPLES)
        self.adapters: dict[str, HostAdapter] = standard_host_adapters()
        self.descriptors = tuple(item.descriptor_json for item in selected)
        self.intent = StartIntent(
            "session", "single-agent", "example-2", "resources-1", '{"problem":"Test preparation"}'
        )

    def preparer(self) -> InstalledWorkflowPreparer:
        return InstalledWorkflowPreparer(
            self.definitions,
            new_catalog(self.installed),
            SCHEMAS,
            self.descriptors,
            lambda: self.configuration,
            self.tariffs,
            self.secrets,
            ServiceEndpoints("http://127.0.0.1:8000/v1"),
            self.directory / "runtime",
            self.adapters,
            self.clock,
        )

    def update(self) -> None:
        assert self.configuration is not None
        self.configuration = replace(self.configuration, resources_json=encode_json(self.settings))

    def set_provider(self, name: str, value: JsonValue) -> None:
        providers = json_object(self.settings["providers"])
        provider = json_object(providers["illustrative-provider"])
        provider[name] = value
        providers["illustrative-provider"] = provider
        self.settings["providers"] = providers
