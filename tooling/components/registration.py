"""Read a prepared component's registration from the wheel that ships it."""

import json
from dataclasses import asdict, dataclass
from email.parser import BytesParser
from pathlib import Path
from typing import cast
from zipfile import ZipFile

DECLARATION_FORMAT = "slow-thinker.component/1"


@dataclass(frozen=True)
class Registration:
    """Component type and version from `component.json`; distribution from wheel metadata."""

    type: str
    type_version: str
    distribution: str
    version: str
    module: str

    def record(self) -> dict[str, str]:
        return asdict(self)


def read_registration(wheels: Path, module: str) -> Registration:
    """The registration of the one wheel in `wheels` that ships `module`'s declaration."""
    declaration_name = f"{module}/component.json"
    matches: list[Path] = []
    for path in sorted(wheels.glob("*.whl")):
        with ZipFile(path) as archive:
            if declaration_name in archive.namelist():
                matches.append(path)
    if len(matches) != 1:
        raise ValueError(f"Expected one built wheel shipping {declaration_name}")
    with ZipFile(matches[0]) as archive:
        names = archive.namelist()
        if f"{module}/__main__.py" not in names:
            raise ValueError(f"The {module} wheel has no module entry point")
        declaration: object = json.loads(archive.read(declaration_name))
        metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
        fields = BytesParser().parsebytes(archive.read(metadata[0]))
    kind, version = _declared(declaration)
    return Registration(kind, version, str(fields["Name"]), str(fields["Version"]), module)


def _declared(declaration: object) -> tuple[str, str]:
    if not isinstance(declaration, dict):
        raise ValueError("A component declaration must be a JSON object")
    record = cast(dict[object, object], declaration)
    kind, version = record.get("type"), record.get("version")
    if record.get("format") != DECLARATION_FORMAT:
        raise ValueError(f"A component declaration must have format {DECLARATION_FORMAT}")
    if not isinstance(kind, str) or not isinstance(version, str):
        raise ValueError("A component declaration must name its type and version")
    return kind, version
