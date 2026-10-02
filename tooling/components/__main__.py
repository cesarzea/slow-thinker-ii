"""Explicit component preparation; experiment startup never installs or updates code."""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

from slow_thinker_ii.adapters.installations import Resolution

from tooling.components.bundle import BundleDescriptor, write_bundle
from tooling.components.external import external_target
from tooling.components.prepare import prepare_component, prepare_recipe
from tooling.components.targets import TARGETS


def _arguments(root: Path) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare independent component installations")
    parser.add_argument("--destination", type=Path, default=root / ".local/components")
    parser.add_argument("--component", choices=(*TARGETS, "all"))
    parser.add_argument("--external-project", type=Path)
    parser.add_argument("--registration", type=Path)
    parser.add_argument("--descriptor", type=Path)
    parser.add_argument("--dependency-project", type=Path, action="append", default=[])
    parser.add_argument(
        "--selector-project",
        type=Path,
        help="Trusted src-layout selector package for redirector preparation",
    )
    arguments = parser.parse_args()
    _external_arguments(parser, arguments)
    if arguments.selector_project is not None and arguments.component not in {"redirector", "all"}:
        parser.error("--selector-project requires --component redirector or all")
    return arguments


def _external_arguments(parser: argparse.ArgumentParser, arguments: argparse.Namespace) -> None:
    if arguments.external_project is not None:
        if arguments.component is not None or arguments.selector_project is not None:
            parser.error("External preparation cannot select a built-in component or selector")
        if arguments.registration is None or arguments.descriptor is None:
            parser.error("External preparation requires --registration and --descriptor")
    elif (
        arguments.registration is not None
        or arguments.descriptor is not None
        or arguments.dependency_project
    ):
        parser.error("Registration, descriptor and dependency projects require --external-project")
    else:
        arguments.component = arguments.component or "sequence"


def _builtins(
    root: Path,
    destination: Path,
    uv: Path,
    arguments: argparse.Namespace,
) -> Path:
    names = TARGETS if arguments.component == "all" else (str(arguments.component),)
    records: dict[str, Resolution] = {}
    for name in names:
        resolution = prepare_component(
            root,
            destination,
            uv,
            Path(sys.executable),
            name,
            selector_project=arguments.selector_project if name == "redirector" else None,
        )
        records[name] = resolution
        sys.stdout.write(f"Prepared {resolution.registration.type_id}: {resolution.identity}\n")
    return write_bundle(destination, records)


def _external(root: Path, destination: Path, uv: Path, arguments: argparse.Namespace) -> Path:
    selected = external_target(
        root,
        arguments.external_project,
        arguments.registration,
        arguments.descriptor,
        tuple(arguments.dependency_project),
    )
    metadata = {
        "descriptor.sha256": hashlib.sha256(selected.descriptor_json.encode("utf-8")).hexdigest(),
        "registration.sha256": hashlib.sha256(
            selected.registration_json.encode("utf-8")
        ).hexdigest(),
    }
    resolution = prepare_recipe(
        root, destination, uv, Path(sys.executable), selected.recipe, metadata
    )
    name = resolution.registration.type_id
    descriptor = BundleDescriptor(
        selected.descriptor_name, selected.descriptor_json, selected.registration_json
    )
    bundle = write_bundle(destination, {name: resolution}, {name: descriptor})
    sys.stdout.write(f"Prepared {name}: {resolution.identity}\n")
    sys.stdout.write(
        f"Descriptor: {bundle.parent / bundle.stem / name / selected.descriptor_name}\n"
    )
    return bundle


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    arguments = _arguments(root)
    destination = Path(str(arguments.destination)).resolve()
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("The pinned uv executable is required")
    operation = _external if arguments.external_project is not None else _builtins
    sys.stdout.write(f"Bundle: {operation(root, destination, Path(uv), arguments)}\n")


if __name__ == "__main__":
    main()
