"""Real artifact verification surrounds a controlled process-context boundary."""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from mcp import Client
from slow_thinker_ii.adapters.installations import ComponentRegistration
from slow_thinker_ii.adapters.process import (
    ComponentConnection,
    ComponentProcess,
    HostSettings,
    InstalledProcess,
)
from support.installations import new_catalog
from support.wheels import lockfile, wheel


def installed(directory: Path) -> InstalledProcess:
    catalog = new_catalog(directory)
    artifact = wheel(directory, "sample-host", "1.0", "class Host: pass\n")
    registration = ComponentRegistration(
        type_id="test.host",
        type_version="1",
        distribution="sample-host",
        version="1.0",
        entry_point="sample_host:Host",
    )
    record = catalog.prepare(lockfile(directory, (artifact,)), directory, registration)
    settings = HostSettings(directory / "bootstrap.json", directory, 3, 3, 1000)
    (directory / "bootstrap.json").write_text("{}")
    return InstalledProcess(catalog, record.identity, "test.host", "1", settings, ())


@pytest.fixture
def connected(monkeypatch: pytest.MonkeyPatch) -> list[bool]:
    entered: list[bool] = []

    @asynccontextmanager
    async def controlled(owner: ComponentProcess) -> AsyncIterator[ComponentConnection]:
        assert isinstance(owner, InstalledProcess)
        entered.append(True)
        yield ComponentConnection(Client("http://127.0.0.1:1"), ())

    monkeypatch.setattr(ComponentProcess, "connect", controlled)
    return entered


@pytest.mark.parametrize("phase", ["none", "before", "after", "record"])
async def test_installation_cannot_change_across_admission_and_execution(
    tmp_path: Path, connected: list[bool], phase: str
) -> None:
    process = installed(tmp_path)
    snapshot = json.loads(process.installation_json())
    record = tmp_path / "installations/catalog" / f"{snapshot['identity']}.json"
    changed = json.dumps({**snapshot, "provenance": {"changed": "yes"}})
    if phase == "before":
        path = tmp_path / "installations/resolutions" / snapshot["identity"] / "environment/extra"
        path.write_text("unadmitted mutation")
    elif phase == "record":
        record.write_text(changed)
    if phase == "none":
        async with process.connect() as connection:
            assert connection.operation_names() == ()
        assert connected == [True]
    else:
        with pytest.raises(ValueError, match="changed"):
            async with process.connect():
                assert phase == "after"
                record.write_text(changed)
        assert bool(connected) == (phase == "after")


def test_installed_type_identity_is_checked_before_launch(tmp_path: Path) -> None:
    process = installed(tmp_path)
    snapshot = json.loads(process.installation_json())
    settings = HostSettings(tmp_path / "config", tmp_path, 1, 1, 1000)
    with pytest.raises(ValueError, match="admitted type"):
        InstalledProcess(new_catalog(tmp_path), snapshot["identity"], "other", "1", settings, ())
    assert process.outcome() is None
