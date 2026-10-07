"""Standalone inspection run as a script by an installed environment's isolated interpreter.

It reads distribution metadata and the shipped declaration file only: nothing of the component
is imported or executed. Arguments: distribution, distribution version, module. It is never
imported: running the file prints its report.
"""

import json
import sys
import sysconfig
from importlib import metadata


def declaration(distribution: str, version: str, module: str) -> str:
    """The text of `<module>/component.json`, which the registered distribution must ship."""
    package = metadata.distribution(distribution)
    if package.version != version:
        raise ValueError("Installed component version differs from registration")
    files = {file.as_posix(): file for file in package.files or ()}
    folder = module.replace(".", "/")
    if f"{folder}/__main__.py" not in files:
        raise ValueError("The registered module has no __main__ in its distribution")
    shipped = files.get(f"{folder}/component.json")
    if shipped is None:
        raise ValueError("The registered module ships no component.json")
    return shipped.read_text(encoding="utf-8")


def main() -> None:
    distribution, version, module = sys.argv[1:]
    text = declaration(distribution, version, module)
    packages = {str(item.metadata["Name"]): item.version for item in metadata.distributions()}
    report = {
        "python": sys.version,
        "platform": sysconfig.get_platform(),
        "packages": packages,
        "declaration": text,
    }
    sys.stdout.write(json.dumps(report))


main()
