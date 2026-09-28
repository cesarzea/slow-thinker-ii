"""Immutable installation evidence, distinct from graph and component versions."""

from typing import Literal

from pydantic import BaseModel, Field


class Record(BaseModel, extra="forbid", frozen=True):
    """Reject unknown fields and assignment after validation."""


class ImplementationBase(Record, frozen=True):
    distribution: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
    version: str = Field(min_length=1)
    entry_point: str = Field(pattern=r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*$")
    requirement: str = Field(min_length=1)


class ComponentRegistration(Record, frozen=True):
    type_id: str = Field(min_length=1)
    type_version: str = Field(min_length=1)
    distribution: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
    version: str = Field(min_length=1)
    entry_point: str = Field(pattern=r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*$")
    base: ImplementationBase | None = None


class WheelArtifact(Record, frozen=True):
    filename: str
    distribution: str
    version: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class Inspection(Record, frozen=True):
    python: str
    platform: str
    packages: dict[str, str]
    entry_point: str
    requirements: tuple[str, ...]
    base_entry_point: str | None


class Resolution(Record, frozen=True):
    schema_version: Literal["1"] = "1"
    identity: str = Field(pattern=r"^[a-f0-9]{32}$")
    registration: ComponentRegistration
    uv_version: str
    lock_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    artifacts: tuple[WheelArtifact, ...]
    inspection: Inspection
    files: dict[str, str]
    provenance: dict[str, str] = Field(default_factory=dict)
