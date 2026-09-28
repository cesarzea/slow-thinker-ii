"""Exercise the real HTTP adapter against deterministic transport responses."""

import httpx
import pytest
from slow_thinker_ii.adapters.tariffs import SOURCE_URL, VercelTariffSource, parse_catalog
from support.catalog import PAYLOAD


async def test_public_catalogue_needs_no_credentials() -> None:
    requests: list[httpx.Request] = []

    def reply(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=PAYLOAD)

    revision = await VercelTariffSource(httpx.MockTransport(reply)).fetch(42)
    assert revision == parse_catalog(PAYLOAD, 42)
    assert len(requests) == 1
    assert str(requests[0].url) == SOURCE_URL
    assert "authorization" not in requests[0].headers


@pytest.mark.parametrize("status", [302, 401, 429, 500])
async def test_download_failure_has_no_hidden_retry(status: int) -> None:
    requests: list[httpx.Request] = []

    def reply(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, headers={"Location": "https://other.example"})

    with pytest.raises(OSError):
        await VercelTariffSource(httpx.MockTransport(reply)).fetch(0)
    assert len(requests) == 1


async def test_network_timeout_is_reported() -> None:
    def reply(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    with pytest.raises(OSError):
        await VercelTariffSource(httpx.MockTransport(reply)).fetch(0)


async def test_oversized_download_is_rejected() -> None:
    def reply(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, content=b" " * (4 * 1024 * 1024 + 1))

    with pytest.raises(ValueError, match="download limit"):
        await VercelTariffSource(httpx.MockTransport(reply)).fetch(0)
