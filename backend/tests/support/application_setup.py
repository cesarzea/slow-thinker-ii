"""Trusted composition uses synthetic access credentials and explicit empty resources."""

from pathlib import Path

from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.preparation import ServiceEndpoints
from slow_thinker_ii.bootstrap import ExecutionSetup

from .installations import new_catalog
from .operator_commands import operator_case
from .operator_http import ORIGIN, TOKEN
from .preparation import SyntheticSecrets


def application_setup(directory: Path) -> ExecutionSetup:
    case = operator_case(directory)
    return ExecutionSetup(
        case.profile,
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
