"""Reject incompatible billing evidence instead of inventing absent rates."""

import pytest
from slow_thinker_ii.adapters.tariffs import parse_catalog
from support.catalog import PAYLOAD


@pytest.mark.parametrize(
    "before, after",
    [
        (b'"input": "0.0000001"', b'"input": null'),
        (b'"input": "0.0000001"', b'"input": "NaN"'),
        (b'"input": "0.0000001"', b'"input": "-1"'),
        (b'"input": "0.0000001"', b'"input": 0.0000001'),
        (b'"input": "0.0000001"', b'"input": "0.0000002"'),
        (b'"input": "0.0000001"', b'"new_charge": "1", "input": "0.0000001"'),
        (b'"input": "0.0000001"', b'"varies_by_provider": true, "input": "0.0000001"'),
        (b'"max": 272001', b'"max": 272000'),
        (b'"context_window": 1050000', b'"context_window": 2000000'),
        (b'"owned_by": "openai"', b'"owned_by": "other"'),
        (b'"input_cache_write":', b'"unknown_cache_category":'),
        (b'"id": "openai/gpt-6-luna"', b'"id": "openai/other"'),
    ],
)
def test_rejects_incompatible_catalogue(before: bytes, after: bytes) -> None:
    assert before in PAYLOAD
    with pytest.raises(ValueError):
        parse_catalog(PAYLOAD.replace(before, after, 1), 0)


@pytest.mark.parametrize("payload", [b"{}", b"null", b'{"object":"list","data":[]}'])
def test_missing_catalogue(payload: bytes) -> None:
    with pytest.raises(ValueError):
        parse_catalog(payload, 0)


def test_rate_changes_preserve_semantics_and_make_new_revision() -> None:
    old = parse_catalog(PAYLOAD, 1)
    new = parse_catalog(PAYLOAD.replace(b'"0.0000001"', b'"0.00000015"'), 2)
    assert old.digest != new.digest
    assert old.tariff.short.input < new.tariff.short.input
    assert old.tariff.long == new.tariff.long
