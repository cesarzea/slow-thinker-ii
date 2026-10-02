"""Trusted composition uses synthetic access credentials and valid resource discovery."""

from dataclasses import replace
from pathlib import Path

from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.preparation import ServiceEndpoints
from slow_thinker_ii.bootstrap import ExecutionSetup
from slow_thinker_ii.contracts import encode_json

from .installations import new_catalog
from .operator_commands import operator_case
from .operator_http import ORIGIN, TOKEN
from .preparation import SyntheticSecrets
from .workspace_data import provider, workspace_resources


def application_setup(directory: Path) -> ExecutionSetup:
    case = operator_case(directory)
    resources = workspace_resources()
    resources["providers"] = {"illustrative-provider": provider("openai", "gpt-6-luna")}
    return ExecutionSetup(
        replace(case.profile, resources_json=encode_json(resources)),
        new_catalog(directory),
        (),
        ServiceEndpoints(ORIGIN + "/v1"),
        SyntheticSecrets(),
        OperatorAccess(TOKEN, (ORIGIN,), ("127.0.0.1:8000",)),
        b"k" * 32,
        directory / "runtime",
        5,
        4,
    )
