"""Installation test configuration uses the repository's pinned toolchain."""

import shutil
import sys
from pathlib import Path

from slow_thinker_ii.adapters.installations import InstallationCatalog


def new_catalog(directory: Path) -> InstallationCatalog:
    executable = shutil.which("uv")
    assert executable is not None, "Verification requires uv on PATH"
    return InstallationCatalog(directory / "installations", Path(executable), Path(sys.executable))
