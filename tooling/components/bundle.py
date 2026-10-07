"""Retain the outcome of one preparation command: what was installed, and where from."""

import json
from pathlib import Path
from uuid import uuid4

from tooling.components.prepare import Preparation


def write_bundle(
    destination: Path, preparations: dict[str, Preparation], identities: dict[str, str]
) -> Path:
    directory = destination / "bundles"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{uuid4().hex}.json"
    payload = {
        "schema_version": "3",
        "installation_root": str(destination),
        "components": {
            name: {
                "resolution": identities[name],
                "registration": preparation.registration.record(),
                "preparation": str(preparation.directory),
            }
            for name, preparation in preparations.items()
        },
    }
    with path.open("x") as stream:
        stream.write(json.dumps(payload, indent=2) + "\n")
    return path
