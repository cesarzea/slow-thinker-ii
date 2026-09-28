"""Parse supported billing semantics explicitly; catalogue metadata stays opaque."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, JsonValue

type Price = Annotated[str, Field(pattern=r"^(?:0|[1-9]\d{0,2})(?:\.\d{1,18})?$")]


class Tier(BaseModel, extra="forbid", strict=True):
    cost: Price
    min: int = 0
    max: int | None = None


class StandardPrices(BaseModel, extra="forbid", strict=True):
    input: Price
    output: Price
    input_cache_read: Price
    input_cache_write: Price
    input_tiers: tuple[Tier, Tier]
    output_tiers: tuple[Tier, Tier]
    input_cache_read_tiers: tuple[Tier, Tier]
    input_cache_write_tiers: tuple[Tier, Tier]


class ModelEntry(BaseModel, extra="allow", strict=True):
    id: str
    owned_by: str
    context_window: int
    max_tokens: int
    type: str
    pricing: dict[str, JsonValue]


class Catalog(BaseModel, extra="forbid", strict=True):
    object: Literal["list"]
    data: list[dict[str, JsonValue]]
