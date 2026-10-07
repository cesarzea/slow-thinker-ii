"""Record explicit resolution inputs, the registration and the provenance of a preparation."""

import json
from importlib.metadata import version
from pathlib import Path

from tooling.components.build import command
from tooling.components.registration import Registration


def write_inputs(registration: Registration, preparation: Path) -> Path:
    """The single exact requirement whose hash-locked closure is resolved."""
    inputs = preparation / "requirements.in"
    inputs.write_text(f"{registration.distribution}=={registration.version}\n")
    return inputs


def write_registration(registration: Registration, preparation: Path) -> Path:
    path = preparation / "registration.json"
    path.write_text(json.dumps(registration.record(), indent=2) + "\n")
    return path


def record_provenance(
    sources: dict[str, str], built: dict[str, str], uv: Path, preparation: Path
) -> dict[str, str]:
    provenance = {
        **{f"source.{name}": checksum for name, checksum in sources.items()},
        **{f"built.{name}": checksum for name, checksum in built.items()},
        "hatchling": version("hatchling"),
        "pip": version("pip"),
        "uv": command([str(uv), "--version"], preparation).strip(),
    }
    (preparation / "provenance.json").write_text(json.dumps(provenance, indent=2))
    return provenance
