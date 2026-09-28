"""Verify installed contents and runtime evidence without updating the environment."""

import sys
import sysconfig
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from ._commands import run
from ._records import ComponentRegistration, Inspection, WheelArtifact
from ._wheels import digest


def inspect_environment(python: Path, registration: ComponentRegistration) -> Inspection:
    base = registration.base
    value = run(
        [
            str(python),
            "-B",
            "-I",
            str(Path(__file__).with_name("_inspect.py")),
            registration.distribution,
            registration.version,
            registration.entry_point,
            base.distribution if base else "",
            base.version if base else "",
            base.entry_point if base else "",
        ],
        python.parent,
        timeout=20,
    )
    inspection = Inspection.model_validate_json(value)
    if base is not None:
        requirement = Requirement(base.requirement)
        if canonicalize_name(requirement.name) != canonicalize_name(base.distribution):
            raise ValueError("Base dependency names do not match")
        if base.version not in requirement.specifier:
            raise ValueError("Resolved base is outside the declared compatibility range")
        if requirement not in {Requirement(item) for item in inspection.requirements}:
            raise ValueError("Base dependency differs from installed package metadata")
    return inspection


def require_inventory(inspection: Inspection, artifacts: tuple[WheelArtifact, ...]) -> None:
    expected = {artifact.distribution: artifact.version for artifact in artifacts}
    actual = {canonicalize_name(name): version for name, version in inspection.packages.items()}
    if actual != expected:
        raise ValueError("Installed distributions differ from the complete lock")
    if inspection.python != sys.version or inspection.platform != sysconfig.get_platform():
        raise ValueError("Installed interpreter does not match the selected build/platform")


def inventory(environment: Path) -> dict[str, str]:
    return {
        path.relative_to(environment).as_posix(): digest(path)
        for path in sorted(environment.rglob("*"))
        if path.is_file()
    }
