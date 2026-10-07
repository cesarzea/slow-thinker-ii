"""Configured resolutions as the platform's installed components and launch targets."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import InstalledComponent, InstalledComponents
from slow_thinker_ii.catalog import ComponentRef, parse_declaration
from slow_thinker_ii.contracts import decode_json

from .catalogs import environment, prepared
from .wheels import ROUTER_DECLARATION

ROUTER = ComponentRef("router", "1.0.0")


def test_configured_resolutions_provide_declarations_and_launch_targets(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    installed = InstalledComponents(catalog, [resolution.identity])
    declaration = parse_declaration(decode_json(ROUTER_DECLARATION))
    assert installed.components() == (
        InstalledComponent(resolution.identity, declaration, "sample_agent"),
    )
    assert installed.module(ROUTER) == "sample_agent"
    python = installed.interpreter(ROUTER)
    assert python == environment(catalog, resolution) / "bin/python"
    with pytest.raises(LookupError, match="llm-call@1.0.0"):
        installed.interpreter(ComponentRef("llm-call", "1.0.0"))
    with pytest.raises(LookupError):
        installed.module(ComponentRef("router", "2.0.0"))
    assert InstalledComponents(catalog, []).components() == ()


def test_every_launch_verifies_the_installation_again(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    installed = InstalledComponents(catalog, [resolution.identity])
    module = next(
        environment(catalog, resolution).glob("lib/python*/site-packages/sample_agent/__init__.py")
    )
    module.write_text("print('changed after startup')\n")
    with pytest.raises(ValueError, match="environment contents changed"):
        installed.interpreter(ROUTER)
    assert installed.module(ROUTER) == "sample_agent"


def test_unverifiable_or_conflicting_resolutions_fail_at_construction(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    with pytest.raises(ValueError, match="same component version"):
        InstalledComponents(catalog, [resolution.identity, resolution.identity])
    with pytest.raises(ValueError, match="Invalid installation identity"):
        InstalledComponents(catalog, ["llm-call-resolution-from-make-components"])
    with pytest.raises(FileNotFoundError):
        InstalledComponents(catalog, ["0" * 32])


def test_a_registration_changed_after_publication_is_refused(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    registration = resolution.registration.model_copy(update={"type_version": "1.0.1"})
    forged = resolution.model_copy(update={"registration": registration})
    record = tmp_path / "installations/catalog" / f"{resolution.identity}.json"
    record.write_text(forged.model_dump_json())
    with pytest.raises(ValueError, match="registration names router@1.0.1"):
        InstalledComponents(catalog, [resolution.identity])
