"""Digest-bound direct rates and schedule cannot be swapped independently of a frozen tariff."""

from dataclasses import replace
from hashlib import sha256

import pytest
from slow_thinker_ii.adapters.models import ModelPricePolicy
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from models.fixtures import profile


def changed_source(field: str, value: JsonValue) -> JsonObject:
    source = json_object(decode_json(profile().revision.source_json))
    normalized = json_object(source["normalized"])
    normalized[field] = value
    source["normalized"] = normalized
    return source


@pytest.mark.parametrize(
    "field,value",
    [
        ("model", "other"),
        ("currency", "EUR"),
        ("input_capacity", 1),
        ("cache_creation", "surcharge"),
        ("schedule", {}),
        ("peak", {}),
        ("off_peak", {"input": "1/0", "cached": "1", "cache_write": "1", "output": "1"}),
        ("off_peak", {"input": "1", "cached": "1", "cache_write": "2", "output": "1"}),
        ("off_peak", {"input": "-1", "cached": "1", "cache_write": "-1", "output": "1"}),
        ("off_peak", {"input": 1, "cached": "1", "cache_write": "1", "output": "1"}),
        ("off_peak", {"input": "1", "cached": "1", "cache_write": "1", "output": "1"}),
    ],
)
def test_unreviewed_source_representation_cannot_supply_policy(
    field: str, value: JsonValue
) -> None:
    settings = profile()
    encoded = encode_json(changed_source(field, value))
    revision = replace(
        settings.revision, source_json=encoded, digest=sha256(encoded.encode()).hexdigest()
    )
    with pytest.raises(ValueError):
        ModelPricePolicy(replace(settings, revision=revision))


@pytest.mark.parametrize("fault", ["digest", "origin", "capacity", "context"])
def test_immutable_source_identity_and_domain_semantics_are_validated(fault: str) -> None:
    settings = profile()
    revision = settings.revision
    if fault == "digest":
        revision = replace(revision, digest="0" * 64)
    elif fault == "origin":
        revision = replace(revision, source="https://other.example")
    elif fault == "capacity":
        revision = replace(revision, tariff=replace(revision.tariff, input_capacity=2_000_000))
    else:
        revision = replace(revision, tariff=replace(revision.tariff, long_context_start=1))
    with pytest.raises(ValueError):
        ModelPricePolicy(replace(settings, revision=revision))
