"""Collision-free namespaces with explicit lifetime and a bootstrap-owned file path."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from slow_thinker_ii.adapters.preparation import HostProfile, HostRequest
from slow_thinker_ii.adapters.process import HostBinding
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import JsonValue, encode_json


class MemorySettings(BaseModel, extra="forbid", strict=True, frozen=True):
    namespace: str = Field(min_length=1, max_length=256)
    retention: Literal["run", "persistent"] = "run"
    max_entries: int = Field(default=1000, gt=0, le=10000)
    max_value_bytes: int = Field(default=65536, gt=0, le=65536)


class MemoryResourceAdapter:
    def __init__(self, storage_root: Path) -> None:
        self._path = storage_root.resolve() / "memory.sqlite3"

    def configure(self, request: HostRequest) -> HostProfile:
        try:
            settings = MemorySettings.model_validate(request.component.config)
        except ValidationError as error:
            raise PreparationRejected("invalid_memory_configuration") from error
        if len(settings.namespace.encode("utf-8")) > 256:
            raise PreparationRejected("invalid_memory_namespace")
        parts: list[JsonValue] = [request.graph.graph_id, request.instance_id, settings.namespace]
        if settings.retention == "run":
            if not request.runtime_id:
                raise PreparationRejected("memory_runtime_required")
            parts.append(request.runtime_id)
        clients = encode_json(
            {
                "memory_store": {
                    "path": str(self._path),
                    "namespace": encode_json(parts),
                }
            }
        )
        return HostProfile(HostBinding(clients))
