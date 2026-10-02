"""Official table parsing rejects unreviewed identity, rates and structure."""

from hashlib import sha256

import pytest
from slow_thinker_ii.adapters.tariffs import (
    DEEPSEEK_PROFILE_ID,
    DEEPSEEK_SOURCE_URL,
    parse_deepseek_pricing,
)
from slow_thinker_ii.contracts import decode_json, json_object
from support.preparation import NOW
from support.workspace_tariffs import DEEPSEEK_PAYLOAD


def test_official_fixture_retains_digest_bound_source_and_peak_context_bands() -> None:
    revision = parse_deepseek_pricing(DEEPSEEK_PAYLOAD, NOW)
    source = json_object(decode_json(revision.source_json))
    normalized = json_object(source["normalized"])
    assert revision.digest == sha256(revision.source_json.encode()).hexdigest()
    assert revision.source == DEEPSEEK_SOURCE_URL and revision.tariff.profile == DEEPSEEK_PROFILE_ID
    assert source["captured_html"] == DEEPSEEK_PAYLOAD.decode()
    assert revision.tariff.short == revision.tariff.long
    assert revision.tariff.long_context_start > revision.tariff.input_capacity
    assert normalized["peak"] == {
        "input": "3/10000000",
        "cached": "3/500000000",
        "cache_write": "3/10000000",
        "output": "3/2500000",
    }
    assert json_object(normalized["schedule"])["excluding_chinese_public_holidays"] is True


@pytest.mark.parametrize(
    "before,after",
    [
        (b"deepseek-flash", b"other-model"),
        (b"1M</td>", b"2M</td>"),
        (b"MAXIMUM: 384K", b"MAXIMUM: 400K"),
        (b"https://api.deepseek.com</a>", b"https://other.example</a>"),
        (b"$0.003", b"EUR 0.003"),
        (b"$0.003", b"$0.004"),
        (b"$0.003", b"$-1"),
        (b"1M INPUT TOKENS<br>(CACHE HIT)", b"UNKNOWN CATEGORY"),
        (b"<td>PEAK</td>", b"<td>OFF-PEAK</td>"),
        (b"excluding Chinese public holidays", b"including Chinese public holidays"),
        (b'colspan="3"', b'colspan="6"'),
        (b'rowspan="6"', b'rowspan="65"'),
        (b'rowspan="6"', b'rowspan="x"'),
        (b"</table>", b""),
        (b"</table>", b"</table><table></table>"),
    ],
)
def test_changed_official_structure_or_semantics_is_rejected(before: bytes, after: bytes) -> None:
    assert before in DEEPSEEK_PAYLOAD
    with pytest.raises(ValueError):
        parse_deepseek_pricing(DEEPSEEK_PAYLOAD.replace(before, after, 1), NOW)


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"<table><td>x</td></table>",
        b"<table><tr><td><td>x</td></td></tr></table>",
        b"<table><tr><td rowspan='2' colspan='5'>x</td></tr></table>",
        b"<table><tr><td>x</td></tr><tr><td colspan='5'>x</td></tr></table>",
        b"<table><tr><td>x</td><td rowspan='2'>x</td><td colspan='3'>x</td></tr>"
        + b"<tr><td colspan='2'>x</td><td colspan='3'>x</td></tr></table>",
        b"<table><tr><td rowspan='0'>x</td></tr></table>",
        b"<table>" + b"<tr></tr>" * 65 + b"</table>",
        b"<i>" * 10001,
        b"<table><tr><td colspan='5'>x</td></tr></table>",
        b"\xff",
    ],
)
def test_malformed_or_excessive_html_is_rejected(content: bytes) -> None:
    with pytest.raises(ValueError):
        parse_deepseek_pricing(content, NOW)


def test_capture_and_clock_bounds_are_checked_before_parsing() -> None:
    for timestamp in (-1, True):
        with pytest.raises(ValueError):
            parse_deepseek_pricing(DEEPSEEK_PAYLOAD, timestamp)
    with pytest.raises(ValueError):
        parse_deepseek_pricing(b"x" * (256 * 1024 + 1), NOW)
