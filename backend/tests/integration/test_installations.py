"""Install actual wheels offline; failed updates cannot damage published resolutions."""

import shutil
import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration, InstallationCatalog
from support.wheels import lockfile, wheel

REGISTRATION = ComponentRegistration(
    type_id="test.agent",
    type_version="1",
    distribution="sample-agent",
    version="1.0",
    entry_point="sample_agent:Agent",
)


@pytest.fixture
def catalog(tmp_path: Path) -> InstallationCatalog:
    executable = shutil.which("uv")
    assert executable is not None, "Verification requires uv on PATH"
    return InstallationCatalog(tmp_path / "installations", Path(executable), Path(sys.executable))


def test_verified_environment_uses_wheels_and_survives_failed_update(
    tmp_path: Path,
    catalog: InstallationCatalog,
) -> None:
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent:\n    pass\n")
    lock = lockfile(tmp_path, (artifact,))
    resolution = catalog.prepare(lock, tmp_path, REGISTRATION)
    python = catalog.interpreter(resolution.identity)
    assert python != Path(sys.executable)
    assert resolution.inspection.packages == {"sample-agent": "1.0"}
    assert resolution.registration.type_version == "1"
    assert resolution.schema_version == "1" and resolution.uv_version == "uv 0.12.19"
    assert resolution.inspection.base_entry_point is None
    assert not any("editable" in file for file in resolution.files)
    before = dict(resolution.files)
    artifact.write_bytes(artifact.read_bytes() + b"changed wheel contents")
    with pytest.raises(ValueError, match="hash mismatch"):
        catalog.prepare(lock, tmp_path, REGISTRATION)
    assert catalog.verify(resolution.identity).files == before
    assert len(list((tmp_path / "installations/catalog").glob("*.json"))) == 1


def test_modified_installed_code_prevents_reuse(
    tmp_path: Path, catalog: InstallationCatalog
) -> None:
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent:\n    pass\n")
    resolution = catalog.prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    environment = catalog.interpreter(resolution.identity).parent.parent
    installed = next(environment.glob("lib/python*/site-packages/sample_agent/__init__.py"))
    installed.write_text("class Modified: pass\n")
    with pytest.raises(ValueError, match="environment contents changed"):
        catalog.interpreter(resolution.identity)


def test_missing_dependency_does_not_publish_partial_installation(
    tmp_path: Path,
    catalog: InstallationCatalog,
) -> None:
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent: pass\n", ("missing-base==1.0",))
    with pytest.raises(RuntimeError, match="Installation command failed"):
        catalog.prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    assert not (tmp_path / "installations/catalog").exists()
