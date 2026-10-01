"""Record explicit resolution inputs and the provenance of prepared wheels."""

import json
from importlib.metadata import version
from pathlib import Path

from tooling.components.build import command
from tooling.components.targets import PreparationTarget


def write_inputs(recipe: PreparationTarget, preparation: Path) -> Path:
    registration = recipe.registration
    inputs = preparation / "requirements.in"
    requirements = (
        f"{registration.distribution}=={registration.version}",
        *recipe.additional_requirements,
    )
    inputs.write_text("\n".join(requirements) + "\n")
    return inputs


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
