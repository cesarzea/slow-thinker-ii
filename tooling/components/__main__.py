"""Explicit component installation; running a graph never builds, resolves or downloads code."""

import argparse
import shutil
import sys
from pathlib import Path

from tooling.components.bundle import write_bundle
from tooling.components.install import install
from tooling.components.prepare import Preparation, prepare_component
from tooling.components.targets import TARGETS


def _arguments(root: Path) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and install component packages")
    parser.add_argument(
        "--destination",
        type=Path,
        default=root / ".local/components",
        help="installation root, the configuration's components.installation_root",
    )
    parser.add_argument("--component", choices=(*TARGETS, "all"), default="all")
    return parser.parse_args()


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    arguments = _arguments(root)
    destination = Path(str(arguments.destination)).resolve()
    found = shutil.which("uv")
    if found is None:
        raise RuntimeError("The pinned uv executable is required")
    uv, python = Path(found).resolve(), Path(sys.executable)
    names = TARGETS if arguments.component == "all" else (str(arguments.component),)
    preparations: dict[str, Preparation] = {}
    identities: dict[str, str] = {}
    for name in names:
        preparation = prepare_component(root, destination, uv, python, name)
        identity = install(preparation, destination, uv, python).identity
        preparations[name], identities[name] = preparation, identity
        registration = preparation.registration
        sys.stdout.write(
            f"Installed {registration.type}@{registration.type_version} "
            f"({registration.distribution} {registration.version}): {identity}\n"
        )
    sys.stdout.write(f"Bundle: {write_bundle(destination, preparations, identities)}\n")
    listed = ", ".join(f'"{identity}"' for identity in identities.values())
    sys.stdout.write(f"Put these identities into components.resolutions: [{listed}]\n")


main()
