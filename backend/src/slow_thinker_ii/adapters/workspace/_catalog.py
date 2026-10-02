"""Discovery of trusted component schemas, reviewed models and effective ceilings."""

import time
from collections.abc import Callable
from pathlib import Path

from slow_thinker_ii.adapters.catalog import ComponentCatalog
from slow_thinker_ii.adapters.preparation import ResourceSettings, model_capabilities
from slow_thinker_ii.application import ExecutionConfiguration, LimitsProfile, workspace
from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object


class WorkspaceCatalog:
    def __init__(
        self,
        schema_directory: Path,
        descriptor_directory: Path,
        registered: tuple[str, ...],
        profile: Callable[[], ExecutionConfiguration | None],
        maximum: LimitsProfile,
        tariffs: workspace.ModelTariffReader,
        wall: Callable[[], float] = time.time,
    ) -> None:
        self._schemas, self._directory, self._registered = (
            schema_directory,
            descriptor_directory,
            registered,
        )
        self._profile, self._maximum, self._tariffs, self._wall = profile, maximum, tariffs, wall

    def read(self) -> JsonObject:
        current = self._profile()
        if current is None:
            raise workspace.WorkspaceError("operator_service_unavailable")
        settings = ResourceSettings.model_validate_json(current.resources_json)
        schemas = ComponentCatalog(self._schemas, self._directory, self._registered)
        types = schemas.components()
        installed = {(choice.type_id, choice.type_version) for choice in settings.installations}
        components: list[JsonValue] = [
            _component(value, key in installed)
            for value in types
            for key in [(str(value["type_id"]), str(value["type_version"]))]
        ]
        models: list[JsonValue] = [
            self._model(value, settings) for value in model_capabilities(settings)
        ]
        return {
            "schema_version": "1",
            "configuration_revision": current.revision,
            "components": components,
            "models": models,
            "graph_schema": schemas.graph_schema(),
            "schema_documents": schemas.schema_documents(),
            "supported_graph_profiles": ["sequence", "bounded-conditional"],
            "limits": {
                "current": workspace.limits_value(current.limits),
                "maximum": workspace.limits_value(self._maximum),
            },
        }

    def _model(self, value: JsonObject, settings: ResourceSettings) -> JsonObject:
        result = json_object(value)
        profile = settings.providers[str(value["provider_profile"])]
        selected = self._tariffs.selected(str(value["billing_profile"]))
        now = self._wall()
        status = "ready"
        if now >= profile.review_expires_at:
            status = "review_expired"
        elif selected is None:
            status = "unavailable"
        elif (
            now < selected.validated_at
            or now - selected.validated_at > profile.maximum_tariff_age_seconds
        ):
            status = "stale"
        result["tariff_status"] = status
        return result


def _component(value: JsonObject, installed: bool) -> JsonObject:
    return {
        "type_id": value["type_id"],
        "type_version": value["type_version"],
        "roles": value["roles"],
        "config_schema": value["config_schema"],
        "resource_slots": value["resource_slots"],
        "operations": value["operations"],
        "installation_status": "ready" if installed else "unavailable",
    }
