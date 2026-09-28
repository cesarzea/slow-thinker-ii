"""Protocol failures remain bounded and distinct from durable admission rejections."""

import pytest
from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.application import PreparationRejected
from support.operator_http import ORIGIN, TOKEN, HttpCase, payload


@pytest.mark.parametrize(
    "url,body,status",
    [
        (
            "/api/v1/sessions",
            {"schema_version": "0.1-draft", "command_id": "blank", "name": " "},
            422,
        ),
        ("/api/v1/runs/missing/stop", {"schema_version": "0.1-draft", "command_id": "stop"}, 404),
        (
            "/api/v1/commands/other/withdraw",
            {"schema_version": "0.1-draft", "command_id": "start"},
            422,
        ),
    ],
)
async def test_command_specific_validation(
    api: HttpCase, url: str, body: dict[str, str], status: int
) -> None:
    assert (await api.client.post(url, json=body)).status_code == status


@pytest.mark.parametrize(
    "reason,status",
    [
        ("invalid_graph_or_resource_configuration", 422),
        ("snapshot_limit", 413),
        ("credential_unavailable", 503),
        ("configuration_changed", 409),
    ],
)
async def test_rejection_status_and_durable_receipt(
    api: HttpCase, reason: str, status: int
) -> None:
    api.case.preparer.failure = PreparationRejected(reason)
    response = await api.client.post("/api/v1/runs", json=api.start())
    assert response.status_code == status
    assert payload(response)["reason"] == reason
    assert payload(await api.client.get("/api/v1/commands/start"))["disposition"] == "rejected"


async def test_mutations_reject_transport_options(api: HttpCase) -> None:
    assert (
        await api.client.post("/api/v1/runs?override=true", json=api.start())
    ).status_code == 400
    assert (
        await api.client.post(
            "/api/v1/runs", json=api.start(), headers={"content-encoding": "gzip"}
        )
    ).status_code == 400
    assert (await api.client.post("/api/v1/runs", content="not json")).status_code == 415


@pytest.mark.parametrize(
    "credential,origins,hosts",
    [
        ("too-short", (ORIGIN,), ("127.0.0.1:8000",)),
        (TOKEN, (), ("127.0.0.1:8000",)),
        (TOKEN, (ORIGIN,), ()),
        (TOKEN, ("https://remote.example",), ("remote.example",)),
        (TOKEN, (ORIGIN + "/path",), ("127.0.0.1:8000",)),
        (TOKEN, (ORIGIN,), ("localhost:8000",)),
    ],
)
def test_invalid_authority_configuration(
    credential: str, origins: tuple[str, ...], hosts: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError):
        OperatorAccess(credential, origins, hosts)
