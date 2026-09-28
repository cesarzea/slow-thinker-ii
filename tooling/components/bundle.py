"""Retain an explicit set of prepared resolutions without changing any active experiment."""

import json
from pathlib import Path
from uuid import uuid4

from slow_thinker_ii.adapters.installations import Resolution


def write_bundle(destination: Path, records: dict[str, Resolution]) -> Path:
    directory = destination / "bundles"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{uuid4().hex}.json"
    payload = {
        "schema_version": "1",
        "catalog_root": str(destination),
        "resolutions": {name: record.identity for name, record in records.items()},
    }
    with path.open("x") as stream:
        stream.write(json.dumps(payload, indent=2) + "\n")
    return path
