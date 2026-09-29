"""Installed coordinator checks use the production resource preparer and synthetic provider."""

import time
from dataclasses import replace
from pathlib import Path

from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, InstalledPlan, TypeInstallation
from slow_thinker_ii.adapters.preparation import (
    InstalledWorkflowPreparer,
    ServiceEndpoints,
    standard_host_adapters,
)
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteOperatorStore,
    SqliteRunStore,
    SqliteTariffStore,
)
from slow_thinker_ii.adapters.tariffs import parse_catalog
from slow_thinker_ii.application import ExecutionCoordinator, PreparedWorkflow, StartIntent
from slow_thinker_ii.contracts import encode_json, json_object
from support.catalog import PAYLOAD
from support.managed_calls import RealClock
from support.preparation import SyntheticSecrets, resource_settings
from support.sequence_plans import EXAMPLES, SCHEMAS

from .conftest import PreparedBundle
from .graph_admission import fixture_configuration


class InstalledPreparer:
    def __init__(self, bundle: PreparedBundle, installed: InstalledPlan, directory: Path) -> None:
        self.bundle, self.installed, self.directory = bundle, installed, directory
        self.selected = selected_types(bundle)
        settings = resource_settings(self.selected)
        providers = json_object(settings["providers"])
        profile = json_object(providers["illustrative-provider"])
        profile["review_expires_at"] = int(time.time()) + 3600
        profile["maximum_output_tokens"] = 1024
        providers["illustrative-provider"] = profile
        settings["providers"] = providers
        self.configuration = replace(
            fixture_configuration(installed.plan.limits_profile),
            resources_json=encode_json(settings),
        )
        self.gateway_port = self.provider_port = 0
        database = SqliteDatabase(directory / "tariffs.sqlite")
        database.initialize()
        self.tariffs = SqliteTariffStore(database)
        self.tariffs.publish(parse_catalog(PAYLOAD, int(time.time())))
        self.secrets = SyntheticSecrets()

    async def prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow:
        endpoints = ServiceEndpoints(
            f"http://127.0.0.1:{self.gateway_port}/v1", f"http://127.0.0.1:{self.provider_port}/v1"
        )
        preparer = InstalledWorkflowPreparer(
            BundledDefinitionStore(EXAMPLES),
            self.bundle.catalog,
            SCHEMAS,
            tuple(item.descriptor_json for item in self.selected),
            lambda: self.configuration,
            self.tariffs,
            self.secrets,
            endpoints,
            self.directory / "hosts",
            standard_host_adapters(),
            time.time,
        )
        return await preparer.prepare(intent, runtime_id)


def selected_types(bundle: PreparedBundle) -> tuple[TypeInstallation, ...]:
    files = {
        "sequence": "sequence",
        "redirector": "redirector",
        "routed-call": "routed-call",
        "bounded-flow": "bounded-flow",
        "llm-call": "llm-call",
        "openai-model": "model",
        "grounded-review": "grounded-review",
    }
    return tuple(
        TypeInstallation(bundle.identities[key], (EXAMPLES / f"{value}.component.json").read_text())
        for key, value in files.items()
    )


def coordinator_setup(
    directory: Path, preparer: InstalledPreparer
) -> tuple[ExecutionCoordinator, SqliteOperatorStore, SqliteRunStore, StartIntent]:
    database, clock = SqliteDatabase(directory / "run.sqlite"), RealClock()
    database.initialize()
    commands = SqliteOperatorStore(database, 1_048_576, clock)
    commands.configure(preparer.configuration)
    session = commands.create_session("session", "Installed workflow").receipt.target_id
    assert session is not None
    plan = preparer.installed.plan
    intent = StartIntent(
        session, plan.graph_id, plan.revision, preparer.configuration.revision, plan.input_json
    )
    runs = SqliteRunStore(database, 1_048_576)
    coordinator = ExecutionCoordinator(commands, runs, preparer, clock, 45, 15, 4)
    return coordinator, commands, runs, intent
