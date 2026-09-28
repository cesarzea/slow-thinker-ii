"""Enumerate owned source without traversing dependencies or generated output."""

import json
from dataclasses import dataclass
from pathlib import Path

from tooling.quality.json_shapes import json_array, json_object


@dataclass(frozen=True)
class Locations:
    roots: tuple[str, ...]
    files: tuple[str, ...]
    excluded: frozenset[str]
    extensions: frozenset[str]


def read_locations(root: Path) -> Locations:
    value: object = json.loads((root / "tooling/locations.json").read_text())
    if not json_object(value):
        raise ValueError("Location manifest must be an object")
    return Locations(
        roots=_strings(value, "roots"),
        files=_strings(value, "files"),
        excluded=frozenset(_strings(value, "excluded")),
        extensions=frozenset(_strings(value, "extensions")),
    )


def _strings(value: dict[str, object], key: str) -> tuple[str, ...]:
    items = value.get(key)
    if not json_array(items) or not all(isinstance(item, str) for item in items):
        raise ValueError(f"Invalid location field: {key}")
    return tuple(str(item) for item in items)


def source_files(root: Path, locations: Locations) -> list[Path]:
    found: list[Path] = []
    for directory, directories, names in root.walk():
        directories[:] = [name for name in directories if name not in locations.excluded]
        found.extend(
            directory / name for name in names if Path(name).suffix in locations.extensions
        )
    return sorted(found)


def approved_path(path: str, locations: Locations) -> bool:
    return path in locations.files or any(path.startswith(f"{root}/") for root in locations.roots)
