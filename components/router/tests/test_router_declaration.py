"""The packaged declaration is the contract example; configurations are checked against it."""

import json
from pathlib import Path

import pytest
from router_fakes import config
from slow_thinker_host import JsonObject, read_declaration
from slow_thinker_router import RouterConfig, parse_config

EXAMPLE = Path(__file__).resolve().parents[3] / "docs/contracts/examples/router.component.json"


def test_packaged_declaration_equals_the_contract_example() -> None:
    assert read_declaration("slow_thinker_router") == json.loads(EXAMPLE.read_text("utf-8"))


def test_initial_configuration_of_the_declaration_is_runnable() -> None:
    initial = read_declaration("slow_thinker_router")["initial_config"]
    assert isinstance(initial, dict)
    assert parse_config(initial) == RouterConfig(
        ("yes", "no"), 'def route(received, node_input):\n    return "yes", received\n'
    )


@pytest.mark.parametrize(
    "settings",
    [
        {**config(), "outputs": []},
        {**config(), "outputs": ["Accepted"]},
        {**config(), "outputs": ["yes", "yes"]},
        {**config(), "script": ""},
        {**config(), "extra": True},
        {"outputs": ["yes"]},
    ],
)
def test_invalid_configurations_are_rejected(settings: JsonObject) -> None:
    with pytest.raises(ValueError, match="The Router configuration is invalid"):
        parse_config(settings)
