"""Server configuration for the browser journeys, derived from the reference example."""

import json
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def journey_configuration(workspace: Path, environment: Mapping[str, str]) -> dict[str, object]:
    document: dict[str, object] = json.loads(
        (ROOT / "examples/server-configuration.json").read_text(encoding="utf-8")
    )
    api = environment["SLOW_THINKER_TEST_API_ORIGIN"]
    browser = environment["SLOW_THINKER_TEST_BROWSER_ORIGIN"]
    document["database"] = str(workspace / "state.sqlite3")
    document["workspace"] = str(workspace / "runs")
    document["server"] = {
        "public_url": api,
        "allowed_hosts": [_host(api), _host(browser)],
        "allowed_origins": [browser],
        "static_directory": None,
    }
    document["components"] = {
        "installation_root": str(workspace / "components"),
        "uv": "uv",
        "python": "python",
        "resolutions": [],
    }
    return document


def _host(origin: str) -> str:
    return origin.split("://", 1)[1]
