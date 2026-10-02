"""Backend resource selection is explicit, versioned and contains references, never credentials."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

Positive = Annotated[int, Field(gt=0)]
Identity = Annotated[str, Field(min_length=1)]


class Record(BaseModel, extra="forbid", strict=True, frozen=True):
    """Unknown options cannot silently change the execution or billing profile."""


class InstallationChoice(Record, frozen=True):
    type_id: Identity
    type_version: Identity
    resolution_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    host_adapter: Identity


class ProviderProfile(Record, frozen=True):
    provider: Literal["openai", "deepseek"] = "openai"
    billing_profile: Identity = "openai.gpt-6-luna.standard.text.v1"
    model: Identity
    returned_models: tuple[Identity, ...] = Field(min_length=1)
    credential_ref: Identity
    default_output_tokens: Positive
    maximum_output_tokens: Positive
    review_expires_at: Positive
    maximum_tariff_age_seconds: Positive


class ResourceSettings(Record, frozen=True):
    schema_version: Literal["1"]
    installations: tuple[InstallationChoice, ...] = Field(min_length=1)
    providers: dict[str, ProviderProfile]


class ModelReference(Record, frozen=True):
    provider_profile: Identity
    model: Identity
