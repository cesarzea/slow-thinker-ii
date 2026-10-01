"""JSON startup configuration contains references, never credential values."""

import os
import sys
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.adapters.preparation import (
    EnvironmentSecrets,
    ResourceSettings,
    ServiceEndpoints,
)
from slow_thinker_ii.application import ExecutionConfiguration
from slow_thinker_ii.contracts import decode_json, encode_json

from ._execution import ExecutionSetup
from ._public_limits import PublicLimits

Positive = Annotated[int, Field(gt=0)]


class StartupConfiguration(BaseModel, extra="forbid", strict=True, frozen=True):
    schema_version: Literal["1"]
    revision: str = Field(min_length=1)
    limits: PublicLimits
    resources: ResourceSettings
    installation_catalog: str
    descriptors: tuple[str, ...] = Field(min_length=1)
    runtime_directory: str
    gateway_url: str
    operator_origins: tuple[str, ...] = Field(min_length=1)
    operator_hosts: tuple[str, ...] = Field(min_length=1)
    operator_credential_env: str
    provider_credentials: dict[str, str]
    preparation_seconds: Positive
    maximum_commands: Positive


def read_document(path: Path) -> str:
    if path.name == "slow-thinker.keys.json" or path.resolve().name == "slow-thinker.keys.json":
        raise ValueError("This file cannot be used as startup configuration")
    with path.open("rb") as source:
        value = source.read(1_048_577)
    if len(value) > 1_048_576:
        raise ValueError("Startup documents must not exceed one MiB")
    return encode_json(decode_json(value.decode("utf-8")))


def load_execution_setup(path: Path) -> ExecutionSetup:
    try:
        record = StartupConfiguration.model_validate_json(read_document(path))
        return compose_setup(record, path.resolve().parent)
    except (OSError, ValueError):
        raise ValueError("Invalid or unavailable execution configuration") from None


def compose_setup(record: StartupConfiguration, directory: Path) -> ExecutionSetup:
    limits = record.limits.internal()
    credential = EnvironmentSecrets({"operator": record.operator_credential_env}).resolve(
        "operator"
    )
    configuration = ExecutionConfiguration(
        record.revision, limits, record.resources.model_dump_json()
    )
    python = Path(sys.executable)
    return ExecutionSetup(
        configuration,
        InstallationCatalog(
            (directory / record.installation_catalog).resolve(), python.with_name("uv"), python
        ),
        tuple(read_document(directory / name) for name in record.descriptors),
        ServiceEndpoints(record.gateway_url),
        EnvironmentSecrets(record.provider_credentials),
        OperatorAccess(credential, record.operator_origins, record.operator_hosts),
        sha256(("operator-cursors:" + credential).encode()).digest(),
        (directory / record.runtime_directory).resolve(),
        record.preparation_seconds,
        record.maximum_commands,
    )


def configured_execution() -> ExecutionSetup | None:
    path = os.environ.get("SLOW_THINKER_CONFIGURATION")
    return None if path is None else load_execution_setup(Path(path))
