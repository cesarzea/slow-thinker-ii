"""Installed checks require an explicitly selected bundle; normal CI has no such prerequisite."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.contracts import decode_json, json_object


@dataclass(frozen=True)
class PreparedBundle:
    catalog: InstallationCatalog
    identities: dict[str, str]


@pytest.fixture
def prepared_bundle() -> PreparedBundle:
    path = Path(os.environ["SLOW_THINKER_TEST_BUNDLE"])
    record = json_object(decode_json(path.read_text()))
    assert record["schema_version"] == "1" and isinstance(record["catalog_root"], str)
    identities = json_object(record["resolutions"])
    assert set(identities) == {"sequence", "llm-call", "openai-model", "grounded-review"}
    assert all(isinstance(value, str) for value in identities.values())
    python = Path(sys.executable)
    catalog = InstallationCatalog(Path(record["catalog_root"]), python.with_name("uv"), python)
    return PreparedBundle(catalog, {key: str(value) for key, value in identities.items()})
