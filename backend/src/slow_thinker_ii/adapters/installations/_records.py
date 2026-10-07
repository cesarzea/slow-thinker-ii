"""Installation records: the registration, wheel artifacts, the inspection and the resolution."""

from typing import Literal

from pydantic import BaseModel, Field

from slow_thinker_ii.contracts import JsonValue

DISTRIBUTION = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
MODULE = r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$"
VERSION = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"


class Record(BaseModel, extra="forbid", frozen=True):
    """Rejects unknown fields and assignment after validation."""


class ComponentRegistration(Record, frozen=True):
    """The `registration.json` of a preparation: the component and the distribution shipping it.

    `type` and `type_version` name the component (`router`, `1.0.0`); `version` is the
    distribution's version; `module` is the importable package run with `python -m`.
    """

    type: str = Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")
    type_version: str = Field(pattern=VERSION)
    distribution: str = Field(pattern=DISTRIBUTION)
    version: str = Field(min_length=1)
    module: str = Field(pattern=MODULE)


class WheelArtifact(Record, frozen=True):
    filename: str
    distribution: str
    version: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class Inspection(Record, frozen=True):
    """What the installed environment reports about itself; `declaration` is the shipped text."""

    python: str
    platform: str
    packages: dict[str, str]
    declaration: str


class Resolution(Record, frozen=True):
    """A published installation: inputs, installed file digests and the inspection evidence."""

    schema_version: Literal["2"] = "2"
    identity: str = Field(pattern=r"^[a-f0-9]{32}$")
    registration: ComponentRegistration
    uv_version: str
    lock_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    artifacts: tuple[WheelArtifact, ...]
    inspection: Inspection
    files: dict[str, str]
    provenance: dict[str, JsonValue] = Field(default_factory=dict[str, JsonValue])
