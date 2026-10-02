"""Personal routes inherit operator authority and remain absent from viewer composition."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slow_thinker_ii.bootstrap import create_app
from support.catalog import RecordedCatalog
from support.definition_http import PARENT, ROOT, DefinitionHttp, reference, variant
from support.operator_http import ORIGIN, TOKEN


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", ROOT),
        ("GET", ROOT + "/source"),
        ("GET", ROOT + "/detail"),
        ("POST", ROOT),
        ("POST", ROOT + "/validate"),
        ("POST", ROOT + "/draft"),
    ],
)
@pytest.mark.parametrize(
    "header,value,status",
    [
        ("authorization", "Bearer wrong", 401),
        ("host", "evil.example", 403),
        ("origin", "http://evil.example", 403),
        ("sec-fetch-site", "cross-site", 403),
    ],
)
async def test_all_routes_require_operator_authority(
    definitions: DefinitionHttp, method: str, path: str, header: str, value: str, status: int
) -> None:
    response = await definitions.client.request(
        method, path, content=variant(), headers={header: value}
    )
    assert response.status_code == status and TOKEN not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert all(item.origin == "bundled" for item in definitions.service.page(100).items)


@pytest.mark.parametrize("header", ["authorization", "host", "origin"])
async def test_duplicate_authority_headers(definitions: DefinitionHttp, header: str) -> None:
    value = "127.0.0.1:8000" if header == "host" else definitions.client.headers[header]
    response = await definitions.client.get(ROOT, headers=[(header, value)] * 2)
    assert response.status_code in (401, 403)


def test_viewer_exposes_bundled_catalog_without_authoring_routes(tmp_path: Path) -> None:
    app = create_app(tmp_path / "viewer.sqlite", RecordedCatalog())
    with TestClient(app, base_url=ORIGIN) as client:
        assert client.get("/api/v1/graphs").status_code == 200
        for path in (ROOT, ROOT + "/source", ROOT + "/detail"):
            assert client.get(path, params=PARENT).status_code == 404
        for path in (ROOT, ROOT + "/validate", ROOT + "/draft"):
            assert (
                client.post(path, json={"source": PARENT, "target": reference()}).status_code == 404
            )
