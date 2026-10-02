"""Retain an explicit set of prepared resolutions without changing any active experiment."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from slow_thinker_ii.adapters.installations import Resolution


@dataclass(frozen=True)
class BundleDescriptor:
    name: str
    descriptor_json: str
    registration_json: str


def write_bundle(
    destination: Path,
    records: dict[str, Resolution],
    descriptors: dict[str, BundleDescriptor] | None = None,
) -> Path:
    directory = destination / "bundles"
    directory.mkdir(parents=True, exist_ok=True)
    identity = uuid4().hex
    path = directory / f"{identity}.json"
    payload = {
        "schema_version": "1",
        "catalog_root": str(destination),
        "resolutions": {name: record.identity for name, record in records.items()},
    }
    if descriptors:
        payload["descriptors"] = _descriptors(directory / identity, records, descriptors)
    with path.open("x") as stream:
        stream.write(json.dumps(payload, indent=2) + "\n")
    return path


def _descriptors(
    directory: Path,
    records: dict[str, Resolution],
    descriptors: dict[str, BundleDescriptor],
) -> dict[str, str]:
    if set(descriptors) - set(records):
        raise ValueError("Bundle descriptors must belong to included resolutions")
    directory.mkdir()
    paths: dict[str, str] = {}
    for name, descriptor in descriptors.items():
        if not re.fullmatch(r"[a-z][a-z0-9_.-]*", name) or not re.fullmatch(
            r"[a-z][a-z0-9.-]*\.component\.json", descriptor.name
        ):
            raise ValueError("Bundle descriptor names must be safe component identities")
        target = directory / name
        target.mkdir()
        path = target / descriptor.name
        path.write_text(descriptor.descriptor_json + "\n", encoding="utf-8")
        (target / "registration.json").write_text(
            descriptor.registration_json + "\n", encoding="utf-8"
        )
        paths[name] = str(path.resolve())
    return paths
