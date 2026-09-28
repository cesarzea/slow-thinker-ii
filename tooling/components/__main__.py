"""Explicit component preparation; experiment startup never installs or updates code."""

import argparse
import shutil
import sys
from pathlib import Path

from slow_thinker_ii.adapters.installations import Resolution

from tooling.components.bundle import write_bundle
from tooling.components.prepare import prepare_component, prepare_sequence
from tooling.components.targets import TARGETS


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Prepare independent component installations")
    parser.add_argument("--destination", type=Path, default=root / ".local/components")
    parser.add_argument("--component", choices=(*TARGETS, "all"), default="sequence")
    arguments = parser.parse_args()
    destination = Path(str(arguments.destination)).resolve()
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("The pinned uv executable is required")
    names = TARGETS if arguments.component == "all" else (str(arguments.component),)
    records: dict[str, Resolution] = {}
    for name in names:
        resolution = (
            prepare_sequence(root, destination, Path(uv), Path(sys.executable))
            if name == "sequence"
            else prepare_component(root, destination, Path(uv), Path(sys.executable), name)
        )
        records[name] = resolution
        sys.stdout.write(f"Prepared {resolution.registration.type_id}: {resolution.identity}\n")
    sys.stdout.write(f"Bundle: {write_bundle(destination, records)}\n")


if __name__ == "__main__":
    main()
