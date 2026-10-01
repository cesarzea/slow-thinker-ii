"""Preflight installed contracts before allocating run state, clients or business-call authority."""

from collections.abc import Mapping
from pathlib import Path

from slow_thinker_ii.adapters.installations import InstallationCatalog, Resolution
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import ResolvedInstance

from ._composition_contracts import validate_compositions
from ._conditional_compiler import ConditionalCompiler
from ._installed_records import ConfiguredInstance, InstalledPlan, TypeInstallation
from ._installed_types import installed_types, resolved_instance
from ._models import ComponentRecord, GraphRecord
from ._schemas import ContractSchemas
from ._sequence_compiler import SequenceCompiler


class InstalledGraphCompiler:
    def __init__(
        self,
        catalog: InstallationCatalog,
        schema_directory: Path,
        types: tuple[TypeInstallation, ...],
        description_seconds: float = 20,
    ) -> None:
        self._catalog = catalog
        self._schemas = ContractSchemas(schema_directory)
        self._compiler = SequenceCompiler(schema_directory)
        self._conditional = ConditionalCompiler(schema_directory)
        self._types = installed_types(
            types, self._schemas, (schema_directory / "component.schema.json").read_text()
        )
        self._seconds = description_seconds

    def compile(
        self, graph_json: str, input_json: str, host_configs: Mapping[str, str] | None = None
    ) -> InstalledPlan:
        value = json_object(decode_json(graph_json))
        self._schemas.graph(value)
        graph = GraphRecord.model_validate(value)
        overrides = dict(host_configs or {})
        if set(overrides) - set(graph.components):
            raise ValueError("Host configurations reference an unknown instance")
        resolved: list[ResolvedInstance] = []
        configurations: list[ConfiguredInstance] = []
        for identity, spec in graph.components.items():
            instance, config = self._resolve(identity, spec, overrides.get(identity))
            resolved.append(instance)
            configurations.append(config)
        compiler = (
            self._conditional
            if graph.execution_profile == "bounded-conditional"
            else self._compiler
        )
        plan = compiler.compile(graph_json, input_json, tuple(resolved))
        validate_compositions(graph, {instance.instance_id: instance for instance in resolved})
        return InstalledPlan(plan, tuple(configurations))

    def _resolve(
        self, identity: str, spec: ComponentRecord, host_config: str | None
    ) -> tuple[ResolvedInstance, ConfiguredInstance]:
        key = spec.type_id, spec.type_version
        if key not in self._types:
            raise ValueError("No approved installation for the pinned component type")
        selected = self._types[key]
        manifest = json_object(decode_json(selected.descriptor_json))
        self._schemas.validate(spec.config, encode_json(manifest["config_schema"]))
        registration = self._catalog.verify(selected.resolution_id).registration
        if (registration.type_id, registration.type_version) != key:
            raise ValueError("Selected installation does not implement the configured type")
        config = encode_json(spec.config) if host_config is None else host_config
        description = self._catalog.describe(selected.resolution_id, config, self._seconds)
        verified = Resolution.model_validate_json(description.installation_json).registration
        if verified != registration:
            raise ValueError("Installation registration changed during graph preflight")
        instance = resolved_instance(identity, manifest, description.operations)
        return instance, ConfiguredInstance(
            identity, selected.resolution_id, selected.descriptor_json, description
        )
