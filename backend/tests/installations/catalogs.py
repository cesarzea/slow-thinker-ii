"""Installation catalogs on the repository's pinned toolchain, and the sample component."""

import shutil
import sys
from collections.abc import Mapping
from pathlib import Path

from slow_thinker_ii.adapters.installations import (
    ComponentRegistration,
    InstallationCatalog,
    Resolution,
)

from .wheels import component_files, lockfile, wheel

REGISTRATION = ComponentRegistration(
    type="router",
    type_version="1.0.0",
    distribution="sample-agent",
    version="1.0",
    module="sample_agent",
)


def new_catalog(directory: Path) -> InstallationCatalog:
    executable = shutil.which("uv")
    assert executable is not None, "Verification requires uv on PATH"
    return InstallationCatalog(directory / "installations", Path(executable), Path(sys.executable))


def sample_wheel(directory: Path, files: Mapping[str, str] | None = None) -> Path:
    """`sample-agent` 1.0 shipping `sample_agent` with the Router's declaration by default."""
    return wheel(directory, "sample-agent", "1.0", files or component_files("sample_agent"))


def prepared(
    directory: Path, registration: ComponentRegistration = REGISTRATION
) -> tuple[InstallationCatalog, Resolution]:
    """A catalog in `directory` with the sample component installed and published."""
    directory.mkdir(parents=True, exist_ok=True)
    catalog = new_catalog(directory)
    lock = lockfile(directory, (sample_wheel(directory),))
    return catalog, catalog.prepare(lock, directory, registration, {"source": "tests"})


def environment(catalog: InstallationCatalog, resolution: Resolution) -> Path:
    """The installed environment of a resolution, from its verified interpreter."""
    return catalog.interpreter(resolution.identity).parent.parent
