"""Normalize the reviewed direct OpenAI Standard, nonregional text profile."""

from fractions import Fraction
from hashlib import sha256

from pydantic import JsonValue, TypeAdapter

from slow_thinker_ii.accounting import Tariff, TariffRevision, TokenRates

from ._models import Catalog, ModelEntry, StandardPrices, Tier

SOURCE_URL = "https://ai-gateway.vercel.sh/v1/models"
MODEL_ID = "openai/gpt-6-luna"
PROFILE_ID = "openai.gpt-6-luna.standard.text.v1"
LONG_CONTEXT_START = 272_001


def _prices(values: dict[str, JsonValue]) -> StandardPrices:
    if values.get("varies_by_provider", False) is not False:
        raise ValueError("Provider-dependent rates require a reviewed mapping")
    excluded = {"web_search", "service_tiers", "fast", "regional", "varies_by_provider"}
    standard = {key: value for key, value in values.items() if key not in excluded}
    return StandardPrices.model_validate_json(TypeAdapter(dict[str, JsonValue]).dump_json(standard))


def _rates(tiers: tuple[Tier, Tier], base: str) -> tuple[Fraction, Fraction]:
    short, long = tiers
    if (short.min, short.max, long.min, long.max) != (0, LONG_CONTEXT_START, 272_001, None):
        raise ValueError("Unsupported pricing band boundaries")
    if Fraction(short.cost) != Fraction(base):
        raise ValueError("Inconsistent base and short-context rate")
    return Fraction(short.cost), Fraction(long.cost)


def _tariff(model: ModelEntry) -> Tariff:
    if (model.owned_by, model.type, model.context_window, model.max_tokens) != (
        "openai",
        "language",
        1_050_000,
        128_000,
    ):
        raise ValueError("Model identity or capacity changed; profile review required")
    prices = _prices(model.pricing)
    ordinary = _rates(prices.input_tiers, prices.input)
    cached = _rates(prices.input_cache_read_tiers, prices.input_cache_read)
    writes = _rates(prices.input_cache_write_tiers, prices.input_cache_write)
    output = _rates(prices.output_tiers, prices.output)
    return Tariff(
        PROFILE_ID,
        "gpt-6-luna",
        model.context_window,
        model.max_tokens,
        LONG_CONTEXT_START,
        TokenRates(ordinary[0], cached[0], writes[0], output[0]),
        TokenRates(ordinary[1], cached[1], writes[1], output[1]),
    )


def parse_catalog(payload: bytes, now: int) -> TariffRevision:
    catalog = Catalog.model_validate_json(payload)
    matches = [model for model in catalog.data if model.get("id") == MODEL_ID]
    if len(matches) != 1:
        raise ValueError("Catalogue must contain the selected model exactly once")
    encoded = TypeAdapter(dict[str, JsonValue]).dump_json(matches[0])
    model = ModelEntry.model_validate_json(encoded)
    return TariffRevision(
        sha256(payload).hexdigest(), now, SOURCE_URL, _tariff(model), payload.decode()
    )
