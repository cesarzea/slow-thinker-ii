"""The shipped declaration is read from the installed package and must match the registration."""

import json
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration

from .catalogs import REGISTRATION, new_catalog, sample_wheel
from .wheels import ROUTER_DECLARATION, component_files, lockfile


def refused(directory: Path, files: dict[str, str], registration: ComponentRegistration) -> str:
    """The message of a refused preparation, after checking that nothing was published."""
    lock = lockfile(directory, (sample_wheel(directory, files),))
    with pytest.raises((ValueError, RuntimeError)) as raised:
        new_catalog(directory).prepare(lock, directory, registration)
    assert not (directory / "installations/catalog").exists()
    return str(raised.value)


def test_a_declaration_of_another_version_is_refused(tmp_path: Path) -> None:
    registration = REGISTRATION.model_copy(update={"type_version": "2.0.0"})
    message = refused(tmp_path, component_files("sample_agent"), registration)
    assert message == (
        "The installed declaration is router@1.0.0, but the registration names router@2.0.0"
    )


def test_a_declaration_of_another_type_is_refused(tmp_path: Path) -> None:
    document = json.loads(ROUTER_DECLARATION)
    document["type"] = "classifier"
    files = component_files("sample_agent", json.dumps(document))
    message = refused(tmp_path, files, REGISTRATION)
    assert "is classifier@1.0.0, but the registration names router@1.0.0" in message


def test_an_invalid_declaration_is_refused(tmp_path: Path) -> None:
    document = json.loads(ROUTER_DECLARATION)
    del document["ports"]
    files = component_files("sample_agent", json.dumps(document))
    assert "ports" in refused(tmp_path, files, REGISTRATION)


def test_a_package_without_its_declaration_is_refused(tmp_path: Path) -> None:
    files = component_files("sample_agent", declaration=None)
    assert "ships no component.json" in refused(tmp_path, files, REGISTRATION)


def test_a_module_that_cannot_run_is_refused(tmp_path: Path) -> None:
    files = component_files("sample_agent")
    del files["sample_agent/__main__.py"]
    assert "has no __main__" in refused(tmp_path, files, REGISTRATION)


def test_a_module_of_another_distribution_is_refused(tmp_path: Path) -> None:
    registration = REGISTRATION.model_copy(update={"module": "json"})
    assert "has no __main__" in refused(tmp_path, component_files("sample_agent"), registration)


@pytest.mark.parametrize(
    "field,value",
    [("type", "Router"), ("type_version", "1.0"), ("module", "sample-agent"), ("module", "")],
)
def test_malformed_registrations_are_refused(field: str, value: str) -> None:
    document = REGISTRATION.model_dump()
    document[field] = value
    with pytest.raises(ValueError, match=field):
        ComponentRegistration.model_validate(document)


def test_a_registration_reads_the_file_that_component_tooling_writes() -> None:
    text = '{"type": "router", "type_version": "1.0.0", "distribution": "sample-agent",'
    text += ' "version": "1.0", "module": "sample_agent"}'
    assert ComponentRegistration.model_validate_json(text) == REGISTRATION
    with pytest.raises(ValueError, match="entry_point"):
        ComponentRegistration.model_validate_json(text[:-1] + ', "entry_point": "x:Y"}')
