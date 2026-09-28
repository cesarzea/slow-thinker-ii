"""Production graph preparation with injectable, registered host-profile extensions."""

from ._endpoints import ServiceEndpoints
from ._host_profiles import HostAdapter, HostProfile, HostRequest, PlainHostAdapter
from ._models import ResourceSettings
from ._openai_hosts import OpenAIClientAdapter, OpenAIResourceAdapter
from ._preparer import InstalledWorkflowPreparer
from ._secrets import EnvironmentSecrets, SecretSource


def standard_host_adapters() -> dict[str, HostAdapter]:
    return {
        "mcp": PlainHostAdapter(),
        "openai-client": OpenAIClientAdapter(),
        "openai-model": OpenAIResourceAdapter(),
    }


__all__ = [
    "ResourceSettings",
    "ServiceEndpoints",
    "HostAdapter",
    "HostProfile",
    "HostRequest",
    "PlainHostAdapter",
    "OpenAIClientAdapter",
    "OpenAIResourceAdapter",
    "InstalledWorkflowPreparer",
    "EnvironmentSecrets",
    "SecretSource",
    "standard_host_adapters",
]
