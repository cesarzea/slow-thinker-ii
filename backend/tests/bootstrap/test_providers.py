"""The gateway's one provider: routing by each model's provider, keys from the environment.

The dispatch is private to `bootstrap`, so these tests import its module directly.
"""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.application import LlmModel
from slow_thinker_ii.bootstrap import load_configuration
from slow_thinker_ii.bootstrap._providers import ProviderDispatch, configured_provider
from slow_thinker_ii.bootstrap._secrets import EnvironmentSecrets
from slow_thinker_ii.contracts import JsonObject, value_at_pointer
from support.clock import FakeClock
from support.configuration import llm_models
from support.examples import FLASH, LUNA, changed
from support.providers import ScriptedProvider

from .configurations import SECRETS, local, without, written

REQUEST: JsonObject = {"model": LUNA, "messages": [{"role": "user", "content": "A cat."}]}


def simulated(model: LlmModel) -> LlmModel:
    return LlmModel(replace(model.settings, provider="simulated"), model.tariff)


async def test_simulated_models_go_to_the_simulated_provider_and_others_to_http() -> None:
    clock = FakeClock()
    network, scripted = ScriptedProvider(clock), ScriptedProvider(clock)
    dispatch = ProviderDispatch(network, scripted)
    luna, flash = llm_models()
    await dispatch.complete(luna, REQUEST, 5)
    await dispatch.complete(simulated(flash), REQUEST, 5)
    await dispatch.complete(flash, REQUEST, 5)
    assert [request.llm for request in network.requests] == [LUNA, FLASH]
    assert [request.llm for request in scripted.requests] == [FLASH]


async def test_configured_providers_answer_without_reaching_the_network(tmp_path: Path) -> None:
    document = without(local(tmp_path), ("llm", "providers", "deepseek"))
    document = changed(document, ("llm", "providers", "simulated"), {})
    document = changed(document, ("llm", "models", 1, "provider"), "simulated")
    document = changed(document, ("llm", "models", 1, "replies"), ["first", "second"])
    configuration = load_configuration(written(tmp_path, document))
    provider = configured_provider(configuration, EnvironmentSecrets(SECRETS))
    luna, flash = configuration.models
    replies = [await provider.complete(flash, REQUEST, 5) for _ in range(3)]
    contents = [value_at_pointer(r.body, ("choices", 0, "message", "content")) for r in replies]
    assert contents == ["first", "second", "first"]
    no_time = await provider.complete(luna, REQUEST, 0)  # the OpenAI endpoint, nothing sent
    assert no_time.status == 504
    assert no_time.body["error"] == {
        "code": "provider_timeout",
        "message": "No time was left for the provider call.",
        "type": "timeout_error",
    }
    deepseek = llm_models()[1]  # its provider is not configured here
    unconfigured = await provider.complete(deepseek, REQUEST, 5)
    assert (unconfigured.status, unconfigured.body["error"]) == (
        502,
        {
            "code": "provider_error",
            "message": "No provider endpoint is configured for “deepseek”.",
            "type": "provider_error",
        },
    )


def test_a_missing_or_invalid_key_names_its_variable_only(tmp_path: Path) -> None:
    configuration = load_configuration(written(tmp_path, local(tmp_path)))
    missing = {"OPENAI_API_KEY": "sk-openai-test-key"}
    with pytest.raises(ValueError) as raised:
        configured_provider(configuration, EnvironmentSecrets(missing))
    assert str(raised.value) == (
        "The environment variable DEEPSEEK_API_KEY (the deepseek API key) is not set."
    )
    spaced = {**SECRETS, "OPENAI_API_KEY": "sk openai with spaces"}
    with pytest.raises(ValueError, match="The openai provider cannot be used") as invalid:
        configured_provider(configuration, EnvironmentSecrets(spaced))
    assert "sk openai" not in str(invalid.value)
