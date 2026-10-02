"""Trusted profiles reject malformed identities, capabilities and bounds."""

from dataclasses import replace

import pytest
from model_provider_fixture import config, record
from slow_thinker_host import JsonValue
from slow_thinker_model_provider import parse_config


@pytest.mark.parametrize("provider", ["openai", "deepseek"])
def test_configuration_round_trips_the_explicit_profile(provider: str) -> None:
    selected = parse_config(record(provider))
    assert selected.provider == provider and selected.model_alias == "bound-model"
    assert selected.default_output_tokens == 8 and selected.maximum_output_tokens == 32


@pytest.mark.parametrize(
    "field,value",
    [
        ("provider", "other"),
        ("provider", False),
        ("model", "other"),
        ("model", 1),
        ("model_alias", ""),
        ("model_alias", False),
        ("default_output_tokens", 0),
        ("default_output_tokens", True),
        ("maximum_output_tokens", 1),
        ("maximum_output_tokens", "32"),
        ("reasoning_efforts", {}),
        ("reasoning_efforts", ["high"]),
        ("reasoning_efforts", ["none", 1]),
        ("extra", 1),
    ],
)
def test_invalid_configuration_is_rejected(field: str, value: JsonValue) -> None:
    with pytest.raises(ValueError):
        parse_config({**record(), field: value})


def test_direct_immutable_configuration_checks_its_own_values() -> None:
    with pytest.raises(ValueError):
        replace(config(), model="")
    with pytest.raises(ValueError):
        replace(config("openai"), reasoning_efforts=("high",))
