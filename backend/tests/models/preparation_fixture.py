"""Production preparer with explicitly synthetic description-only installations."""

from dataclasses import dataclass, replace
from pathlib import Path

from slow_thinker_ii.adapters.catalog import TypeInstallation
from slow_thinker_ii.adapters.installations import ComponentRegistration
from slow_thinker_ii.adapters.preparation import InstalledWorkflowPreparer, ServiceEndpoints
from slow_thinker_ii.adapters.sqlite import SqliteModelTariffStore
from slow_thinker_ii.adapters.tariffs import DEEPSEEK_PROFILE_ID
from slow_thinker_ii.application import workspace
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.installations import new_catalog
from support.installed_graphs import SOURCE, types
from support.preparation import NOW, PreparationCase
from support.sequence_plans import EXAMPLES, ROOT, SCHEMAS
from support.wheels import lockfile, wheel
from support.workspace_data import workspace_resources
from support.workspace_tariffs import RecordedDeepSeek


@dataclass
class Definitions:
    source: str

    def definition(self, graph_id: str, revision: str) -> str:
        value = json_object(decode_json(self.source))
        assert value["graph_id"] == graph_id and value["revision"] == revision
        return self.source


@dataclass(frozen=True)
class ModelInstallations:
    directory: Path
    selected: tuple[TypeInstallation, ...]
    model: TypeInstallation


def model_installations(directory: Path) -> ModelInstallations:
    selected = types(directory)
    artifact = wheel(directory, "model-description", "1.0", SOURCE)
    descriptor = (ROOT / "components/model-provider/model-provider.component.json").read_text()
    registration = ComponentRegistration(
        type_id="model-provider",
        type_version="0.1.0",
        distribution="model-description",
        version="1.0",
        entry_point="model_description:Component",
    )
    record = new_catalog(directory).prepare(
        lockfile(directory, (artifact,)), directory, registration
    )
    return ModelInstallations(directory, selected, TypeInstallation(record.identity, descriptor))


def model_preparer(
    case: PreparationCase, definitions: Definitions, reader: workspace.ModelTariffReader | None
) -> InstalledWorkflowPreparer:
    return InstalledWorkflowPreparer(
        definitions,
        new_catalog(case.installed),
        SCHEMAS,
        case.descriptors,
        lambda: case.configuration,
        case.tariffs,
        case.secrets,
        ServiceEndpoints("http://127.0.0.1:8000/v1"),
        case.directory / "runtime",
        case.adapters,
        case.clock,
        model_tariffs=reader,
    )


async def preparation_case(
    directory: Path, installed: ModelInstallations
) -> tuple[PreparationCase, Definitions]:
    case = PreparationCase(directory, installed.directory, installed.selected)
    model_descriptor = json_object(decode_json(installed.model.descriptor_json))
    installations = case.settings["installations"]
    assert isinstance(installations, list)
    installations.append(
        {
            "type_id": model_descriptor["type_id"],
            "type_version": model_descriptor["type_version"],
            "resolution_id": installed.model.resolution_id,
            "host_adapter": "model-resource",
        }
    )
    case.descriptors = (*case.descriptors, installed.model.descriptor_json)
    configure_providers(case)
    definitions = model_definition(case)
    SqliteModelTariffStore(case.database, DEEPSEEK_PROFILE_ID).publish(
        await RecordedDeepSeek().fetch(NOW)
    )
    return case, definitions


def configure_providers(case: PreparationCase) -> None:
    providers = json_object(workspace_resources()["providers"])
    for identity, value in providers.items():
        profile = json_object(value)
        profile.update(
            review_expires_at=NOW + 3600, default_output_tokens=8, maximum_output_tokens=32
        )
        providers[identity] = profile
    case.settings["providers"] = providers
    case.update()


def model_definition(case: PreparationCase) -> Definitions:
    source = json_object(decode_json((EXAMPLES / "single-agent.graph.json").read_text()))
    model = json_object(json_object(source["components"])["model"])
    model.update(
        type_id="model-provider",
        type_version="0.1.0",
        config={"provider_profile": "deepseek-flash", "model": "deepseek-alias"},
    )
    source["components"] = {**json_object(source["components"]), "model": model}
    definitions = Definitions(encode_json(source))
    case.intent = replace(
        case.intent, graph_id=str(source["graph_id"]), graph_revision=str(source["revision"])
    )
    return definitions
