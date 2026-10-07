"""Packaged declarations are read as data and gate the bootstrap a host starts with."""

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from host_fixtures import bootstrap
from slow_thinker_host import JsonObject, JsonValue, check_bootstrap, read_declaration

DECLARATION: JsonObject = {
    "type": "echo",
    "version": "1.0.0",
    "placements": ["node"],
    "config_schema": {
        "type": "object",
        "properties": {"mode": {"enum": ["loud", "quiet"]}},
        "additionalProperties": False,
    },
}


def test_declaration_is_read_from_the_package_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "declared_fixture"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "component.json").write_text(json.dumps(DECLARATION), encoding="utf-8")
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])
    assert read_declaration("declared_fixture") == DECLARATION


def test_matching_bootstrap_is_accepted() -> None:
    check_bootstrap(replace(bootstrap(), config={"mode": "loud"}), DECLARATION)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("component", "echo@2.0.0", "names echo@2.0.0, not echo@1.0.0"),
        ("position", "output", "cannot be placed at position output"),
        ("config", {"mode": "silent"}, "configuration is invalid: /mode: 'silent' is not one"),
    ],
)
def test_mismatching_bootstrap_is_rejected(field: str, value: JsonValue, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        check_bootstrap(replace(bootstrap(), **{field: value}), DECLARATION)


@pytest.mark.parametrize(
    "declaration",
    [{**DECLARATION, "placements": "node"}, {**DECLARATION, "config_schema": None}],
)
def test_malformed_declarations_are_rejected(declaration: JsonObject) -> None:
    with pytest.raises(ValueError):
        check_bootstrap(bootstrap(), declaration)
