"""The gateway's one `LlmProvider`: simulated models to the simulated provider, others to HTTP."""

from slow_thinker_ii.adapters.providers import HttpProvider, ProviderEndpoint, SimulatedProvider
from slow_thinker_ii.application import LlmModel, LlmProvider, ProviderReply
from slow_thinker_ii.contracts import JsonObject

from ._configuration import ProviderSection, ServerConfiguration
from ._models import SIMULATED
from ._secrets import EnvironmentSecrets


class ProviderDispatch:
    """Routes each call by `model.settings.provider`.

    Configuration validation guarantees that every model's provider is configured; for any other
    provider the HTTP provider answers 502 without sending anything.
    """

    def __init__(self, network: LlmProvider, simulated: LlmProvider) -> None:
        self._network = network
        self._simulated = simulated

    async def complete(
        self, model: LlmModel, request: JsonObject, timeout_s: float
    ) -> ProviderReply:
        simulated = model.settings.provider == SIMULATED
        provider = self._simulated if simulated else self._network
        return await provider.complete(model, request, timeout_s)


def configured_provider(
    configuration: ServerConfiguration, secrets: EnvironmentSecrets
) -> ProviderDispatch:
    """One endpoint per configured network provider, with its key read from the environment."""
    endpoints = {section.name: _endpoint(section, secrets) for section in configuration.providers}
    return ProviderDispatch(HttpProvider(endpoints), SimulatedProvider(configuration.replies))


def _endpoint(section: ProviderSection, secrets: EnvironmentSecrets) -> ProviderEndpoint:
    key = secrets.require(section.credential_env, f"the {section.name} API key")
    try:
        return ProviderEndpoint(section.name, section.base_url, key, section.timeout_seconds)
    except ValueError as error:  # its message repeats neither the URL nor the key
        raise ValueError(f"The {section.name} provider cannot be used: {error}") from None
