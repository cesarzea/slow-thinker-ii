"""Standalone inspection executed by the installed environment's isolated interpreter."""

import importlib
import inspect
import json
import sys
import sysconfig
from importlib import metadata
from pathlib import Path
from typing import cast


def registered_class(distribution: str, version: str, entry_point: str) -> type[object]:
    package = metadata.distribution(distribution)
    if package.version != version:
        raise ValueError("Installed component version differs from registration")
    module, name = entry_point.split(":")
    component: object = getattr(importlib.import_module(module), name)
    if not isinstance(component, type):
        raise ValueError("Registered component must be a public class")
    origin = Path(inspect.getfile(component)).resolve()
    if origin not in {
        Path(str(package.locate_file(file))).resolve() for file in package.files or ()
    }:
        raise ValueError("Registered class does not belong to its distribution")
    return cast(type[object], component)


def main() -> None:
    distribution, version, entry_point, base_name, base_version, base_entry = sys.argv[1:]
    component = registered_class(distribution, version, entry_point)
    if base_name:
        base = registered_class(base_name, base_version, base_entry)
        if component is base or not issubclass(component, base):
            raise ValueError("The component does not inherit from its registered base")
    packages = {str(item.metadata["Name"]): item.version for item in metadata.distributions()}
    sys.stdout.write(
        json.dumps(
            {
                "python": sys.version,
                "platform": sysconfig.get_platform(),
                "packages": packages,
                "entry_point": entry_point,
                "requirements": metadata.requires(distribution) or [],
                "base_entry_point": base_entry or None,
            }
        )
    )


if __name__ == "__main__":
    main()
