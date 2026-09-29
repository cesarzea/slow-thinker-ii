"""Startup fixtures use local paths, exact type identities and synthetic credentials."""

from pathlib import Path

from slow_thinker_ii.accounting import display_amount
from slow_thinker_ii.adapters.catalog import TypeInstallation
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object

from .operator_commands import operator_case
from .operator_http import ORIGIN
from .preparation import resource_settings
from .sequence_plans import EXAMPLES


def startup_record(directory: Path) -> JsonObject:
    profile = operator_case(directory).profile
    descriptors = tuple(
        EXAMPLES / f"{name}.component.json" for name in ("sequence", "llm-call", "model")
    )
    types = tuple(
        TypeInstallation(f"{index:032x}", path.read_text())
        for index, path in enumerate(descriptors)
    )
    limits = json_object(decode_json(profile.limits.to_json()))
    for key in ("run_budget", "session_budget", "month_budget"):
        value = limits[key]
        assert isinstance(value, int)
        limits[key] = display_amount(value)
    return {
        "schema_version": "1",
        "revision": "startup-1",
        "limits": limits,
        "resources": resource_settings(types),
        "installation_catalog": "installations",
        "descriptors": [str(path) for path in descriptors],
        "runtime_directory": "runs",
        "gateway_url": ORIGIN + "/v1",
        "operator_origins": [ORIGIN],
        "operator_hosts": ["127.0.0.1:8000"],
        "operator_credential_env": "SLOW_THINKER_TEST_OPERATOR_TOKEN",
        "provider_credentials": {"test-provider": "SLOW_THINKER_TEST_PROVIDER_KEY"},
        "preparation_seconds": 10,
        "maximum_commands": 4,
    }
