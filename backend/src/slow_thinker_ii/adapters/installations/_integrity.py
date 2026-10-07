"""Inspect installed environments and check their contents without changing them."""

import sys
import sysconfig
from pathlib import Path

from packaging.utils import canonicalize_name

from slow_thinker_ii.catalog import ComponentDeclaration, ComponentRef, parse_declaration
from slow_thinker_ii.contracts import decode_json

from ._commands import run
from ._records import ComponentRegistration, Inspection, WheelArtifact
from ._wheels import digest

INSPECTION = Path(__file__).with_name("_inspect.py")


def inspect_environment(python: Path, registration: ComponentRegistration) -> Inspection:
    """Runs the standalone inspection with the environment's isolated interpreter."""
    module, distribution = registration.module, registration.distribution
    output = run(
        [str(python), "-B", "-I", str(INSPECTION), distribution, registration.version, module],
        python.parent,
        timeout=20,
    )
    return Inspection.model_validate_json(output)


def require_inventory(inspection: Inspection, artifacts: tuple[WheelArtifact, ...]) -> None:
    expected = {artifact.distribution: artifact.version for artifact in artifacts}
    actual = {canonicalize_name(name): version for name, version in inspection.packages.items()}
    if actual != expected:
        raise ValueError("Installed distributions differ from the complete lock")
    if inspection.python != sys.version or inspection.platform != sysconfig.get_platform():
        raise ValueError("Installed interpreter does not match the selected build/platform")


def declared(inspection: Inspection, registration: ComponentRegistration) -> ComponentDeclaration:
    """The shipped declaration; it must be valid and name the registered component."""
    declaration = parse_declaration(decode_json(inspection.declaration))
    expected = ComponentRef(registration.type, registration.type_version)
    if declaration.ref != expected:
        raise ValueError(
            f"The installed declaration is {declaration.ref}, but the registration names {expected}"
        )
    return declaration


def inventory(environment: Path) -> dict[str, str]:
    """The digest of every installed file, by its path inside the environment."""
    return {
        path.relative_to(environment).as_posix(): digest(path)
        for path in sorted(environment.rglob("*"))
        if path.is_file()
    }
